# Búsqueda exclusiva de un artefacto real del kernel Orbis PS4 13.02

**Fecha de corte:** 26 de agosto de 2026.
**Objetivo:** localizar el primer artefacto público que contenga bytes del kernel Orbis 13.02, código de kernel, disassembly o pseudocódigo verificable para comparar `ffs_mountfs()`/`ffs_reload()` con otra versión.
**Restricción:** sólo análisis público y estático. No se ejecutaron exploits, corrupción de memoria ni payloads contra hardware.

## Conclusión ejecutiva

No se localizó un artefacto público verificable que contenga bytes, un dump, ELF, disassembly o pseudocódigo del **kernel Orbis PS4 13.02**. El resultado más cercano es `AetherPS/Fusion`, cuyo commit `1d7c0314ade52858496195e53bcc85de274def51` publica un header `Shared/Offsets-1302.h` con direcciones y funciones auxiliares. Ese archivo es una tabla de offsets, no un kernel ni una reconstrucción de sus bytes, y no contiene referencias a `ffs_mountfs()` o `ffs_reload()`.

Los repositorios de SLOPOS, `ps4-linux-loader`, `ps4-payload-sdk`, OpenOrbis, Mira, kpayload, Vue After Free, PPPwn y los forks examinados contienen headers, código de payload, módulos de userland/WebKit, utilidades de dumping o un kernel **Linux** destinado a ser cargado por PS4. Ninguno aporta el kernel Orbis 13.02. `libSceNKWebKit.sprx` y `kernel.ts` de Vue son módulos/código de userland; no deben tratarse como el kernel Orbis.

En consecuencia, Celsius/`ffs_mountfs()` continúa sin poder confirmarse estáticamente para Orbis 13.02. El único código verificable de `ffs_mountfs()` encontrado procede de FreeBSD histórico o de headers de FreeBSD incluidos en SDKs; eso demuestra el antecedente upstream, no la presencia byte-identical en Orbis.

## Criterio de aceptación

Un resultado sólo se habría aceptado como **VERIFIED** si proporcionaba al menos una de estas piezas: un archivo binario identificado como kernel Orbis 13.02 con hash y procedencia; un dump legítimo de memoria/kernel; un ELF o imagen descifrada/reconstruida del kernel; un disassembly/pseudocódigo con offsets de instrucciones y referencias cruzadas; o una publicación primaria que incluyera el artefacto descargable y permitiera reproducir la correspondencia.

Los siguientes elementos no satisfacen el criterio por sí solos: tablas de offsets, headers de estructuras, código FreeBSD upstream, payloads `.elf`/`.bin`, ISOs BD-J, `libSceNKWebKit.sprx`, `kernel.ts` de Vue, logs, afirmaciones de “identical kernel” y vídeos sin artefacto descargable.

## Artefactos y candidatos inspeccionados

