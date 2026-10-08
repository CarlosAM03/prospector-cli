# Prospector CLI — v0.8.x Master Implementation Design

**Proyecto:** Prospector CLI  
**Documento:** Plan maestro y diseño técnico de implementación  
**Versión del documento:** 1.0  
**Línea de desarrollo:** v0.8.x  
**Rama:** `v0.8.0`  
**Baseline funcional:** `ee6b69e` — v0.7.x  
**Baseline documental:** `482ab03`  
**Decisión arquitectónica:** `ADR-008 — Política de Normalización del Pipeline Global`  
**Estado:** APPROVED — Owner Design Approved  
**Alcance:** v0.8.1–v0.8.6  

---

# 1. Propósito

Este documento define el alcance, los contratos técnicos, la arquitectura, los componentes, las reglas, la implementación incremental, las pruebas y los criterios de aceptación de Prospector CLI `v0.8.x`.

Su objetivo es implementar la etapa obligatoria de normalización determinista en el pipeline global de Prospector Engine.

La implementación deberá:

1. Conservar el comportamiento funcional validado de `v0.7.x`.
2. Preservar los resultados originales consolidados.
3. Generar resultados normalizados independientes.
4. Centralizar las reglas de normalización.
5. Integrar obligatoriamente la normalización en todas las rutas públicas de búsqueda soportadas.
6. Adaptar CLI y exportadores para consumir resultados normalizados.
7. Mantener el manejo de resultados parciales e incidencias recuperables.
8. Preservar las restricciones y garantías existentes de extracción.
9. Establecer cobertura determinista de pruebas.
10. Preparar una arquitectura extensible sin implementar funcionalidades de versiones posteriores.

Este documento complementa el `ADR-008`, cuya autoridad normativa prevalece ante cualquier contradicción.

No autoriza por sí solo la implementación autónoma. Su aprobación será seguida por la elaboración de un runbook específico para Codex.

---

# 2. Autoridades y evidencias

## 2.1 Orden de autoridad

1. Decisiones explícitas aprobadas por el propietario.
2. ADR-008 aprobado.
3. Este documento, una vez aprobado.
4. Código funcional del baseline `v0.7.x`.
5. Contratos comprobados por pruebas.
6. Documentación técnica CURRENT.
7. Documentación histórica.
8. Inventarios y propuestas preliminares.

Ninguna propuesta preliminar podrá modificar silenciosamente una decisión normativa.

## 2.2 Baseline

El baseline aceptado es:

`ee6b69e90972fce62fb5f9cedcee23acbd3c6b15`

La rama documental inicial de `v0.8.0` contiene:

`482ab033a9e45c6dfddf0e4c914cb942772a8cf3`

La suite funcional de referencia contiene:

- 113 pruebas unitarias aprobadas.
- 28 pruebas de integración aprobadas.
- 141 pruebas aprobadas en total.
- Una prueba E2E live excluida.

Las búsquedas reales previamente realizadas obtuvieron:

- 75 negocios para Maquila, Tijuana.
- 50 negocios para hospitales, Tijuana.
- Exportación CSV y XLSX.
- Incidencias recuperables sin interrupción del procesamiento completo.

Estos resultados forman parte del baseline, pero no representan una garantía universal de completitud del catálogo de Google Maps.

---

# 3. Alcance funcional

## 3.1 Incluido

La versión implementará:

- Modelo independiente `NormalizedBusiness`.
- Preservación de `Business` original.
- Resultado global con ambas representaciones.
- Reglas deterministas por campo.
- Normalizador independiente de fuentes.
- Recuperación ante fallos controlados por campo.
- Integración con `SearchIssue`.
- Orquestación obligatoria de normalización.
- Integración con `ProspectorEngine`.
- Compatibilidad del wrapper histórico.
- Presentación normalizada en CLI.
- Exportaciones normalizadas CSV/XLSX.
- Pruebas unitarias, de integración y regresión.
- Documentación de los contratos nuevos.

## 3.2 Excluido

No implementar:

- Deduplicación empresarial.
- Fusión de negocios.
- Multi-input o multi-query.
- Batch processing.
- Concurrencia.
- Browser pooling.
- Nuevas fuentes.
- Geocodificación.
- Corrección factual.
- Validación externa de información.
- Enriquecimiento adicional.
- API o FastAPI.
- Persistencia en bases de datos.
- Nuevos exportadores.
- CRM, jobs o mecanismos comerciales.
- Refactor general de Google Maps.
- Rediseño de BrowserRuntime.
- Reescritura de Website Engine.

Estas exclusiones son obligatorias para todos los patches.

---

# 4. Arquitectura objetivo

## 4.1 Pipeline global

```text
Consumer
    |
    v
SearchQuery / Configuration
    |
    v
ProspectorEngine
    |
    v
GLOBAL PIPELINE
    |
    +-- Source Dispatch
    |       |
    |       +-- Google Maps Pipeline
    |                |
    |                +-- Navigation
    |                +-- Feed / Summary
    |                +-- Detail
    |                +-- Website
    |                |
    |                v
    |             Business[]
    |
    +-- Normalization
    |       |
    |       +-- Field Rules
    |       +-- Field Recovery
    |       +-- Issue Collection
    |       |
    |       v
    |   NormalizedBusiness[]
    |
    v
SearchResult
    |
    +-- businesses
    |      NormalizedBusiness[]
    |
    +-- original_businesses
    |      Business[]
    |
    +-- issues
    |      SearchIssue[]
    |
    +-- query
    +-- execution_time
    +-- total_found
    |
    v
Consumer / ExportService
```

