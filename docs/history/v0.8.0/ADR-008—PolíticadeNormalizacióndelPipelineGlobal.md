# ADR-008 — Política de Normalización del Pipeline Global

**Proyecto:** Prospector CLI  
**Versión objetivo:** v0.8.x  
**Tipo:** Architecture Decision Record (ADR)  
**Estado:** APPROVED — Owner Decision  
**Baseline técnico:** v0.7.x — `ee6b69e`  
**Rama de desarrollo:** `v0.8.0`  
**Baseline documental:** `482ab03`  
**Componente:** Prospector Engine — Global Normalization Pipeline  
**Alcance:** Arquitectura, contratos y política de normalización  

---

# 1. Contexto

Prospector CLI es una herramienta de prospección que obtiene, estructura y enriquece información empresarial mediante pipelines de extracción específicos para cada fuente.

La arquitectura del proyecto distingue entre:

- **Interfaces consumidoras:** responsables de configurar búsquedas, solicitar ejecuciones y presentar resultados.
- **Prospector Engine:** responsable de gobernar el pipeline global de procesamiento.
- **Pipelines internos de fuentes:** responsables de navegar, extraer y enriquecer información.
- **Modelos de datos:** responsables de representar los resultados obtenidos.
- **Servicios de exportación:** responsables de producir las salidas solicitadas por los consumidores.

Actualmente, Google Maps es la única fuente implementada.

Durante `v0.7.x` se estabilizó su pipeline interno, integrado por las fases de:

1. Obtención de candidatos y extracción inicial (*Summary*).
2. Recuperación y verificación de información específica (*Detail*).
3. Enriquecimiento mediante los sitios web disponibles (*Website*).

Este proceso genera objetos `Business` que representan los datos consolidados de cada negocio.

Los resultados son funcionales, pero pueden presentar variaciones de capitalización, formato, espacios y representación, determinadas por las fuentes consultadas.

La arquitectura global del proyecto contempla una etapa posterior de **normalización determinista** destinada a producir información consistente y homogénea.

`v0.8.x` implementará dicha etapa sin modificar las responsabilidades ni el comportamiento funcional de los pipelines internos existentes.

La normalización no debe confundirse con extracción, enriquecimiento, identificación de negocios, validación factual, deduplicación o fusión de registros.

---

# 2. Problema arquitectónico

Actualmente, el resultado de extracción se entrega directamente mediante `SearchResult`, sin una etapa global e independiente de normalización.

Esto genera las siguientes limitaciones:

- Diferencias de presentación entre campos equivalentes.
- Ausencia de una representación normalizada explícita.
- Imposibilidad de consultar simultáneamente resultados originales y normalizados mediante un contrato establecido.
- Dependencia de las transformaciones particulares de cada extractor.
- Riesgo de introducir normalizaciones diferentes entre consumidores.
- Falta de una política común para errores y transformaciones parciales.

La solución debe permitir que toda fuente incorporada al motor produzca datos originales consolidados y que éstos atraviesen una etapa común de normalización.

También debe evitar la pérdida de información y conservar el funcionamiento del pipeline de Google Maps validado durante `v0.7.x`.

---

# 3. Decisión arquitectónica

## 3.1 Alternativa seleccionada

Se adopta formalmente:

**B + R3 — Frontera común de normalización con representación independiente.**

La normalización constituye una etapa obligatoria del pipeline global de Prospector Engine.

El motor deberá:

1. Ejecutar el pipeline interno de la fuente seleccionada.
2. Recibir los negocios originales consolidados.
3. Aplicar normalización determinista.
4. Generar una representación independiente por negocio.
5. Conservar las representaciones originales.
6. Consolidar resultados normalizados, originales e incidencias.
7. Entregar el resultado al consumidor correspondiente.

La normalización será ejecutada por un componente especializado, independiente de cualquier fuente.

No se implementarán reglas generales de normalización directamente en los scrapers de origen.

