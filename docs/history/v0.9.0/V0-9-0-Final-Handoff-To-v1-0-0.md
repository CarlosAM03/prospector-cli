# Prospector CLI — Final Handoff from v0.9.x to v1.0.0

**Origen:** v0.9.x `OWNER ACCEPTED / COMPLETE` sobre implementación `c7193d55a36618e934e29a9678b3f9b01e9b6543`; cierre documental v0.9.7 publicado en `origin/v0.9.0` como `71cb7f8981281ce68a2e9936ba01554e69e8c7ed` y detallado en `V0-9-0-Owner-Acceptance-Closure.md`. P91–P96 y G01–G23 aceptados. No existe release/tag v0.9.x por inferencia.

**Próximo sprint:** `v1.0.0 — FINAL HARDENING AND STABLE RELEASE`. Este handoff no es el Master Design ni el runbook de v1.0.0 y no autoriza implementarlo todavía.

**Estado de transición:** `READY TO BEGIN v1.0.0 PLANNING`. No implica que v1.0.0 esté implementada, etiquetada o publicada.

Objetivos de transición, sujetos a la futura planificación y aprobación de v1.0.0: hardening y estabilidad del CLI; congelamiento de contratos públicos; validación final y regresión; documentación de usuario; packaging/distribución; preparación del primer release estable. Podrá estudiarse una distribución `.exe` o instalador, pero no se produjo en v0.9.7. La eventual extracción física de Prospector Engine y una API como consumidor son posibilidades **post-v1**, no funcionalidades del CLI v1.0.0 ni trabajo autorizado ahora. No se introduce FastAPI.

Invariantes a preservar en la planificación siguiente: normalización global obligatoria de ADR-008; dos vistas `Business`/`NormalizedBusiness`; compatibilidad individual y legacy; batch secuencial con límites aprobados; deduplicación solo por identidad Google Maps verificada conforme a ADR-009/P92; `UNVERIFIED` exportable; ausencia de merge comercial o matching heurístico; CSV/XLSX de siete columnas. La limitación de posibles falsos negativos por identidad `UNVERIFIED` fue aceptada explícitamente y no debe transformarse tácitamente en un requisito de matching v1.

La aceptación funcional previa de v0.8.x conserva la salvedad N31: no hubo inspección live pareada de originales y normalizados; las invariantes se validaron offline. La aceptación live v0.9.x G23 proviene de dos batches posteriores del CLI, no de la investigación P92. Cualquier nueva política de identidad, histórico, persistencia, API o consumidores externos requiere decisión arquitectónica separada.
