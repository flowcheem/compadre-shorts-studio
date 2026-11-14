# Compadre Shorts Studio

## Google Drive cloud intake

- Copia los vídeos de PlayStation a una carpeta de Google Drive configurada como ENTRADA.
- El workflow revisa la carpeta cada 15 minutos y solo procesa vídeos sin cambios durante al menos 10 minutos.
- Toma un único vídeo pendiente por ejecución para evitar concurrencia sobre el mismo original.
- Descarga y renderiza en GitHub Actions; el Mac no participa.
- Los renders quedan como artefacto privado del workflow durante 7 días.
- El original no se borra durante la descarga ni el renderizado.

## Limpieza segura

El comando cleanup-after-publish exige el ID de un vídeo de YouTube y consulta YouTube Data API. Solo elimina permanentemente el original si YouTube confirma simultáneamente processingStatus=succeeded y uploadStatus=processed, y si el archivo está en un estado Compadre permitido. Un error de render o publicación nunca autoriza el borrado.

La limpieza todavía no se ejecuta automáticamente desde el workflow: falta conectar y probar la etapa de publicación OAuth de YouTube. Hasta entonces, los originales se conservan.

## Secretos OAuth requeridos

Configurar OAuth en Google Cloud, habilitar Google Drive API y autorizar la cuenta propietaria de la carpeta. Guardar estos GitHub Actions secrets:

- GOOGLE_CLIENT_ID
- GOOGLE_CLIENT_SECRET
- GOOGLE_REFRESH_TOKEN
- GOOGLE_DRIVE_INPUT_FOLDER_ID

El token debe tener permisos para listar, descargar, actualizar propiedades y borrar archivos de Drive, y leer el estado de procesamiento de YouTube. No compartir la contraseña de Google.

## Límites y estado

- Los runners alojados de GitHub tienen un límite de 6 horas por trabajo. El vídeo de una hora debe caber; depende del códec, tamaño y carga de render.
- Render actual: segmentos de 60 segundos, máximo 10, encuadre safe (imagen completa sobre fondo desenfocado).
- No hay todavía seguimiento semántico fiable del protagonista.
- La publicación automática de YouTube y el borrado automático solo se activarán después de validar la integración OAuth de YouTube.
