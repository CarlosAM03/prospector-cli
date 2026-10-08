# Prospector CLI — v0.9.x Autonomous Implementation Runbook

**Proyecto:** Prospector CLI  
**Versión objetivo:** `v0.9.x` (`v0.9.1`–`v0.9.6`)  
**Fecha de elaboración:** 2026-10-06  
**Rama/commit de referencia:** `v0.8.0` / `d1880e7ca305ff326eeac9e1e7c1ccd02e981b1d`  
**Autoridades:** ADR-008 (`APPROVED`), ADR-009 (`APPROVED`), `V0-9-x-Master-Implementation-Design.md` (`ACCEPTED — DESIGN BASELINE`)  
**Estado del runbook:** `APPROVED BY OWNER — READY FOR IMPLEMENTATION`  
**Estado de implementación:** `NOT STARTED / NOT AUTHORIZED`  
**Tipo de documento:** procedimiento operativo normativo para una ejecución **posteriormente autorizada** de Codex.  

> **Control de autorización.** La creación, lectura y aceptación de este runbook **no autorizan** a Codex a escribir archivos de producción o pruebas, crear o cambiar ramas, realizar commits, pushes, merges, tags o releases, ejecutar búsquedas reales ni actualizar GitHub. Antes de entrar en modo de escritura debe existir una autorización **explícita y separada** del propietario que indique entorno, rama y alcance permitido. Sin ella, toda acción de Codex queda limitada a inspección de solo lectura, diseño y reporte. Ningún «seguir adelante» implícito reemplaza este control.

---

## 1. Propósito, jerarquía y resultado esperado

Este runbook define cómo Codex implementará, **solo una vez autorizado**, el Master en seis patches secuenciales verificables: P91, P92, P93, P94, P95 y P96. No redefine la arquitectura ni toma decisiones de negocio. Ante diferencias entre documentos, prevalecen ADR-008 y ADR-009 aprobados; luego el Master aceptado y, por último, este procedimiento. Si la contradicción modifica una decisión normativa, **STOP / OWNER REVIEW**; no crear una interpretación unilateral.

**Resultado esperado de v0.9.x:** un consumidor Python invoca `ProspectorEngine.search_many(queries)` con entre 1 y 5 `BatchQuery` ordenadas y límites propios entre 1 y 100. El Engine ejecuta **una consulta por vez** y retorna resultados individuales completos más asignaciones de deduplicación **únicamente interconsulta** basadas en identidad de establecimiento verificable. El CLI permite configurar 2 o 3 búsquedas, confirmar antes de iniciar y exportar **un CSV o XLSX por consulta válida**, con siete columnas. No se produce una lista comercial global ni merge de campos. El Engine no exporta archivos.

**No objetivos:** dedupe intraconsulta adicional, detección difusa, carga de CSV históricos, CRM, campañas, persistencia, APIs HTTP, SaaS, multitenancy, colas, workers, concurrencia intra-batch, pooling, nuevas fuentes, cambios a ADR-008, hardening general de v1.0.0 ni primer release estable.

La experiencia DATRA es evidencia de separación de fases (`FiltroEntreBusquedas` versus `FiltroExistentes`), no fuente de reglas comerciales dentro del Engine. Nunca prometer ausencia absoluta de duplicados: la garantía se limita a **identidades verificadas**.

---

## 2. Preflight obligatorio y condiciones de entrada

**Solo inspección previa; no cambiar estado Git ni archivos.** Antes de cualquier patch:

1. Leer íntegramente ADR-008, ADR-009 aprobado y Master aceptado; leer README, `docs/architecture.md`, `docs/roadmap.md`, `docs/scripting-pipeline.md`, `docs/pipelines/google_maps.md`, `tests/README.md` y archivos de código directamente involucrados.
2. Verificar el cierre documental de v0.8.0; si GitHub todavía presenta `OWNER_ACCEPTANCE_PENDING`, **registrar** la discrepancia, sin dar por publicado un cierre no reflejado allí ni editarlo automáticamente. La aceptación del propietario y su salvedad N31 no equivalen a modificación remota.
3. Registrar en el acta el resultado de `git branch --show-current`, `git rev-parse HEAD`, `git status --short`, `git log -1 --oneline` y `git diff --stat`.
4. Comprobar que el código base corresponde a `d1880e7...` o a un sucesor documentado y autorizado; no asumirlo porque la rama se llame `v0.8.0`.
5. Si hay archivos locales sin confirmar o una rama/commit inesperados, **STOP** y consultar al propietario. No usar `git checkout`, `reset`, `clean`, `stash`, `rebase` o comandos destructivos para «arreglar» la situación.
6. Verificar versión de Python, dependencias disponibles y cómo el proyecto carga `src`. No instalar/actualizar dependencias de manera no autorizada.
7. Ejecutar baseline **solo si la autorización posterior permite pruebas offline**: `python -m compileall -q src` y tests unitarios/integración/suite `-m "not e2e"`. El baseline histórico aceptado fue **185 PASS (151 unit + 34 integration), 1 E2E deseleccionada**, no un resultado que deba falsificarse o exigirse como mismo número después de añadir pruebas.
8. Confirmar explícitamente que `PROSPECTOR_RUN_E2E` está desactivada y que no se realizarán llamadas live, navegación Google Maps ni website enrichment externos durante las pruebas del runbook.

### 2.1. Comandos sugeridos (Windows PowerShell; solo cuando se autoricen pruebas)

```powershell
# Lecturas de Git
 git branch --show-current
 git rev-parse HEAD
 git status --short
 git log -1 --oneline
 git diff --stat

# Desactivar opt-in E2E y usar directorios temporales exclusivos.
Remove-Item Env:PROSPECTOR_RUN_E2E -ErrorAction SilentlyContinue
$base = Join-Path $env:TEMP ("prospector-v09-" + [guid]::NewGuid().ToString("N"))
python -m compileall -q src
python -m pytest tests\unit -q -m "not e2e" --basetemp="${base}-unit"
python -m pytest tests\integration -q -m "not e2e" --basetemp="${base}-integration"
python -m pytest -q -m "not e2e" --basetemp="${base}-all"
```

Si un comando no funciona por diferencias de entorno, registrar el error exacto, aislar si es infraestructura o funcionalidad, y repetir mediante método equivalente sin cambiar comportamiento de código de producción. Evitar el `--basetemp` fijo que previamente dio `WinError 5`.

**Gate PRE-0:** autoridades disponibles, base trazable, permisos explícitos, worktree conocido y validación inicial documentada. Sin este gate, no se comienza P91.

---

## 3. Política de autonomía y restricciones permanentes

### 3.1. Codex puede hacer, únicamente tras autorización de implementación

- Editar solo archivos estrictamente necesarios para los contratos y patches autorizados.
- Agregar tipos y módulos mínimos, pruebas deterministas y documentación correspondiente a funcionalidades realmente implementadas.
- Ejecutar `compileall`, pytest y verificaciones estáticas locales **offline** aprobadas.
- Construir fixtures sintéticos con identidades conocidas; usar el flujo DATRA solo como inspiración estructural sin mezclar datos de clientes/campañas.
- Registrar progreso, bloqueos, pruebas, diffs y decisiones en los documentos operativos locales de ejecución.
- Corregir defectos del mismo patch demostrados por una prueba, sin cambiar contratos del ADR o Master.

### 3.2. Codex no puede asumir autorización para

- Ejecutar pruebas live/E2E, Chrome sobre Google Maps o inspección externa de sitios.
- Realizar acciones de Git que modifiquen la historia, ramas remotas o publicación (`commit`, `push`, merge, tag, release); estas requieren autorización independiente aunque el código local esté aprobado.
- Convertir un token de navegación (`href`, `!1s` u otro) en identidad estable sin prueba verificable y documentada.
- Hacer matching por nombre, categoría, teléfono, dirección, correo o dominio; introducir scoring, umbrales, aproximación o merges comerciales.
- Modificar los doce campos de `Business`/`NormalizedBusiness`, la normalización de ADR-008, contratos públicos v0.8.x o el comportamiento del modo de búsqueda individual.
- Añadir campañas, históricos, bases de datos, FastAPI, jobs, pooling, concurrencia intra-batch ni límites distintos a los aprobados.
- Reescribir pruebas para ocultar resultados, deshabilitar gates o declarar aceptación del propietario.

**Regla operativa:** una autorización futura de *implementación local* no otorga por sí sola autorización de Git remoto, pruebas live o release.

---

## 4. Evidencia y documentos de ejecución

Cuando la implementación sea autorizada, crear o actualizar **solo en la ubicación local aprobada** (propuesta: `temp/Planeacion/v0.9.0/`):

