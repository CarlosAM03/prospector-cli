# Prospector CLI — v0.9.x Master Implementation Design

**Proyecto:** Prospector CLI  
**Versión objetivo:** `v0.9.x`  
**Fecha:** 2026-10-06  
**Baseline técnico:** rama `v0.8.0`, commit `d1880e7ca305ff326eeac9e1e7c1ccd02e981b1d`  
**Autoridad normativa:** `ADR-009 — Multi-query secuencial, deduplicación estricta interconsulta y procedencia` (`APPROVED`); ADR-008 sigue vigente.  
**Estado de este diseño:** **`ACCEPTED — DESIGN BASELINE`** (aceptación documental solicitada expresamente por el propietario).  
**Estado del código v0.9.x:** **`NOT IMPLEMENTED / IMPLEMENTATION NOT AUTHORIZED`**.  
**Control:** no autoriza cambios locales o remotos, commits, ramas, merges, tags, pruebas live ni releases. La aceptación de diseño no constituye autorización de ejecución.

---

## 1. Propósito y jerarquía de decisiones

Este documento traduce ADR-009 a contratos técnicos, integración modular, secuencia de patches, pruebas y gates verificables para Codex. No introduce reglas de negocio, campañas ni decisiones contrarias a ADR-008/ADR-009. En caso de contradicción prevalecen los ADR aprobados; Codex debe detenerse y escalarla, no resolverla unilateralmente.

**Objetivo funcional:** recibir **1–5 `BatchQuery`** en el Engine, ejecutarlas una tras otra, conservar un `SearchResult` íntegro por búsqueda válida, y producir **una vista exportable independiente por consulta**, suprimiendo únicamente apariciones interconsulta de una **identidad de establecimiento verificable** que haya sido asignada a una consulta anterior. El CLI permite capturar **2–3 búsquedas** (la búsqueda individual continúa intacta), confirmarlas antes de iniciar y exportar un CSV o XLSX por búsqueda válida. Ningún resultado global comercial fusionado.

**Fuera de alcance:** deduplicación intraconsulta adicional; merge de campos comerciales; históricos CSV/XLSX, base de datos, CRM, campañas, matching difuso, scoring, API/FastAPI, SaaS, multi-tenant, jobs, colas, persistencia, concurrencia/pooling y nuevas fuentes. `v1.0.0` queda reservado para hardening y primer release estable.

## 2. Baseline real y restricciones de compatibilidad

Componentes de partida confirmados en `d1880e7`:

- `src/engines/prospector_engine.py`: `ProspectorEngine(config).search(query)` resuelve límite y fuente, llama `execute_global_search(...)`.
- `src/engines/global_pipeline.py`: llama fuente una vez, preserva `Business[]`, normaliza una vez y construye `SearchResult`.
- `src/models/search_query.py`: `SearchQuery(source, keyword, location)` es una dataclass **mutable**.
- `src/models/search_result.py`: `businesses: list[NormalizedBusiness]`, `original_businesses: list[Business]`, `issues`, `query`, `execution_time`, `total_found` derivado de longitud y comprobación de cardinalidad.
- `src/models/business.py` y `normalized_business.py`: 12 campos; **no poseen identificador de establecimiento**.
- `src/scraper/google_maps/result_list.py`: candidatos con `href`, identidad temporal `index/name/href`, y `Business`; deduplica href repetidos para evitar procesar de nuevo tarjetas recicladas (**no** constituye deduplicación empresarial).
- `src/scraper/google_maps/detail_panel.py`: extrae un token con `extract_place_id(href)` y verifica coincidencia URL/panel antes de enriquecer; esta verificación de navegación **no prueba por sí sola** que cualquier token sea un identificador global y estable.
- `src/scraper/google_maps/scraper.py`: `_SourceResult` y `_enrich_businesses(...)` devuelven los `Business` ordenados; website enrichment los actualiza sin crear empresas adicionales.
- `src/engines/browser_runtime.py`: crea y destruye browser/Playwright por búsqueda.
- `src/services/export_service.py`: `export(SearchResult, format)` genera nombre; CSV/XLSX actuales leen `result.businesses` y exportan **Name, Category, Address, Phone, Email, Website, Language**.
- `src/main.py`: menú individual `New Search`, límite default 50, máximo Google Maps 100, presentación y exportación.

