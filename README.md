# Compadre Shorts Studio

Fábrica local de Shorts para el canal **Compadre Gameplay**. Prepara clips verticales a partir de gameplays propios, con revisión humana antes de publicarlos.

## Enfoque

- Procesamiento local con FFmpeg en macOS; los vídeos pesados no se renderizan en GitHub Actions.
- Salida vertical 9:16 a 1080×1920.
- Preset visual `viral` con contraste, saturación y enfoque moderadamente reforzados; preset `clean` sin ese tratamiento.
- Procesamiento de audio opcional: normalización de sonoridad y control de picos con FFmpeg.
- Cortes configurables y manifiesto JSON para organizar cada lote.
- Revisión humana obligatoria antes de publicar.
- Publicación en YouTube solo en una fase posterior, mediante OAuth y autorización explícita.

## Requisitos

- macOS
- Python 3.11+
- FFmpeg y ffprobe
- Espacio de disco para los originales y los vídeos generados

## Instalación

```bash
brew install ffmpeg
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Uso

Preparar clips de 60 segundos con el estilo viral y audio normalizado (valores predeterminados):

```bash
compadre-shorts input.mp4 --output renders --duration 60
```

Elegir un aspecto limpio y conservar el nivel de audio original:

```bash
compadre-shorts input.mp4 --output renders --style clean --audio-processing original
```

La normalización usa un objetivo de sonoridad y un limitador de picos. No equivale a eliminar ruido, separar efectos ni mezclar música. Si el original no tiene audio, el programa lo registra en el manifiesto.

## Qué hace y qué no hace esta versión

- Convierte y recorta el vídeo en formato vertical 1080×1920.
- Aplica un tratamiento visual moderado según el preset.
- Puede equilibrar la sonoridad y limitar picos del audio original del juego.
- El modo `smart` sigue siendo una segmentación por intervalos: **no** detecta semánticamente persecuciones, tiroteos ni momentos divertidos.
- No genera subtítulos ni diálogos inventados.
- No añade música ni efectos de sonido externos.
- No selecciona automáticamente los mejores momentos todavía.

## Criterio editorial

La duración final debe depender del potencial del momento, no de una duración rígida. Como orientación: humor o sorpresa 15–90 s; persecuciones y tiroteos 45–180 s; escenas cinematográficas 60–180 s. Hook en los primeros 1–3 segundos, progresión clara y desenlace fuerte. Revisar cada clip antes de publicar.

## Seguridad y derechos

- No subir vídeos originales, renders, claves, tokens OAuth ni archivos `.env` al repositorio.
- Usar únicamente gameplay propio o autorizado.
- Utilizar música y efectos con licencias adecuadas.
- No publicar lotes masivos sin revisión.
- No se promete viralidad ni monetización.

## Próximas fases

1. Análisis de candidatos por ventanas usando señales visuales y de audio, con puntuación explicable y revisión humana.
2. Plantillas de texto de impacto configurables, sin atribuirlas como transcripción.
3. Miniaturas y metadatos sugeridos para YouTube.
4. Flujo de publicación opcional con OAuth y confirmación explícita.

- [Hoja de ruta](docs/ROADMAP.md)
- [Criterios editoriales](docs/EDITORIAL.md)
