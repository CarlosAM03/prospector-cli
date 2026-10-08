# v0.9.x — Validation Matrix

Estados: PASS, BLOCKED, NOT RUN, PENDING OWNER LIVE AUTHORIZATION. PASS significa evidencia ejecutada, no plan de prueba. G01–G23 conservan numeración y significado de ADR-009.

| Gate | Contrato | Evidencia observada | Estado |
|---|---|---|---|
| G01 | Compatibilidad individual | P96 full 262 PASS; `test_global_normalization_pipeline.py`, `test_cli_transitional_compatibility.py`, `test_export_service.py`; `search()` y wrapper comparten normalización única | PASS |
| G02 | Entradas Engine 1–5, tipos/límites/fuente pre-browser | `tests/unit/test_batch_contracts.py`: 24 PASS, `_preflight_batch` sin I/O | PASS |
| G03 | CLI 2–3 y confirmación | `test_batch_cli.py` cubre iniciar tras 2, tercera opcional, cancelación y límite inválido antes del Engine | PASS |
| G04 | Secuencialidad/cleanup | `test_batch_coordinator.py`: A/B/C open-close ordenado, máximo una fuente activa; P93 231 full PASS | PASS |
| G05 | Queries iguales, entradas/archivos separados | P94 prueba entradas distintas; P95 `test_cli_exports_separate_files_and_empty_suppressed_view` y colisión exclusiva | PASS |
| G06 | SearchResult íntegro | `test_batch_coordinator.py` preserva original/normalizado/orden/count/issue; P92 sidecar alineado | PASS |
| G07 | Identidad verificada, primera asignación | `P92IdentityEvidence.md` restringe namespace; tests P94 A/B/C confirman asignación exacta | PASS |
| G08 | Sin supresión especulativa | P92 negativos y P94 unknown, namespace distinto, sucursales/homónimos exportables | PASS |
| G09 | Procedencia de supresión | `test_abc_first_verified_occurrence_wins_across_queries_only` y prueba Engine verifican `winner` anterior exacto | PASS |
| G10 | Sin merge/reemplazo | `test_homonyms_branches_and_complementary_fields_are_not_merged`; objetos `SearchResult` preservados | PASS |
| G11 | Exportación independiente | `test_batch_export.py`: CSV/XLSX siete columnas, vacío válido, FAILED sin archivo, sin overwrite | PASS |
| G12 | Continuidad/partial | `test_controlled_failure_continues_and_partial_keeps_result`: A/C conservadas, B FAILED; C PARTIAL | PASS |
| G13 | Parada crítica/prefijo | `test_unexpected_or_runtime_failure_interrupts_with_completed_prefix`, cleanup flag y sidecar estructural detienen con índices pendientes | PASS |
| G14 | Conteos | P94 A/B/C: 9 observados = 6 exportables + 3 suprimidos; prueba integrada y aserción del selector | PASS |
| G15 | Límites sin relleno | P94 A/B/C realiza exactamente tres llamadas fuente con límites propios, ningún scroll/consulta extra | PASS |
| G16 | Sidecar alineado | `_SourceResult` valida longitud/tipo; `test_source_identity_sidecar.py` y test controlado con Website issue; 223 full PASS | PASS |
| G17 | Snapshot defensivo | `test_preflight_snapshots_mutable_queries_and_does_not_mutate_config` y mutación del llamador durante A en `test_three_queries_run_in_order_after_full_snapshot_and_normalize_once` | PASS |
| G18 | Escenario A/B/C | `test_abc_engine_selects_exact_cross_query_ids_without_extra_extraction` y `test_abc_verified_ids_produce_three_disjoint_csv_files`: [1,2,3]/[4,5]/[6] | PASS |
| G19 | Fixture DATRA sintético | `test_datra_style_sectors_with_branches_homonyms_incomplete_and_no_history`: tres sectores, sucursales/homónimos/incompletos; histórico no entregado al Engine | PASS |
| G20 | Ausencia de históricos | Auditoría P96 de `src/`/diff: sin CSV histórico, DB, campañas, estado persistido ni API; `rg` focalizado en módulos batch/CLI/export | PASS |
| G21 | Métricas seguras | P93 mide `execution_time` por consulta/lote; `QueryFailure` entrega categoría/mensaje fijo, pruebas de no filtración; no URLs en métricas o logs de batch | PASS |
| G22 | Regresión/exportación individual | P95 260 full PASS; `test_cli_transitional_compatibility.py`, `test_export_service.py` conservan ruta individual | PASS |
| G23 | Validación live general de aceptación | Decisión expresa del propietario v0.9.7: Run A (100/100/100, 0/5/2 supresiones, q03 PARTIAL 85/83/2) y Run B (30/40/50, 0 supresiones); seis CSV locales independientes con siete columnas y 94/95/83 y 30/40/50 filas. P92 fue otra investigación, no G23. Ver `V0-9-0-Owner-Acceptance-Closure.md`. | PASS / OWNER LIVE ACCEPTED |

G01–G22 quedaron cubiertos offline con pruebas y auditoría del diff P96; 262 PASS, una E2E deseleccionada. Los reportes JUnit `P96-unit.xml`, `P96-integration.xml` y `P96-full.xml` registran 194/68/262 tests, cero fallos/errores/skips dentro de la selección offline. G23 corresponde únicamente a los dos batches completos ejecutados posteriormente por el propietario y aceptados expresamente en v0.9.7; no se volvió a ejecutar Google Maps durante este cierre documental. `UNVERIFIED` exportable es una limitación aceptada, no un FAIL.
