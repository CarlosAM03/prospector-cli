# ADR-009 — Multi-query secuencial, deduplicación estricta interconsulta y procedencia

**Proyecto:** Prospector CLI  
**Versión objetivo:** `v0.9.x`  
**Fecha de decisión:** 2026-10-06  
**Baseline de diseño:** `v0.8.0` — `d1880e7ca305ff326eeac9e1e7c1ccd02e981b1d`  
**Estado del ADR:** **`APPROVED` — decisión documental explícita del propietario**  
**Estado de implementación:** **`NOT AUTHORIZED / NOT IMPLEMENTED`**  
**Autoridad:** propietario del proyecto (decisiones P01–P07 confirmadas en la conversación)  
**Relación:** complementa ADR-008; no lo sustituye ni modifica.  
**Control de publicación:** este documento se entrega fuera del repositorio. Su aprobación **no** autoriza commits, branches, merges, tags, releases, pruebas live ni modificaciones de GitHub.

---

## 1. Contexto, problema y evidencia

En el baseline de `v0.8.x`, `ProspectorEngine(config).search(query)` resuelve una única búsqueda mediante Google Maps, conserva el `Business[]` consolidado de origen, realiza una sola normalización global obligatoria y devuelve `SearchResult` con `businesses: list[NormalizedBusiness]`, `original_businesses: list[Business]`, `issues`, `query`, `execution_time` y `total_found`. El CLI y `ExportService` soportan CSV y XLSX con siete columnas; el wrapper legado `search_businesses()` conserva su contrato.

El flujo operativo de prospección compartido por el propietario distingue archivos de extracción independientes, un filtro **entre búsquedas**, un filtro contra **registros existentes** y preparación/revisión de listas finales. En los libros de trabajo de DATRA aparecen hojas o etapas como `FiltroEntreBusquedas`, `FiltroExistentes` y `ResultadosEnBrutoyNeto`, junto con decisiones humanas `CONSERVAR`/`DESCARTAR`. Esta evidencia orienta la **separación de responsabilidades**; no incorpora campañas ni reglas comerciales de DATRA al Engine. Las coincidencias humanas basadas en campos de presentación no prueban por sí solas identidad de establecimiento.

**Problema a resolver:** una operación de múltiples búsquedas debe devolver **una lista independiente por consulta**, suprimiendo de las listas posteriores únicamente las observaciones cuya identidad de establecimiento está **verificada** y ya fue asignada a una consulta anterior del **mismo lote**. No se producirá una lista global fusionada, ni se comparará contra históricos externos.

### 1.1. Objetivos

- Configurar todas las búsquedas antes de ejecutarlas y procesarlas secuencialmente.
- Conservar íntegramente cada `SearchResult` individual y sus dos representaciones.
- Garantizar que **ninguna identidad verificada** se exporte en más de una lista del lote.
- Trazar observaciones exportadas y suprimidas, sin fusión de campos de negocio.
- Exportar cada resultado válido de forma independiente, con las mismas siete columnas actuales.
- Mantener al Engine reutilizable y libre de lógica de campañas, CRM, clientes, persistencia o multitenancy.

### 1.2. No objetivos

- Garantizar que todas las empresas exportadas sean distintas cuando no exista identidad verificable.
- Garantizar que sean prospectos inéditos respecto a los históricos de DATRA u otros consumidores.
- Realizar matching difuso, deduplicación contra CSV/XLSX/base de datos o enriquecimiento mediante merge entre búsquedas.
- Administrar colas, tenants, autorizaciones, almacenamiento, API HTTP o concurrencia global.

---

## 2. Decisiones vinculantes

### D01 — API pública, solicitudes y validación

Se incorporará una API síncrona independiente:

```python
@dataclass(frozen=True)
class BatchQuery:
    query: SearchQuery
    limit: int

class ProspectorEngine:
    def search_many(self, queries: Sequence[BatchQuery]) -> BatchSearchResult:
        ...
```

El ejemplo expresa la **forma pública conceptual**. `SearchQuery` de `v0.8.x` es mutable: `frozen=True` en `BatchQuery` **no** congela transitivamente su contenido. En la frontera del batch se creará una **instantánea defensiva y validada** del valor de `source`, `keyword`, `location` y `limit`; toda ejecución se basará en esa instantánea, nunca en modificaciones posteriores de los objetos del llamador. No se cambia por ello `SearchQuery` existente. El diseño físico de dataclasses/constructores deberá garantizar esta regla con pruebas, sin afirmar inmutabilidad profunda inexistente.