| Archivo | Contrato mínimo |
|---|---|
| `ImplementationProgress.md` | Inicio/fin, baseline, patch activo, acciones, archivos y gate por patch |
| `ImplementationBlockers.md` | Riesgos, STOP, evidencia, fecha, estado, resolución del propietario |
| `ValidationMatrix.md` | G01–G23 con casos, tests, ejecución, resultado y prueba de cumplimiento |
| `AuditDiff.md` | Archivos tocados, motivo, diff previsto vs real, invariantes, cambios fuera de alcance |
| `EvidenceIndex.md` | Referencia a logs y reportes, comandos exactos, ambiente, SHA/estado Git, runs offline y aceptación |

La carpeta `temp/` puede estar ignorada por Git: no confundir esta evidencia local con contenido publicado en repositorio. Conservar copia trazable antes del cierre y no publicar por defecto archivos DATRA o datos de terceros. En cada checkpoint registrar:

```text
CHECKPOINT: P9X
Start SHA / Branch / Worktree status:
Scope and changed files:
Tests run (exact commands):
PASS / FAIL / SKIP / NOT RUN:
Regression vs baseline:
Gate IDs verified:
Observed risks / remaining work:
Unexpected changes:
STOP conditions checked:
Decision: PASS | FAIL | BLOCKED
Owner authorization reference (if relevant):
```

**No simular evidencia:** un test no ejecutado queda `NOT RUN`; un gate dependiente de prueba live queda `PENDING LIVE AUTHORIZATION`, no `PASS`.

---

## 5. Orden obligatorio de patches y checkpoints

**Secuencia:** `P91 → P92 → P93 → P94 → P95 → P96`. Un patch `BLOCKED` o `FAIL` impide avanzar a dependencias posteriores. Cada patch se concluye con revisión de diff y regresión offline; no combinar arreglos ajenos al patch para «aprovechar» la ejecución.

### P91 — `v0.9.1`: Contratos públicos y preflight

**Objetivo:** introducir contratos de batch sin navegación ni deduplicación operativa, manteniendo `search()` intacto.

**Archivos y responsabilidades:** `src/models/` (tipos públicos y `__init__`), `src/engines/errors.py` (interrupción), fachada `prospector_engine.py`/módulo cohesivo de preflight y tests. Los nombres deben respetar Master §4, con responsabilidad clara y sin nuevas capas artificiales.

**Implementar:**

1. `BatchQuery(query: SearchQuery, limit: int)` como dataclass frozen superficial; hacer snapshot defensivo **real** de `SearchQuery` para aislar cambios posteriores del llamador.
2. `QueryStatus` (`SUCCESS`, `SUCCESS_WITH_ISSUES`, `PARTIAL`, `FAILED`), `ObservationDisposition`, `ObservationRef`, `DuplicateReference`, `QueryFailure`, `BatchQueryResult`, `BatchSearchResult`, y auxiliar tipado de procedencia.
3. `BatchInterruptedError` tipado con prefijo seguro `completed`, índice interrumpido, código de razón e índices no ejecutados. Solo se usará para defectos/aislamiento que obliguen a parar.
4. Validación **pre-Playwright** de secuencia **ordenada de 1 a 5** (no iterador/generador/string/set/map), tipo de cada request, fuente soportada, tipos ya admitidos para keyword/location, límites `type(limit) is int` y `1 <= limit <= 100`, y `EngineConfig` existente, sin cambiar `search()`.
5. `entries` ordenadas con referencias a solicitudes *snapshot*, semántica de estados/errores, contadores **derivados** y estructura de selección de exportación sin inventar datos.

**Tests:** 0/1/5/6; `None`, tipos inválidos, `True`, 0/100/101; fuente no soportada; entrada mutable alterada durante ejecución simulada; queries iguales con índice distinto; fallo `FAILED` sin resultado; selección no duplicada y en rango; conteos coherentes. No iniciar navegador.

**Criterios:** P91 `PASS` solo si ninguna entrada inválida alcanza Playwright y todos los contratos satisfacen Master §4; regresión previa sin fallos. **Evidencia:** modelos, tests, comandos, diff y resultado.

### P92 — `v0.9.2`: Identidad de fuente y sidecar

**Objetivo:** transportar un vector de evidencias 1:1 con el `Business[]` original, sin alterar campos de negocio o normalizar dos veces.

