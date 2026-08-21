# PS4 PUP Extractor — auditoría estática

## Procedencia

Fuente proporcionada por el usuario: `https://www.mediafire.com/download/daw1d5iaap03yhe/PS4+PUP+Extractor.exe`.

La URL inicial devuelve una página HTML de MediaFire. El enlace directo incluido en esa página se descargó como muestra separada. No se ejecutó el archivo ni se abrió con Wine.

## Identidad de la muestra

| Campo | Resultado |
|---|---|
| Archivo | `PS4_PUP_Extractor.real.exe` |
| Tamaño | `34304` bytes |
| Tipo | PE32 GUI Intel 80386, ensamblado Mono/.NET |
| MD5 | `8f1be4b9dac156de5b13d13b3f3bb52a` |
| SHA-256 | `59f7839eebc0c481e38e0e58f9df1ae85a3bb7f81c089ffbd4e452bf08c91859` |
| Importación principal | `mscoree.dll` |
| Ruta de build visible | `c:\Users\jon\Documents\Visual Studio 2012\Projects\PS4 PUP Extractor\...` |
| Ejecución | No realizada |

## Capacidades observables

Las cadenas UTF-16 contienen filtros `PUP files|*.PUP`, `PS4 PUP Files|*.PUP`, `SLB2`, mensajes de validación de PUP y `extracted correctly`. También atribuyen la herramienta a `j0lama` y mencionan investigación de `skfu` sobre la estructura SLB2.

Esto demuestra que el programa es un extractor del **contenedor exterior SLB2/PUP**. Es coherente con separar `PS4UPDATE1.PUP` y `PS4UPDATE2.PUP`, que ya hemos hecho mediante el parser estático local.

No se observaron strings de `libSceNKWebKit`, `libkernel_web`, `SELF`, `SPRX`, `WebKit`, `JavaScriptCore`, `AES`, `RSA`, claves o contraseñas. La ausencia de strings no prueba por sí sola la ausencia de criptografía, pero el alcance visible de la herramienta es extracción SLB2, no descifrado de módulos internos.

## Conclusión

La herramienta es útil para **extraer las dos entradas del contenedor PUP**. No proporciona el WebKit ni el disco/rootfs PS4, no muestra una ruta de descifrado del contenido interno y no sustituye una extracción autorizada de `libSceNKWebKit.sprx`.

El archivo no fue ejecutado. La muestra y sus hashes quedan preservados en el workspace aislado.
