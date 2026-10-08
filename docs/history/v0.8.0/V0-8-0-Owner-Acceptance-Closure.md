# Prospector CLI — Acta de aceptación y cierre documental de v0.8.0

**Fecha:** 2026-10-06 (America/Tijuana)  
**Repositorio:** `CarlosAM03/prospector-cli`  
**Rama:** `v0.8.0`  
**SHA revisado:** `d1880e7ca305ff326eeac9e1e7c1ccd02e981b1d`  
**Estado funcional:** `OWNER ACCEPTED` — aceptación expresada por el propietario en la conversación de revisión.  
**Estado de sincronización documental con GitHub:** `NOT YET COMMITTED`  
**Release / tag / merge:** `NOT AUTHORIZED`.

## 1. Alcance aceptado

Se acepta el pipeline global de normalización determinista de v0.8.x, la conservación de la representación `Business` original junto con `NormalizedBusiness`, la compatibilidad de consumidores y las exportaciones CSV/XLSX de siete columnas. No se añaden multi-query, deduplicación, merge, concurrencia ni cambios de reglas.

## 2. Evidencia

- `ValidationMatrix.md`: N01–N27 y N30 `PASS`; N28–N29 `PASS_OFFLINE`. N31 originalmente `OWNER_PENDING`.
- Ejecuciones de suite registradas en el handoff: 151 unitarias, 34 integración, 185 totales aprobadas; una E2E live deseleccionada.
- Búsqueda real `maquila`, `tijuana`, límite 75 (2026-10-06): primera salida, 40 negocios con `feed/partial_results`, 183.30 s y cinco incidencias recuperables; segunda salida, 75 negocios, 336.02 s y seis incidencias recuperables.
- CSV adjuntos verificados: `google_maps_maquila_tijuana_20261004_043211.csv` (75), `google_maps_maquila_tijuana_20261006_043736.csv` (40), `google_maps_maquila_tijuana_20261006_051154.csv` (75); siete encabezados: `Name`, `Category`, `Address`, `Phone`, `Email`, `Website`, `Language`.
- Los CSV muestran salida normalizada, no objetos `Business` originales de esa misma ejecución.

## 3. N31 — decisión de aceptación del propietario

El propietario declaró expresamente suficientes las ejecuciones manuales y sus CSV para aceptar funcionalmente la versión y solicitó darla por cerrada a nivel documental. Se conserva la matriz de pruebas controladas como evidencia de preservación, orden, cardinalidad e independencia de originales y normalizados.

**Salvedad:** no se acredita una inspección manual pareada de `result.original_businesses` y `result.businesses` de una misma ejecución tal como solicitaba el handoff operativo. **No registrar esta subcomprobación como ejecutada ni como PASS.** La aceptación del propietario se registra con esta limitación explícita. No sustituye una prueba que no ocurrió ni modifica retroactivamente ADR-008 o el Master Design.

## 4. Riesgos residuales aceptados para el cierre funcional

- Feed parcial de la primera ejecución, no reproducido en la segunda como pérdida permanente.
- Anomalía puntual de clasificación categoría/dirección de Baja Border Maquila: posible parsing/extracción; no modificar normalización sin reproducción.
- Permisos de directorio fijo `pytest --basetemp` en Windows: workaround de ruta única verificado.
- Mutabilidad de colecciones `SearchResult`, clasificación de avisos telefónicos e índices internos de CLI: no bloqueantes.
- La comprobación local de `git status` y evidencia que Git ignora no puede verificarse únicamente con GitHub remoto.

## 5. Cambios documentales necesarios en repositorio

- `docs/roadmap.md`: marcar `v0.8.x` como `OWNER ACCEPTED`, con evidencia live y salvedad N31; mantener `v0.9.x` como siguiente objetivo pendiente de ADR actualizado.
- `docs/architecture.md`: actualizar etiqueta de versión sin alterar contratos ni afirmar publicación.
- `README.md` y `docs/scripting-pipeline.md`: corregir referencias a aceptación live pendiente cuando corresponda.
- Asociar este registro y `ValidationMatrix.md` revisada al SHA aceptado mediante una ruta de documentación rastreable. Los archivos originales bajo `temp/` permanecen ignorados por Git salvo autorización para una copia documental versionada.
- Revisar diff, ejecutar validación documental mínima, y luego solicitar autorización independiente para commit / tag / merge / release.

## 6. Resolución

**Se registra la aceptación funcional del propietario de `v0.8.0`, con salvedad N31 documentada.** El cierre **en GitHub** seguirá pendiente hasta publicar cambios documentales revisados. Esta acta no prueba ni afirma que ya se haya actualizado GitHub, que exista tag o que se haya publicado release.