**Compatibilidad no negociable:** mantener firmas/semántica de `search()`, `search_businesses()` legado, `EngineConfig`, `SearchQuery`, `SearchResult`, `Business`, `NormalizedBusiness`, `SearchIssue`, normalización ADR-008 y exportación individual de siete columnas. La extensión de identidad no debe añadir campos a los modelos comerciales ni exigir que el consumidor de `search()` realice deduplicación.

## 3. Arquitectura objetivo y flujo

```text
CLI modo múltiple / Consumer Python
             |
       BatchQuery[1..5]
             |
       ProspectorEngine.search_many()
             |
  preflight total + snapshot defensivo
             |
       BatchCoordinator (secuencial)
             |
    +--------+---------+---------+
    |                  |         |
  Consulta 0        Consulta 1 ... Consulta N
    |                  |         |
  BrowserRuntime individual, extracción + enrichment
    |                  |         |
  Business[] + SourceIdentity[]  (sidecar alineado)
    |                  |         |
  Normalización global ADR-008 (una sola vez)
    |                  |         |
  SearchResult íntegro + identidad interna correlacionada
    |                  |         |
    +------------------+---------+
             |
  Dedupe interconsulta por identidad validada
  (sin mutar SearchResult, sin merge de campos)
             |
  BatchSearchResult / BatchQueryResult[]
     |          |               |
  export_indices, suppressed, unverified
             |
        CLI / ExportService
             |
   archivo 0 | archivo 1 | ... archivo N
      CSV/XLSX de siete columnas cada uno
```

El Engine retorna **datos, nunca archivos**. El CLI decide formato y persistencia de cada archivo. Ningún navegador se comparte entre consultas de un mismo lote; esto **no** es una exclusión mutua global entre invocaciones independientes.

## 4. Contratos públicos del batch

Los siguientes tipos fijan la estructura semántica mínima. La organización física exacta puede ajustarse en patches sin alterar nombres públicos ni invariantes.

```python
@dataclass(frozen=True)
class BatchQuery:
    query: SearchQuery
    limit: int

class QueryStatus(str, Enum):
    SUCCESS = "success"
    SUCCESS_WITH_ISSUES = "success_with_issues"
    PARTIAL = "partial"
    FAILED = "failed"

class ObservationDisposition(str, Enum):
    EXPORTED = "exported"
    SUPPRESSED_DUPLICATE = "suppressed_duplicate"
    IDENTITY_UNVERIFIED_EXPORTED = "identity_unverified_exported"

@dataclass(frozen=True)
class ObservationRef:
    query_index: int
    business_index: int

@dataclass(frozen=True)
class DuplicateReference:
    duplicate: ObservationRef
    winner: ObservationRef
    identity: "VerifiedSourceIdentity"

@dataclass(frozen=True)
class QueryFailure:
    category: str                  # categoría pública segura
    message: str                   # mensaje fijo y seguro
    exception_type: str | None = None  # nombre de clase, sin repr ni traceback

@dataclass
class BatchQueryResult:
    request: BatchQuery             # snapshot de entrada, no referencia mutable original
    status: QueryStatus
    result: SearchResult | None
    error: QueryFailure | None
    export_indices: list[int]
    suppressed: list[DuplicateReference]
    unverified_identity_indices: list[int]
    # procedencia por ocurrencia accesible mediante auxiliar tipado de solo lectura

@dataclass
class BatchSearchResult:
    entries: list[BatchQueryResult]
    execution_time: float
    # métricas agregadas calculadas desde entries, no duplicadas manualmente

class ProspectorEngine:
    def search_many(self, queries: Sequence[BatchQuery]) -> BatchSearchResult: ...
```

**Reglas del contrato:**

