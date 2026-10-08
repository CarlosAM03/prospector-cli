# Prospector CLI — v0.8.x Autonomous Implementation Runbook

**Proyecto:** Prospector CLI  
**Documento:** Autonomous Implementation Runbook  
**Versión del documento:** 1.0  
**Línea de desarrollo:** v0.8.x  
**Rama:** `v0.8.0`  
**Baseline funcional:** `ee6b69e`  
**Baseline documental:** `482ab03`  
**ADR:** ADR-008 — Política de Normalización del Pipeline Global  
**Diseño:** v0.8.x Master Implementation Design  
**Patches:** v0.8.1–v0.8.6  
**Checkpoints:** P81–P86  
**Estado:** APPROVED — Owner Approval and Execution Authorization  

---

# 1. Propósito

Este documento define el procedimiento operativo para implementar autónomamente los seis patches de Prospector CLI `v0.8.x`, de acuerdo con los contratos y decisiones arquitectónicas aprobados.

El objetivo es incorporar la normalización determinista obligatoria al pipeline global de Prospector Engine, preservando el comportamiento funcional alcanzado durante `v0.7.x`.

La implementación deberá producir:

- Un modelo independiente `NormalizedBusiness`.
- Preservación íntegra de los objetos `Business` originales.
- Un módulo especializado de normalización.
- Aplicación determinista de reglas por campo.
- Manejo recuperable de campos no normalizables.
- Integración obligatoria al pipeline global.
- Acceso a ambas representaciones desde Python.
- Presentación y exportación normalizada desde CLI.
- Pruebas de integridad y compatibilidad.
- Documentación consistente con el código implementado.

Este runbook organiza la ejecución, pero no sustituye al ADR ni al Master Implementation Design.

**La existencia de este documento no autoriza automáticamente el inicio de la implementación.**

La autorización deberá proporcionarse mediante una instrucción de ejecución explícita del propietario.

---

# 2. Jerarquía de autoridad

Durante la ejecución se aplicará el siguiente orden:

1. Instrucciones explícitas y aprobadas del propietario.
2. ADR-008.
3. Master Implementation Design v0.8.x.
4. Este Autonomous Implementation Runbook.
5. Código y contratos funcionales del baseline.
6. Pruebas y evidencias verificadas.
7. Documentación CURRENT.
8. Registros históricos y documentos preliminares.

En caso de contradicción normativa:

- No inventar una decisión.
- No reinterpretar el ADR para justificar código existente.
- No modificar documentos aprobados unilateralmente.
- Registrar el conflicto.
- Detener únicamente el trabajo que dependa del conflicto.
- Continuar con tareas independientes si resulta seguro.

Los documentos preliminares no tienen autoridad para modificar contratos aprobados.

---

# 3. Modelo de autonomía

## 3.1 Autonomía permitida

Una vez autorizada la ejecución completa, Codex podrá:

- Crear archivos necesarios dentro del alcance aprobado.
- Modificar componentes previstos en los patches.
- Implementar reglas y modelos definidos.
- Refactorizar mínimamente las interfaces afectadas.
- Crear y actualizar pruebas.
- Ejecutar verificaciones offline.
- Corregir defectos introducidos por sus cambios.
- Actualizar documentación conforme al estado verificado.
- Registrar avances y bloqueos.
- Ejecutar todos los patches secuencialmente.
- Continuar al siguiente checkpoint cuando el anterior cumpla sus condiciones.

No deberá solicitar aprobación para cada cambio rutinario de implementación que esté claramente autorizado por el diseño.

## 3.2 Autonomía restringida

La autorización de implementación no concede permiso para:

- Cambiar decisiones arquitectónicas.
- Añadir funcionalidades.
- Alterar políticas aprobadas.
- Ejecutar pruebas live.
- Consultar Google Maps durante las pruebas.
- Introducir dependencias externas sin necesidad aprobada.
- Cambiar la estrategia de múltiples fuentes.
- Implementar deduplicación o merge.
- Crear una API.
- Publicar releases.
- Modificar ramas ajenas.
- Hacer merge a main.
- Eliminar evidencias históricas.
- Ocultar fallos de pruebas.
- Modificar contratos públicos fuera del ADR.
- Reescribir el historial Git.
- Ejecutar cambios destructivos sobre archivos del usuario.

## 3.3 Operaciones Git

Codex podrá utilizar Git para:

- Inspeccionar el historial.
- Comparar cambios.
- Revisar archivos modificados.
- Verificar el baseline.
- Inspeccionar los diffs.
- Confirmar que no existen cambios ajenos inesperados.

Por defecto, no estará autorizado para:

