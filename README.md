# Compadre Shorts Studio

Fábrica local de Shorts para **Compadre Gameplay**. Prepara clips verticales desde gameplays propios, con revisión antes de publicar.

## Estado v0.4 — base de producción

- Procesamiento local con FFmpeg; los vídeos no se renderizan en GitHub Actions.
- Salida 1080×1920, preset visual `viral` y audio normalizado por defecto.
- **Encuadre `center` por defecto:** llena el lienzo 9:16 (1080×1920), sin bandas difuminadas. Puede recortar partes de la acción.
- Encuadre `safe` disponible como alternativa de conservación completa, con fondo ampliado y desenfocado.
- FFmpeg se ejecuta con `-nostdin` para evitar que consuma accidentalmente entradas del Terminal.
- Manifiesto JSON con parámetros, estado de revisión y limitaciones conocidas.

## Importante: seguimiento del protagonista

Las pruebas locales mostraron que Apple Vision solo detectó personas en una parte del clip y que CSRT/KCF perdieron el objetivo o se desviaron a objetos del escenario. Por tanto, **ninguno de esos resultados controla el recorte de producción**.

La identificación autónoma y persistente del protagonista de GTA V sigue en desarrollo. No se presenta la detección genérica de personas como reconocimiento de identidad. Hasta validar un método específico con gameplay real, el modo seguro preserva toda la imagen.

## Requisitos

- macOS, Python 3.11+ y FFmpeg/ffprobe.
- Instalación: `brew install ffmpeg`, `python3 -m venv .venv`, `source .venv/bin/activate`, `pip install -e .`.

## Uso

Valores predeterminados: preset viral, audio normalizado y recorte vertical `center`.

```bash
compadre-shorts input.mp4 --output renders --duration 60
```

Alternativa para conservar toda la imagen (incluye fondo desenfocado):

```bash
compadre-shorts input.mp4 --output renders-center --framing safe
```

Opciones `--style clean|viral`, `--audio-processing original|normalize`, `--framing center|safe`, `--mode sequential|smart`.

La normalización ajusta sonoridad y picos; no elimina ruido ni separa efectos. El modo `smart` todavía segmenta por intervalos y no detecta semánticamente persecuciones, tiroteos ni humor.

## Lo que aún no hace

- No identifica de forma fiable al protagonista en todos los gameplays.
- No selecciona automáticamente los mejores momentos.
- No genera subtítulos ni diálogos inventados.
- No añade música ni efectos externos.
- No publica en YouTube; una futura publicación requerirá OAuth y autorización explícita.

## Criterio editorial y seguridad

Revisar cada clip antes de publicarlo. Usar gameplay propio/autorizado y música/SFX con licencia. No subir vídeos, tokens, claves ni archivos `.env` al repositorio. No se promete viralidad ni monetización.
