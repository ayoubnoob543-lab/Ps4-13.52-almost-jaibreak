# Referencias públicas: USB desde BD-J en PS4

## Conclusión ejecutiva

Las fuentes públicas revisadas no muestran una API BD-J estándar de PS4 que permita a un Xlet benigno enumerar dispositivos USB. Lo que sí aparece es una separación de capas:

1. El disco Blu-ray inicia el flujo BD-J.
2. En implementaciones de jailbreak, código posterior al escape puede leer un `payload.bin` desde USB y entregarlo a componentes nativos.
3. Eso no demuestra que un Xlet BD-J normal pueda enumerar, montar o leer arbitrariamente un USB.

Por tanto, el acceso USB observado en loaders públicos es **función posterior al exploit**, no una capacidad demostrada del BD-J estándar.

## Fuentes

### ConsoleMods: BD-JB

La guía pública describe un Blu-ray grabado como punto de entrada y un USB con `payload.bin` para el flujo de jailbreak. También indica que el USB se utiliza después de preparar el medio y que el resultado depende de un exploit compatible con el firmware. La página no documenta una API Java BD-J para enumerar dispositivos USB; describe un loader y payloads en una cadena de explotación [1].

Clasificación del USB como capacidad BD-J estándar: `NO EVIDENCE`.

### HENloader_Source

El README de `iaceene/HENloader_Source` describe un loader de explotación y afirma que, tras el flujo privilegiado, lee `payload.bin` del USB y lo copia a `/data/payload.bin`. El mismo README contiene referencias a `System.getSecurityManager()`, inicialización de offsets de kernel, payloads y modos de explotación [2].

Esto es evidencia de que un **loader post-exploit** puede usar USB en una cadena de jailbreak, pero no de que un Xlet benigno pueda realizar esa operación. El repositorio queda fuera del proyecto BD-J seguro y no se ha ejecutado ni incorporado.

Clasificación: `DOCUMENTED_ONLY` para la existencia del flujo descrito; `OUT_OF_SCOPE` para el cascarón.

### PSXHAX / Mr_lou

La discusión histórica plantea que un disco de arranque podría combinarse teóricamente con un filesystem USB mediante BD-Live. La misma discusión indica que PS3/PS4 no usarían de forma accesible para el usuario un USB como área BUDA, sino almacenamiento interno. El texto es una opinión y una experiencia histórica de terceros, no una especificación de PS4 13.52 [3].

Clasificación: `HISTORICAL_ONLY` y `UNVERIFIED`.

### ConsoleMods: medios admitidos

La guía indica que BD-R y BD-RE son los medios usados para BD-J y que copiar un `payload.bin` a USB forma parte de los procedimientos de jailbreak, no del arranque de un BD-J estándar [1].

## Qué significa para nuestro disco

La ISO local usa únicamente APIs públicas BD-J y no contiene código para USB. La pantalla `USB: not requested` es deliberada. Añadir rutas como `/mnt/usb0`, `payload.bin`, escritura en `/data` o inicialización de offsets no sería una prueba neutral de compatibilidad: sería incorporar lógica específica de loaders y explotación.

El cascarón puede demostrar:

- que el BDJO y el JAR son coherentes;
- que el Xlet inicia;
- que las APIs BD-J públicas enlazan;
- que la aplicación no solicita acceso nativo ni a dispositivos.

No puede demostrar, sin una API/documentación PS4 específica, que un USB sea accesible desde BD-J.

## Respuesta a la pregunta técnica

**¿Hay un ejemplo público de listar dispositivos USB desde un Xlet BD-J normal de PS4?** No se encontró uno verificable en las fuentes revisadas.

**¿Hay ejemplos públicos de USB en exploits de PS4?** Sí: los loaders públicos describen la lectura de un `payload.bin` desde USB, pero dentro de una cadena de jailbreak/post-exploit. No es una API BD-J estándar y no debe copiarse al cascarón.

**¿Qué falta para una implementación legítima?** Una especificación o stub verificable de Sony que documente la API, permisos, ruta, formato y contrato de acceso a medios extraíbles. El SDK público utilizado para el proyecto no aporta esa interfaz.

## Referencias

[1]: https://consolemods.org/wiki/PS4:BD-JB "ConsoleMods — PS4 BD-JB"
[2]: https://github.com/iaceene/HENloader_Source "iaceene/HENloader_Source"
[3]: https://www.psxhax.com/threads/playstation-4-bd-j-ps4-blu-ray-java-homebrew-answers-by-mr_lou.1535/page-4 "PSXHAX — PS4 BD-J Homebrew Answers, page 4"