| Artefacto | Qué contiene realmente | Tipo de firmware/procedencia | ¿Bytes de kernel Orbis 13.02? | ¿Permite localizar FFS? | Clasificación |
|---|---|---|---|---|---|
| [`AetherPS/Fusion`](https://github.com/AetherPS/Fusion) commit [`1d7c031`](https://github.com/AetherPS/Fusion/commit/1d7c0314ade52858496195e53bcc85de274def51) | `Shared/Offsets-1302.h`, código fuente de utilidad/driver y daemon | PS4 13.02 declarado; commit de ArabPixel, 20-01-2026 | No | No | **SOURCE_ONLY** para offsets; **INVALID** como dump |
| [`alferdoss/SLOPOS-offsets`](https://github.com/alferdoss/SLOPOS-offsets), `ps4/1302.h` | Header de offsets; el propio README indica que la tabla kexec se copia de fuentes de offsets | 13.02; commit de reestructuración `42273e2`, 07-08-2026 | No | No | **DERIVED/SOURCE_ONLY** |
| [`ps4-linux/ps4-linux-loader`](https://github.com/ps4-linux/ps4-linux-loader) | Headers FreeBSD, offsets PS4, código kexec y payloads para arrancar **Linux** | Soporte declarado 13.02/13.04; no contiene imagen Orbis | No; el kernel referido es Linux | No | **INVALID** como kernel Orbis; **SOURCE_ONLY** para offsets |
| [`ps4-payload-dev/sdk`](https://github.com/ps4-payload-dev/sdk) | SDK, `crt/kernel.c`, headers FreeBSD 9.3 y muestras de kdump | SDK de payload; no imagen Orbis | No | No | **SOURCE_ONLY** para infraestructura |
| [`Al-Azif/vue-after-free`](https://github.com/Al-Azif/vue-after-free) | `src/download0/kernel.ts`, JavaScript/WebKit y recursos de userland | Exploit Vue/WebKit; módulo o script de userland | No | No | **INVALID** como kernel |
| [`adri22235/ps4-suid-scanner`](https://github.com/adri22235/ps4-suid-scanner) | `1304.c/h`, `scanner_1304.iso`, `hen.bin`, Java/BD-J y WebKit | Investigación 13.04; afirma “based on 13.02 (identical kernel)” | No | No | **SOURCE_ONLY** para la afirmación; **INVALID** como dump |
| `scanner_1304.iso` | Imagen UDF BD-J de 16 MiB | ISO de userland/BD-J | No | No | **INVALID** |
| `hen.bin` del scanner | Payload compilado que incorpora componentes de HEN/kpayload | Binario de payload, no kernel retail | No | No | **INVALID** |
| [`OpenOrbis/OpenOrbis-PS4-Toolchain`](https://github.com/OpenOrbis/OpenOrbis-PS4-Toolchain) | Toolchain y headers de APIs/estructuras | No firmware Orbis kernel 13.02 | No | No | **INVALID** |
| [`OpenOrbis/mira-project`](https://github.com/OpenOrbis/mira-project) | Código de Mira, parches, offsets históricos y estructuras | Firmwares antiguos; no 13.02 kernel | No | No | **INVALID** para el objetivo |
| [`TheOfficialFloW/PPPwn`](https://github.com/TheOfficialFloW/PPPwn) | Exploit PPPoE, stages y tablas auxiliares | Firmwares históricos; no kernel 13.02 | No | No | **INVALID** |
| Repositorios públicos de Pharaoh2k | Perfil y repositorios públicos revisados; herramientas de payload/debug | No apareció tabla primaria 13.02 ni dump Orbis | No | No | **UNVERIFIED** |
| PSDevWiki [`Kernel`](https://www.psdevwiki.com/ps4/Kernel) | Índice general de reverse engineering, dumps y strings de otras áreas | Wiki; no página/archivo de kernel Orbis 13.02 | No | No | **SOURCE_ONLY** como índice |
| PSDevWiki [`Vulnerabilities`](https://www.psdevwiki.com/ps4/Vulnerabilities) | Descripciones de vulnerabilidades y cadenas históricas | Documentación; no dump 13.02 | No | No directamente | **SOURCE_ONLY** |

## Inspección del candidato AetherPS/Fusion

El commit `1d7c0314ade52858496195e53bcc85de274def51` añade dos archivos y 209 líneas. `Shared/Offsets-1302.h` comienza con `InitKernel1302()` y asigna expresiones del tipo `kernelBase + constante` a símbolos como `prison0`, `rootvnode`, `copyin`, `copyout`, `kernel_map`, `kmem_alloc`, `allproc`, `proc_rwmem`, `vm_map_*` y funciones SBL. No hay sección binaria, array de bytes, formato ELF, hash de kernel, nombre de imagen retail, símbolo FFS ni instrucciones desensambladas.

El repositorio declara soporte para 9.00 y 12.02 en su README actual, mientras que el commit histórico añade offsets 13.02. Sus releases inspeccionados son paquetes de Fusion, no imágenes del kernel Orbis. Las ramas y forks visibles no revelaron un archivo adicional que cambiara esta clasificación.

**Hash Git del header en el commit:** `1d7c0314ade52858496195e53bcc85de274def51` identifica el commit; el contenido puede reproducirse desde la URL del commit. El header no es un hash del kernel y no permite verificar igualdad de bytes.

## Inspección de SLOPOS y sus fuentes

El header público [`ps4/1302.h`](https://github.com/alferdoss/SLOPOS-offsets/blob/master/ps4/1302.h) contiene macros de offsets. Su comentario atribuye la tabla kexec a ArabPixel. El historial consultado muestra el commit `42273e2180cae9aa0c1a67332994d75e1baa713c`, de 7 de agosto de 2026, que reestructura y rellena headers; el blob observado tiene 2.823 bytes y SHA-1 Git `238bc8086d6a7bd6c13397a6e8f68dd807b4a4d0`.

Este objeto es un header C, no un dump. Los valores coincidentes con otra tabla sólo prueban coincidencia de offsets publicados. No contienen bytes vecinos de las funciones, referencias cruzadas, segmentos ejecutables, strings de kernel ni instrucciones que permitan identificar `ffs_mountfs()`.

## Inspección de `ps4-linux-loader`

El árbol público contiene `freebsd-headers/ps4-offsets/1302.h`, `linux/fw_offsets.h`, `linux/ps4-kexec-common/kernel.c` y payloads relacionados. El código de `kernel.c` calcula bases, localiza patrones y usa primitivas de kexec para cargar un kernel Linux; el repositorio también explica que los archivos `bzImage` e `initramfs.cpio.gz` son el kernel Linux y su initramfs para arrancar en la PS4. Ninguno es el kernel Orbis que se pretende comparar.

El README marca 13.02/13.04 y 13.50 con signos de interrogación en algunas entradas. Aunque existieran payloads compilados para esos firmwares, siguen siendo payloads Linux/loader y no un dump del kernel retail Orbis. Por tanto, no sirven para demostrar la implementación de `ffs_mountfs()`.

## Inspección de SDK, OpenOrbis, Mira y kpayload

Los headers `freebsd-headers/ufs/ffs/ffs_extern.h`, `fs.h` y similares en SDKs y loaders son copias o adaptaciones de headers upstream. El código `crt/kernel.c` implementa funciones de infraestructura para operar después de obtener ejecución privilegiada; no contiene una imagen del kernel Orbis ni el cuerpo desensamblado de `ffs_mountfs()`.

Mira contiene código de driver, parches y tablas históricas para firmwares antiguos. OpenOrbis contiene toolchain, headers y APIs de homebrew. Los repositorios de kpayload contienen código fuente de payload y tablas por firmware. La búsqueda de nombres `ffs_mountfs`, `ffs_reload`, `system_fs_image`, `1302.bin`, `kernel.bin`, `kernel.elf` y equivalentes no produjo un artefacto Orbis 13.02 aceptable.

## Forks, ramas, releases y lineage

Se inspeccionaron refs visibles y forks de `ps4-suid-scanner`, Fusion, `dumper-testing`, `ps4-linux-loader` y repositorios relacionados. Los forks de `ps4-suid-scanner` sólo replican el proyecto de investigación; los forks de `ps4-linux-loader` replican headers, kexec y payload Linux; y los forks de Fusion replican la tabla/código de utilidad. No apareció un archivo de kernel Orbis 13.02 ni una fuente primaria de Pharaoh2k con bytes o disassembly.

La afirmación de `adri22235/ps4-suid-scanner` de que 13.04 está “based on 13.02 (identical kernel)” sigue siendo una afirmación documental. La existencia de tablas iguales o derivadas no transforma esas tablas en evidencia de igualdad byte a byte.

## Hashes de artefactos inspeccionados localmente

| Archivo local | Tipo observado | SHA-256 |
|---|---|---|
| `slopos-ps4-1302.h` | C source/header | `34a206ffa48a406f6d15879b40e941de5e9d0db094bfd2d0932a6cf58961066a` |
| `ps4-linux-loader-1302.h` | C source/header | `99f31669ec1f576b1c10558e5642213faea25ab6173e72fade4373382e7d71cb` |
| `sdk-crt-kernel.c` | C source | `d80175cad703f6e7249f4f35b50c0c60134acef9ea861bb1af2c6b3f271a42a3` |
| `adri/hen.bin` | Payload DOS/COM-like según `file` | `f29bd1f0ac5cc1edef6ebccb735ef6c4dff702711cc3b9f465e66fd03dd707ce` |
| `adri/scanner_1304.iso` | UDF filesystem image | `6ed15acd9cfb2539e034cde72a9003f52cf6338f04549670e1b8d515d948bd30` |

Estos hashes identifican los artefactos descargados; no son hashes de kernels Orbis.

## Respuesta a las preguntas operativas

**¿Se encontró un kernel Orbis 13.02 real?** No. No se encontró un dump, binario retail/debug descifrado, ELF, `kernel.bin`, `system_fs_image` con kernel, reconstrucción o disassembly verificable.

**¿Cuál es el artefacto más cercano?** `AetherPS/Fusion` `Shared/Offsets-1302.h`, seguido por SLOPOS `ps4/1302.h` y el header equivalente de `ps4-linux-loader`. Todos son tablas de offsets o infraestructura, no bytes de kernel.

**¿Permiten localizar `ffs_mountfs()` o `ffs_reload()`?** No. Ninguno contiene código, bytes de instrucciones, referencias cruzadas o una dirección atribuida a esas funciones.

**¿Qué prueba existe de Celsius en esos artefactos?** Sólo documentación y código FreeBSD upstream reproducible. No existe correspondencia demostrada entre el código FreeBSD vulnerable y bytes/pseudocódigo de Orbis 13.02.

**¿Qué artefacto cerraría la incertidumbre?** Un kernel Orbis 13.02 retail legítimo con SHA-256 verificable y su disassembly, o un dump/pseudocódigo de `ffs_mountfs()`/`ffs_reload()` que exponga las lecturas de `fs_cssize`, `fs_contigsumsize`, `fs_ncg`, `fs_bsize`, `fs_fsize`, los tipos y los cálculos antes de `malloc`. Para establecer un parche, se necesitaría el mismo artefacto funcional de 13.50 y un diff reproducible de la función.

## Referencias

[1]: https://github.com/AetherPS/Fusion "AetherPS/Fusion"
[2]: https://github.com/AetherPS/Fusion/commit/1d7c0314ade52858496195e53bcc85de274def51 "Fusion commit 1d7c031: 13.02 Kernel offsets"
[3]: https://github.com/alferdoss/SLOPOS-offsets "SLOPOS-offsets"
[4]: https://github.com/ps4-linux/ps4-linux-loader "ps4-linux/ps4-linux-loader"
[5]: https://github.com/ps4-payload-dev/sdk "ps4-payload-dev/sdk"
[6]: https://github.com/Al-Azif/vue-after-free "Al-Azif/vue-after-free"
[7]: https://github.com/adri22235/ps4-suid-scanner "adri22235/ps4-suid-scanner"
[8]: https://github.com/OpenOrbis/OpenOrbis-PS4-Toolchain "OpenOrbis PS4 Toolchain"
[9]: https://github.com/OpenOrbis/mira-project "OpenOrbis/mira-project"
[10]: https://github.com/TheOfficialFloW/PPPwn "TheOfficialFloW/PPPwn"
[11]: https://github.com/Pharaoh2k "Pharaoh2k GitHub profile"
[12]: https://www.psdevwiki.com/ps4/Kernel "PS4 Developer wiki: Kernel"
[13]: https://www.psdevwiki.com/ps4/Vulnerabilities "PS4 Developer wiki: Vulnerabilities"
[14]: https://github.com/AetherPS/Fusion/releases "Fusion releases"
[15]: https://github.com/Al-Azif/ps4-exploit-host "Al-Azif PS4 exploit host"
[16]: https://github.com/Al-Azif/dumper-testing "Al-Azif dumper-testing"
[17]: https://github.com/Al-Azif/ps4-re-utilities "Al-Azif ps4-re-utilities"
[18]: https://github.com/Al-Azif/ps4-payload-sdk "Al-Azif ps4-payload-sdk"
[19]: https://github.com/Al-Azif/psfree-lapse "Al-Azif psfree-lapse"
