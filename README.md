# Compadre Shorts Studio

Fábrica local de Shorts para el canal **Compadre Gameplay**. El objetivo inicial es transformar gameplays propios de GTA 6 en clips verticales que se puedan revisar antes de publicarlos.

## Enfoque

- Procesamiento local con FFmpeg en macOS; los vídeos pesados no se renderizan en GitHub Actions.
- Salida vertical 9:16 a 1080×1920.
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

## Uso previsto

Cortar un gameplay en segmentos consecutivos de 60 segundos:

```bash
compadre-shorts input.mp4 --output renders --mode sequential --duration 60
```

El modo `smart` de la primera versión es una preparación conservadora basada en intervalos; **no** detecta todavía semánticamente persecuciones, tiroteos ni momentos divertidos.

## Criterio editorial

La duración final debe depender del potencial del momento, no de una duración rígida. Como orientación: humor o sorpresa 15–90 s; persecuciones y tiroteos 45–180 s; escenas cinematográficas 60–180 s. Hook en los primeros 1–3 segundos, progresión clara y desenlace fuerte. No publicar lotes masivos sin revisar ni repetir clips indiscriminadamente.

## Seguridad y derechos

- No subir vídeos originales, renders, claves, tokens OAuth ni archivos `.env` al repositorio.
- Usar únicamente gameplay propio o autorizado.
- Utilizar música y efectos con licencias adecuadas.
- La narración sintética es opcional y nunca debe inventar hechos ni contradecir lo que se ve.
- No se promete viralidad ni monetización.

## Estado del proyecto

Base documental inicial. La siguiente implementación incorpora la CLI de corte/renderizado y el manifiesto. La detección inteligente de escenas, subtítulos, voz sintética, conexión OAuth y analítica quedan para fases posteriores.

- [Hoja de ruta](docs/ROADMAP.md)
- [Criterios editoriales](docs/EDITORIAL.md)