## 3.2 Pipeline objetivo

```text
Consumer
    |
    v
SearchQuery / EngineConfig
    |
    v
ProspectorEngine
    |
    v
GLOBAL PIPELINE
    |
    +-- Source Pipeline
    |       |
    |       +-- Google Maps
    |               |
    |               +-- Navigation
    |               +-- Result Feed / Summary
    |               +-- Detail Enrichment
    |               +-- Website Enrichment
    |               |
    |               v
    |          Business[]
    |
    v
Normalization Pipeline
    |
    +-- Deterministic Field Rules
    +-- Field-Level Recovery
    +-- Normalization Issues
    |
    v
NormalizedBusiness[]
    |
    v
Global Search Result
    |
    +-- Normalized Businesses
    +-- Original Businesses
    +-- Search Issues
    +-- Execution Metadata
    |
    v
Consumer
    |
    +-- CLI
    |     +-- Normalized Output
    |     +-- CSV / XLSX
    |
    +-- Python Consumer
          +-- Normalized Output
          +-- Original Output
```

La arquitectura permitirá incorporar otros pipelines de fuentes sin duplicar el módulo de normalización.

El contrato general del pipeline deberá permanecer estable entre versiones, aunque su implementación interna pueda evolucionar manteniendo compatibilidad.

---

# 4. Obligatoriedad de normalización

La normalización es **obligatoria**.

Toda búsqueda que utilice las rutas soportadas del motor deberá atravesar el pipeline global de normalización después de finalizar la extracción y el enriquecimiento correspondientes.

No se establece un modo opt-in ni un mecanismo para omitir la normalización durante la operación normal del motor.

La obligación aplica a:

- ProspectorEngine.
- CLI.
- Consumidores Python.
- Rutas históricas de acceso a extracción que continúen siendo soportadas.
- Nuevos consumidores incorporados posteriormente.

Los consumidores pueden decidir qué representación mostrar, conservar o exportar, pero no decidir si el motor ejecuta la normalización.

La política de presentación es distinta de la política de procesamiento.

---

# 5. Definición de resultado original

## 5.1 Business original

Se define como **resultado original** el objeto `Business` consolidado que actualmente produce el pipeline de extracción y enriquecimiento de `v0.7.x`.

Este resultado comprende los datos disponibles después de completar las operaciones de la fuente.

Puede incluir:

- Parsing.
- Extracción de campos.
- Enriquecimiento.
- Transformaciones históricas implementadas.
- Recuperación parcial de datos.
- Correcciones específicas del extractor ya aprobadas.

Por tanto, *original* no significa HTML sin procesar, atributos del DOM ni respuestas originales del navegador.

El objetivo es preservar exactamente el resultado funcional consolidado del motor previo a la normalización.

## 5.2 Inmutabilidad lógica del original

El proceso de normalización no deberá modificar los objetos `Business` recibidos.

Los valores originales permanecerán disponibles tras generar la representación normalizada.

La independencia entre ambas representaciones será una garantía obligatoria del módulo.

No se permitirá que las modificaciones posteriores sobre una representación alteren accidentalmente la otra.

---

# 6. Modelo NormalizedBusiness

## 6.1 Modelo independiente

Se aprueba la creación de un modelo específico:

`NormalizedBusiness`

Su responsabilidad será representar los campos de un negocio después de aplicar la política de normalización.

`NormalizedBusiness` no sustituye la responsabilidad de `Business` dentro del pipeline de extracción.

Ambos representan el mismo negocio desde etapas distintas del procesamiento global.

## 6.2 Correspondencia estructural

La representación normalizada mantendrá correspondencia con los campos soportados de `Business`.

El modelo inicial comprenderá:

```python
name
category
address
phone
website
email
language
website_title
website_description
has_contact_page
has_about_page
website_status
```

No se añadirán campos derivados que impliquen inferencia, enriquecimiento o clasificación empresarial.

## 6.3 Independencia