1. `search_many` recibe una secuencia ordenada, materializada/snapshot **una vez**. Rechazar cadenas, `set`, mappings, generadores no pertenecientes al contrato y entradas sin orden determinista. La secuencia de 0 o más de 5 elementos es inválida.
2. Antes de Playwright, comprobar cada `BatchQuery` (tipo exacto), `SearchQuery` (tipo), `source == Source.GOOGLE_MAPS`, `keyword/location` con tipos conformes al contrato vigente, `limit` con `type(limit) is int` y `1 <= limit <= 100`; validar la `EngineConfig` compartida. No cambiar por esta implementación la política individual previamente aceptada para keyword/location.
3. `BatchQuery(frozen=True)` **no** congela profundamente `SearchQuery`: crear snapshot separado con nueva `SearchQuery(source, keyword, location)` y `limit` primitivo. En el batch nunca retener ni consultar posteriormente el objeto mutable original del llamador. Para demostrar aislamiento ante mutaciones durante la ejecución, utilizar pruebas con un fake que muta las entradas luego del snapshot.
4. `BatchQuery.limit` sobrescribe **solo durante esa búsqueda** el límite individual; `EngineConfig.limit` continúa como default 50 en `search()`; no se muta config ni la API legado.
5. `BatchQueryResult.result` siempre es el `SearchResult` de una búsqueda **íntegra y no filtrada** o `None` ante fallo tipado; no reconstruir `SearchResult` reduciendo `businesses` y rompiendo sus originales/contador.
6. `entries` conserva cardinalidad y orden de las solicitudes si el lote concluye normalmente, inclusive las fallidas controladas. Solicitudes iguales tienen entradas separadas.
7. `export_indices` es una subsecuencia ordenada sin repetidos de `[0, ..., result.total_found - 1]`; `suppressed` y `unverified_identity_indices` identifican posiciones del **mismo** resultado. `FAILED` => `result=None`, `error` presente, selecciones vacías. En entrada válida => `error=None`.
8. Exponer acceso explícito a la procedencia por observación (por ejemplo `observations: tuple[ObservationProvenance,...]` en `BatchQueryResult`); la representación concreta podrá ser dataclass auxiliar, pero deberá permitir inspeccionar consulta, posición, identidad/tipo, disposición y ganador. No exigir datos comerciales duplicados: se accede a originales y normalizados a través de índices de `SearchResult`.
9. `total_observations = total_exportable + duplicates_suppressed` para entradas con resultado válido. Cada observación se clasifica una sola vez. `unverified_identity_indices` es subconjunto de `export_indices`, **no** una tercera categoría que sume adicionalmente.
10. Las listas expuestas no representan inmutabilidad profunda; no hacer afirmaciones de thread safety o snapshot transaccional después de la entrega al consumidor. No agregar mutabilidad compartida entre resultados del batch o con la entrada original.

### 4.1. Errores e interrupción crítica

Un fallo fatal **tipado y acotado** de una consulta => `FAILED` con `QueryFailure` seguro y el lote continúa. Las incidencias recuperables permanecen en `SearchResult.issues`:

- `PARTIAL` si aparece `feed/partial_results` u otro marcador explícito de adquisición parcial aprobado.
- `SUCCESS_WITH_ISSUES` si existen issues, pero no marcador de adquisición parcial.
- `SUCCESS` si no existen issues.

Errores inesperados de programación, ruptura de invariantes, desalineación de identidad o cleanup no confiable **interrumpen** el batch: **no** convertirlos en `FAILED` recuperable ni continuar. Definir `BatchInterruptedError(ProspectorError)` (o error tipado específico) con atributos seguros `completed: BatchSearchResult` (prefijo **únicamente de consultas completadas**), `interrupted_query_index`, `reason_code` y `remaining_query_indices`; encadenar causa real para diagnóstico interno sin incluirla en mensajes públicos. No inventar resultados vacíos de consultas no intentadas. Si el fallo ocurre dentro de una búsqueda y no hay un `SearchResult` válido, esa búsqueda no pertenece al prefijo completado. El CLI presenta la interrupción y puede ofrecer exportar **solo** resultados ya completados de forma segura; no informa éxito del lote.

### 4.2. Preservación del resultado individual

No tocar `SearchResult.__post_init__`, `total_found` ni reglas de `NormalizationEngine`. Cada búsqueda pública `search()` y batch usa la **misma implementación subyacente**, con una normalización por búsqueda. Exponer evidencia interna de fuente mediante un resultado de ejecución **privado** compuesto (`SearchResult`, `identities`), no añadir campos a los doce campos de negocio y no hacer que las APIs individuales dedupliquen.

