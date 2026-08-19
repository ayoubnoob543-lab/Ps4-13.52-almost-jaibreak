# Fuentes externas verificadas

## Sony PlayStation 4 OSS WebKit

URL: https://www.playstation.com/en-us/oss/ps4/webkit/

La página oficial de Sony ofrece fuentes WebKit por rangos de firmware. Incluye `WebKit-601-1250.zip` y `WebKit-616-1250.zip` para 12.50–12.52, y `WebKit-601-1300.zip` y `WebKit-616-1300.zip` para 13.00–13.04. No lista una fuente WebKit específica para 13.52. La página declara que el código se publica bajo licencias BSD/LGPL aplicables y permite modificación para uso propio y reverse engineering para depurar modificaciones. Esto convierte los paquetes 13.00–13.04 en la base pública más cercana, pero no en una fuente exacta de 13.52.

## OpenOrbis PS4 Toolchain

URL: https://github.com/OpenOrbis/OpenOrbis-PS4-Toolchain

El proyecto ofrece un toolchain abierto para aplicaciones homebrew de PS4 sin el SDK oficial. Declara dependencia de Clang y LLD, la variable `OO_PS4_TOOLCHAIN`, headers y library stubs, y herramientas como `create-eboot`, `create-lib`, `readoelf` y `LibOrbisPkg`. Su roadmap indica que el soporte GPU/rendering no se considera totalmente finalizado en las versiones descritas. Es adecuado como toolchain legal para aplicaciones y pruebas de ABI, pero no proporciona automáticamente el SDK propietario ni las librerías internas necesarias para compilar el WebKit retail de Orbis.

## PS4OSSCode

URL: https://github.com/FreeBSDKernel9-0/PS4OSSCode

El corpus reúne fuentes WebKit de varias generaciones, incluyendo `WebKit-601-1250`, `WebKit-616-1250`, `WebKit-601-1300` y `WebKit-616-1300`, además de versiones antiguas y FreeBSD. Su README advierte que las modificaciones propietarias de Sony no están incluidas. Por tanto, el corpus puede servir como fuente estructural y base de comparación, pero no prueba la existencia de `libSceNKWebKit.sprx`, `libkernel_web.sprx`, `libSceLibcInternal.sprx` ni un binario retail 13.52.

## Consecuencia para el kit

La ruta reproducible legítima queda dividida en dos objetivos. El primero es una build de WebKit/JSC basada en la fuente OSS más cercana disponible, con un toolchain abierto y un perfil de compatibilidad documentado. El segundo, separado, sería una build retail-compatible con PS4 13.52; ésta permanece bloqueada por la falta de una fuente 13.52 específica, SDK/headers internos, ABI de plataforma y librerías propietarias de Orbis. No se debe presentar la primera como una réplica de la segunda.

## PS4 Developer Wiki: relaciones de módulos y límites

Fuentes: https://www.psdevwiki.com/ps4/Vulnerabilities y https://www.psdevwiki.com/ps4/Internet_Browser

Estas páginas documentan la relación entre el navegador, `libSceNKWebKit.sprx`, `libkernel_web.sprx` y `libSceLibcInternal.sprx`, y muestran referencias de user-agent para PS4 13.52. No publican una copia verificable de los tres módulos, sus SHA-256, un Build ID de la misma revisión ni tablas completas de GOT/vtables verificadas contra bytes 13.52. La evidencia se clasifica como `DOCUMENTED_ONLY`.

La página oficial de Sony consultada enumera fuentes OSS WebKit hasta los rangos 13.00–13.04, no una fuente específica 13.52. Por tanto, el wiki no cierra la brecha de identidad binaria.
