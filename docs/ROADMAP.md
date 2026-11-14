# Hoja de ruta

## Fase 1 — Preparación local
- [x] CLI con FFmpeg/ffprobe
- [x] Exportación vertical 1080×1920
- [x] Manifiesto JSON por lote
- [x] Prueba con gameplay real en macOS
- [x] Preset viral y normalización de audio
- [x] Encuadre seguro que conserva el fotograma completo
- [ ] Validar render seguro con la prueba local de 3 minutos

## Fase 2 — Identificación autónoma del protagonista
- [x] Medir límites de Apple Vision, CSRT y KCF con GTA V
- [ ] Evaluar detector de personajes en gameplay renderizado
- [ ] Asociación temporal y reidentificación del mismo personaje
- [ ] Recuperación tras oclusiones/cambios de escena
- [ ] Medida de confianza y fallback automático al encuadre seguro
- [ ] Validar sin selección manual en clips de 3 minutos y después en un gameplay largo

## Fase 3 — Selección inteligente de momentos
- Analizar señales visuales y de audio para proponer persecuciones, tiroteos, acrobacias, humor, sorpresas y escenas cinematográficas.
- Puntuar candidatos con razones verificables; no confundir intervalos con detección semántica.

## Fase 4 — Acabado
- Subtítulos solo cuando exista diálogo/narración real.
- Textos dinámicos de impacto sin presentarlos como transcripción.
- Miniaturas y metadatos sugeridos.

## Fase 5 — YouTube
- OAuth de Google, permisos mínimos y tokens fuera del repositorio.
- Publicación solo tras aprobación explícita.

## Fase 6 — Métricas
- Seguimiento de visualizaciones, retención e interacción, sin prometer viralidad.