## 4.2 Separación de responsabilidades

### Pipeline de fuente

Responsable de:

- Navegación.
- Obtención de candidatos.
- Identificación.
- Extracción.
- Enriquecimiento.
- Preservación de resultados parciales.

No será responsable de ejecutar reglas generales de normalización.

### Pipeline global

Responsable de:

- Ejecutar la estrategia de fuente.
- Recibir datos consolidados.
- Normalizar obligatoriamente.
- Conservar originales.
- Consolidar incidencias.
- Construir el resultado público.

### Normalization Engine

Responsable de:

- Aplicar reglas deterministas.
- Crear objetos independientes.
- Recuperar campos no normalizables.
- Emitir incidencias recuperables.

No dependerá de Playwright, navegador, Google Maps, archivos CSV, interfaz CLI o servicios de red.

### Consumidores

Responsables de presentar, exportar o conservar las representaciones disponibles.

No implementarán reglas propias de normalización.

---

# 5. Diseño de modelos

## 5.1 Business

Archivo existente:

`src/models/business.py`

Se conservará como representación original consolidada.

El pipeline de extracción continuará generando instancias `Business`.

La normalización no modificará sus valores.

No se incorporarán propiedades de presentación ni campos de almacenamiento de valores normalizados a `Business`.

## 5.2 NormalizedBusiness

Archivo nuevo:

`src/models/normalized_business.py`

Se implementará mediante un modelo explícito de datos, inicialmente una `dataclass`.

Campos:

```python
@dataclass
class NormalizedBusiness:
    name: str
    category: str | None = None
    address: str | None = None
    phone: str | None = None
    website: str | None = None
    email: str | None = None

    language: str | None = None
    website_title: str | None = None
    website_description: str | None = None

    has_contact_page: bool | None = None
    has_about_page: bool | None = None
    website_status: int | None = None
```

Esta estructura representa el contrato inicial esperado.

No debe implementarse como alias de `Business` ni compartir identidad de objeto con el original.

Se permitirá una instancia mutable con independencia garantizada. No se requiere inmutabilidad física del modelo.

La construcción deberá copiar los valores necesarios y evitar referencias mutables compartidas.

Los campos actuales son escalares inmutables, pero las pruebas deberán proteger también futuras extensiones del modelo.

## 5.3 SearchResult

Archivo existente:

`src/models/search_result.py`

El contrato global objetivo será:

```python
@dataclass
class SearchResult:
    query: SearchQuery
    businesses: list[NormalizedBusiness]
    original_businesses: list[Business]
    execution_time: float
    issues: list[SearchIssue]
```

Conservando:

```python
@property
def total_found(self) -> int:
    return len(self.businesses)
```

La representación pública predeterminada será:

`result.businesses`

Los originales estarán disponibles en:

`result.original_businesses`

Se establece:

```python
len(result.businesses) == len(result.original_businesses)
```

Para toda búsqueda completada por el pipeline global.

La relación entre ambas listas será posicional, estable y uno a uno.

No se añadirán reglas de comparación, fusión ni deduplicación entre negocios.

### Compatibilidad transicional

Durante la implementación incremental, los constructores y pruebas existentes que utilizan `SearchResult(query)` deben continuar funcionando cuando corresponda.

La migración del resultado de fuente al resultado global se realizará de forma explícita y controlada.

No se permitirá que una ruta pública complete una búsqueda exitosa devolviendo una lista de `Business` sin normalizar.

Tampoco se construirán resultados falsamente normalizados rellenando `original_businesses` con referencias a objetos normalizados.

Para los resultados vacíos, ambas colecciones podrán permanecer vacías.

El diseño de la representación interna transicional no debe convertirse en un segundo modelo público permanente si no existe necesidad demostrada.

---

# 6. Contrato de normalización

## 6.1 Entrada

El normalizador recibirá:

`Business`

No recibirá HTML, DOM, Playwright Page, resultados del navegador ni elementos específicos de Google Maps.

## 6.2 Salida

Por cada entrada producirá:

- Una instancia independiente `NormalizedBusiness`.
- Cero o más incidencias recuperables.

## 6.3 Interface propuesta

```python
class NormalizationEngine:

    def normalize_business(
        self,
        business: Business,
        *,
        candidate: str | None = None,
        issue_collector=None,
    ) -> NormalizedBusiness:
        ...

    def normalize_businesses(
        self,
        businesses: list[Business],
        *,
        issue_collector=None,
    ) -> list[NormalizedBusiness]:
        ...
```

El contrato anterior es la propuesta técnica preferida.

La implementación podrá dividir internamente las reglas por responsabilidad, siempre que se mantenga una sola frontera pública de normalización.

No se necesita una jerarquía de plugins, un registry dinámico ni un framework de pipelines adicional.

## 6.4 Invariantes

Para cada negocio:

- Se crea una representación nueva.
- El original permanece intacto.
- Todos los campos permitidos se procesan.
- Los valores no transformables se conservan.
- Los campos independientes no se descartan ante un fallo localizado.

Para la colección:

- Se conserva la cantidad.
- Se conserva el orden.
- No se fusionan negocios.
- No se altera la identidad de origen.
- No se comparten objetos mutables entre representaciones.

---

# 7. Catálogo técnico de reglas

## 7.1 Reglas generales

Las transformaciones utilizarán operaciones puras sobre valores.

No se aceptarán llamadas de red, consultas externas o reglas dependientes del sistema operativo.

Para cadenas:

- Preservar contenido significativo.
- Aplicar únicamente las transformaciones autorizadas por campo.
- Mantener `None` como `None`.
- No inferir información ausente.
- No convertir automáticamente valores ambiguos en datos aparentemente válidos.