**Reglas:**

1. El Engine acepta **1 a 5** solicitudes, inclusive. Rechaza `0`, `6+`, secuencias sin orden y tipos ajenos al contrato; no trunca, redondea ni descarta consultas silenciosamente.
2. El CLI ofrece modo individual (`search()`) y modo múltiple de **2 o 3** consultas; permite confirmar tras la segunda o capturar la tercera. Tres es la capacidad máxima/recomendada del CLI inicial; el Engine permite cinco para otros consumidores.
3. Cada `BatchQuery.limit` se valida como `int` **no booleano**, de **1 a 100** para Google Maps. Corresponde a resultados **extraídos** por consulta, no a prospectos únicos exportables.
4. Se validan **todas** las entradas (estructura, fuente soportada, límites y tipos/configuración aplicables) **antes** de iniciar Playwright. No se inicia una ejecución parcial por entrada inválida.
5. Las solicitudes idénticas por contenido siguen siendo ejecuciones distintas y se identifican por **posición en el lote**.
6. `EngineConfig.limit` mantiene el valor por defecto de `50` para `search()`. La búsqueda por lote usa el límite individual de `BatchQuery` sin mutar el `EngineConfig` original ni imponer esa nueva semántica al wrapper legado.
7. La captura de keyword, ubicación y límite, la revisión del resumen y la **confirmación explícita de inicio** pertenecen al CLI, no al Engine.

### D02 — Ejecución secuencial y aislamiento

- La operación se ejecuta en **orden de entrada**, exactamente **una consulta a la vez**.
- Cada consulta dispone de su `BrowserRuntime` y sus páginas; Playwright/Chromium se cierran antes de iniciar la siguiente. No se incorpora pooling ni reutilización de navegador entre consultas.
- Se reutilizan el pipeline existente y las mismas reglas de extracción, enriquecimiento, normalización y recuperación: **una normalización por búsqueda**, sin volver a normalizar para deduplicar o exportar.
- Un batch es una coordinación **local a una invocación**. No provee un candado global entre procesos, instancias ni tenants; los futuros consumidores administrarán admisión, capacidad y concurrencia de peticiones independientes.
- Un fallo fatal controlado de **una consulta** no impide ejecutar las siguientes, siempre que el aislamiento y la limpieza de recursos sigan garantizados (véase D09).

### D03 — Identidad de establecimiento, evidencia y transporte

La unidad de deduplicación es el **mismo establecimiento de origen**, no la marca, razón social, cadena, categoría o campaña.

**Evidencia admisible:**

1. Un identificador de establecimiento de Google Maps con contrato de extracción, estructura y validación demostrados por pruebas.
2. Una referencia exacta de fuente canonicalizada mediante una regla explícitamente probada como identificador unívoco del mismo establecimiento.

No bastan por sí solos nombre, dirección, teléfono, correo, dominio, web corporativa, categoría, proximidad textual, índice del feed ni `href` arbitrario. No se admite una equivalencia entre **distintos tipos de identificador** sin una regla de correspondencia verificada; se deberá evitar confundir cadenas idénticas pertenecientes a espacios de nombres distintos. La identidad canónica incluye, al menos conceptualmente, **fuente + tipo de identificador + valor validado**. La extracción, validación y canonicalización concretas se especificarán y probarán en el Master Implementation Design; ninguna forma de `href` o `place ID` se presupone infalible.

El scraper ya utiliza `href` e identidad interna durante la extracción, pero `Business` y `NormalizedBusiness` públicos constan de 12 campos sin identificador de establecimiento. Se aprueba transportar evidencia mediante **sidecar posicional** por observación, preservando la correspondencia con el `Business` de origen hasta el coordinador del batch. Deben satisfacerse invariantes de longitud, orden y procedencia; si hay desalineación, **no** se podrá realizar supresión insegura. Este transporte mínimo no cambia las reglas ADR-008 ni añade campos comerciales a los modelos.

**P01 aprobada:** ante identidad no verificable o evidencia contradictoria, **conservar** la observación exportable e identificarla como no verificable; no deduplicar por parecido ni inferencia. La insuficiencia de identidad no constituye por sí misma un error fatal.

### D04 — Dedupe exclusivamente interconsulta, ganador y alcance

Se aprueba la política **first verified occurrence wins**, siguiendo orden de consulta y orden de observación dentro de ella.