- `git commit`.
- `git push`.
- `git merge`.
- `git rebase`.
- `git reset --hard`.
- `git clean`.
- `git tag`.
- Eliminar o renombrar ramas.

La autorización para crear commits por patch deberá otorgarse separadamente.

La implementación podrá realizarse sin commits intermedios, utilizando checkpoints documentales y pruebas.

No deben descartarse modificaciones preexistentes del usuario.

---

# 4. Precondiciones obligatorias

Antes de modificar código, ejecutar:

```powershell
git branch --show-current

git status --short

git rev-parse HEAD

git log -6 --oneline

git merge-base --is-ancestor ee6b69e HEAD
```

## 4.1 Rama

La rama esperada es:

`v0.8.0`

Si la rama actual es distinta, detener la implementación.

No cambiar de rama automáticamente.

## 4.2 Baseline

Comprobar que el commit funcional `ee6b69e` pertenece al historial actual.

La implementación no necesita comenzar exactamente en `482ab03`, ya que podrán existir cambios documentales posteriores.

Registrar el HEAD real al inicio.

## 4.3 Árbol de trabajo

Inspeccionar:

- Modificaciones versionadas.
- Archivos nuevos.
- Archivos ignorados relevantes.
- Documentos de planificación.
- Evidencias previas.

La carpeta `temp/` está ignorada por Git.

No depender exclusivamente de `git status` para evaluar la documentación local.

Si existen cambios de producción previos cuyo origen no sea verificable, no sobrescribirlos.

## 4.4 Autoridades disponibles

Verificar la existencia e integridad del:

- ADR-008.
- Master Implementation Design.
- Autonomous Implementation Runbook.

Si algún documento normativo falta o presenta contradicciones esenciales, no iniciar cambios dependientes de él.

## 4.5 Dependencias

Verificar que el entorno Python pueda ejecutar las pruebas.

El proyecto utiliza:

```powershell
python -m pip install -r requirements-dev.txt
```

No actualizar dependencias fijadas sin justificación aprobada.

No ejecutar instalaciones innecesarias si el entorno ya funciona.

---

# 5. Baseline de pruebas

Antes del primer patch:

```powershell
Remove-Item Env:PROSPECTOR_RUN_E2E -ErrorAction SilentlyContinue

python -m compileall -q src

python -m pytest tests\unit -q -p no:cacheprovider

python -m pytest tests\integration -q -p no:cacheprovider

python -m pytest -q -p no:cacheprovider
```

Resultados históricos esperados:

```text
Unit: 113 passed
Integration: 28 passed
Full suite: 141 passed, 1 deselected
```

Estos valores constituyen la referencia histórica del baseline.

La cantidad de pruebas aumentará conforme se implementen los nuevos contratos.

No exigir que el número de pruebas permanezca exactamente igual durante `v0.8.x`.

**Cualquier fallo inicial debe registrarse antes de modificar código**, distinguiendo defectos preexistentes de regresiones posteriores.

No ejecutar:

```powershell
$env:PROSPECTOR_RUN_E2E = "1"
```

No realizar pruebas live de Google Maps sin autorización explícita.

---

# 6. Restricciones arquitectónicas permanentes

Durante toda la ejecución deberán preservarse las siguientes condiciones.

## 6.1 Google Maps

No modificar el comportamiento funcional de:

- Navigation.
- Result Feed.
- Summary.
- Detail.
- Website enrichment.
- Identity verification.
- Browser cleanup.
- Manejo de resultados parciales.

Sólo se permitirán modificaciones mínimas en los límites entre componentes que sean necesarias para separar extracción y resultado global.

## 6.2 Normalización

La normalización:

- Será obligatoria.
- Se ejecutará después del enriquecimiento.
- Será independiente de fuentes.
- No realizará llamadas externas.
- No modificará originales.
- Producirá exactamente un normalizado por original.
- Será determinista.
- Será idempotente.
- Recuperará campos ambiguos.
- Mantendrá progreso parcial.
- No deduplicará ni fusionará Businesses.

## 6.3 Configuración

Preservar:

```text
Engine default: 50
Google Maps Engine maximum: 100
CLI default: 50
CLI maximum: 100
Legacy wrapper default: 50
```

Preservar las excepciones de comportamiento legacy documentadas.

La nueva orquestación no debe imponer automáticamente las validaciones del Engine al wrapper histórico.

## 6.4 Exportación

Preservar:

```text
Name
Category
Address
Phone
Email
Website
Language
```

El esquema y orden de las columnas deben mantenerse.

Los valores exportados deberán proceder de `NormalizedBusiness`.

---

# 7. Estrategia general de ejecución

La implementación será secuencial:

```text
BASELINE
   |
   v
v0.8.1 — Data Contracts
   |
  P81
   |
   v
v0.8.2 — Deterministic Rules
   |
  P82
   |
   v
v0.8.3 — Normalization Engine
   |
  P83
   |
   v
v0.8.4 — Global Integration
   |
  P84
   |
   v
v0.8.5 — Consumer Integration
   |
  P85
   |
   v
v0.8.6 — Regression & Acceptance
   |
  P86
   |
   v
READY FOR OWNER ACCEPTANCE
```

Cada patch debe cumplir sus criterios de aceptación antes de comenzar el siguiente.

No avanzar con pruebas fallidas o contratos públicos incoherentes.

No modificar simultáneamente múltiples componentes no relacionados sólo para acelerar el trabajo.

La autonomía debe minimizar retrabajos y regresiones.

---

# 8. Registros operativos

Mantener la evidencia local bajo:

```text
temp/Planeacion/v0.8.0/
```

Crear, cuando se autorice la implementación:

```text
ImplementationProgress.md
ImplementationBlockers.md
ValidationMatrix.md
```

No duplicarlos si ya existen.

## 8.1 ImplementationProgress

Para cada patch registrar:

```text
Patch:
Status:
Starting HEAD:
Files created:
Files modified:
Contracts implemented:
Tests added:
Tests modified:
Tests executed:
Failures:
Corrections:
Final verification:
Gate result:
```

Estados permitidos:

```text
NOT_STARTED
IN_PROGRESS
BLOCKED
IMPLEMENTED
TESTED
GATE_PASSED
```

No marcar un patch como `GATE_PASSED` por el simple hecho de haber escrito el código.

## 8.2 ImplementationBlockers

Registrar:

```text
Blocker ID:
Patch:
Severity:
Evidence:
Affected contract:
Reproduction:
Attempted resolution:
Required decision:
Status:
```

No registrar bloqueos especulativos como defectos demostrados.

## 8.3 ValidationMatrix

Mantener los criterios N01–N31 del Master Implementation Design.

Para cada requisito registrar:

```text
Requirement:
Test:
Patch:
Observed result:
Evidence:
Status:
```

Estados permitidos:

```text
NOT_TESTED
PASS
FAIL
BLOCKED
OWNER_PENDING
```

No declarar un requisito aprobado sin evidencia reproducible.

---

# 9. Procedimiento común por patch

Cada patch seguirá este protocolo.

## Paso A — Inspección

Leer exclusivamente los módulos relevantes y sus dependencias.

Identificar:

- Interfaces afectadas.
- Comportamiento vigente.
- Pruebas existentes.
- Contratos que deben conservarse.
- Riesgos específicos.

## Paso B — Implementación

Realizar los cambios mínimos necesarios.

Evitar refactors generales.

No introducir abstractions especulativas.

## Paso C — Pruebas focalizadas

Ejecutar las pruebas directamente relacionadas.

Corregir fallos atribuibles al patch.

## Paso D — Regresión completa

Ejecutar:

```powershell
python -m compileall -q src

python -m pytest -q -p no:cacheprovider

git diff --check
```

La suite deberá continuar funcionando offline.

## Paso E — Auditoría de diff

Revisar:

```powershell
git diff --stat

git diff --check

git status --short
```

También inspeccionar archivos nuevos y documentación ignorada cuando corresponda.

Comprobar que los cambios pertenecen al alcance del patch.

## Paso F — Checkpoint

Registrar:

- Evidencias.
- Pruebas.
- Archivos afectados.
- Riesgos residuales.
- Resultado del gate.

Sólo continuar si el gate está aprobado.

---

# 10. PATCH v0.8.1 — Data Contracts

## Objetivo

Incorporar los contratos de datos necesarios para representar resultados originales y normalizados.

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

## Operaciones autorizadas

1. Crear el modelo independiente `NormalizedBusiness`.
2. Incorporar los 12 campos aprobados.
3. Preparar `SearchResult` para dos representaciones.
4. Preservar construcción transicional.
5. Proteger orden y cardinalidad.
6. Documentar los estados transitorios permitidos.

## Restricciones

No integrar todavía normalización al Engine.

No modificar CLI.

No modificar Google Maps.

No cambiar la presentación pública efectiva durante este patch.

No convertir originales en objetos normalizados ficticios para satisfacer anotaciones.

## Pruebas mínimas

- Construcción de NormalizedBusiness.
- Tipos de sus campos.
- Valores opcionales.
- Objetos independientes.
- Business original intacto.
- SearchResult vacío.
- Total found.
- Correspondencia de colecciones.
- Compatibilidad con pruebas existentes.
- Ausencia de colecciones mezcladas accidentalmente.

## Checkpoint P81

Registrar:

```text
P81 — DATA CONTRACTS

NormalizedBusiness created:
SearchResult prepared:
Original representation preserved:
Transitional compatibility:
Model tests:
Full regression:
Unexpected changes:

GATE: PASS / FAIL
```

### Condiciones de aprobación

- Modelo nuevo independiente.
- Contrato de 12 campos consistente.
- Sin modificación del pipeline de extracción.
- Suite completa verde.
- Ausencia de regresiones públicas no autorizadas.

Si P81 falla, no iniciar v0.8.2.

---

# 11. PATCH v0.8.2 — Deterministic Field Rules

## Objetivo

Crear el catálogo de funciones puras de normalización.

## Archivos principales

```text
src/engines/normalization/__init__.py
src/engines/normalization/rules.py
tests/unit/test_normalization_rules.py
```

## Reglas autorizadas

Implementar exclusivamente:

```text
name
category
address
phone
website
email
language
```

Preservar la metadata restante.

## Reglas de implementación

- Sin navegador.
- Sin red.
- Sin información externa.
- Sin inferencias.
- Sin validación empresarial.
- Sin modificación de Business.
- Sin acceso a SearchResult.
- Sin comparar negocios.

## Pruebas obligatorias

### Textos

- Mayúsculas Unicode.
- Acentos.
- Espacios externos.
- Espacios repetidos.
- Caracteres significativos.
- Valores opcionales.
- Idempotencia.

### Teléfonos

- Diez dígitos sin separadores.
- Diez dígitos con guiones.
- Diez dígitos con paréntesis.
- Diez dígitos con puntos.
- Prefijo internacional explícito.
- Extensiones.
- Caracteres desconocidos.
- Longitud inesperada.
- Preservación de dígitos.
- Idempotencia.

### URLs

- Rutas sensibles a mayúsculas.
- Parámetros.
- Fragmentos.
- Espacios externos.
- Protocolos.
- Valores ausentes.

### Emails

- Uppercase.
- Lowercase.
- Espacios externos.
- Valor ambiguo.
- Preservación de la dirección completa.

### Language y metadata

- Etiquetas regionales.
- Separadores.
- `None`.
- Booleanos.
- Estado HTTP.
- Metadata textual preservada.

## Checkpoint P82

```text
P82 — DETERMINISTIC RULES

Rules implemented:
Unit tests:
Idempotence:
Unicode:
Phone safety:
Email safety:
URL safety:
Metadata preservation:
Full regression:

GATE: PASS / FAIL
```

### Condiciones de aprobación

- Reglas puras.
- Casos válidos y contraejemplos cubiertos.
- Sin pérdida de información.
- Idempotencia verificada.
- Suite completa verde.

No iniciar P83 con reglas ambiguas no resueltas.

---

# 12. PATCH v0.8.3 — Normalization Engine

## Objetivo

Construir el módulo que recibe Businesses consolidados y produce NormalizedBusinesses independientes.

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

## Comportamiento obligatorio

El normalizador deberá:

1. Recibir un Business.
2. Procesar sus campos.
3. Aplicar reglas seguras.
4. Preservar valores ambiguos.
5. Registrar incidencias recuperables.
6. Continuar tras fallos controlados.
7. Crear un NormalizedBusiness.
8. Preservar intacto el Business original.

Para listas:

- Mantener orden.
- Mantener cantidad.
- No fusionar objetos.
- No producir duplicados adicionales.
- No compartir estado mutable.

## Semántica de errores

Reutilizar:

```text
SearchIssue
IssueCollector
```

Etapa:

```text
normalization
```

Códigos:

```text
field_unverifiable
field_unavailable
```

No introducir un segundo Error Model.

No registrar warnings por campos legítimamente ausentes o que ya cumplen una regla.

El tratamiento controlado de ambigüedad debe diferenciarse de errores internos inesperados.

## Pruebas obligatorias

- Normalización completa.
- Normalización parcial.
- Campo ambiguo.
- Varios campos ambiguos.
- Progreso posterior a un fallo.
- Original inalterado.
- Independencia de objetos.
- Cardinalidad.
- Orden.
- Correspondencia.
- SearchIssue.
- Mensajes seguros.
- Determinismo.
- Idempotencia.

## Checkpoint P83

```text
P83 — NORMALIZATION ENGINE

Engine implemented:
Independent outputs:
Originals preserved:
Field recovery:
Issues:
Order:
Cardinality:
Determinism:
Idempotence:
Full regression:

GATE: PASS / FAIL
```

### Condiciones de aprobación

- Normalization Engine operativo offline.
- Originales intactos.
- Incidencias correctas.
- Recuperación por campo.
- Suite verde.
- Ningún cambio en extracción de Google Maps.