## 5. Identidad verificable de Google Maps

### 5.1. Contrato interno

```python
@dataclass(frozen=True)
class VerifiedSourceIdentity:
    source: Source
    kind: str                  # namespace explícito y admitido
    value: str                 # token canónico validado

@dataclass(frozen=True)
class SourceIdentityEvidence:
    verified: VerifiedSourceIdentity | None
    verification_state: str    # VERIFIED / UNVERIFIED, sin suponer certeza
    # códigos internos de razón seguros; no URL cruda en issues públicos
```

- En `_SourceResult` llevar `identities: list[SourceIdentityEvidence]` **posicionalmente** alineadas con `businesses`. Para casos controlados de fuente vacía: ambos vectores vacíos; ningún resultado no vacío puede salir con evidencia faltante o desalineada.
- En la extracción del feed mantener `href`/`identity` temporal sin agregar identidad a `Business`. En la etapa de detalle se registra evidencia del mismo candidato con identidad comprobada cuando corresponda; el sidecar sigue el mismo orden que `_enrich_businesses` y no se reordena durante website enrichment.
- **No equiparar automáticamente** el token actual `extract_place_id()` con un ID empresarial estable. Ese helper identifica tokens para sincronización; requiere **comprobación adicional** del formato/tipo de token, su vinculación al candidato y validación por una transición/panel que corresponda a ese mismo establecimiento. La coincidencia de nombre por sí sola no es prueba suficiente; un `href` sin identidad comprobable permanece `UNVERIFIED`.
- Para `v0.9.x` **no habilitar por defecto** otras clases de URL o canonicalizaciones heurísticas: admitir solo un tipo de token Google Maps para el cual un fixture positivo y negativos prueben estructura, namespace, exactitud y no confusión entre establecimientos. Comparación exacta de identidad `(source, kind, value)`; sin equivalencia cross-kind sin prueba normativa.
- Si no se puede demostrar inequívocamente estabilidad/semántica de ese token o su asociación, marcar `UNVERIFIED`; **no inventar ni interpolar IDs**. El objetivo es deduplicación **segura**, no maximizar número de fusiones. No depender de disponibilidad universal de IDs.
- El contrato debe distinguir **ausencia/ambigüedad de identidad de un candidato** (conservarlo, no deduplicar) de **defecto estructural del sidecar** (detener operación: no es seguro suprimir).
- Mantener observación de detalle `identity_unverifiable` y recuperación previamente aprobadas sin cambios de clasificación; una identidad empresarial `UNVERIFIED` no necesariamente implica generar un `SearchIssue` nuevo por cada empresa. Reportar contadores de identidad no verificada por consulta.

### 5.2. Evidencia mínima de validación del token

Exigir fixtures con: dos ocurrencias del mismo establecimiento; dos sucursales de una cadena; token semejante por prefijo/subcadena; token de namespace desconocido; href sin token; URL cambiada; panel incorrecto/homónimo; navegación fallida; resumen preservado; website enrichment fallido. Un parser que solo encuentre `!1s` **no satisface** este gate. Si las pruebas no permiten demostrar la semántica del token elegido, la funcionalidad debe operar conservadoramente con identidades `UNVERIFIED` y registrar el **bloqueo de efectividad**; no elevar matching especulativo ni declarar cumplido G07 mediante fixtures inventados de fuente real. El responsable aprueba cualquier ampliación a otro identificador.

## 6. Deduplicación estricta interconsulta

**Entrada:** resultados individuales íntegros y sidecars verificados en orden de consulta/observación.  
**Salida:** `export_indices`, `suppressed`, `unverified_identity_indices`, procedencia por observación y métricas.  
**Estado efímero:** índice `VerifiedSourceIdentity -> ObservationRef` para **consultas anteriores**.

Algoritmo normativo:

```text
seen_previous = {}
for query_index, completed_search in ordered_completed_entries:
    seen_current = {}
    for business_index, evidence in enumerate(completed_search.identities):
        if evidence.verified is None:
            export_indices.add(business_index)
            unverified_identity_indices.add(business_index)
            disposition = IDENTITY_UNVERIFIED_EXPORTED
        elif evidence.verified in seen_previous:
            suppressed.add(duplicate=(query_index, business_index),
                           winner=seen_previous[evidence.verified])
            disposition = SUPPRESSED_DUPLICATE
        else:
            export_indices.add(business_index)
            disposition = EXPORTED
            # La primera ocurrencia de esta consulta tiene precedencia
            seen_current.setdefault(evidence.verified,
                                    (query_index, business_index))
        record_provenance(...)
    # Solo después de terminar la consulta: no deduplicar intraconsulta.
    for identity, reference in seen_current.items():
        seen_previous.setdefault(identity, reference)
```

**Nota:** si una misma identidad figura dos veces **en una sola consulta**, se conservan ambas conforme a v0.8.x. Las consultas posteriores se asignan a la **primera** observación de la consulta precedente ganadora. Los fallos `FAILED` no aportan identidades; `PARTIAL` sí aporta las que fueron verificadas.

**Invariantes:**

- Para `i < j`, un ID verificado exportable en `i` no vuelve a exportarse en `j`; identidades `UNVERIFIED` no se excluyen.
- El índice es **local** a cada invocación; sin persistencia ni dedupe entre lotes.
- Una supresión hace referencia a una observación verificable **anterior**, existente y alineada; un ganador jamás se reemplaza por un registro posterior más completo.
- No se mezcla ni completa ningún campo comercial y no se modifica ningún `SearchResult`.
- La selección conserva el orden relativo y solo elimina de la **vista exportable**, no de la colección original.
- Ninguna supresión basada solo en nombre, dirección, email, teléfono, web/dominio, índice, categoría o similitud textual.

## 7. Exportación, CLI y naming

### 7.1. Adaptador de exportación

`ExportService.export(result: SearchResult, format)` mantiene contrato y comportamiento individual. Incorporar una ruta explícita, por ejemplo:

```python
ExportService.export_batch_entry(
    entry: BatchQueryResult,
    format: ExportFormat,
    batch_id: str,
    query_index: int,
) -> str
```

La ruta crea **solo** una `ExportSelection` o `ExportView` de datos `NormalizedBusiness` con `query` y lista de negocios seleccionados mediante `export_indices`, sin fabricar un `SearchResult` inconsistente ni mutar las listas originales. Reutilizar serializadores/esquema CSV/XLSX existentes a través de un protocolo de lectura o helper compartido, manteniendo intacta la ruta pública individual. No duplicar lógica para siete columnas ni asumir que todo exportable es `SearchResult`. Exportación queda fuera del Engine.

- Para `SUCCESS`, `SUCCESS_WITH_ISSUES` o `PARTIAL`: archivo solicitado con 7 columnas y filas filtradas por `export_indices`.
- Si `export_indices=[]` y existe `SearchResult` válido: generar **encabezados, cero filas** y mensaje explícito `X duplicados suprimidos`.
- Para `FAILED`: **no** crear archivo.
- CSV y XLSX conservarán el mismo orden de columnas, nombres, celdas normalizadas y hoja Excel actual `Businesses`; probar ambos formatos. `skip export` no escribe nada.
- Naming no colisionable: utilizar la estrategia existente más identificador de operación (`batch_id`) e índice ordinal `q01`, `q02`, etc. Las consultas iguales y dos lotes iniciados en el mismo instante no deben sobrescribirse: ID efímero único por operación y protección de colisiones/no reemplazo silencioso. No agregar ID en columnas del prospecto.
- Ante fallo de IO/exportación, informar archivo/consulta afectados sin alterar resultado Engine; no declarar éxito de exportación para archivos incompletos. El adaptador no utiliza IDs desconocidos para intentar deduplicar después.

### 7.2. Contrato de interacción CLI