Los valores vacíos y compuestos exclusivamente por espacios requieren tratamiento conservador: cuando una regla de presentación no produzca información significativa, no se inventará un valor sustituto.

No se introducirá una política general de validación semántica en el normalizador.

## 7.2 Name

Regla:

1. Eliminar espacios externos.
2. Unificar secuencias de espacios de presentación.
3. Convertir a mayúsculas Unicode.
4. Preservar caracteres, acentos y puntuación restantes.

Ejemplos:

```text
"  Hospital   Excel "
    ->
"HOSPITAL EXCEL"

"Clínica Médica del Río"
    ->
"CLÍNICA MÉDICA DEL RÍO"
```

No eliminar símbolos comerciales ni corregir ortografía.

No usar este resultado para verificar identidad de Google Maps.

## 7.3 Category

Regla:

1. Eliminar espacios externos.
2. Unificar espacios de presentación.
3. Convertir a mayúsculas.

Ejemplo:

```text
" Hospital privado "
    ->
"HOSPITAL PRIVADO"
```

No reclasificar categorías.

No intentar reparar categorías que representen direcciones u otros errores de extracción.

Las correcciones específicas ya implementadas en el scraper conservarán su responsabilidad.

## 7.4 Address

Preservar contenido y grafía.

Se permite eliminar espacios externos evidentemente ajenos a la dirección.

No se permite:

- Convertir toda la dirección a mayúsculas o minúsculas.
- Eliminar componentes.
- Reordenar elementos.
- Traducir nombres.
- Inferir códigos postales.
- Inferir países.
- Geocodificar.

Ejemplo:

```text
"  Av. Diego Rivera 2312, Tijuana, B.C.  "
    ->
"Av. Diego Rivera 2312, Tijuana, B.C."
```

La limpieza no debe reescribir la estructura interna de la dirección.

## 7.5 Phone

El normalizador distinguirá entre números inequívocos y formatos ambiguos.

### Números de diez dígitos

Cuando el valor contenga exactamente diez dígitos y únicamente separadores de presentación reconocibles:

```text
"6641234567"
    ->
"664 123 4567"

"(664) 123-4567"
    ->
"664 123 4567"

"664.123.4567"
    ->
"664 123 4567"
```

Formato: `3 3 4`.

### Prefijos internacionales explícitos

Cuando exista un prefijo internacional explícito `+` con un patrón inequívoco previamente contemplado:

```text
"+1 (619) 301-9068"
    ->
"+1 619 301 9068"
```

La regla no inferirá ni eliminará dígitos.

No se aceptará interpretar una secuencia inicial de dígitos como código de país sin evidencia explícita.

Para otros patrones internacionales, se preservará la presentación original si no existe una regla segura.

### Extensiones

Ejemplo:

```text
"664 123 4567 ext. 25"
```

Cuando el valor incluya una extensión, no se eliminará.

La primera implementación conservará el valor completo si no existe una regla aprobada para representar inequívocamente número base y extensión.

### Ambigüedad

Un teléfono con letras, múltiples números o partes no reconocidas no deberá modificarse destructivamente.

Si no resulta posible aplicar una regla segura:

- Preservar el valor original.
- Registrar una incidencia cuando exista un intento fallido real de normalización.
- Continuar con los demás campos.

No incorporar `phonenumbers` ni inferencia regional como dependencia de esta versión.

## 7.6 Website

Normalización mínima:

- Eliminar espacios externos.
- Preservar protocolo.
- Preservar host.
- Preservar ruta.
- Preservar parámetros.
- Preservar fragmentos.
- Preservar diferencias de mayúsculas y minúsculas.

Ejemplo:

```text
" https://example.com/Products/ItemA?id=7 "
    ->
"https://example.com/Products/ItemA?id=7"
```

No reconstruir URLs.

No resolver redirecciones.

No verificar disponibilidad.

No eliminar fragmentos o parámetros.

## 7.7 Email

Reglas:

1. Eliminar espacios externos.
2. Convertir a minúsculas.
3. Mantener completo el valor obtenido.
4. No reconstruir local parts ambiguos.

Ejemplo:

```text
"  INFO@EXAMPLE.COM "
    ->
"info@example.com"
```

Contraejemplo:

```text
"974-9586impex@mcna.com.mx"
```

No se intentará separar un prefijo telefónico sin evidencia.

La normalización no equivale a validación de entregabilidad del correo.

Las reglas históricas de extracción `mailto:` permanecerán en Website Engine.

## 7.8 Language

Reglas:

- Eliminar espacios externos.
- Convertir a mayúsculas.
- Preservar etiquetas y separadores.

Ejemplos:

```text
"es-MX" -> "ES-MX"
"en-US" -> "EN-US"
"es-la" -> "ES-LA"
```

No inferir idioma a partir del website o dirección.

## 7.9 Website metadata

Campos:

```text
website_title
website_description
has_contact_page
has_about_page
website_status
```

Preservar exactamente los valores consolidados.

No realizar interpretaciones adicionales.

No convertir booleanos ni estados HTTP en textos.

No aplicar automáticamente mayúsculas o minúsculas a metadatos fuera del catálogo.

---

# 8. Atomicidad y recuperación por campo

## 8.1 Atomicidad individual

Cada transformación tendrá dos resultados permitidos:

1. Valor normalizado completo.
2. Valor original conservado.

No se permitirán transformaciones parcialmente aplicadas dentro del mismo campo.

## 8.2 Progreso acumulativo