**Archivos y responsabilidades:** `src/scraper/google_maps/result_list.py`, `detail_panel.py`/auxiliares estrictamente necesarios, `scraper.py`/`_SourceResult`, `src/engines/global_pipeline.py` (ruta privada compatible), tests unitarios/integración sin red.

**Implementar:**

1. Tipos internos `VerifiedSourceIdentity(source, kind, value)` y `SourceIdentityEvidence(verified | None, verification_state, reason)` con namespaces explícitos y comparación exacta.
2. Sidecar ordenado `identities` de igual longitud que `businesses` del mismo `_SourceResult`, incluidos caminos de recuperación y fallos de enriquecimiento.
3. Transporte de evidencia desde feed → detail → resultado consolidado → contexto privado (`SearchResult`, sidecar). La ruta pública `search()` continúa devolviendo solo `SearchResult` actual.
4. Una política **demostrada** de validación del identificador del **mismo establecimiento**: formato/namespace conocido, vínculo al candidato y verificación de navegación/panel correcta cuando aplica. `extract_place_id(href)` utilizado para navegación **no certifica estabilidad por sí solo**.
5. `UNVERIFIED` ante ausencia, ambigüedad, fallo de verificación o formato desconocido; nunca sintetizar IDs. Un sidecar desalineado es defecto estructural crítico, no un caso corriente `UNVERIFIED`.

**Tests exigidos:** mismo establecimiento dos veces; dos sucursales; nombres homónimos; identificadores con prefijos parecidos; `href` sin token/desconocido; token `!1s` sin prueba adicional; panel incorrecto, fallo de detalle, fallback, website inspection fallido, preservación summary, ausencia y errores; continuidad de orden/cantidad y dos vistas de v0.8.x.

**Gate P92 (crítico):** demostrar **qué** identificador está reconocido y **por qué** es estable y vinculado al establecimiento. Distinguir `VERIFIED` vs `UNVERIFIED` con fixtures negativos suficientes. Si solo hay supuestos o se necesitaría deduplicar especulativamente, registrar `BLOCKED: IDENTITY_EVIDENCE_INSUFFICIENT`, **STOP / OWNER REVIEW** y no declarar funcional la deduplicación real. No realizar una búsqueda live «para confirmarlo» sin autorización expresa.

### P93 — `v0.9.3`: Coordinación secuencial y fallos

**Objetivo:** implementar `ProspectorEngine.search_many(queries)` reusando la ejecución individual, con runtime independiente por consulta.

**Implementar:**

1. Preflight/snapshot de **todo el lote** antes de abrir Playwright.
2. Ejecutar cada `BatchQuery` con límite propio, **sin mutar** `EngineConfig` ni el `SearchQuery` original, usando misma extracción/enrichment/normalización única de `search()`.
3. Asegurar cierre de páginas/Chromium/Playwright **antes** de empezar consulta siguiente; ninguna exclusión mutua global entre invocaciones distintas.
4. Conservar cada `SearchResult` completo y sidecar alineado; clasificar `SUCCESS`, `SUCCESS_WITH_ISSUES`, `PARTIAL` (`feed/partial_results`) y `FAILED`.
5. Capturar únicamente fallos fatales **tipados, controlados y seguros** por consulta, sin traceback ni URL en `QueryFailure`; continuar siguientes consultas tras estos fallos.
6. Ante bug inesperado, invariantes violados o cleanup no confiable: **interrumpir** con `BatchInterruptedError` y prefijo de entradas ya completadas, distinguiendo consulta interrumpida y aún no ejecutadas; no capturar `Exception` globalmente ni inventar resultados.
7. Registrar duración por consulta y duración total sin introducir nueva política de logging global.

**Tests:** A/B/C ordenado; contador de navegadores simultáneos máximo 1 dentro del lote; B `FAILED` y A/C conservadas; `PARTIAL` de 40/75 simulada; error normalización inesperado; browser cleanup fallido; ninguna continuación tras ruptura de aislamiento; preservación de `Business`/`NormalizedBusiness`/issues/orden/total; límites 100 por request.

**Gate P93:** `PASS` si la suite controlada confirma secuencialidad, cleanup, clasificación y compatibilidad individual. La fuente live no es un requisito offline.

### P94 — `v0.9.4`: Dedupe interconsulta y procedencia

**Objetivo:** seleccionar observaciones exportables **sin cambiar los resultados individuales** y sin merge de campos.