Cada `NormalizedBusiness` se construirá sin compartir estado mutable con su `Business` original.

La independencia deberá mantenerse incluso si posteriormente se incorporan estructuras internas mutables.

No se aceptará una copia superficial cuando ésta permita contaminación entre representaciones.

## 6.4 Identidad y cardinalidad

Cada Business original producirá exactamente un NormalizedBusiness.

La normalización no podrá:

- Crear negocios adicionales.
- Eliminar negocios existentes.
- Reordenar resultados.
- Fusionar negocios.
- Deduplicar negocios.
- Cambiar la identidad empresarial.
- Mezclar campos entre negocios diferentes.

Se establece:

```text
len(original_businesses)
    ==
len(normalized_businesses)
```

Para cada posición `i`:

```text
original_businesses[i]
    corresponde a
normalized_businesses[i]
```

La identidad de origen permanece gobernada por el pipeline específico de extracción.

No se realizarán nuevas operaciones de identificación empresarial durante normalización.

---

# 7. Contrato del resultado global

## 7.1 Evolución de SearchResult

El resultado público deberá permitir recuperar:

- Consulta realizada.
- Negocios normalizados.
- Negocios originales.
- Tiempo de ejecución.
- Incidencias recuperables.
- Cantidad total de negocios.

Se conservará el significado de `total_found`.

La cantidad total dependerá del número de negocios extraídos, no del éxito individual de sus campos normalizados.

## 7.2 Representación predeterminada

La representación predeterminada entregada para presentación y exportación será la normalizada.

Se establece conceptualmente:

```python
result.businesses
# NormalizedBusiness[]

result.original_businesses
# Business[]

result.total_found
# Count of extracted businesses

result.issues
# SearchIssue[]
```

La definición concreta de propiedades, constructores y almacenamiento interno corresponde al diseño técnico.

`SearchResult` podrá evolucionar para soportar formalmente este contrato.

La incorporación de `NormalizedBusiness` constituye una evolución intencional de los contratos públicos de `v0.8.x`.

No se exige conservar una identidad de tipos entre `Business` y `NormalizedBusiness`.

## 7.3 Compatibilidad

Se preservarán los comportamientos existentes que no estén expresamente modificados por este ADR:

- Consulta de origen.
- Orden.
- Cardinalidad.
- Tiempo de ejecución.
- Incidencias previas.
- Identidad de los candidatos.
- Gestión de fallos recuperables.
- Manejo de errores fatales.

Los cambios de tipo y semántica de la representación predeterminada deberán documentarse y protegerse con pruebas.

No se permitirá interpretar una compatibilidad de firma como garantía de igualdad semántica entre valores originales y normalizados.

---

# 8. Política de consumidores

## 8.1 CLI

Durante `v0.8.x`, el CLI:

- Mostrará exclusivamente negocios normalizados.
- Conservará su flujo de búsqueda interactivo.
- Mantendrá su presentación general.
- Permitirá exportar CSV y XLSX.
- Exportará exclusivamente los datos normalizados.
- Presentará las incidencias recuperables relevantes.

No será obligatorio ofrecer al usuario del CLI una selección entre resultados originales y normalizados.

El original permanecerá disponible internamente mediante el resultado del Engine.

## 8.2 Consumidores Python

Los consumidores Python deberán poder consultar explícitamente ambas representaciones.

La disponibilidad del original no implica persistencia automática ni escritura de archivos adicionales.

Cada consumidor podrá decidir qué hacer con ambas representaciones.

## 8.3 API futura

La futura API podrá:

- Presentar resultados originales.
- Presentar resultados normalizados.
- Presentar ambas representaciones.
- Permitir seleccionar cuáles conservar o exportar.

La implementación de FastAPI, persistencia, decisiones de base de datos y flujos interactivos de API no pertenece a `v0.8.x`.

El módulo de normalización no dependerá de FastAPI ni de mecanismos particulares de persistencia.

---

# 9. Política de normalización por campo

