# Compadre Shorts Studio

## Flujo cloud

1. Copia el gameplay de PlayStation en la carpeta ENTRADA de Google Drive.
2. GitHub Actions revisa Drive cada 15 minutos y solo toma archivos sin cambios durante 10 minutos.
3. Descarga un único vídeo y lo procesa en un runner cloud; no utiliza el Mac.
4. Renderiza hasta 10 clips verticales de 60 segundos con encuadre safe (conserva toda la imagen sobre fondo desenfocado).
5. Publica cada clip como público en el canal autorizado, con título, descripción y etiquetas.
6. Verifica el procesamiento de todos los Shorts y solo entonces elimina el original de Drive.
7. Guarda los renders y el manifiesto de publicación como artefacto privado durante 7 días.

## Seguridad, reintentos y duplicados

- Si falla la descarga, el render, una publicación o la verificación de YouTube, el original no se elimina.
- Los IDs de los Shorts publicados se guardan como propiedades privadas del archivo de Drive. Si una ejecución se interrumpe, el siguiente intento verifica y reutiliza esos IDs en vez de volver a publicar los mismos clips.
- La limpieza solo se permite cuando todos los clips de la ejecución han pasado la verificación de YouTube. El borrado de Drive es permanente.
- Los trabajos de Drive se procesan de uno en uno. Los estados de procesamiento abandonados se pueden reintentar después de 8 horas.
- Los títulos y etiquetas actuales son plantillas genéricas; no describen automáticamente el contenido específico de cada jugada.

## Configuración OAuth y secretos

Habilitar Google Drive API y YouTube Data API v3 en Google Cloud. Crear credenciales OAuth y autorizar la misma cuenta que administra la carpeta de Drive y el canal de YouTube.

Scopes que debe conceder el consentimiento OAuth:

- https://www.googleapis.com/auth/drive
- https://www.googleapis.com/auth/youtube.upload
- https://www.googleapis.com/auth/youtube.readonly

Guardar en GitHub Actions Secrets:

- GOOGLE_CLIENT_ID
- GOOGLE_CLIENT_SECRET
- GOOGLE_REFRESH_TOKEN
- GOOGLE_DRIVE_INPUT_FOLDER_ID

No compartir la contraseña de Google ni incluir credenciales en el repositorio. La cuenta autorizada debe tener acceso de edición a la carpeta ENTRADA y permisos de publicación en el canal.

**Importante:** los proyectos OAuth externos que permanecen en estado Testing emiten refresh tokens que caducan a los 7 días cuando solicitan estos scopes. Para automatización diaria continua, hay que resolver el estado de publicación/verificación del proyecto OAuth o renovar la autorización cuando caduque. No se debe asumir que un token de pruebas será permanente.

## Límites y capacidades actuales

- Los runners alojados de GitHub tienen un límite máximo de 6 horas por trabajo. Un vídeo de 60 minutos debe caber, pero el tiempo depende del tamaño, códec y carga del render.
- Se publican hasta 10 clips por gameplay. El sistema actual los segmenta de forma programada; todavía no reconoce semánticamente las mejores jugadas, persecuciones o momentos cómicos.
- El encuadre safe no es seguimiento automático del protagonista. Preserva la imagen completa para evitar cortar la acción mientras se valida un tracker específico de gameplay.
- Los archivos de salida y el manifiesto quedan como artefacto del workflow durante 7 días; no se conserva una copia permanente en Drive.