- Una identidad verificable se asigna a la **primera consulta** donde aparece.
- Toda coincidencia verificada en una **consulta posterior** se suprime **solo de la vista exportable** de esa consulta. Se conserva el objeto individual original/normalizado y su referencia de supresión.
- **P02 aprobada:** si una observación posterior tiene más campos, **no** reemplaza la ganadora y **no** completa sus campos. Solo se registra como duplicada.
- **P03 aprobada:** **no se introduce deduplicación dentro de la misma consulta**. Si un identificador se repite dentro de la consulta ganadora, se conserva su comportamiento individual de `v0.8.x`, sin deduplicación adicional; sus repeticiones en consultas posteriores sí quedan asignadas a la consulta ganadora. Por tanto, la garantía de unicidad se refiere **entre archivos**, no dentro de un mismo archivo.
- Observaciones sin identidad verificada se conservan incluso si sus campos parecen iguales.
- Resultados válidos con `feed/partial_results` pueden ganar precedencia si su identidad es verificable.
- No existe estado de deduplicación entre operaciones `search_many()` diferentes.
- El orden de los registros conservados en cada vista exportable sigue el orden original de su `SearchResult`.

**Ejemplo (identidades verificadas):**

```text
Consulta A: [1, 2, 3]  -> Archivo A: [1, 2, 3]
Consulta B: [2, 4, 5]  -> Archivo B: [4, 5]      (2 -> A)
Consulta C: [1, 5, 6]  -> Archivo C: [6]         (1 -> A; 5 -> B)
```

**Garantía:** los conjuntos de **identidades verificadas** presentes en archivos de **consultas distintas** del mismo lote son disjuntos. **No** se garantiza exclusión completa de posibles duplicados sin identidad verificable ni novedad frente a registros históricos.

### D05 — Procedencia y ausencia de merge de campos

El término *merge* en `v0.9.x` **no** designa reconstrucción, combinación ni sustitución de datos comerciales. Se limita a **asociación de ocurrencias y procedencia de la asignación**.

Cada observación deberá permitir localizar:

- Índice de consulta e índice de observación, `SearchQuery`/solicitud de origen y fuente.
- Identidad de establecimiento verificada, o marca de identidad desconocida.
- Correspondencia con `Business` y `NormalizedBusiness` originales del mismo `SearchResult`.
- Estado de exportación: `EXPORTED`, `SUPPRESSED_DUPLICATE` o `IDENTITY_UNVERIFIED_EXPORTED`.
- Para cada observación suprimida: referencia estable **dentro del lote** a la consulta/observación ganadora y motivo de supresión por identidad.

No se modifican teléfonos, nombres, direcciones, correos, web ni metadata entre consultas. No se eliminan observaciones de los resultados individuales ni del resultado batch en memoria. No se exige manifiesto persistido, archivo de auditoría JSON ni almacenamiento de identidades entre lotes.

### D06 — Contratos de resultados

El contrato conceptual será:

```python
@dataclass
class BatchQueryResult:
    request: BatchQuery
    status: QueryStatus
    result: SearchResult | None
    error: QueryFailure | None
    export_indices: list[int]
    suppressed: list[DuplicateReference]
    unverified_identity_indices: list[int]

@dataclass
class BatchSearchResult:
    entries: list[BatchQueryResult]
    execution_time: float
```

Estos son **contratos semánticos mínimos**; el Master Implementation Design podrá formalizar auxiliares y tipos, siempre que no reduzca ninguna garantía del ADR.

Invariantes:

1. `entries` corresponde, en cardinalidad y orden, a las solicitudes de entrada en los resultados de operación completada normalmente. Cada consulta fallida controlada se conserva como entrada `FAILED`.
2. En un resultado válido, `result` es un `SearchResult` íntegro, no filtrado: `len(result.businesses) == len(result.original_businesses) == result.total_found`.
3. `export_indices` es una selección ordenada de índices válidos de `result.businesses`. Ningún índice suprimido puede aparecer allí. Cada índice de la consulta se clasifica exactamente una vez.
4. `suppressed` registra los índices omitidos y la observación ganadora de una consulta **anterior**. `unverified_identity_indices` registra observaciones exportadas sin identidad verificable.
5. En `FAILED`, no existe `SearchResult` y las colecciones de observaciones/exportación de esa entrada están vacías.
6. Conteos globales calculados a partir de entradas con resultados válidos: `total_observations = total_exportable + duplicates_suppressed`. No se aplica dedupe intraconsulta.
7. Una copia o vista para exportación no puede alterar los originales, los normalizados, `issues`, el orden ni `total_found` de `SearchResult`.