**Implementar:** algoritmo puro sin Playwright con índice efímero `VerifiedSourceIdentity -> ObservationRef` de **consultas anteriores**. Al recorrer cada entrada: usar `seen_previous` para suprimir coincidencias; `seen_current` separado para no hacer dedupe dentro de la misma consulta; al terminar, transferir solo la primera observación de cada identidad nueva al índice de las consultas futuras. El ganador pertenece a la menor posición de consulta y observación aplicables; un `PARTIAL` válido también puede ganar. Identidades desconocidas siempre exportables.

**Salidas:** `export_indices`, `suppressed: DuplicateReference[]`, `unverified_identity_indices`, procedencia por observación (estado/consulta/índice/evidencia/ganador), y métricas derivadas. Los `SearchResult` originales/normalizados/issues/total_found se conservan intactos; sin fill-in, reemplazo ni mezcla de campos comerciales.

**Tests:** A `[1,2,3]`, B `[2,4,5]`, C `[1,5,6]` → archivos `[1,2,3]`, `[4,5]`, `[6]`; misma identidad repetida *dentro* de A debe seguir apareciendo dos veces en A; identidad repetida en consulta posterior apunta a primera observación de A; fuente/namespace diferente no equivale; `UNVERIFIED` se conserva; sucursales y homónimos no se colapsan; nombre distinto con mismo ID verificado se asigna; datos posteriores más completos no sustituyen al ganador; `FAILED` no contribuye al índice; `PARTIAL` sí.

**Invariantes obligatorias:**

```text
total_observations = total_exportable + duplicates_suppressed
unverified_identity_indices ⊆ export_indices
export_indices: únicos, orden ascendente y dentro de rango
suppressed: cada índice vinculado exactamente a un ganador anterior
SearchResult: cardinalidad original == normalizada == total_found
sin doble clasificación, sin reordenamiento, sin mutación
```

**Gate P94:** `PASS` únicamente si se satisfacen todas las invariantes con pruebas puras, no con la presunción de que Google Maps siempre aporta IDs.

### P95 — `v0.9.5`: CLI y exportación individual

**Objetivo:** que el usuario configure 2 o 3 búsquedas antes del navegador y obtenga archivos separados con dedupe interconsulta aplicada.

**Implementar:**

1. Mantener flujo `New Search` de `main.py`; añadir `Multiple Searches`.
2. Capturar keyword, ubicación y límite por búsqueda (default 50, máximo 100); tras dos permitir iniciar o añadir tercera; impedir cuarta; mostrar resumen completo y confirmar antes de ejecutar.
3. Si se cancela, no crear navegador ni archivo. Invocar `search_many()` una sola vez.
4. Mostrar por consulta estado, límite, obtenidos, exportables, suprimidos, identidades no verificadas, issues, tiempo y fallos seguros.
5. Agregar adaptador de vista exportable (`ExportSelection` / `ExportView`) que seleccione `NormalizedBusiness` por `export_indices`, **sin fabricar un SearchResult falso** ni modificar originales. Reutilizar serialización del `ExportService` actual y siete columnas en el mismo orden.
6. Si se solicita exportación, generar **un archivo CSV o XLSX por resultado válido** (`SUCCESS`, `SUCCESS_WITH_ISSUES`, `PARTIAL`), incluido encabezado/hoja `Businesses` y cero filas cuando todo fue suprimido; `FAILED` no crea archivo. Permitir omitir exportación.
7. Naming incorpora identificador efímero único de lote, ordinal `q01`, `q02`, etc. y protección contra sobrescritura incluso con queries iguales; no agregar columnas extras de identidad.
8. Ante error de filesystem/IO, indicar consulta afectada y archivo incompleto sin declarar éxito de exportación; no perder resultados del Engine. En interrupción crítica no presentar batch como completo; ofrecer solamente resultados previos seguros conforme al Master.

**Tests:** interacción cancelar/iniciar tras segunda/agregar tercera; CLI no inicia navegador antes de confirmar; cuatro no admitidas; nombres de archivo únicos; CSV/XLSX estructura de siete campos; XLSX hoja `Businesses`; cero exportables produce encabezados/hoja sin filas; `FAILED` sin archivo; formato omitido; queries iguales; fallo IO; preservación del modo individual y `ExportService.export()` anterior.

**Gate P95:** salida separada por búsqueda válida, sin duplicados de identidad verificada entre archivos distintos, sin regresión de exportación individual.