El fallo de un campo no revertirá las transformaciones válidas de otros campos.

Ejemplo:

```text
Business:
    name = "  Hospital Excel "
    category = "Hospital privado"
    phone = "664 123 4567 ext. texto"

NormalizedBusiness:
    name = "HOSPITAL EXCEL"
    category = "HOSPITAL PRIVADO"
    phone = "664 123 4567 ext. texto"
```

La ambigüedad telefónica no deberá invalidar el nombre ni la categoría.

## 8.3 Ausencia de datos

No son errores:

- `None` en campos opcionales.
- Un valor que ya cumple la regla.
- Un campo cuya política establece preservación.
- Un resultado vacío legítimo.

## 8.4 Errores inesperados

No se ocultarán defectos internos del programa mediante capturas indiscriminadas de excepciones.

Distinguir entre:

- Ambigüedad controlada del dato.
- Fallo recuperable de una transformación.
- Incumplimiento del contrato de entrada.
- Error interno inesperado.

Sólo los casos recuperables usarán la preservación por campo.

Los errores internos fatales conservarán trazabilidad y seguirán el Error Model del motor.

---

# 9. Error Model de normalización

## 9.1 Contrato vigente

Se reutilizarán:

```text
SearchIssue
IssueCollector
SearchResult.issues
```

No se creará un segundo sistema de errores.

## 9.2 Nueva etapa

Se incorpora:

`normalization`

## 9.3 Códigos propuestos

```text
normalization/field_unverifiable
normalization/field_unavailable
```

- `field_unverifiable`: el valor existe, pero no puede interpretarse de manera suficientemente segura para transformarlo.
- `field_unavailable`: una operación controlada de normalización no pudo producir el valor esperado.

No se requiere registrar incidencias para reglas que conservan deliberadamente un valor por política, sin producir un fallo.

## 9.4 Contexto por negocio y campo

La identificación de incidencias deberá permitir conocer:

- Business afectado.
- Campo afectado.
- Razón segura.
- Resultado de recuperación.

El modelo público `SearchIssue` tiene actualmente:

```python
stage
code
message
candidate
exception_type
```

No se añadirán campos públicos por defecto.

Para conservar el contrato, la información de campo y negocio deberá representarse mediante códigos o referencias seguros y acotados, sin utilizar textos completos de direcciones, emails, websites o excepciones como identificadores.

Se recomienda utilizar un identificador por posición estable dentro del resultado, y emitir mensajes que incluyan el campo afectado mediante un catálogo controlado.

El CLI podrá mostrar un nombre de negocio cuando la relación con el índice resulte inequívoca y no exponga datos adicionales innecesarios.

Si una necesidad demostrada exige ampliar SearchIssue, deberá documentarse el cambio antes de implementarlo.

## 9.5 Catálogo seguro

Ampliar el catálogo de mensajes permitidos en:

`src/engines/issue_collector.py`

No permitir cadenas arbitrarias procedentes del DOM, sitios web o valores originales como mensajes de incidencias.

Las incidencias originales de feed, detail y website se preservarán.

---

# 10. Integración del pipeline global

## 10.1 Estado actual

Actualmente:

```python
ProspectorEngine.search()
    -> _run_google_maps()
```

Y el wrapper legacy:

```python
search_businesses()
    -> _run_google_maps()
```

`_run_google_maps()` realiza actualmente las tres fases y construye un `SearchResult`.

Esta estructura no constituye todavía una orquestación global completa.

## 10.2 Estado objetivo

Debe existir una ruta de procesamiento común para todas las entradas públicas soportadas.

Conceptualmente:

```text
ProspectorEngine.search()
        |
        v
Global Execution
        |
        +-- Source Execution
        +-- Normalization
        +-- Result Assembly
```

El wrapper deberá utilizar igualmente la orquestación global, sin duplicar las reglas ni sustituir la configuración aprobada.

## 10.3 Separación de resultados de fuente y global

El pipeline de fuente deberá continuar produciendo datos originales consolidados.

La responsabilidad de crear las representaciones normalizadas pertenece al procesamiento global.

Se permitirá una adaptación mínima del contrato interno que hoy devuelve `_run_google_maps()` para separar extracción y resultado público final.

Evitar un rediseño amplio del scraper.

No crear un segundo pipeline completo específico del wrapper.

## 10.4 Compatibilidad de límites

Se preserva:

```text
EngineConfig default: 50
Google Maps Engine maximum: 100
CLI maximum: 100
Legacy wrapper default: 50
```

El wrapper conserva las excepciones de comportamiento legacy previamente aprobadas.

La nueva etapa común no alterará:

- Parámetros públicos del wrapper.
- Política de límite legacy.
- Comportamiento de navegación históricamente conservado.
- Condiciones de error anteriores, salvo el cambio público explícito de representación normalizada.

Las pruebas de compatibilidad deberán actualizarse para distinguir llamadas a una nueva frontera global de llamadas directas al scraper interno.

## 10.5 Ejecución única

Una búsqueda deberá ejecutar una sola normalización global.

No se permitirá normalizar primero dentro de `_run_google_maps()` y nuevamente desde `ProspectorEngine`.

No se añadirá normalización desde CLI o ExportService.

## 10.6 Métricas

El tiempo de normalización podrá registrarse como métrica interna diferenciada de extracción y enriquecimiento.

`execution_time` deberá representar la ejecución completa del motor, incluida la normalización.

No se incorporará telemetría persistente, infraestructura externa ni nuevos archivos de logging.

---

# 11. Adaptación de consumidores

## 11.1 CLI

Archivo:

`src/main.py`

El CLI mantendrá:

- Menú actual.
- Entrada de keyword.
- Entrada de location.
- Default 50.
- Máximo 100.
- Presentación de errores.
- Opciones CSV/XLSX.

La salida de negocios utilizará:

`result.businesses`

Los valores mostrados procederán de `NormalizedBusiness`.

No se añadirá una pregunta para elegir entre original y normalizado.

No se mostrará una segunda lista de negocios originales.

## 11.2 ExportService

Archivo:

`src/services/export_service.py`

Se mantendrán los formatos actuales.

El servicio no ejecutará normalización.

Consumirá el resultado ya normalizado.

No requiere nuevas opciones para persistencia o selección de vistas.

## 11.3 CSV/XLSX

Archivos:

```text
src/exporters/csv.py
src/exporters/excel.py
```

Se preservará el esquema:

```text
Name
Category
Address
Phone
Email
Website
Language
```

Las filas corresponderán a `NormalizedBusiness`.

No se exportarán automáticamente ambas representaciones.

No se modificarán nombres ni orden de columnas.

Los exportadores no deberán depender del tipo `Business` original cuando ya reciban el nuevo modelo.

Si las interfaces actuales por atributos son suficientes, sólo se actualizarán anotaciones, documentación y pruebas.

---

# 12. Diseño de patches

La implementación se divide en seis patches secuenciales.

Cada patch deberá contar con pruebas independientes y mantener el proyecto en un estado coherente.

No se permitirá avanzar con regresiones conocidas introducidas por un patch anterior.

---

# PATCH v0.8.1 — Data Contracts

## Objetivo

Introducir las estructuras necesarias para soportar resultados originales y normalizados sin modificar todavía las rutas funcionales de extracción.

## Alcance

1. Crear `NormalizedBusiness`.
2. Definir la correspondencia de sus 12 campos.
3. Preparar `SearchResult` para ambas representaciones.
4. Conservar compatibilidad transicional de construcción.
5. Garantizar independencia entre objetos.
6. Documentar la futura transición de tipos públicos.

## Archivos principales

Crear:

```text
src/models/normalized_business.py
tests/unit/test_normalized_business.py
```

Modificar:

```text
src/models/search_result.py
tests/unit/test_models.py
```

Otros archivos sólo cuando exista dependencia técnica demostrada.

## Diseño

`NormalizedBusiness` se implementará como modelo independiente.

`SearchResult` permitirá representar los originales sin obligar a activar todavía la normalización en los métodos públicos.

No se cambiará el comportamiento efectivo de `ProspectorEngine.search()` hasta el patch de integración global.

La migración de tipos deberá proteger los tests y mocks que construyen `SearchResult(query)`.

No se permitirá crear estados híbridos donde `result.businesses` contenga accidentalmente originales y normalizados mezclados.

## Pruebas

- Creación de NormalizedBusiness.
- Correspondencia de campos.
- Valores opcionales.
- Independencia de instancias.
- Original intacto.
- SearchResult vacío.
- Correspondencia de colecciones.
- Total found.
- Compatibilidad de construcción transicional.

## Gate P81

- Pruebas nuevas verdes.
- Suite anterior verde.
- Sin modificaciones de Google Maps.
- Sin cambios de CLI.
- Contratos transicionales documentados.

---

# PATCH v0.8.2 — Deterministic Field Rules

## Objetivo

Implementar el catálogo de transformaciones como funciones independientes y deterministas.

## Alcance

- Name.
- Category.
- Address.
- Phone.
- Website.
- Email.
- Language.
- Preservación de metadata.

## Archivos principales

Crear un paquete cohesivo, por ejemplo:

```text
src/engines/normalization/
    __init__.py
    rules.py
```

Pruebas:

```text
tests/unit/test_normalization_rules.py
```

## Diseño

Cada regla recibirá un valor y devolverá un valor.

No utilizar estado global mutable.

No utilizar dependencias externas para manipular números telefónicos.

Las reglas no accederán al modelo SearchResult ni a la lista de negocios.

No implementar deduplicación ni comparaciones entre registros.

## Pruebas

Incluir al menos:

- Mayúsculas Unicode.
- Acentos.
- Espacios repetidos.
- Espacios externos.
- Valores opcionales.
- Números telefónicos de diez dígitos.
- Prefijos internacionales.
- Extensiones.
- Longitudes desconocidas.
- Caracteres inesperados.
- Email ya normalizado.
- Email con prefijos ambiguos.
- URLs sensibles a mayúsculas.
- URLs con parámetros.
- Dirección original.
- Metadata no modificada.
- Idempotencia por campo.

Cada regla deberá incluir casos válidos y contraejemplos.

## Gate P82

- Todas las reglas deterministas.
- Pruebas verdes.
- Ninguna operación de red.
- Ninguna dependencia de Google Maps.
- Idempotencia comprobada.
- Sin pérdida silenciosa de información.

---

# PATCH v0.8.3 — Normalization Engine

## Objetivo

Construir la etapa que transforma Businesses en NormalizedBusinesses y gestiona la recuperación por campo.

## Archivos principales

Crear:

```text
src/engines/normalization/normalization_engine.py
tests/unit/test_normalization_engine.py
```

Modificar:

```text
src/engines/issue_collector.py
```

## Alcance

1. Aplicar reglas.
2. Crear objetos independientes.
3. Preservar originales.
4. Mantener orden.
5. Mantener cardinalidad.
6. Recuperar campos ambiguos.
7. Generar incidencias seguras.
8. Mantener progreso acumulativo.

## Diseño

El módulo deberá distinguir una transformación completada de una transformación no segura.