---

# 13. PATCH v0.8.4 — Global Pipeline Integration

## Objetivo

Incorporar obligatoriamente la normalización al pipeline global para todas las entradas públicas soportadas.

Este es el principal checkpoint arquitectónico.

## Archivos principales

```text
src/engines/prospector_engine.py
src/scraper/google_maps/scraper.py
src/models/search_result.py
```

Opcional, sólo si existe necesidad demostrada:

```text
src/engines/global_pipeline.py
```

Pruebas:

```text
tests/integration/test_global_normalization_pipeline.py
```

## Estado inicial

Actualmente:

```python
ProspectorEngine.search()
    -> _run_google_maps()

search_businesses()
    -> _run_google_maps()
```

El diseño objetivo requiere una etapa común posterior a extracción.

## Comportamiento objetivo

```text
Public entrypoint
        |
        v
Global execution
        |
        +-- Source execution
        |
        +-- Normalization
        |
        +-- Result assembly
        |
        v
SearchResult
```

## Reglas de implementación

- Normalizar exactamente una vez.
- Evitar duplicar la ejecución de fuente.
- Preservar límites aprobados.
- Preservar errores fatales.
- Preservar incidencias anteriores.
- Preservar BrowserRuntime.
- Preservar la identidad.
- Preservar resultados parciales.
- Preservar cleanup.
- Construir un resultado con ambas representaciones.

La fuente no deberá incorporar reglas generales de normalización.

Los consumidores públicos no deberán omitir el pipeline global.

## Compatibilidad legacy

Verificar por separado:

```text
ProspectorEngine:
    Default 50
    Maximum 100

Legacy wrapper:
    Default 50
    Existing accepted limit behavior
```

Los valores legacy no deberán validarse automáticamente mediante las restricciones exclusivas del nuevo Engine.

No convertir una función histórica en un alias que modifique silenciosamente su política de entrada.

## Tiempo de ejecución

`SearchResult.execution_time` deberá incluir la normalización.

No duplicar los tiempos de ejecución.

Mantener las métricas internas opcionales cuando existan.

## Pruebas obligatorias

- Engine normaliza.
- Wrapper normaliza.
- Normalización única.
- Originales disponibles.
- Normalizados disponibles.
- Exactitud de los valores.
- Total found.
- Orden.
- Cardinalidad.
- Incidencias originales.
- Incidencias nuevas.
- Resultados parciales.
- Errores fatales.
- Cleanup.
- Límites.
- Cien negocios controlados offline.
- Contratos de retorno.

Evitar mocks que validen exclusivamente llamadas sin inspeccionar los datos generados.

## Checkpoint P84

```text
P84 — GLOBAL PIPELINE

Engine integration:
Wrapper integration:
Shared execution path:
Normalization exactly once:
Original preservation:
Normalized output:
Legacy limits:
Typed errors:
Partial results:
Issue propagation:
Browser cleanup:
Full regression:

GATE: PASS / FAIL
```

### Condiciones de aprobación

- Ninguna ruta pública soportada omite normalización.
- Ningún proceso normaliza dos veces.
- Las fuentes siguen funcionando.
- Wrapper compatible.
- Suite verde.
- Ausencia de regresión de identidad o cleanup.

No continuar a P85 si la integración global presenta defectos.

---

# 14. PATCH v0.8.5 — Consumer Integration

## Objetivo

Hacer que el CLI y las exportaciones consuman exclusivamente datos normalizados.

## Archivos principales

```text
src/main.py
src/services/export_service.py
src/exporters/csv.py
src/exporters/excel.py
```

## Comportamiento obligatorio

### CLI

- Mantener el menú.
- Mantener opciones.
- Mantener límites.
- Mantener flujo interactivo.
- Presentar valores normalizados.
- Mostrar incidencias recuperables.

### Exportaciones

- Mantener CSV.
- Mantener XLSX.
- Mantener siete columnas.
- Mantener orden.
- Exportar normalizados.
- No exportar originales automáticamente.

### Python

Mantener acceso a:

```python
result.businesses
result.original_businesses
result.issues
result.total_found
```

## Pruebas obligatorias

- Name uppercase.
- Category uppercase.
- Phone normalizado.
- Email lowercase.
- Language uppercase.
- Address preservada.
- Website preservada.
- CLI muestra normalizados.
- CSV contiene normalizados.
- XLSX contiene normalizados.
- Esquema sin cambios.
- Conteo correcto.
- Orden correcto.
- Datos originales disponibles.
- Fallos parciales visibles.

## Checkpoint P85