1. Conservar ruta individual y sus mensajes esenciales.
2. Añadir opción `Multiple Searches` sin llevar lógica del Engine al menú.
3. Pedir `keyword`, `location`, `limit` para consulta 1 y consulta 2. Tras la segunda permitir `Start after confirmation` o `Add third`; al llegar a la tercera no aceptar más.
4. Validar localmente límite (Enter = 50; máximo 100, entero positivo) y conservar captura/normalización compatible de keyword/location. Mostrar resumen **completo** de las 2–3 solicitudes y pedir **confirmación explícita** antes del primer navegador.
5. Cancelación en preflight => 0 navegadores, 0 archivos.
6. Llamar `search_many` una vez con los `BatchQuery` preconfigurados; presentar status, observados, exportables, suprimidos, sin identidad y issues por consulta.
7. Tras ejecución, permitir elegir CSV/XLSX/omitir exportación según flujo CLI, sin introducir selección de campañas ni históricos. Un archivo **por entrada válida**, incluidos resultados vacíos tras filtro; entrada `FAILED` no produce archivo.
8. Ante interrupción crítica, informar consultas completadas, interrupción y no ejecutadas. Solo exportar prefijo seguro si así lo decide el flujo del consumidor, sin presentar la operación como éxito.

## 8. Estrategia de módulos y dependencias

**Propuesta de ownership (nombres físicos finales sujetos a la estructura mínima del patch, sin nuevos subsistemas artificiales):**

| Responsabilidad | Ubicación objetivo | Cambio permitido |
|---|---|---|
| `BatchQuery`, resultados, referencias, enums, errores seguros | `src/models/` y `src/engines/errors.py` | Nuevos tipos, exports explícitos |
| Preflight, snapshot, coordinación secuencial | `src/engines/prospector_engine.py` + `src/engines/batch/` solo si aporta cohesión | Reusar ejecución existente |
| Normalización global + transporte de identidad privado | `src/engines/global_pipeline.py` | Extensión privada compatible |
| Evidencia y sidecar de Google Maps | `src/scraper/google_maps/` | Transporte mínimo, no nuevos scrapers |
| Índice de identidad y filtro interconsulta | `src/engines/batch/` | Algoritmo puro, independiente de Playwright |
| Protocolo/adapter de selección exportable | `src/services/`, `src/exporters/` | Sin cambiar ruta individual |
| Captura y presentación | `src/main.py` o helpers CLI puntuales | CLI como adapter, no dedupe |
| Pruebas | `tests/unit/`, `tests/integration/` | Fixtures sintéticos, cero red por defecto |
| Documentación CURRENT y tests | `README.md`, `docs/`, `tests/README.md` | Describir verificado, nunca adelantado |

`BatchCoordinator` depende de contratos públicos y función de ejecución individual, no de módulos de interfaz CLI o exporters. El algoritmo de deduplicación no debe importar Playwright. El scraper no conoce batches, exportaciones, campañas ni clientes. ExportService no conoce browser ni DOM.

## 9. Plan de patches y checkpoints

**Secuencia con freeze de diseño:** completar cada patch en orden; mantener el commit base trazable y no combinar cambios no relacionados. Todos los gates offline se ejecutan **sin** `PROSPECTOR_RUN_E2E`.

### Patch `v0.9.1` — Contratos y preflight (`P91`)

**Implementar:** `BatchQuery`, `BatchQueryResult`, `BatchSearchResult`, enums, `ObservationRef`, `DuplicateReference`, `QueryFailure`, tipo de interrupción; preflight/snapshot del Engine; getters/cómputos de contadores. Sin navegador ni dedupe real todavía.

**Probar:** 0/1/5/6 entradas, `bool` como límite, límites 0/100/101, fuente ajena, tipos inválidos, secuencia sin orden, duplicado de query, `EngineConfig` sin mutación, snapshot contra mutación del llamador. Contratos `FAILED`/válido y invariantes de reconciliación.

**Gate P91:** tipos públicos bien documentados y entradas inválidas rechazadas antes de Playwright; suite previa verde.

### Patch `v0.9.2` — Identidad y sidecar (`P92`)

**Implementar:** transporte de `SourceIdentityEvidence[]` desde feed/detail hacia `_SourceResult` y frontera global privada. Validación de token estricto, asociación con establecimiento comprobado, estructura de namespace, estado `UNVERIFIED`. No modificar los doce campos ni normalizar dos veces.

**Probar:** token verificado, token desconocido, dos establecimientos, sucursales, homónimos, fallo de panel, fallback, enriquecimiento parcial, preservación del orden, website failure, identidades alineadas. Prueba negativa contra uso directo de `!1s` como prueba automática de identidad.