Si un campo no se puede normalizar:

- Conservar el original en NormalizedBusiness.
- Registrar una incidencia cuando exista fallo controlado.
- Procesar los campos restantes.

Una excepción inesperada que revele un defecto de programación no se tratará como una simple ambigüedad.

No introducir capturas globales indiscriminadas.

## Pruebas

- Un Business completo.
- Business con campos parciales.
- Business con todos los opcionales ausentes.
- Múltiples Businesses.
- Identidades con nombres repetidos.
- Fallo de un campo.
- Varios fallos recuperables.
- Campos posteriores correctamente procesados.
- Correspondencia posicional.
- Original sin mutaciones.
- Independencia de objetos.
- Incidencias seguras.
- Idempotencia.
- Determinismo.

## Gate P83

- Engine de normalización operativo offline.
- Sin integración live.
- Sin cambios en el pipeline de fuente.
- Recuperación por campo demostrada.
- Suite completa verde.

---

# PATCH v0.8.4 — Global Pipeline Integration

## Objetivo

Hacer que todas las rutas públicas soportadas atraviesen obligatoriamente una misma etapa global de normalización.

## Archivos principales

Modificar:

```text
src/engines/prospector_engine.py
src/scraper/google_maps/scraper.py
src/models/search_result.py
```

Crear un componente mínimo de orquestación compartida sólo si resulta necesario:

```text
src/engines/global_pipeline.py
```

Agregar:

```text
tests/integration/test_global_normalization_pipeline.py
```

## Diseño

La implementación separará conceptualmente:

1. Ejecutar fuente.
2. Obtener originales.
3. Normalizar.
4. Construir resultado global.

`ProspectorEngine` gobernará la ejecución del pipeline global.

El wrapper histórico utilizará la misma etapa común, preservando sus diferencias de entrada.

No se permitirá que los consumidores públicos omitan accidentalmente la normalización.

No modificar:

- Navigation.
- Feed.
- Detail.
- Website Engine.
- Browser Runtime.

## Compatibilidad

Verificar explícitamente:

- Default CLI 50.
- Máximo Engine 100.
- Wrapper legacy default 50.
- Comportamientos legacy de límites.
- Fatal typed errors.
- Errores recuperables.
- Browser cleanup.
- Resultados parciales.
- Orden de Businesses.

La salida pública exitosa deberá contener objetos NormalizedBusiness.

Los Business originales deberán estar disponibles en original_businesses.

## Pruebas

- ProspectorEngine → normalización obligatoria.
- Wrapper → normalización obligatoria.
- Normalización ejecutada exactamente una vez.
- Una sola fuente.
- Resultados parciales.
- Incidencias previas preservadas.
- Incidencias de normalización incorporadas.
- Cardinalidad.
- Orden.
- Tiempo completo de ejecución.
- Errores fatales preservados.
- Límites legacy.
- 100 resultados offline.
- Browser cleanup.

## Gate P84

- Ninguna ruta pública sin normalización.
- Sin rutas duplicadas de extracción.
- Sin regresión de identidad.
- Wrapper legacy compatible.
- Tests completos verdes.

---

# PATCH v0.8.5 — Consumer Integration

## Objetivo

Adaptar el CLI y la exportación para consumir la representación normalizada sin agregar nuevas funcionalidades de presentación.

## Archivos principales

```text
src/main.py
src/services/export_service.py
src/exporters/csv.py
src/exporters/excel.py
```

Modificar únicamente los archivos que realmente lo requieran.

Pruebas:

```text
tests/integration/test_cli_transitional_compatibility.py
tests/integration/test_export_service.py
tests/integration/test_global_normalization_pipeline.py
```

## Alcance

- Presentación normalizada.
- Exportación CSV normalizada.
- Exportación XLSX normalizada.
- Preservación del esquema.
- Compatibilidad del menú.
- Incidencias recuperables visibles.

## Diseño

No crear opciones nuevas para exportar originales en CLI.

No exportar dos archivos automáticamente.

No modificar los nombres de las siete columnas.

No incorporar persistencia.

No ejecutar normalización dentro del exportador.

## Pruebas

- CLI muestra nombre en mayúsculas.
- Categoría en mayúsculas.
- Teléfono formateado.
- Email en minúsculas.
- Idioma en mayúsculas.
- Direcciones preservadas.
- Websites funcionalmente intactos.
- CSV contiene valores normalizados.
- XLSX contiene valores normalizados.
- Ambos formatos conservan esquema.
- La salida no presenta datos mezclados entre negocios.
- Los errores parciales aparecen en consola.
- Datos originales accesibles por Python.

## Gate P85

- Presentación coherente.
- Exportación coherente.
- Sin cambios de experiencia no aprobados.
- CSV/XLSX compatibles.
- Suite completa verde.

---

# PATCH v0.8.6 — Regression, Documentation & Acceptance

## Objetivo

Validar de manera integral la implementación de `v0.8.x` y preparar la aceptación del propietario.

Este patch no incorpora nuevas funcionalidades.

## Alcance

1. Auditoría de contratos.
2. Pruebas unitarias.
3. Pruebas de integración.
4. Regresión offline.
5. Integridad de originales.
6. Integridad de normalizados.
7. Compatibilidad legacy.
8. Documentación.
9. Auditoría de diff.
10. Preparación de prueba manual.

## Archivos

Documentación oficial aplicable:

```text
README.md
docs/architecture.md
docs/roadmap.md
docs/scripting-pipeline.md
docs/pipelines/google_maps.md
docs/contributing.md
tests/README.md
```

Registros locales de implementación bajo:

```text
temp/Planeacion/v0.8.0/
```

Los documentos normativos aprobados no se reescribirán retroactivamente para justificar implementaciones divergentes.

## Pruebas finales

```powershell
python -m compileall -q src

python -m pytest tests\unit -q -p no:cacheprovider

python -m pytest tests\integration -q -p no:cacheprovider

python -m pytest -q -p no:cacheprovider

git diff --check
git status --short
```

Las pruebas predeterminadas serán offline.

No habilitar E2E live sin autorización expresa.

## Auditoría de integridad

Revisar:

- Preservación de los 12 campos originales.
- Independencia de objetos.
- Correspondencia posicional.
- Cardinalidad.
- Idempotencia.
- Determinismo.
- Progreso parcial.
- Incidencias.
- Límites.
- Identidad.
- Exportaciones.
- Cleanup.
- Tiempos.
- Contratos públicos.

## Evidencia manual

La aceptación final podrá utilizar una o dos búsquedas reales ejecutadas por el propietario.

Estas búsquedas no serán ejecutadas autónomamente por Codex.

La verificación manual deberá comprobar:

- Resultados obtenidos.
- Datos originales preservados.
- Vista normalizada.
- Campos no normalizados.
- Incidencias.
- CSV/XLSX.
- Finalización correcta.
- Ausencia de regresiones operativas evidentes.

No se exigirá que todos los Businesses dispongan de todos los campos opcionales.

## Gate P86

- Suite offline verde.
- Diff auditado.
- Sin regresiones críticas conocidas.
- Documentación CURRENT correcta.
- Evidencia clara de limitaciones.
- Release candidate preparada para aceptación manual.

El propietario conserva la autoridad de aceptación.

---

# 13. Matriz de dependencias

| Patch | Depende de | Entregable |
|---|---|---|
| v0.8.1 | Baseline + ADR-008 | Contratos de datos |
| v0.8.2 | ADR-008 | Reglas puras |
| v0.8.3 | v0.8.1–v0.8.2 | Normalization Engine |
| v0.8.4 | v0.8.3 | Pipeline global |
| v0.8.5 | v0.8.4 | CLI y exportadores |
| v0.8.6 | v0.8.1–v0.8.5 | Regresión y aceptación |

La implementación seguirá el orden establecido para reducir estados transitorios incompatibles.

No se iniciará un patch nuevo sin cerrar los defectos bloqueantes introducidos por el anterior.

---

# 14. Política de implementación incremental

Los patches representan hitos técnicos, no autorizaciones para introducir cambios de arquitectura independientes.

Cada patch deberá:

1. Comenzar sobre el estado validado del anterior.
2. Mantener cambios focalizados.
3. Incorporar pruebas necesarias.
4. Ejecutar regresión offline.
5. Documentar diferencias relevantes.
6. Preservar contratos aprobados.
7. Evitar funcionalidades futuras.

Si una prueba histórica espera deliberadamente resultados originales en `SearchResult.businesses`, deberá actualizarse cuando el contrato global cambie expresamente a NormalizedBusiness.

No se debilitarán pruebas que detecten identidad incorrecta, pérdida de datos o alteraciones de orden.

En patches intermedios se permitirán adaptadores internos transitorios, pero éstos no deberán permanecer como rutas públicas que omitan normalización al completar v0.8.x.

---

# 15. Matriz integral de aceptación

| ID | Requisito | Verificación |
|---|---|---|
| N01 | Modelo separado | Unit |
| N02 | Original preservado | Unit/Integration |
| N03 | Independencia | Unit |
| N04 | Orden inalterado | Integration |
| N05 | Cardinalidad inalterada | Integration |
| N06 | Name uppercase | Unit |
| N07 | Category uppercase | Unit |
| N08 | Address preservada | Unit |
| N09 | Phone 3-3-4 | Unit |
| N10 | Internacional explícito | Unit |
| N11 | Extensiones preservadas | Unit |
| N12 | Website segura | Unit |
| N13 | Email lowercase | Unit |
| N14 | Language uppercase | Unit |
| N15 | Metadata preservada | Unit |
| N16 | Idempotencia | Unit |
| N17 | Determinismo | Unit |
| N18 | Recuperación por campo | Unit |
| N19 | SearchIssue seguro | Unit/Integration |
| N20 | Engine obligatorio | Integration |
| N21 | Wrapper obligatorio | Integration |
| N22 | Compatibilidad legacy | Integration |
| N23 | Normalización única | Integration |
| N24 | CLI normalizado | Integration |
| N25 | CSV normalizado | Integration |
| N26 | XLSX normalizado | Integration |
| N27 | Siete columnas | Integration |
| N28 | Sin regresiones de Google Maps | Regression |
| N29 | Cleanup preservado | Regression |
| N30 | Suite completa offline | Regression |
| N31 | Aceptación manual | Owner |

Las pruebas deben verificar valores y tipos concretos, no limitarse a comprobar que una función fue llamada.

---

# 16. Riesgos y mitigaciones

## R01 — Regresión del pipeline de Google Maps

**Riesgo:** introducir cambios que alteren navegación o enriquecimiento.

**Mitigación:** mantener las modificaciones fuera de los componentes de fuente salvo la frontera mínima de integración.

## R02 — Pérdida de originales

**Riesgo:** mutaciones accidentales sobre Business.

**Mitigación:** construcción de NormalizedBusiness independiente y pruebas explícitas de no mutación.

## R03 — Doble normalización

**Riesgo:** normalizar dentro de la fuente y otra vez desde el Engine.

**Mitigación:** una sola frontera global y pruebas de ejecución única.