### D07 — Exportación por consulta

`search_many()` **no crea archivos ni decide rutas o formatos**. El CLI u otro consumidor ejecuta la exportación mediante `ExportService` sobre una **vista/adaptador exportable** derivada de `export_indices` y alineada con los contratos que necesite el exportador; no se construirán resultados falsos con originales desalineados o estadísticas engañosas.

- Una consulta `SUCCESS`, `SUCCESS_WITH_ISSUES` o `PARTIAL` produce, **si el usuario solicita exportación**, un archivo independiente CSV o XLSX con sus observaciones exportables y el esquema existente de **siete columnas**.
- **P05 aprobada:** si el resultado es válido pero todos sus registros fueron suprimidos, se genera un archivo **con encabezados y cero filas**, y el CLI muestra de forma explícita cuántos duplicados se omitieron.
- Una consulta `FAILED` **no** genera archivo.
- Se generan nombres no colisionables con índice de consulta e identificador único de lote/ejecución, incluso para búsquedas idénticas y archivos vacíos.
- El usuario selecciona el formato conforme al flujo compatible del CLI; no hay archivo fusionado comercial ni columnas adicionales en CSV/XLSX.
- El CLI informa extraídos, exportables, suprimidos, identidades no verificables e incidencias por consulta.

### D08 — Límites, resultados únicos y coste operativo

- **P04 aprobada:** Engine `1–5` solicitudes, CLI múltiple `2–3`, y `1–100` extracciones solicitadas por consulta Google Maps. Una operación con cinco límites de 100 puede acumular **hasta 500 observaciones** antes del filtro, sin garantizar que Google Maps alcance ese número.
- El límite de `BatchQuery` opera **antes** de la deduplicación. Los archivos individuales pueden contener menos negocios o cero.
- No se relanza una consulta ni se navega adicionalmente para **rellenar** los negocios deduplicados. No existe cuota garantizada de prospectos únicos.
- La cantidad máxima de consultas es un control acotado por invocación, **no** una garantía de tiempo máximo ni un límite global para un futuro servicio multitenant.

### D09 — Estados, errores y continuidad

Estados para consultas **intentadas**:

- `SUCCESS`: `SearchResult` válido sin incidencias.
- `SUCCESS_WITH_ISSUES`: resultado válido con incidencias recuperables, sin marcador aprobado de extracción parcial.
- `PARTIAL`: resultado válido con `feed/partial_results` u otro indicador de adquisición incompleta aprobado.
- `FAILED`: error fatal **controlado/tipado**, sin resultado válido.

**P06 aprobada:** si B falla de forma controlada y A terminó, se conserva A y se intenta C. El error se expresa como `QueryFailure` seguro: tipo/categoría, consulta e información pública suficiente, sin trazas, URLs sensibles ni estado interno del navegador. La ausencia de identidad no supone error fatal. Los errores inesperados de programación **no** se capturan indiscriminadamente.

**Regla de parada:** ante fallo de cleanup que impida garantizar aislamiento, error inesperado no recuperable o integridad crítica violada, el lote **se detiene**: nunca inicia la siguiente búsqueda bajo recursos inciertos. No se presentarán consultas no ejecutadas como `FAILED` ni como resultados vacíos normales; se debe comunicar explícitamente la **interrupción del lote** e identificar qué consultas sí terminaron y cuáles no se intentaron, preservando la evidencia disponible sin afirmar que el batch concluyó. El Master concretará el tipo de error y transporte del prefijo completado, cumpliendo estas garantías.

La configuración inválida de entrada o lote se rechaza en **preflight**, antes de iniciar navegador alguno.

### D10 — Históricos y reglas de negocio (exclusión aprobada)

**P07 aprobada:** deduplicar contra CSV/XLSX ya existentes, una base de datos, un CRM, contactos/clientes previos o campañas **no forma parte de `v0.9.x` ni de los requisitos de `v1.0.0`**. La hoja `FiltroExistentes` del proceso de DATRA representa otra responsabilidad.

Los siete campos exportados hoy no contienen evidencia estable suficiente para equiparar sin riesgo registros históricos. Esos casos exigirán un contrato independiente de identidad histórica, revisión de coincidencias ambiguas y responsabilidad del consumidor. No se añadirá lectura de CSV como entrada de `search_many`, estado persistente ni política comercial al Engine.

### D11 — Métricas y observabilidad

