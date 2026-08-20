# Estado final reproducible WebKit/WPE

**Fecha:** 2026-08-20
**Repositorio:** `ayoubnoob543-lab/firmware-lab`
**Rama:** `webkit-ps4-1352-kit`
**Commit inspeccionado:** `4164b868248cabb813f3866f6fa20f8b03e7925f`

## Material privado recuperado

Se descargaron selectivamente únicamente los materiales bajo `webkit-kit` necesarios para este trabajo: `WPE_HOST_BUILD_STATUS.md`, `README_CONTINUIDAD_WEBKIT.md`, `WEBKITGTK_CAPABILITY_MATRIX.md`, `sources.lock.json`, hashes, scripts host y los tres fixtures HTML privados.

| Fixture | SHA-256 |
|---|---|
| `homebrew/fixtures/page1.html` | `3854930be7753028e3800233758f7015f5f2be590fe3663f0fb61ab035f36e7b` |
| `homebrew/fixtures/page2.html` | `66b593648c6cec245b505cad043d75a2c2c32d9c2ef0092b203fa17f500dd399` |
| `homebrew/fixtures/page3.html` | `5993bffdc8ff066c281f6786088abae42fd3e6900ee6c3cc86804774bd84ee87` |

El archivo privado `homebrew/build/host/smoke-output.txt` describe un harness seguro/stub con gráficos no disponibles. No se utilizó ni se presenta como resultado WPE.

## Fuentes y configuración

| Componente | Versión | SHA-256 | Estado documentado |
|---|---:|---|---|
| WPE WebKit | 2.52.6 | `b2bafef2751625b7fdf530f230ff0f542ff0eeba3590c3a989d931b2a55c858e` | fuente configurada |
| libwpe | 1.16.3 | `c880fa8d607b2aa6eadde7d6d6302b1396ebc38368fe2332fa20e193c7ee1420` | PASS |
| WPEBackend-fdo | 1.16.1 | `544ae14012f8e7e426b8cb522eb0aaaac831ad7c35601d1cf31d37670e0ebb3b` | PASS |

El build reutilizado fue `/tmp/wpewebkit-2.52.6-build`. La configuración final de bajo consumo fue `PORT=WPE`, `ENABLE_MINIBROWSER=ON`, `ENABLE_UNIFIED_BUILDS=OFF`, `ENABLE_WEBASSEMBLY=OFF`, `ENABLE_JIT=OFF` y `USE_GSTREAMER=OFF`. No se modificó el código fuente del engine.

## Comandos ejecutados

```sh
gh repo clone ayoubnoob543-lab/firmware-lab /home/ubuntu/wpe-private-repo \
  -- --branch webkit-ps4-1352-kit --filter=blob:none --no-checkout

git sparse-checkout set --stdin
cmake -S /tmp/wpe-sources/wpewebkit-2.52.6 \
  -B /tmp/wpewebkit-2.52.6-build -G Ninja \
  -DENABLE_WEBASSEMBLY=OFF -DENABLE_JIT=OFF
ninja -C /tmp/wpewebkit-2.52.6-build -j2 MiniBrowser
```

También se probó `-j1` en el mismo árbol. Todos los intentos conservaron las fuentes y los objetos existentes; no se inició una compilación limpia desde cero.

## Resultado de build

`libwpe` 1.16.3 y WPEBackend-fdo 1.16.1 permanecen documentados como compilados correctamente. La configuración CMake WPE terminó correctamente. Sin embargo, no se generaron las bibliotecas finales de WPE WebKit ni `MiniBrowser`.

El bloqueo final reproducible ocurrió durante la compilación de JavaScriptCore con `-j2`, en `Source/JavaScriptCore/bytecompiler/BytecodeGenerator.cpp`: `cc1plus` terminó externamente y dejó mensajes de assembler truncado, incluyendo `open CFI at the end of file; missing .cfi_endproc directive`. El mensaje terminal de Ninja fue:

```text
c++: fatal error: Terminated signal terminated program cc1plus
ninja: build stopped: subcommand failed.
```

El mismo patrón de terminación externa se observó previamente en `DFGSpeculativeJIT.cpp`, `UnifiedSource` de WebCore y unidades Wasm. No apareció un error semántico confirmado del código fuente. En el último estado no existe ningún archivo `MiniBrowser` ni biblioteca `libWPEWebKit*.so*` enlazada bajo el build.

## Smoke WPE y comparación

El smoke WPE **no se ejecutó** porque no existe un ejecutable WPE WebKit enlazado. Por tanto, no se presentan resultados WPE para DOM, CSS/Flexbox/Grid, JavaScript, eventos, formularios, SVG, imágenes, Canvas, localStorage o navegación.

| Capacidad | Baseline WebKitGTK privado | WPE 2.52.6 |
|---|---|---|
| DOM | PASS documentado | NOT_TESTED: MiniBrowser no enlazado |
| CSS/Flexbox/Grid | PASS documentado | NOT_TESTED: MiniBrowser no enlazado |
| JavaScript | PASS documentado | NOT_TESTED: MiniBrowser no enlazado |
| Eventos y formularios | PASS documentado | NOT_TESTED: MiniBrowser no enlazado |
| SVG, imágenes y Canvas | PASS documentado | NOT_TESTED: MiniBrowser no enlazado |
| localStorage | PASS documentado | NOT_TESTED: MiniBrowser no enlazado |
| Navegación page1→page2→page3 | PASS documentado | NOT_TESTED: MiniBrowser no enlazado |

## Validaciones y restricciones