### P96 — `v0.9.6`: Regresión integral, documentación y auditoría

**Objetivo:** demostrar G01–G22 offline y dejar v0.9.x lista para revisión manual, **no** aceptarla ni publicarla automáticamente.

**Actividades obligatorias:**

1. Completar `ValidationMatrix.md` de G01–G23 con vínculos a pruebas reales: marcar G23 `PENDING OWNER LIVE AUTHORIZATION` (no ejecutar live).
2. Compilar, ejecutar tests unitarios/integración y suite completa `-m "not e2e"`; usar temp únicos y conservar logs. Comparar regresión con baseline 185 PASS, sin exigir conteo idéntico.
3. Ejecutar fixtures sintéticos representativos de DATRA: listas de varios sectores, repetidos entre consultas, homónimos, sucursales, registros incompletos, casos históricos **solo como negativos** que prueben que no se leen ni comparan.
4. Auditar **todo diff** respecto al SHA de baseline autorizado y enumerar cada archivo nuevo/modificado. Clasificar cada cambio dentro de uno de P91–P96. Detectar cambios inesperados, dependencias nuevas, APIs nuevas no aprobadas, campo 13, alteración de límites, merge o dedupe intraconsulta.
5. Actualizar README, `docs/architecture.md`, `docs/roadmap.md`, `docs/scripting-pipeline.md`, `docs/pipelines/google_maps.md`, `docs/contributing.md` si corresponde y `tests/README.md`, diferenciando CURRENT verificado de NEXT/TARGET y de pendientes de aceptación. No declarar `v0.9.x ACCEPTED` ni `RELEASED`.
6. Revalidar específicamente `search()`, wrapper legado y export individual; comprobar errores y limpieza por sesión; reportar rendimiento simulado y límites observados.
7. Elaborar reporte final con gates, SHA/worktree, defectos, deuda aceptable, riesgos críticos y decisión solicitada al propietario.

**Gate P96:** `PASS OFFLINE / OWNER ACCEPTANCE PENDING` solamente si G01–G22 están cubiertos y sin defectos bloqueantes. Si una prueba requerida falla, `FAIL` y corregir dentro de alcance o escalar. G23 no cambia de pendiente por inferencia.

---

## 6. Matriz compacta de trazabilidad de gates G01–G23

| Gate | Prueba indispensable | Patch principal |
|---|---|---|
| G01 | `search()` y wrapper legado, normalización una vez, interfaces y errores | P93 / P96 |
| G02 | 1–5 válidas, 0/6/tipos/fuentes/límites inválidos rechazados antes del browser | P91 |
| G03 | CLI 2–3, confirmación, cancelación sin ejecuciones | P95 |
| G04 | Orden secuencial y cleanup por consulta, sin solapamiento | P93 |
| G05 | Dos queries iguales, dos entradas y archivos sin colisión | P91 / P95 |
| G06 | Originales/normalizados/issues/orden/count preservados | P92 / P93 |
| G07 | Mismo establecimiento verificado solo en primera exportación | P92 / P94 |
| G08 | Homónimos, sucursales, identidad desconocida conservados | P92 / P94 |
| G09 | Cada supresión traza ganador anterior | P94 |
| G10 | Sin merge/reemplazo desde observación posterior | P94 |
| G11 | CSV/XLSX 7 columnas; vacío válido; FAILED sin archivo | P95 |
| G12 | B falla tipado y C continúa; parciales persisten | P93 |
| G13 | Interrupción crítica y prefijo seguro, sin simular pendientes | P93 |
| G14 | Conteo de observados/exportables/suprimidos consistente | P94 |
| G15 | Sin extracción adicional para compensar deduplicados | P93 / P94 |
| G16 | Sidecar completo y alineado en todas las rutas | P92 |
| G17 | Snapshot de `SearchQuery` contra modificación externa | P91 / P93 |
| G18 | A/B/C producen vistas/archivos disjuntos por identidad verificada | P94 / P95 |
| G19 | Escenarios DATRA sintéticos, no heurísticos de campañas | P92 / P94 |
| G20 | Sin histórico CSV/DB/campañas/estado persistido | P96 |
| G21 | Métricas seguras por query y lote; sin URLs sensibles | P93 / P96 |
| G22 | Regresión CLI y export individual v0.8.x | P95 / P96 |
| G23 | Live autorizado por propietario, con evidencia y diff revisado | **Posterior, no automático** |