Sin imponer SLA, el Engine debe permitir observar duración por consulta y del lote, cantidad solicitada, observada, exportable y suprimida, identidades no verificables, fallos controlados y marcadores de parcialidad. La observabilidad no debe imprimir información sensible ni forzar cambios de logging global.

---

## 3. Compatibilidad y límites de arquitectura

Permanecen compatibles y sin cambios semánticos: `ProspectorEngine.search()`, el wrapper `search_businesses()` legado, `EngineConfig` individual, `SearchQuery`, `SearchResult`, `Business`, `NormalizedBusiness`, `SearchIssue`, normalización ADR-008, ciclo de vida individual y exportadores CSV/XLSX de siete columnas.

El transporte adicional de identidad debe integrarse sin que una llamada individual tenga que aplicar deduplicación, sin normalización duplicada y sin sobreescribir información de origen. No se introducen API HTTP, FastAPI, persistencia, jobs, cron, cola, multitenancy, limitación global de procesos, navegador compartido, merge comercial, fuentes nuevas ni sistemas de campañas.

La futura API multitenant será responsable de la **concurrencia entre peticiones**; la ejecución secuencial aquí se limita **a cada lote**.

---

## 4. Matriz de aceptación obligatoria

| Gate | Prueba o criterio | Aceptación esperada |
|---|---|---|
| G01 | Regresión `v0.8.x` | `search()` y wrapper legado intactos; normalización única y resultados alineados |
| G02 | Entradas del Engine | Acepta 1–5 y rechaza 0/6+, tipos, fuentes y límites inválidos antes del navegador |
| G03 | Flujo del CLI | Modo 2–3 solicitudes; keyword, ubicación, límite, resumen y confirmación antes de ejecutar |
| G04 | Recursos | Orden secuencial, sin solapamiento y con cleanup de Playwright entre búsquedas |
| G05 | Búsquedas iguales | Mantiene entradas/archivos distintos sin sobrescribir |
| G06 | Integridad original | Todas las vistas y `SearchIssue` de cada `SearchResult` se preservan |
| G07 | Identidad confirmada | Un establecimiento verificable solo puede asignarse a la primera consulta |
| G08 | Evidencia insuficiente | Homónimos, sucursales e IDs desconocidos no se suprimen especulativamente |
| G09 | Procedencia | Cada supresión apunta a observación ganadora válida anterior |
| G10 | Merge | No hay combinación de campos ni reemplazo por observación posterior más completa |
| G11 | Exportadores | Archivo de siete columnas por consulta válida; archivo con encabezados y cero filas si aplica; ninguno para `FAILED` |
| G12 | Continuidad | Una consulta `FAILED` controlada no impide la siguiente; las parciales conservan datos |
| G13 | Parada crítica | Cleanup/integridad comprometidos detienen operación y diferencian no ejecutadas |
| G14 | Reconciliación | `extraídas = exportables + suprimidas` para resultados válidos |
| G15 | Límites | La deduplicación no rellena límite ni ejecuta consultas adicionales |
| G16 | Identidad posicional | Sidecar y `Business[]` alineados, incluso con enriquecimiento parcial y recuperación |
| G17 | Instantánea de solicitudes | Mutaciones posteriores del input no modifican una ejecución ya recibida |
| G18 | Prueba A/B/C | Tres vistas separadas, sin intersección de identidades verificadas, preservando originales |
| G19 | Fixture DATRA sintético | Nombre similar, sitio compartido, sucursales e identidad ausente nunca producen falsos positivos |
| G20 | Exclusión de históricos | No se utiliza CSV/XLSX antiguo, DB ni reglas `CONSERVAR`/`DESCARTAR` |
| G21 | Visibilidad de operación | Tiempos y conteos por consulta y lote sin filtrar secretos |
| G22 | Regresión/exportación | CSV/XLSX existentes mantienen esquema, orden y contrato del consumidor |
| G23 | Validación live | Solo con permiso independiente del propietario; auditar diff y evidencias antes del cierre |

Las pruebas de identidad y deduplicación deben ser **offline, reproducibles y controladas**. Las pruebas live de Google Maps no sustituyen las pruebas de invariantes y no quedan autorizadas por este ADR.

---

## 5. Riesgos, limitaciones y tratamiento