## R04 — Incompatibilidad de consumidores

**Riesgo:** cambios de tipo público en SearchResult.

**Mitigación:** migración controlada de contratos, anotaciones, mocks y tests.

## R05 — Wrapper sin normalización

**Riesgo:** acceso directo a `_run_google_maps()`.

**Mitigación:** reconciliar las rutas públicas y probar ambas.

## R06 — Transformaciones destructivas

**Riesgo:** eliminar dígitos, modificar URLs o reconstruir emails.

**Mitigación:** catálogo cerrado de reglas y contraejemplos.

## R07 — Incidencias excesivas

**Riesgo:** reportar campos correctos como fallidos.

**Mitigación:** distinguir valores preservados deliberadamente de fallos reales.

## R08 — Ampliación de alcance

**Riesgo:** introducir deduplicación, validación, APIs u otras funcionalidades.

**Mitigación:** exclusiones explícitas, auditoría de diff y gates.

## R09 — Pruebas verdes sin funcionalidad real

**Riesgo:** mocks que no comprueban el procesamiento global.

**Mitigación:** tests que inspeccionen originales, normalizados, incidencias y archivos exportados.

---

# 17. Restricciones sobre componentes existentes

Salvo un defecto demostrable relacionado directamente con esta versión, no modificar:

```text
src/engines/navigation/
src/engines/selector/
src/engines/browser_runtime.py
src/engines/website/
src/scraper/google_maps/detail_panel.py
src/scraper/google_maps/result_list.py
src/scraper/google_maps/search.py
```

El wrapper y la orquestación sí podrán modificarse dentro del alcance aprobado.

No reconstruir los siete patches de `v0.7.x`.

No introducir una nueva abstracción genérica de todas las fuentes si una orquestación común mínima resulta suficiente.

No convertir Normalization Engine en un framework extensible de plugins.

---

# 18. Documentación durante implementación

La documentación local bajo:

`temp/Planeacion/v0.8.0/`

contendrá:

- ADR-008.
- Este Master Implementation Design.
- Runbook autónomo posterior.
- Checkpoints.
- Progreso de implementación.
- Bloqueos.
- Resultados de validación.
- Auditoría final de aceptación.

Este documento será la fuente de diseño aprobada.

No duplicar el diseño normativo en documentos equivalentes.

La documentación oficial se actualizará conforme las capacidades se implementen y verifiquen.

Hasta entonces, CURRENT no deberá declarar normalización completada.

---

# 19. Política de aceptación y release

Un patch puede considerarse implementado cuando:

- Cumple sus criterios.
- Sus pruebas focalizadas pasan.
- No introduce regresiones.
- Respeta ADR-008.
- No modifica contratos fuera del alcance aprobado.

La línea completa `v0.8.x` sólo podrá recomendarse para aceptación cuando:

- Los seis patches estén implementados.
- El pipeline global funcione.
- Los resultados originales estén disponibles.
- La normalización sea obligatoria.
- CLI y exportadores usen normalizados.
- La suite offline completa pase.
- El diff final esté auditado.
- La documentación refleje el código.
- No queden defectos críticos conocidos.

La aceptación final exige decisión explícita del propietario.

No confundir:

```text
IMPLEMENTED
TESTED
READY FOR MANUAL ACCEPTANCE
ACCEPTED
RELEASED
```

Estos estados no son equivalentes.

---

# 20. Preparación de la implementación autónoma

Después de aprobar este documento se elaborará un runbook autónomo independiente.

Ese runbook definirá:

- Preconditions.
- Orden exacto de trabajo.
- Checkpoints por patch.
- Comandos de pruebas.
- Registros de evidencia.
- Política de bloqueos.
- Límites de autonomía.
- Operaciones Git permitidas.
- Restricciones live.
- Entregable final.

El runbook no podrá modificar las decisiones de ADR-008 ni los contratos definidos en este documento.

La implementación deberá ser reproducible, auditable e incremental.

No se autoriza comenzar la implementación durante la etapa de reconciliación documental.

---

# 21. Resultado esperado

Al finalizar v0.8.x, Prospector CLI deberá ofrecer:

```python
result = ProspectorEngine(config).search(query)

# Normalized output
result.businesses

# Consolidated original output
result.original_businesses

# Original and normalization issues
result.issues

# Extracted business count
result.total_found
```

Con las garantías siguientes:

- Ambos conjuntos corresponden uno a uno.
- La representación normalizada es independiente.
- Ningún dato original se modifica.
- La normalización se ejecuta siempre.
- Los campos ambiguos se conservan.
- Las transformaciones correctas no se pierden por fallos parciales.
- El CLI presenta normalizados.
- CSV/XLSX exportan normalizados.
- Las fuentes siguen siendo responsables únicamente de extracción y enriquecimiento.
- No se implementan funciones de v0.9.x o posteriores.

---

# 22. Resolución del diseño

**STATUS: APPROVED — OWNER DESIGN APPROVED**

Se propone implementar `v0.8.x` mediante seis patches:

1. `v0.8.1` — Data Contracts.
2. `v0.8.2` — Deterministic Field Rules.
3. `v0.8.3` — Normalization Engine.
4. `v0.8.4` — Global Pipeline Integration.
5. `v0.8.5` — Consumer Integration.
6. `v0.8.6` — Regression, Documentation & Acceptance.

El diseño cumple la arquitectura B + R3 establecida por ADR-008.

Su aprobación autorizará la preparación del runbook de implementación autónoma y la alineación documental local, pero no constituye por sí sola una orden de implementación ni de publicación.

**Fin del documento.**