**Gate P92:** invariante de identidad demostrado y evidencia de identidad suficientemente verificable; si no, **STOP / OWNER REVIEW** antes de declarar operativa la deduplicación live. Nunca relajar D03 silenciosamente.

### Patch `v0.9.3` — Batch coordinator y fallos (`P93`)

**Implementar:** `search_many()` síncrono; invocación de la ejecución individual con límite por request y sidecar, un runtime por consulta, preservación de todos los resultados, estados `SUCCESS`, `SUCCESS_WITH_ISSUES`, `PARTIAL`, `FAILED`, excepción de interrupción crítica y prefijo completado.

**Probar:** A/B/C ordenado; sin solapamiento; cierre antes de siguiente; B `FAILED` controlado no impide C; `feed/partial_results`; error inesperado; cleanup fallido; entradas no ejecutadas diferenciadas; resultados originales/normalizados íntegros.

**Gate P93:** secuencialidad, aislamiento, errores y compatibilidad individual con regresión offline.

### Patch `v0.9.4` — Dedupe y procedencia (`P94`)

**Implementar:** algoritmo **puro** interconsulta con `seen_previous/seen_current`; export_indices, suppressed con ganador, identidades unverified y métricas; no merge comercial ni dedupe intraconsulta.

**Probar:** A `[1,2,3]`, B `[2,4,5]`, C `[1,5,6]`; consulta idéntica repetida; duplicados internos de A no suprimidos; ganador de A `PARTIAL`; A `FAILED` y B/C; IDs de distintos namespaces; resultados sin ID; conflicto nombre/teléfono con ID distinto; complementos posteriores no sustituyen ganador.

**Gate P94:** `observaciones = exportables + suprimidas`; exclusión exacta solo de identidades verificadas de consultas anteriores; procedencia íntegra.

### Patch `v0.9.5` — CLI y ExportService (`P95`)

**Implementar:** interacción 2–3 queries con confirmación; adapter de vista filtrada; export CSV/XLSX por entrada válida; naming sin colisiones; resumen explícito de vacíos/fallos/issues; ningún archivo desde Engine.

**Probar:** cancelar, comenzar tras 2, agregar tercera, no cuarta; archivos distintos para consultas iguales; fila de encabezados y cero datos; FAILED sin archivo; layout siete columnas y XLSX `Businesses`; skip; fallo controlado de IO; regresión individual.

**Gate P95:** independencia de archivos, compatibilidad de exportadores y ausencia de mutación `SearchResult`.

### Patch `v0.9.6` — Regresión, documentación y acceptance (`P96`)

**Implementar:** matriz G01–G23, documentación CURRENT actualizada a los hechos de código, pruebas controladas representativas del flujo DATRA, auditoría del diff, métricas con ejecución simulada; ninguna funcionalidad extra.

**Pruebas requeridas:** `python -m compileall -q src`, unitarias, integración y suite completa `-m "not e2e"`, con `--basetemp` único en Windows donde corresponda. Comparar cobertura/regresiones con baseline de 185 PASS registrado en `v0.8.x` sin exigir que el conteo permanezca igual tras añadir pruebas.

**Gate P96:** G01–G22 probados/documentados offline; G23 pendiente de autorización live **separada**. Sin tag, release ni proclamación de `v0.9.x ACCEPTED` por el solo hecho de pasar los patches.

## 10. Matriz de trazabilidad G01–G23