`git diff --check` no reportó errores en el checkout privado. Los hashes de los tres fixtures fueron registrados arriba. No se usaron Sony SDK, módulos SPRX, JSCBRIDGE, offsets, exploits, payloads, ROP/JOP ni ABI privada. No se afirmó compatibilidad con hardware Sony ni con módulos retail.

> **Veredicto:** WPE WebKit 2.52.6 quedó configurado correctamente y sus dependencias públicas libwpe/WPEBackend-fdo están documentadas como PASS, pero MiniBrowser y las bibliotecas finales no pudieron enlazarse en este host por terminaciones externas de `cc1plus` asociadas a límites de recursos/ejecución. El smoke HTML WPE queda `NOT_RUN`; el baseline GTK no se reutiliza como resultado WPE.

## Actualización de esta sesión: estrategia incremental de bajo consumo

Se inspeccionó el checkout privado en la rama `webkit-ps4-1352-kit` y se conservaron `/tmp/wpewebkit-2.52.6-build` y todos sus objetos. El host reportó 6 CPU lógicas, 3,8 GiB de RAM, 2 GiB de swap sin uso y aproximadamente 30 GiB libres en `/tmp`; los límites de memoria y tiempo del proceso eran `unlimited`.

La configuración efectiva inspeccionada fue `PORT=WPE`, `ENABLE_MINIBROWSER=ON`, `ENABLE_UNIFIED_BUILDS=OFF`, `ENABLE_WEBASSEMBLY=OFF`, `ENABLE_JIT=OFF`, `USE_GSTREAMER=OFF`, Release con GCC 13 y `-O3 -DNDEBUG` para las reglas normales. El dry-run de Ninja mostró 8.167 unidades pendientes en este árbol reconfigurado; el target final previsto es la biblioteca `libWPEWebKit-2.0.so.1.9.10`, los procesos WPE y `bin/MiniBrowser`.

El último fallo normal ocurrió en `Source/JavaScriptCore/bytecompiler/BytecodeGenerator.cpp`: `cc1plus` terminó externamente y el assembler dejó `open CFI at the end of file; missing .cfi_endproc directive`. No apareció un error semántico confirmado del código fuente.

Se probaron flags mínimos únicamente para esa unidad. La compilación manual con parsing exacto de la orden Ninja, `-O0 -g0 -fno-inline-functions -fno-unroll-loops -fno-ipa-cp` y `-DRELEASE_WITHOUT_OPTIMIZATIONS` produjo un objeto ELF relocatable válido de 7.267.224 bytes y un depfile de 88.625 bytes. Ninja todavía lo marca como pendiente porque los metadatos de dependencias muestran muchos objetos más antiguos que el `cmakeconfig.h` generado en la reconfiguración; no se falsificaron timestamps ni se eliminaron `.ninja_deps`, ya que eso podría reutilizar objetos incompatibles.

No se generó aún `bin/MiniBrowser` ni ninguna biblioteca final WPE WebKit. En consecuencia:

```text
WPE_MINIBROWSER_BUILD = BLOCKED
WPE_RUNTIME = BLOCKED
WPE_HTML_SMOKE = NOT_RUN
```

El bloqueo restante es completar de forma segura las unidades invalidadas del árbol reconfigurado y enlazar la biblioteca final; el smoke page1→page2→page3 no se ejecutó porque no existe un ejecutable WPE verificable. El baseline WebKitGTK no se presenta como resultado WPE.

## Cierre de la iteración incremental

Tras reparar el depfile de `BytecodeGenerator.cpp`, el build serial avanzó hasta `157/7003` con las reglas originales y volvió a fallar en `WebGLRenderingContextBase.cpp` por terminación externa de `cc1plus` durante el ensamblado (`bad register name %rc`, `open CFI ... missing .cfi_endproc`), consistente con presión de recursos y no con diagnóstico semántico.

La unidad `WebGLRenderingContextBase.cpp` también fue compilada manualmente con la orden Ninja exacta, `-O0 -g0`, flags de reducción de consumo y `-DRELEASE_WITHOUT_OPTIMIZATIONS`; el resultado fue un ELF relocatable válido de 6.691.672 bytes con depfile de 167.287 bytes. Sin embargo, Ninja no almacena sus dependencias hasta ejecutar la regla, por lo que no fue posible marcarla como realizada sin recompilarla bajo la regla estándar.

Se probó una mitigación global reversible sustituyendo temporalmente `-O3` por `-O0` en `build.ninja`; se restauró inmediatamente tras comprobar que WebKit exige además `-DRELEASE_WITHOUT_OPTIMIZATIONS` en todas las unidades Release. Esa variante no produjo artefactos finales y no se conserva como configuración activa. No se hizo clean ni se borraron objetos.

Estado final reproducible de esta iteración:

```text
WPE_MINIBROWSER_BUILD = BLOCKED
WPE_RUNTIME = BLOCKED
WPE_HTML_SMOKE = NOT_RUN
```

Bloqueo exacto: el host de 3,8 GiB RAM/2 GiB swap no puede completar de forma fiable las unidades C++ pesadas con las reglas Release actuales; el intento normal termina en el ensamblador, y la compilación global `-O0` requiere una reconfiguración coherente con `RELEASE_WITHOUT_OPTIMIZATIONS` que invalidaría gran parte del árbol. No existe `bin/MiniBrowser` ni biblioteca final `libWPEWebKit-2.0.so` verificable, por lo que no se afirma ningún resultado WPE ni se ejecuta el smoke HTML.