Las transformaciones serán deterministas, conservadoras e independientes de servicios externos.

## 9.1 Name

Campo: `name`

Reglas:

- Eliminar espacios externos innecesarios.
- Unificar espacios repetidos de presentación.
- Convertir el texto a mayúsculas.
- Preservar el contenido textual restante.

No corregir ortografía ni inferir nombres oficiales.

Ejemplo:

```text
Original:
  Maquiladora   Parker

Normalizado:
MAQUILADORA PARKER
```

## 9.2 Category

Campo: `category`

Reglas:

- Limpiar espacios de presentación.
- Convertir a mayúsculas.
- Preservar la categoría identificada por la fuente.

No reclasificar ni traducir categorías.

Ejemplo:

```text
Original:
Empresa de suministros industriales

Normalizado:
EMPRESA DE SUMINISTROS INDUSTRIALES
```

## 9.3 Address

Campo: `address`

Reglas:

- Preservar contenido, grafía y componentes disponibles.
- No convertir direcciones completas a mayúsculas o minúsculas.
- No inferir colonias, códigos postales, ciudades o países.
- No ejecutar geocodificación.

No reconstruir direcciones.

La normalización se limitará a limpieza superficial segura, cuando corresponda.

## 9.4 Phone

Campo: `phone`

Reglas:

- Eliminar ruido de presentación reconocible.
- Conservar todos los dígitos significativos.
- Conservar prefijos internacionales explícitos.
- No inferir códigos de país.
- No suprimir extensiones sin identificar su significado.
- Agrupar números de diez dígitos inequívocos como `3 3 4`.

Ejemplo:

```text
Original:
(664) 123-4567

Normalizado:
664 123 4567
```

Número internacional explícito:

```text
Original:
+1 (619) 301-9068

Normalizado:
+1 619 301 9068
```

La presentación internacional no deberá alterar ni eliminar dígitos.

Si el número contiene una longitud ambigua, extensiones no interpretables o componentes cuya eliminación pueda causar pérdida de información, se conservará el valor original del campo.

No se incorporará una librería de inferencia regional como requisito del módulo.

## 9.5 Website

Campo: `website`

Reglas:

- Preservar la URL funcional.
- Eliminar únicamente espacios externos de presentación.
- No convertir indiscriminadamente rutas y parámetros a minúsculas.
- No eliminar segmentos, consultas o fragmentos sin una regla aprobada.
- No inferir protocolos ni dominios alternativos.

La normalización no realizará validación de disponibilidad ni navegación adicional.

## 9.6 Email

Campo: `email`

Reglas:

- Eliminar espacios externos innecesarios.
- Convertir a minúsculas.
- Preservar el valor completo cuando su interpretación sea segura.
- No reconstruir correos mediante inferencias.

No se aplicarán heurísticas para separar prefijos numéricos ambiguos.

Ejemplo pendiente de evidencia:

```text
974-9586impex@mcna.com.mx
```

No se inventará una corrección para este caso.

## 9.7 Language

Campo: `language`

Reglas:

- Eliminar espacios externos.
- Convertir el valor a mayúsculas.
- Preservar subetiquetas y separadores existentes.
- No inferir idiomas faltantes.

Ejemplo:

```text
Original:
es-MX

Normalizado:
ES-MX
```

## 9.8 Metadata web

Campos:

```python
website_title
website_description
has_contact_page
has_about_page
website_status
```

Durante `v0.8.x`, se preservará su contenido y semántica.

No se agregarán nuevas operaciones de clasificación o interpretación.

Los indicadores booleanos permanecerán booleanos y el estado HTTP conservará su representación numérica.

---

# 10. Determinismo

El módulo de normalización deberá producir siempre el mismo resultado ante los mismos valores de entrada y la misma política.

La normalización no dependerá de:

- Estado del navegador.
- Google Maps.
- Sitios web.
- Fecha u hora.
- Configuración regional implícita del sistema.
- Servicios externos.
- Datos de otros Businesses.