**La matriz extendida y contratos completos están en el Master y ADR.** No cambiar nombre, numeración ni significado de G01–G23.

---

## 7. STOP / OWNER REVIEW: condiciones de parada inmediata

Detener de inmediato, preservar trabajo/evidencia y reportar antes de avanzar cuando ocurra cualquiera de los siguientes:

1. No se puede certificar identidad Google Maps suficientemente estable y perteneciente al mismo establecimiento. No sustituir con `href`, `!1s` o coincidencias textuales por conveniencia.
2. Sidecar de identidad faltante, longitud desigual, desorden o asociación equivocada que requiera romper ADR-008 o modelos públicos de 12 campos.
3. Un cambio afecta firma, política, compatibilidad o semántica de `search()`, wrapper, `SearchResult`, `ExportService.export()` o normalización única.
4. Aislamiento de Playwright no verificable, cierre defectuoso o necesidad de encubrir errores inesperados como recuperables.
5. Se requiere cambiar dedupe a intraconsulta, introducir merge comercial, matching heurístico, históricos, campañas, persistencia, API o ejecución paralela.
6. Pruebas deterministas fallidas o regresión no explicada; nunca rebajar asserts para obtener verde.
7. Trabajo Git inicial sucio, rama o SHA diferentes a los autorizados; intervención de otro proceso que cambia archivos durante patch.
8. Se necesita una nueva dependencia, acceso a internet, cambio de límite, fuente o semántica de token de identidad no aprobados.
9. Cualquier prueba live, escritura en GitHub, branch, commit, tag, merge, release o publicación documental sin autorización específica.
10. Una decisión del ADR/Master está incompleta o se contradice con el código real de modo que obliga a elegir una política arquitectónica.

**Plantilla de bloqueo:**

```text
STOP ID:
Patch / Gate:
SHA / Branch / Changed files:
Observed behavior and exact evidence:
Normative contract threatened:
Why a safe implementation is impossible within current authorization:
Options and tradeoffs (no unilateral choice):
Tests already executed:
Safely preserved work / rollback not performed:
Required owner decision:
Status: BLOCKED — AWAITING OWNER
```

**No usar** `git reset --hard`, `git clean -fd`, revertir archivos del propietario ni borrar evidencia en respuesta a un STOP. Documentar propuestas, no ejecutar restauración destructiva.

---

## 8. Ciclo autónomo permitido por patch (una vez autorizado)

```text
1. Leer contratos ADR-009 + Master + tests afectados
2. Inspeccionar código y git status (solo lectura)
3. Registrar objetivo, alcance y tests del patch
4. Hacer cambios mínimos dentro de scope autorizado
5. Compilar y ejecutar tests focalizados offline
6. Ejecutar suite de regresión offline
7. Auditar diff y side effects
8. Actualizar evidencia y ValidationMatrix
9. Verificar STOP conditions
10. Marcar P9X PASS / FAIL / BLOCKED
11. Solo si PASS, continuar al siguiente patch
```

No crear commits entre patches sin permiso expreso. Si el propietario autoriza commits locales, tratarlos como checkpoints separados del permiso para `push`; registrar SHA real y jamás inventar hashes. No ejecutar reintentos live para resolver incertidumbre de identidad. No actualizar README a `CURRENT` antes de que código y pruebas lo justifiquen.

---

## 9. Criterios de finalización y auditoría de entrega

Al terminar P96, producir en el entorno autorizado un **informe de implementación** que incluya:

- Autoridades usadas, SHA de partida, rama, estado final del worktree, permisos efectivamente otorgados.
- Tabla P91–P96 con cambios reales y gates `PASS`, `FAIL` o `BLOCKED`.
- Matriz G01–G22 con logs offline y G23 expresamente pendiente (salvo posterior autorización live).
- Resultado de `compileall`, suite unitaria, integración y completa con totales, exclusiones y tiempos de ejecución.
- Auditoría de diff: ficheros afectados, riesgos, compatibilidad, dependencias nuevas (idealmente ninguna), cambios de configuración, exclusiones confirmadas.
- Evidencia de identidad verificable; límites y cobertura; tasa de observaciones `UNVERIFIED` en fixtures sin presentarla como métrica live.
- Escenarios fallidos/recuperados, cleanup, prefijo de interrupción crítica y naming/exportaciones por consulta.
- Deuda residual con clasificación bloqueante/no bloqueante y propuesta de decisión del propietario.
- Explicitud de que **el Engine no conoce campañas, históricos, clientes o tenants**; deduplica solo dentro de un `search_many()` y entre consultas diferentes.

