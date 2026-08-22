# Revisión estática de `dump_pkg_links` — sesión 71

## Fuente

- Repositorio: `InvoxiPlayGames/dump_pkg_links`
- URL: https://github.com/InvoxiPlayGames/dump_pkg_links
- Rama: `master`
- Descripción: script de mitmproxy/mitmweb para registrar enlaces de paquetes PS4 durante descargas.
- Contenido observado: `README.md`, `dump_pkg_links.py` y metadatos GitHub. No se ejecutó el script ni se configuró un proxy.

## Qué hace

El README describe una herramienta que observa solicitudes de descarga de contenido PS4 y escribe enlaces en archivos de texto como `pkg_links_app.txt`, `pkg_links_ac.txt` y `pkg_links_patch.txt`. Está orientada a capturar URLs de paquetes durante descargas de PSN mediante un proxy local.

El repositorio no contiene PUPs, dumps de filesystem, módulos `SPR X/SELF`, `libSceNKWebKit.sprx`, `libkernel_web.sprx`, `rt.jar`, `bdjstack.jar` ni hashes de esos artefactos. Tampoco ofrece un método para descifrar PKG o extraer módulos internos. El propio README advierte que los PKG están cifrados y que la captura de enlaces no proporciona las claves por paquete.

## Relevancia para WebKit 13.52

La herramienta podría servir para obtener enlaces de contenido descargable, pero eso no equivale a obtener el firmware 13.52 ni sus módulos internos. No proporciona acceso a `libSceNKWebKit.sprx` y no resuelve el bloqueo de análisis retail. Además, usarla contra PSN o una consola real requeriría una operación de red y configuración externa que no se realizó.

## Clasificación

| Hallazgo | Clasificación |
|---|---|
| Existencia pública del repositorio y su script | `DIRECT_DOCUMENTATION` |
| Captura de enlaces PKG durante descargas | `DOCUMENTED_ONLY` |
| Obtención de `libSceNKWebKit.sprx` o `libkernel_web.sprx` | `DISCARDED` |
| Obtención de claves o descifrado de PKG | `DISCARDED` |
| Evidencia específica de PS4 13.52/WebKit | `UNVERIFIED` |

## Conclusión

`dump_pkg_links` no aporta el WebKit que falta. Es una herramienta de observación de URLs de paquetes, no un extractor de firmware ni un parser de módulos PS4. Se conserva como referencia documental, pero no debe confundirse con una ruta para obtener o descifrar `libSceNKWebKit.sprx`.
