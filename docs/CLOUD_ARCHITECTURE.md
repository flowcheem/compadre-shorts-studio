# Arquitectura cloud-first de Compadre Shorts Studio

## Objetivo
Procesar gameplays fuera del ordenador del usuario, con coste inicial cero. El Mac será solo un dispositivo para abrir la web y cargar/descargar archivos; no instala dependencias ni renderiza.

## Cadena

1. **Interfaz — Cloudflare Pages (Free):** panel para crear trabajos, ver estados y descargar resultados.
2. **API — Cloudflare Worker (Free):** autenticación, creación de trabajos, validación y coordinación. No renderiza vídeo: el límite gratuito de CPU por solicitud no sirve para FFmpeg.
3. **Almacenamiento — Cloudflare R2 (Free tier):** originales y resultados privados, con carga/descarga directa y URLs temporales emitidas por el backend. Cuota publicada: 10 GB-mes, 1 millón de operaciones clase A y 10 millones clase B; egreso sin coste.
4. **Motor — GitHub Actions:** runner Ubuntu estándar ejecuta FFmpeg/ffprobe. El repositorio es público, por lo que los runners estándar son gratuitos. El runner tiene 4 CPU, 16 GB RAM, 14 GB SSD y límite de 6 horas por job.
5. **Publicación — YouTube Data API:** OAuth, autorización explícita y credenciales guardadas como secretos.

## Primera etapa: render cloud privado
El workflow `.github/workflows/cloud-render.yml` toma el nombre de un objeto dentro de un bucket R2 privado, descarga el vídeo usando secretos del repositorio, genera clips verticales y sube el ZIP de resultados al mismo bucket. No publica el vídeo ni los resultados como artefactos públicos de GitHub.

### Secretos que habrá que configurar en GitHub
- `R2_ACCOUNT_ID`
- `R2_BUCKET`
- `R2_ACCESS_KEY_ID`
- `R2_SECRET_ACCESS_KEY`

La clave R2 debe tener acceso solo al bucket de trabajo. Nunca se pegan claves ni URLs firmadas en el chat, en los inputs del workflow o en el código.

## Límites
- Cloudflare Worker no procesa vídeo; el plan gratuito limita el tiempo de CPU por solicitud.
- R2 Free: 10 GB-mes; los originales grandes pueden superar esa capacidad. Definir retención y borrar temporales automáticamente.
- GitHub Actions: runner limitado a 14 GB de disco y 6 horas por job; el workflow aplica un límite preventivo de 12 GB al vídeo fuente y máximo de 30 clips por ejecución.
- La selección actual sigue siendo por intervalos. Aún no detecta semánticamente persecuciones, tiroteos, humor ni identifica de forma persistente al protagonista.
- El plan gratuito permite un MVP y pruebas reales, no procesamiento ilimitado garantizado.

## Orden
1. Configurar R2 y secretos, y validar un render remoto privado.
2. Crear panel Cloudflare Pages + Worker y disparo seguro de trabajos.
3. Añadir análisis visual/audio, detección de eventos y seguimiento temporal robusto.
4. Añadir metadatos, miniaturas, OAuth y publicación en YouTube tras autorización.