| Gate ADR | Evidencia mínima / test principal | Patch |
|---|---|---|
| G01 | `search()` y wrapper legado mantienen contrato, normalización única y errores | P93/P96 |
| G02 | `1..5`, fuentes/tipos/límites incorrectos bloqueados antes del navegador | P91 |
| G03 | CLI 2–3, confirmación y cancelación sin ejecución | P95 |
| G04 | Registro fake de aperturas/cierres sin solapamiento | P93 |
| G05 | Queries iguales generan entradas/archivos únicos | P91/P95 |
| G06 | `Business[]`, `NormalizedBusiness[]`, issues, orden, `total_found` idénticos | P92/P93 |
| G07 | Identificador válido A/B genera una sola asignación interconsulta | P92/P94 |
| G08 | Homónimos, sucursales y desconocidos permanecen exportables | P92/P94 |
| G09 | Suprimidos contienen `winner` previo exacto | P94 |
| G10 | No hay sustitución de email/teléfono/campos desde posterior | P94 |
| G11 | CSV/XLSX 7 columnas, vacío válido y FAILED sin archivo | P95 |
| G12 | B fallido controlado; A y C conservados, parciales preservados | P93 |
| G13 | Cleanup crítico detiene con prefijo y no ejecutadas identificables | P93 |
| G14 | Contadores y partición exacta de observaciones válidas | P94 |
| G15 | Sin scroll/reintentos para reponer duplicados | P93/P94 |
| G16 | Sidecar alineado con `Business[]`, incluso fallos | P92 |
| G17 | Copias defensivas contra mutación del `SearchQuery` fuente | P91/P93 |
| G18 | Fixture A/B/C y archivos disjuntos por ID verificado | P94/P95 |
| G19 | Fixture sintético inspirado en DATRA; sin heurísticas comerciales | P92/P94 |
| G20 | Sin CSV histórico/DB/campañas en código ni contratos | P96 |
| G21 | Métricas por query/lote sin URL cruda/secretos | P93/P96 |
| G22 | Exportación individual y pruebas previas sin regresión | P95/P96 |
| G23 | Live **solo si propietario lo autoriza**, diff auditado | aceptación posterior |

## 11. Condiciones STOP, controles y evidencia

**STOP / consultar propietario antes de continuar** si:

1. No se puede verificar un identificador de establecimiento con seguridad suficiente sin cambiar política D03 o scraping de origen.
2. La propagación del sidecar requiere alterar los 12 campos o las garantías ADR-008.
3. Un patch rompe `search()`/wrapper individual, `SearchResult`, exportación individual o normalización única.
4. El cleanup entre consultas no se puede garantizar, o el error model necesita capturar inesperados como recuperables.
5. Se propone scoring, heurística por nombre/dirección, dedupe intraconsulta, lectura de históricos, merge de campos, concurrencia, servidor, campañas, datos persistidos o nuevas fuentes.
6. Las pruebas deterministas no pasan; no modificar assertions para ocultar defectos.
7. Se pretende ejecutar live, crear commits, publicar documentos en GitHub, cambiar branch o release sin autorización independiente.

**Registros propuestos de ejecución (solo al autorizar implementación):** `ImplementationProgress.md`, `ImplementationBlockers.md`, `ValidationMatrix.md`, `AuditDiff.md`, `EvidenceIndex.md` en carpeta local de planificación. Incluir SHA inicial/final, patch, archivos, comandos, PASS/FAIL, bloqueos, gate y decisión; `temp/` puede ser ignorado por Git, por lo que conservar copia y trazabilidad externas antes de cierre. Las pruebas live se registrarán en un gate aparte y nunca se inferirán de CSV históricos.

## 12. Política de aceptación y relación con v1.0.0

- **Este Master:** `ACCEPTED — DESIGN BASELINE`, porque el propietario solicita expresamente su aceptación documental conforme a ADR-009. Este estado **no** certifica implementación, tests ni actualización del repositorio.
- **ADR-009:** `APPROVED` y autoridad obligatoria; ADR-008 continúa vigente.
- **Implementación:** `NOT AUTHORIZED`; se necesitará autorización separada para Codex, edición local, pushes, branches o pruebas live.
- **Cierre técnico futuro de v0.9.x:** solo tras P91–P96, evidencias G01–G22, revisión de riesgos, validación del propietario y G23 si se autoriza una ejecución real. No crear release/tag por inferencia.
- **v1.0.0:** no agrega campañas, históricos, merge especulativo ni FastAPI; comprende hardening, contratos estables, instalación limpia, regresión, observabilidad y primer release estable autorizado.

**Resolución del diseño:** `ACCEPTED`. Las reglas de este Master desarrollan, pero no reemplazan, ADR-009. El Runbook autónomo que se prepare después deberá citar ambos y conservar todos los gates y STOP definidos aquí.