**Estados posibles al concluir ejecución offline:**

- `IMPLEMENTED / OFFLINE VERIFIED / OWNER ACCEPTANCE PENDING`: todos los patches y G01–G22 PASS, sin live.
- `IMPLEMENTED / BLOCKED`: existe STOP o gate fallido, no presentar como completo.
- `PARTIALLY IMPLEMENTED`: no terminaron todos los patches; enumerar faltantes.

**Prohibido autodeclarar:** `OWNER ACCEPTED`, `CLOSED`, `RELEASED`, `G23 PASS`, tag o v1.0.0 estable sin decisiones expresas separadas. El primer release estable previsto sigue siendo v1.0.0, posterior a su propio hardening.

---

## 10. Prompt de activación posterior (NO ejecutar sin autorización del propietario)

> **Este bloque es una plantilla**, no una orden actual. Copiar a Codex solo cuando se haya autorizado explícitamente implementación local y se hayan señalado rama, alcance y permisos. Sustituir los marcadores por datos reales.

```text
Actúa como ingeniero implementador autónomo de Prospector CLI v0.9.x.

AUTORIZACIÓN DE IMPLEMENTACIÓN LOCAL: <PEGAR DECLARACIÓN EXPRESA DEL PROPIETARIO>
RAMA / WORKTREE AUTORIZADOS: <VALOR CONFIRMADO>
SHA DE PARTIDA ACEPTADO: <SHA REAL>
AUTORIZACIÓN DE PRUEBAS OFFLINE: <SÍ / NO>
AUTORIZACIÓN DE COMMITS LOCALES: <SÍ / NO>
AUTORIZACIÓN DE PUSH / GITHUB: <SÍ / NO>
AUTORIZACIÓN DE PRUEBAS LIVE: <SÍ / NO, DEFAULT NO>

Autoridades obligatorias, en este orden:
1. ADR-008 APPROVED.
2. ADR-009 APPROVED.
3. V0-9-x-Master-Implementation-Design.md ACCEPTED.
4. V0-9-x-Autonomous-Implementation-Runbook.md.

Ejecuta estrictamente los patches P91–P96 en ese orden y respeta G01–G23.
No modificar arquitecturas aprobadas, ni dar por hecho autorización de Git
remoto, E2E, navegadores externos, branches, merges, releases o tags.

Preflight primero: inspecciona Git, detecta cambios ajenos, valida baseline,
documenta estado y permisos. Si falta un permiso o hay divergencia, STOP.

Por patch: implementa el mínimo necesario, prueba offline, documenta
resultado verificable, audita diff, evalúa STOP, registra PASS/FAIL/BLOCKED.
Nunca avances desde un patch BLOCKED o FAIL.

Identidad: dedupe solo interconsulta y solo con establecimiento verificable.
Si no puedes demostrar semántica de identificador estable, STOP/OWNER REVIEW.
No cambies 12 campos ni ADR-008. No hagas merge comercial o matching difuso.

Al finalizar, entrega ImplementationProgress, ImplementationBlockers,
ValidationMatrix, AuditDiff, EvidenceIndex e informe con estado final.
No declares OWNER ACCEPTED, CLOSED ni RELEASED. G23 no es offline.
```

---

## 11. Resolución documental

**ADR-008:** `APPROVED`  
**ADR-009:** `APPROVED`  
**Master v0.9.x:** `ACCEPTED — DESIGN BASELINE`  
**Runbook v0.9.x:** `APPROVED BY OWNER — READY FOR IMPLEMENTATION`  
**Código v0.9.x:** `NOT IMPLEMENTED`  
**P91–P96:** `NOT STARTED`  
**GitHub/branches/commits/live/release:** `NOT AUTHORIZED`  

**Criterio de aceptación documental del runbook:** el propietario aprobó este procedimiento como listo para implementación; esta aprobación no sustituye las autorizaciones específicas de entorno, rama y alcance requeridas para entrar en modo de escritura. Cualquier cambio a decisiones de identidad, dedupe, límites, compatibilidad o exclusiones deberá volver a revisión arquitectónica, no resolverse editando este documento unilateralmente.

**Fin del Autonomous Implementation Runbook — v0.9.x.**