```text
P85 — CONSUMER INTEGRATION

CLI:
CSV:
XLSX:
Seven-column schema:
Normalized presentation:
Original access:
Recoverable issues:
CLI interaction:
Full regression:

GATE: PASS / FAIL
```

### Condiciones de aprobación

- Todas las salidas utilizan normalizados.
- Originales accesibles desde Python.
- Esquemas conservados.
- No se introduce persistencia.
- Suite verde.

---

# 15. PATCH v0.8.6 — Regression, Documentation & Acceptance

## Objetivo

Auditar la línea `v0.8.x` completa y preparar su aceptación.

Este patch no incorpora nuevas funcionalidades.

## 15.1 Pruebas finales

Ejecutar:

```powershell
Remove-Item Env:PROSPECTOR_RUN_E2E -ErrorAction SilentlyContinue

python -m compileall -q src

python -m pytest tests\unit -q -p no:cacheprovider

python -m pytest tests\integration -q -p no:cacheprovider

python -m pytest -q -p no:cacheprovider

git diff --check
```

Registrar las cantidades finales reales.

No asumir cantidades de pruebas.

## 15.2 Auditoría de contratos

Comprobar:

- Business original.
- NormalizedBusiness independiente.
- SearchResult.
- SearchIssue.
- ProspectorEngine.
- Legacy wrapper.
- CLI.
- ExportService.
- CSV/XLSX.
- Configuración.
- Error Model.

## 15.3 Regresión funcional

Verificar que se conservan:

- Navigation.
- Result Feed.
- Detail identity.
- Website enrichment.
- Browser lifecycle.
- Resultados parciales.
- Manejo de errores.
- Límites.

No declarar que el comportamiento live ha sido certificado mediante pruebas exclusivamente offline.

## 15.4 Auditoría de diff

Inspeccionar todos los cambios de implementación.

Detectar:

- Funcionalidades no aprobadas.
- Cambios accidentales.
- Dependencias innecesarias.
- Duplicación de normalización.
- Modificaciones de identidad.
- Cambios en exportadores.
- Contratos inconsistentes.
- Supresión de errores.
- Pruebas debilitadas.
- Código no utilizado.
- Abstracciones especulativas.

## 15.5 Documentación

Actualizar la documentación CURRENT únicamente con comportamientos comprobados.

Preservar:

- ADR-008.
- Master Implementation Design.
- Este Runbook.

No reescribir retrospectivamente las autoridades para justificar desviaciones.

Documentar diferencias inevitables únicamente cuando hayan sido aprobadas.

## 15.6 Aceptación live

Codex no deberá ejecutar pruebas live sin autorización.

Preparar un procedimiento manual para el propietario que permita revisar:

- Una búsqueda real.
- Resultado original.
- Resultado normalizado.
- CSV/XLSX.
- Incidencias.
- Ausencia de cambios indebidos en extracción.

No exigir nuevas búsquedas como parte de la suite offline.

## Checkpoint P86

```text
P86 — FINAL ACCEPTANCE AUDIT

Compileall:
Unit tests:
Integration tests:
Full suite:
Model contracts:
Global pipeline:
Wrapper:
CLI:
CSV:
XLSX:
Original preservation:
Normalization issues:
Git diff audit:
Documentation:
Known limitations:
Live verification:

GATE: PASS / FAIL
```

### Condiciones de aprobación

- Suite offline completa verde.
- Requisitos N01–N30 verificados.
- Documentación consistente.
- Sin defectos críticos conocidos.
- Sin funciones fuera del alcance.
- Sin alteraciones indebidas de Google Maps.
- Evidencia preparada para validación manual.

N31 permanece sujeto al propietario.

El estado final permitido será:

`READY FOR OWNER ACCEPTANCE`

No declarar `ACCEPTED` ni `RELEASED`.

---

# 16. Mapeo de aceptación a checkpoints

La matriz N01–N31 del Master Implementation Design deberá utilizarse como autoridad.

Distribución principal:

| Checkpoint | Requisitos |
|---|---|
| P81 | N01–N05 |
| P82 | N06–N17 |
| P83 | N02–N05, N16–N19 |
| P84 | N02–N05, N18–N23, N28–N29 |
| P85 | N24–N27 |
| P86 | N01–N30 |
| Owner | N31 |

Un requisito puede verificarse en varios checkpoints.

No basta con marcar una casilla: debe existir una prueba o evidencia inspeccionable.

---

# 17. Política de fallos

## 17.1 Fallos corregibles

Codex podrá corregir autónomamente:

- Errores sintácticos.
- Errores de tipado introducidos.
- Fallos de pruebas causados por el patch.
- Incompatibilidades transicionales previstas.
- Regresiones localizadas.
- Errores en mocks.
- Defectos de normalización.
- Errores de importación.
- Problemas de integración aprobados por el diseño.