Una transformación no deberá requerir información obtenida mediante otra búsqueda.

La implementación no podrá producir diferencias arbitrarias entre ejecuciones equivalentes.

---

# 11. Idempotencia

Las reglas individuales deberán ser idempotentes.

Para una regla `N`:

```text
N(N(value)) == N(value)
```

El módulo deberá mantener la misma propiedad respecto a los valores normalizados.

Una normalización posterior de valores previamente normalizados no deberá añadir espacios, eliminar información adicional ni deteriorar resultados.

La aplicación repetida de reglas no modificará los objetos `Business` originales.

La compatibilidad de tipos entre representaciones será tratada mediante contratos explícitos durante el diseño técnico.

---

# 12. Normalización parcial y recuperación

## 12.1 Política general

La normalización operará con recuperación por campo.

La imposibilidad de normalizar un campo no provocará por sí sola la pérdida del negocio completo.

Se conservarán todas las transformaciones seguras ya obtenidas.

Cuando una transformación no pueda realizarse de forma confiable:

1. Se mantendrá el valor original del campo en NormalizedBusiness.
2. Se conservarán las demás transformaciones válidas.
3. Se registrará una incidencia recuperable.
4. Se continuará procesando el resto de los campos y negocios.

Esta política preserva progreso acumulativo sin imponer atomicidad total por negocio.

## 12.2 Valores que no requieren cambios

Un campo que ya cumple con la política no representa un fallo.

No deberá generar incidencias por el simple hecho de permanecer igual.

Tampoco generarán automáticamente incidencias los campos opcionales ausentes cuando su ausencia sea válida.

## 12.3 Campos ambiguos

No se inventarán valores para completar resultados ambiguos.

La preservación del original tendrá prioridad sobre transformaciones potencialmente destructivas.

## 12.4 Excepciones inesperadas

La recuperación por campo aplica a anomalías controladas de normalización.

Los defectos internos inesperados del programa no deberán ocultarse indiscriminadamente como si fueran datos ambiguos.

Su clasificación respetará el Error Model vigente.

---

# 13. Integración con SearchIssue

Las incidencias recuperables de normalización utilizarán el Error Model público existente.

Se adopta la etapa:

```text
normalization
```

El registro deberá identificar de manera segura:

- Negocio afectado.
- Campo afectado.
- Tipo de incidencia.
- Tratamiento aplicado.

La implementación podrá establecer códigos específicos para errores de normalización, respetando las restricciones actuales de SearchIssue e IssueCollector.

La consola podrá mostrar el nombre del negocio y el campo no normalizado.

No se incorporarán indiscriminadamente datos sensibles, excepciones completas, HTML o trazas internas a los mensajes públicos.

Las incidencias de normalización coexistirán con las incidencias previas de extracción y enriquecimiento.

No sustituirán ni eliminarán los errores originales.

---

# 14. Compatibilidad del pipeline global

## 14.1 Integración obligatoria

ProspectorEngine será responsable de garantizar que las búsquedas ejecuten el procesamiento global completo.

La normalización se realizará después de completar el pipeline interno correspondiente.

El módulo de normalización no ejecutará navegación, extracción ni enriquecimiento.

## 14.2 Wrapper histórico

El wrapper `search_businesses()` deberá integrarse al procesamiento global obligatorio.

Se preservarán los contratos históricos de entrada que permanezcan aprobados, incluida la política específica de compatibilidad de límites.

La normalización común no impondrá retroactivamente restricciones exclusivas de EngineConfig sobre rutas legacy.

Las diferencias de configuración de entrada no deberán producir diferencias injustificadas en las reglas de normalización.

El diseño técnico determinará el punto compartido de orquestación para evitar duplicaciones y ciclos de dependencia.

## 14.3 Pipelines internos

No se modificarán las responsabilidades funcionales de:

- Navigation.
- Result Feed.
- Summary.
- Detail Panel.
- Website Engine.
- BrowserRuntime.
- Selector Engine.

La etapa de normalización recibirá negocios ya consolidados.

No deberá intervenir durante la verificación de identidades, la navegación o el enriquecimiento.

---

# 15. Compatibilidad de exportación

Se conservarán los formatos:

- CSV.
- XLSX.

Se conservará el esquema actual de siete columnas:

```text
Name
Category
Address
Phone
Email
Website
Language
```

Las exportaciones del CLI utilizarán valores normalizados.

Los campos adicionales de NormalizedBusiness no se incorporarán automáticamente al esquema exportado.

No se permitirá mezclar originales y normalizados dentro de una misma exportación sin un contrato explícito.

La evolución necesaria de interfaces de exportación deberá ser mínima y verificable.

No se implementará persistencia ni otro formato de exportación en esta versión.

---

# 16. Garantías de integridad

La implementación deberá garantizar:

1. **Preservación:** el original permanece intacto.
2. **Independencia:** las representaciones no comparten estado mutable.
3. **Correspondencia:** cada normalizado pertenece a su original.
4. **Cardinalidad:** no se crean ni eliminan negocios.
5. **Orden:** la secuencia de negocios no cambia.
6. **Determinismo:** mismas entradas generan mismas salidas.
7. **Idempotencia:** repetir reglas no modifica adicionalmente resultados.
8. **Recuperación:** un campo ambiguo no elimina datos válidos.
9. **Compatibilidad:** los cambios públicos son explícitos y comprobables.
10. **Aislamiento:** normalizar no altera extracción ni enriquecimiento.

La normalización no se utilizará como mecanismo para corregir identidades inciertas.

La semántica de los resultados parciales del motor permanecerá vigente.

---

# 17. Requisitos de pruebas

La implementación incorporará pruebas específicas de normalización.

## Pruebas unitarias

Cubrirán:

- Transformaciones por campo.
- Idempotencia.
- Valores ausentes.
- Valores vacíos.
- Espacios.
- Unicode.
- Mayúsculas y minúsculas.
- Teléfonos de diferentes longitudes.
- Prefijos internacionales.
- Extensiones telefónicas.
- Emails ambiguos.
- URLs con rutas sensibles a mayúsculas.
- Metadata no transformada.
- Errores recuperables.

## Pruebas de integración

Cubrirán:

- Business original a NormalizedBusiness.
- Independencia entre objetos.
- Orden y cardinalidad.
- Continuidad frente a errores parciales.
- Propagación de SearchIssue.
- Contrato de SearchResult.
- Integración obligatoria con ProspectorEngine.
- Compatibilidad del wrapper legacy.
- Presentación del CLI.
- CSV/XLSX normalizados.
- Cleanup y comportamiento existente del runtime.

## Pruebas de regresión

Se conservará y ampliará la suite aprobada durante `v0.7.x`.

Los tests deterministas deberán ejecutarse offline.

No se utilizará Google Maps live como requisito para verificar las reglas de normalización.

Cualquier prueba live adicional requerirá autorización independiente.

---

# 18. Rendimiento

La normalización será local, determinista y acotada por el volumen de resultados procesados.

No realizará:

- Nuevas solicitudes HTTP.
- Navegación web.
- Consultas a servicios externos.
- Extracciones adicionales.
- Operaciones de geocodificación.
- Comparaciones empresariales entre registros.

No deberá incorporar costos relevantes de red o navegador.

Su implementación deberá permitir medir la sobrecarga sin confundirla con tiempos de extracción y enriquecimiento.

---

# 19. Exclusiones

Quedan explícitamente fuera de `v0.8.x`:

