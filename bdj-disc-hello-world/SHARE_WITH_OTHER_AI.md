# Contexto BD-J Hello World para análisis externo

## Qué enviar

La otra IA puede recibir estos archivos en formatos admitidos:

- `src/org/homebrew/MyXlet.java`: fuente completa del Xlet benigno.
- `Makefile.txt`: instrucciones de build en formato de texto.
- `README.md`: alcance y dependencias.
- `ISO_STATIC_METADATA.json`: metadatos y hashes de la imagen.
- `BDJO_STATIC_METADATA.txt`: resultado de la inspección textual del BDJO.
- `docs/COMPATIBILITY_AUDIT.md`: auditoría estática.
- `docs/LINUX_ENVIRONMENT_CHECK.md`: límites de la validación Linux.
- `docs/PLAYSTATION_BUG_BOUNTY_REPORT.md`: borrador de informe responsable.
- `docs/validation.json`: resultado de validación.

## Qué no puede hacer la otra IA

La plataforma no admite archivos `.iso` ni `.jar`, por lo que no podrá recibir ni inspeccionar directamente el binario de la imagen o el JAR. No se debe renombrar un binario como `.txt`, `.java` o `.json`: eso no lo convierte en código legible y puede provocar un análisis incorrecto.

La ISO original tiene SHA-256 `ad043fc4a1ac6ecd1a9a5cabb876e6daa849d52e5ec1afb3de29822dff148fdb` y mide 16 MiB. El análisis textual sólo permite verificar sus metadatos conocidos; no sustituye la inspección del binario.

## Alcance técnico

El proyecto es un test BD-J benigno. El Xlet crea una escena `HScene`, añade un panel y muestra `Hello World — BD-J test`. No contiene explotación, payload, carga dinámica, red, reflexión, acceso arbitrario a USB, código nativo, escape de sandbox ni acceso al kernel.

## Preguntas adecuadas para la otra IA

La otra IA puede revisar si el código usa correctamente las APIs BD-J de los stubs públicos, si el nombre `org.homebrew.MyXlet` coincide con el BDJO, si el Makefile es reproducible y qué evidencia adicional sería necesaria para confirmar compatibilidad con una PS4 13.52. No debe concluir que existe una vulnerabilidad sólo porque el disco contenga un Xlet o porque la ISO se haya generado correctamente.