Antes de corregir, deberá identificar la causa.

No modificar pruebas exclusivamente para eliminar fallos.

## 17.2 Fallos bloqueantes

Detener el patch afectado si ocurre cualquiera de los siguientes casos:

1. Contradicción normativa sin resolución.
2. Necesidad de modificar una decisión aprobada.
3. Regresión de identidad en Google Maps.
4. Pérdida de datos originales.
5. Alteración inesperada de cantidad u orden.
6. Error fatal ocultado.
7. Doble normalización inevitable con el diseño vigente.
8. Imposibilidad de preservar el contrato legacy.
9. Necesidad demostrada de cambiar componentes fuera del alcance.
10. Pruebas que no pueden pasar sin debilitar invariantes.
11. Dependencia de servicios externos no autorizada.
12. Cambios preexistentes que podrían sobrescribirse.
13. Problemas de entorno que impidan verificar el checkpoint.

Registrar el bloqueo y su evidencia.

## 17.3 Recuperación

No utilizar `git reset --hard`, `git clean` ni otros comandos destructivos para recuperar un checkpoint.

No borrar trabajos previos del usuario.

No sobrescribir documentación histórica.

Si una modificación propia falla, intentar una corrección focalizada.

Si no es posible demostrar integridad, detener el avance.

---

# 18. Condiciones de parada

## STOP-01 — Autoridad

Falta un documento normativo necesario o existe una contradicción esencial.

## STOP-02 — Integridad

Una transformación modifica datos originales o mezcla negocios.

## STOP-03 — Regresión

Se altera una garantía de `v0.7.x`.

## STOP-04 — Compatibilidad

No se puede mantener la ruta legacy dentro del diseño aprobado.

## STOP-05 — Pruebas

Un gate falla y no puede corregirse dentro del alcance.

## STOP-06 — Alcance

La solución requiere funcionalidades de `v0.9.x` o posteriores.

## STOP-07 — Entorno

No es posible ejecutar verificaciones offline confiables.

## STOP-08 — Estado local

Existen cambios ajenos que podrían sobrescribirse.

## STOP-09 — Autorización

Se requiere ejecutar una búsqueda live, hacer push, modificar ramas o realizar una acción no autorizada.

## STOP-10 — Incertidumbre crítica

La implementación exigiría decidir unilateralmente una política no contemplada en las autoridades.

Cuando se active una condición:

- Registrar evidencia.
- Conservar los archivos.
- No destruir el progreso.
- No marcar el checkpoint como aprobado.
- No continuar con patches dependientes.
- Informar exactamente qué decisión o intervención se requiere.

---

# 19. Política de modificaciones permitidas

## Permitido

Crear o modificar código correspondiente a:

```text
src/models/normalized_business.py
src/models/search_result.py
src/engines/normalization/
src/engines/prospector_engine.py
src/engines/issue_collector.py
src/scraper/google_maps/scraper.py
src/main.py
src/services/export_service.py
src/exporters/
```

Crear o modificar pruebas relacionadas bajo:

```text
tests/unit/
tests/integration/
```

El componente `global_pipeline.py` es opcional y sólo se creará si evita duplicación o dependencias inadecuadas.

## Restringido

No modificar salvo necesidad específica demostrada:

```text
src/engines/navigation/
src/engines/selector/
src/engines/browser_runtime.py
src/engines/website/
src/scraper/google_maps/detail_panel.py
src/scraper/google_maps/result_list.py
src/scraper/google_maps/search.py
```

No ampliar dependencias sin autorización.

No introducir nuevas fuentes.

No implementar persistencia.

No cambiar la arquitectura de exportación fuera de lo necesario para consumir NormalizedBusiness.

---

# 20. Estrategia de pruebas

## 20.1 Pruebas de comportamiento

Las pruebas deberán inspeccionar resultados reales.

No limitarse a comprobar:

```python
assert normalize.called_once()
```

También verificar:

```python
assert result.businesses[0].name == "HOSPITAL EXCEL"
assert result.original_businesses[0].name == "Hospital Excel"
```

Las pruebas deben demostrar la transformación efectiva.

## 20.2 Pruebas de independencia

Comprobar:

- Objetos distintos.
- Campos originales intactos.
- Cambios posteriores independientes.
- Ausencia de referencias mutables compartidas.
- Preservación de atributos opcionales.

## 20.3 Pruebas de errores

Verificar que:

- Un fallo afecta sólo al campo correspondiente.
- Se conserva el valor original.
- Se registra la incidencia.
- Continúan los demás campos.
- Continúan los demás negocios.
- No se eliminan incidencias anteriores.

## 20.4 Pruebas de compatibilidad