- Deduplicación de Businesses.
- Merge de registros empresariales.
- Multi-query.
- Multi-input.
- Batch execution.
- Concurrencia.
- Browser pooling.
- Nuevas fuentes de extracción.
- Geocodificación.
- Validación factual externa.
- Clasificación semántica empresarial.
- Reconstrucción heurística de contactos.
- API.
- FastAPI.
- Persistencia en base de datos.
- CRM.
- Jobs.
- Exportadores adicionales.
- Rediseño de Google Maps.
- Reescritura del Website Engine.

La deduplicación y la fusión de registros permanecen dentro del alcance futuro de `v0.9.x`.

---

# 20. Consecuencias de la decisión

## Consecuencias positivas

- Normalización consistente entre consumidores.
- Separación entre extracción y representación.
- Preservación de datos originales.
- Reducción de pérdida accidental de información.
- Reglas independientes de las fuentes.
- Mayor trazabilidad.
- Contrato explícito para consumidores Python.
- Evolución controlada de modelos.
- Posibilidad de ampliar el motor con nuevas fuentes sin duplicar reglas de normalización.

## Costos y responsabilidades

La decisión requiere:

- Crear NormalizedBusiness.
- Crear el módulo de normalización.
- Formalizar el procesamiento global común.
- Evolucionar SearchResult.
- Adaptar la integración del CLI.
- Garantizar compatibilidad del wrapper.
- Adaptar los consumidores de exportación necesarios.
- Incorporar pruebas de normalización e integración.
- Actualizar documentación y contratos públicos.

Estos cambios constituyen evolución arquitectónica intencional de `v0.8.x` y no autorizan refactors generales de componentes funcionales.

---

# 21. Criterios de aceptación arquitectónica

El ADR se considerará correctamente implementado cuando:

1. Toda búsqueda soportada atraviese normalización.
2. Se produzca un NormalizedBusiness independiente por cada Business.
3. Los Business originales se preserven.
4. Los consumidores Python puedan consultar ambas representaciones.
5. El CLI muestre únicamente valores normalizados.
6. CSV/XLSX exporten únicamente valores normalizados.
7. Se conserve orden y cardinalidad.
8. Los campos ambiguos preserven valores originales.
9. Los fallos recuperables se registren con SearchIssue.
10. Las reglas sean deterministas e idempotentes.
11. El wrapper mantenga sus políticas de entrada aprobadas.
12. Los pipelines internos de Google Maps permanezcan funcionales.
13. La suite de regresión continúe satisfactoria.
14. No se introduzcan funcionalidades de versiones posteriores.

---

# 22. Alcance del diseño posterior

Este ADR aprueba la arquitectura y las políticas generales del módulo.

Los documentos de diseño técnico definirán:

- Estructura exacta de NormalizedBusiness.
- Evolución concreta de SearchResult.
- Interfaces internas del normalizador.
- Orquestación compartida entre entradas.
- Catálogo detallado de reglas y contraejemplos.
- Códigos del Error Model.
- Estrategia de pruebas.
- Dependencias y orden de implementación.
- Patches y gates de aceptación.

Estas definiciones deberán respetar las decisiones presentes y no reabrir aspectos ya aprobados sin evidencia técnica.

---

# 23. Resolución

**DECISION: APPROVED**

Prospector CLI incorporará en `v0.8.x` una etapa obligatoria de normalización determinista dentro del pipeline global de Prospector Engine.

La etapa recibirá los Business consolidados producidos por los pipelines internos de las fuentes, preservará dichos originales y generará objetos NormalizedBusiness completamente independientes.

La representación normalizada será la salida predeterminada.

El CLI mostrará y exportará únicamente datos normalizados, mientras que los consumidores Python dispondrán de acceso a ambas representaciones.

Las transformaciones serán conservadoras, deterministas, idempotentes y recuperables por campo, sin eliminar negocios ni alterar su identidad, orden o cardinalidad.

La implementación respetará los contratos de extracción existentes y mantendrá fuera de alcance deduplicación, merge, multi-input y demás funcionalidades de versiones futuras.

**Este ADR establece la política arquitectónica obligatoria para el diseño y la implementación de Prospector CLI v0.8.x.**