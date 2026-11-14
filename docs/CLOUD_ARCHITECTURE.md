# Arquitectura cloud-first de Compadre Shorts Studio

## Objetivo
Procesar gameplays fuera del ordenador del usuario, con una cadena automatizada y coste inicial cero. El Mac queda como dispositivo para abrir la web y cargar/descargar archivos; no instala dependencias ni renderiza.

## Cadena propuesta

1. **Interfaz web — Cloudflare Pages (Free).** Panel para crear trabajos, ver estados y descargar resultados.
2. **API ligera — Cloudflare Worker (Free).** Autenticación, creación de trabajos, validación de metadatos y coordinación. No renderiza vídeo: el límite gratuito de CPU de Workers no sirve para FFmpeg.
3. **Almacenamiento — Cloudflare R2 (Free tier).** Vídeo original y resultados mediante cargas directas/prefirmadas; evitar pasar archivos grandes por el Worker. Cuota publicada: 10 GB-mes, 1 millón de operaciones clase A y 10 millones clase B; salida de datos sin coste.
4. **Motor de vídeo — GitHub Actions en runner estándar Ubuntu.** Descarga el objeto de entrada, ejecuta FFmpeg/ffprobe, genera clips y devuelve resultados. Los runners estándar son gratuitos para repositorios públicos; los privados consumen la cuota mensual del plan. Cada trabajo tiene un máximo de 6 horas y el runner Ubuntu estándar ofrece 4 CPU, 16 GB RAM y 14 GB SSD. Esto hace viable un MVP por lotes moderados, no una promesa de procesamiento ilimitado.
5. **Publicación — YouTube Data API (fase posterior).** OAuth, autorización explícita, secretos fuera del repositorio y control de cuotas/restricciones de Google.

## Primera etapa implementable
El workflow `.github/workflows/cloud-render.yml` permite lanzar un trabajo remoto desde GitHub Actions proporcionando una URL HTTPS de descarga (idealmente una URL temporal de R2). Produce clips verticales 1080×1920 y los entrega como artefacto descargable. Es una primera prueba real de render cloud, todavía sin interfaz web ni subida automática a R2.

## Límites que debemos respetar
- Cloudflare Worker no procesa vídeo: en Free tiene 10 ms de CPU por solicitud y 128 MB de memoria.
- R2 Free tiene 10 GB-mes; un gameplay largo puede superar esa capacidad. Borrar originales y resultados temporales tras la retención acordada.
- GitHub Actions: runners estándar gratuitos en repos públicos; repos privados dependen de minutos incluidos. Un job no puede superar 6 horas. El runner tiene almacenamiento limitado; validar tamaño antes de descargar.
- No incluir tokens, URLs prefirmadas, OAuth ni claves en logs, commits o archivos del repositorio.
- El modo actual de FFmpeg corta por intervalos; todavía NO detecta semánticamente persecuciones, tiroteos, humor ni identifica al protagonista. Esa inteligencia es una fase separada y no se debe anunciar como terminada.
- No asumir que el plan gratuito soportará producción ilimitada. Medir duración, tamaño, minutos de runner y GB almacenados por trabajo.

## Orden de implementación
1. Validar el render remoto desde GitHub Actions.
2. Conectar Cloudflare R2 con carga directa y transferencia automática de resultados.
3. Crear el panel Cloudflare Pages + Worker y un mecanismo seguro para disparar trabajos.
4. Incorporar análisis visual/audio, detección de eventos y seguimiento temporal robusto.
5. Añadir metadatos, miniaturas, OAuth y publicación YouTube tras autorización.

## Estado
La fase 1 es una prueba funcional de infraestructura, no la aplicación web final. El usuario no necesita ejecutar comandos ni procesar vídeos en su Mac.