Comprobar:

- Límites Engine.
- Límites legacy.
- CLI.
- CSV/XLSX.
- Resultados parciales.
- Cleanup.
- Error Model.

## 20.5 Pruebas E2E

La ejecución predeterminada será offline.

No habilitar pruebas live sin autorización.

No sustituir pruebas controladas por búsquedas reales para demostrar reglas de normalización.

---

# 21. Control de rendimiento

La normalización deberá operar localmente.

No se establece un límite temporal absoluto nuevo sin evidencia de referencia.

Las pruebas podrán medir la sobrecarga del proceso sobre colecciones controladas.

No confundir tiempo de extracción con tiempo de normalización.

No introducir paralelismo, cachés externas o procesamiento distribuido para optimizar prematuramente esta etapa.

No sacrificar trazabilidad o integridad por reducciones marginales de tiempo.

---

# 22. Control documental durante la ejecución

Los registros locales deberán reflejar el estado real.

## 22.1 Al iniciar un patch

Registrar:

```text
Patch:
Starting state:
Files expected:
Tests expected:
Risks:
```

## 22.2 Al terminar un patch

Registrar:

```text
Patch:
Files changed:
Contracts:
Tests:
Results:
Failures:
Residual risks:
Gate:
```

## 22.3 Al detectar bloqueo

Actualizar ImplementationBlockers inmediatamente.

No ocultar un fallo esperando resolverlo más adelante sin registrarlo.

## 22.4 Documentación oficial

Actualizarla únicamente cuando el código implementado respalde la afirmación.

No describir la normalización como funcional mientras todavía sea una propuesta.

No declarar aceptación final por completar las pruebas.

---

# 23. Informe final obligatorio

Al terminar la ejecución autorizada, entregar:

```text
PROSPECTOR CLI
v0.8.x AUTONOMOUS IMPLEMENTATION REPORT

REPOSITORY
----------
Branch:
Starting HEAD:
Final HEAD:
Working tree:
Commits created:
Push performed:

AUTHORITIES
-----------
ADR-008:
Master Implementation Design:
Runbook:

PATCHES
-------
v0.8.1 / P81:
v0.8.2 / P82:
v0.8.3 / P83:
v0.8.4 / P84:
v0.8.5 / P85:
v0.8.6 / P86:

IMPLEMENTATION
--------------
Files created:
Files modified:
Contracts changed:
Public API changes:
Source pipeline changes:

VALIDATION
----------
Compileall:
Unit:
Integration:
Full suite:
E2E:
Integrity:
Legacy compatibility:
CSV:
XLSX:

ACCEPTANCE MATRIX
-----------------
N01–N30:
N31:

RISKS
-----
Known limitations:
Unresolved issues:
Blockers:

DIFF AUDIT
----------
Unexpected files:
Scope violations:
Documentation consistency:

FINAL STATUS
------------
READY FOR OWNER ACCEPTANCE
or
BLOCKED

OWNER ACTIONS
-------------
```

El reporte debe distinguir hechos verificados, limitaciones conocidas y pruebas no ejecutadas.

No afirmar que todas las pruebas pasaron si alguna no fue ejecutada.

---

# 24. Criterio de finalización

La ejecución autónoma estará terminada cuando:

1. Se completen P81–P86.
2. Los seis patches cumplan sus gates.
3. Los requisitos N01–N30 tengan evidencia.
4. Los originales permanezcan intactos.
5. La normalización sea obligatoria.
6. SearchResult exponga ambas representaciones.
7. CLI y CSV/XLSX utilicen datos normalizados.
8. Los pipelines de fuente conserven su comportamiento.
9. La regresión offline sea satisfactoria.
10. La documentación sea consistente.
11. No existan defectos bloqueantes conocidos.
12. Se entregue el informe final.

No se requiere un smoke test live autónomo.

El propietario realizará la aceptación operativa posterior.

---

# 25. Resolución del runbook

**STATUS: APPROVED — OWNER APPROVAL**

Este runbook define la ejecución autónoma completa de `v0.8.x` mediante seis checkpoints:

- P81 — Data Contracts.
- P82 — Deterministic Field Rules.
- P83 — Normalization Engine.
- P84 — Global Pipeline Integration.
- P85 — Consumer Integration.
- P86 — Regression, Documentation & Acceptance.

Cada checkpoint obliga a verificar sus contratos antes de permitir el siguiente.

Codex podrá resolver autónomamente problemas técnicos dentro de las decisiones aprobadas, pero no podrá modificar dichas decisiones, ampliar el alcance, ejecutar búsquedas live o publicar cambios sin autorización.

La ejecución completa requiere una orden explícita posterior del propietario.

**Fin del documento.**