| ID | Riesgo | Severidad | Respuesta arquitectónica |
|---|---|---|---|
| R09-01 | Un negocio carece de identificador verificable | Alta | Preservar, marcar y no deduplicar por intuición |
| R09-02 | El `href` cambia o no identifica inequívocamente un establecimiento | Alta | Canonicalización aprobada y testeada; no aceptar `href` genérico |
| R09-03 | Desalineación de sidecar/observación | Alta | Invariantes y bloqueo de supresión insegura |
| R09-04 | Fusión falsa de sucursales de una marca | Alta | Identidad por establecimiento, no por marca, sitio o teléfono |
| R09-05 | Una observación posterior tiene datos más completos | Media | Gana la primera; preservar duplicado para auditoría, sin merge |
| R09-06 | Batches largos por navegación secuencial | Media | Máximo cinco, medición; sin SLA ficticio |
| R09-07 | Vistas vacías sorprenden al consumidor | Media | CSV/XLSX con encabezados y resumen de supresiones |
| R09-08 | Un proceso ajeno ejecuta batches simultáneamente | Media | La concurrencia global es responsabilidad del consumidor |
| R09-09 | Expectativa de prospectos inéditos respecto a históricos | Alta | Documentar que dedupe solo cubre el lote e identidades verificadas |
| R09-10 | Crecimiento en memoria al conservar originales/procedencia | Media | Límite de solicitudes y observaciones; métricas de uso durante hardening |
| R09-11 | Un cleanup incorrecto contamina la búsqueda siguiente | Alta | Detener batch y exponer interrupción, no continuar |

---

## 6. Alternativas consideradas y descartadas

- **Paralelizar consultas:** descartado por consumo y complejidad de recursos; no es responsabilidad del Engine coordinar tenants.
- **Unir las búsquedas en un CSV consolidado:** descartado; deben conservarse listas y archivos independientes.
- **Deduplicar por nombre/dirección/teléfono o scoring:** descartado en esta versión por riesgo de falsos positivos y política P01.
- **Escoger el negocio más completo o combinar campos:** descartado por P02; no se implementa merge comercial.
- **Deduplicar intraconsulta:** descartado por P03 y compatibilidad con `v0.8.x`.
- **Leer históricos DATRA o ingresar CSV para excluir registros:** descartado por P07; pertenece a futuro contrato de consumidor.
- **Persistir índice de identidad o añadir campañas:** descartado; el alcance es la operación efímera del lote.

---

## 7. Consecuencias

**Positivas:** se preservan contratos individuales, se automatiza el equivalente acotado de `FiltroEntreBusquedas`, se entregan archivos separados sin duplicados **verificados** entre búsquedas, se mantiene trazabilidad completa y se prepara una frontera reutilizable para futuros consumidores Python o HTTP.

**Tradeoffs aceptados:** persistirán duplicados ambiguos; no habrá deduplicación histórica, merge de campos ni cuotas garantizadas de prospectos únicos; la ejecución será acumulativamente más lenta y conservará datos extra para auditoría en memoria.

---

## 8. Autoridad, resolución y restricciones de cambio

El propietario **aprueba documentalmente** ADR-009 con las siguientes decisiones explícitas:

| Aprobación | Resolución |
|---|---|
| **P01** | Conservar candidatos sin identidad verificable; no realizar matching especulativo |
| **P02** | Prioridad de primera aparición; no fusionar campos ni preferir observaciones más completas |
| **P03** | Deduplicación solo **entre** consultas, sin alterar `search()` individual |
| **P04** | Engine 1–5, CLI múltiple 2–3, límite por consulta 1–100 y confirmación previa |
| **P05** | Archivo CSV/XLSX de encabezados y cero filas para resultado válido enteramente suprimido |
| **P06** | Continuar tras fallo controlado; detener ante aislamiento inseguro o error no controlado |
| **P07** | Históricos externos fuera de `v0.9.x`; `v1.0.0` reservado para hardening y release |

**Resolución definitiva:** `ADR-009 = APPROVED` como **autoridad de diseño**, que sustituye los borradores previos de ADR-009. ADR-008 permanece vigente. El Master Implementation Design y el Runbook deberán derivarse de estas decisiones; no podrán cambiar límites, reglas de identidad, deduplicación, procedencia, errores ni alcance sin nueva aprobación o enmienda explícita del propietario.

**Control de autorización separado:**

- **Aprobación del ADR:** **SÍ**, otorgada por el propietario.
- **Implementación de `v0.9.x`:** **NO AUTORIZADA**.
- **Cambios locales o en GitHub:** **NO AUTORIZADOS**.
- **Pruebas live, commits, ramas, merges, tags o releases:** **NO AUTORIZADOS**.
- **Estado del repositorio remoto:** este archivo aún **no** representa una actualización publicada de GitHub.

**Fin de ADR-009.**
