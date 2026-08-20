# Evidencia del bundle oficial WPE MiniBrowser 2.53.1

## Procedencia y versión

El bundle se descargó exclusivamente desde el índice oficial de WPE WebKit:

> [WPE MiniBrowser x86_64 beta bundle](https://wpewebkit.org/built-products/x86_64/release/beta/MiniBrowser/)

El índice oficial no ofrece `MiniBrowser_wpe_2.52.6.tar.xz`. El artefacto más cercano disponible en la consulta fue `MiniBrowser_wpe_2.53.1.tar.xz`; por tanto, **no es WebKit/WPE 2.52.6** y no se presenta como tal.

| Campo | Valor |
|---|---|
| WebKit/WPE del bundle | **2.53.1** |
| Build date | `2026-04-22T13:20:24.859040` |
| Platform | WPE |
| Configuration | Release |
| Architecture | x86-64 |
| Official tarball | `MiniBrowser_wpe_2.53.1.tar.xz` |
| Official SHA-256 | `d25e7f19ca68113de5ec29344889717f3796cabff64ea8b05fd3bcd3ecb3b4f7` |
| Local tarball SHA-256 | `d25e7f19ca68113de5ec29344889717f3796cabff64ea8b05fd3bcd3ecb3b4f7` |
| Official checksum verification | **PASS** |

El tarball y su extracción se conservaron fuera de Git en `/home/ubuntu/wpe-bundles/wpe-minibrowser-2.53.1/` del workspace auxiliar de ejecución. No se versiona el tarball de aproximadamente 187 MiB ni la extracción de aproximadamente 699 MiB, para evitar introducir binarios grandes en el repositorio.

## Contenido y ELF

El README incluido indica que deben ejecutarse los wrappers top-level `MiniBrowser` y `WPEWebDriver`; los binarios de `bin/` no funcionan directamente porque usan un loader relativo empaquetado.

| Artefacto | Identidad |
|---|---|
| Wrapper `MiniBrowser` | ELF x86-64 estático; Build ID `b70059ee279cfd0c6053dcd2287788cbfa1ef0de`; SHA-256 `df9887a903c051a320c22b885e8b839aae2cb3f1e72d00d03a7f1aba61e1ab3e` |
| Wrapper `WPEWebDriver` | ELF x86-64 estático; Build ID `c52de9ca1437ed18d17059c3b5369f077c781cbb`; SHA-256 `90df0903c2dc6bd0efd358fc8e1b3f8fd0c906e3b86000fe98b79c9749737228` |
| Runtime `bin/MiniBrowser` | ELF x86-64 PIE dinámico; loader relativo `lib/ld-linux-x86-64.so.2`; SHA-256 `ed61ddedee2b6480ecfd39caa152974e25744f61fd0b422e5efca35b571a083e` |
| Runtime `bin/WPEWebDriver` | ELF x86-64 PIE dinámico; SHA-256 `6ab9eb5c3703580f692ba1b434fed3e0d0b1d176119dd1d6b61db667b264d38a` |
| WPE engine | `lib/libWPEWebKit-2.0.so.1.10.0`, aproximadamente 150 MiB |
| WPE port/backend | `lib/libwpe-1.0.so.1.9.5`, `lib/libWPEBackend-fdo-1.0.so.1.9.5` |
| Loader | `lib/ld-linux-x86-64.so.2` presente |

Las dependencias directas del runtime incluyen `libWPEWebKit-2.0.so.1`, `libwpe-1.0.so.1`, `libWPEBackend-fdo-1.0.so.1`, Wayland, Epoxy, GLib/GIO, GStreamer y ATK. Con `LD_LIBRARY_PATH`/`--library-path` apuntando a `lib` y `sys/lib`, las dependencias directas se resolvieron sin `not found`.

## Ejecución funcional real

La ejecución se hizo con el protocolo público WebDriver, usando los wrappers oficiales del bundle y argumentos `--automation --headless`. El resultado quedó registrado en JSON; hashes de las salidas de esa ejecución:

| Evidencia | SHA-256 |
|---|---|
| Diagnóstico ELF/bundle | `9cff3a14bde95f4b9eac6a0a18b8d32d1ba7d0d31f52fabe817dd6567eb837c5` |
| Smoke WebDriver directo | `fea3b429891daf349ae3436e3a0ea749a2d06e6839cb011fe80c56d1b8c55fe5` |
| Smoke mediante `run_wpe_smoke.sh` | `fea3b429891daf349ae3436e3a0ea749a2d06e6839cb011fe80c56d1b8c55fe5` |
| Matriz runtime WPE | `ced3446d94e9113f4817f14bcf0aedab0a32c9a77275c17280a8c3b5dab01b2b` |

El smoke cargó realmente `page1.html`, `page2.html` y `page3.html`, con `browserVersion: 2.53.1` y resultado general `PASS`:

| Capacidad | Resultado WPE 2.53.1 |
|---|---|
| DOM | PASS |
| CSS computado | PASS |
| Flexbox | PASS |
| Grid | PASS |
| JavaScript | PASS |
| Eventos | PASS |
| Formularios/validación | PASS |
| SVG | PASS |
| Imágenes | PASS |
| Canvas y lectura de píxel | PASS |
| localStorage | PASS |
| Navegación page1→page2→page3 | PASS |
| Historial | PASS |

La prueba no es un resultado WebKitGTK: el JSON declara `runtime: WPE MiniBrowser WebDriver`, y la matriz marca WPE como resultado autoritativo.

## Diferencia respecto a la build objetivo 2.52.6

La build fuente objetivo del proyecto sigue siendo WPE WebKit **2.52.6**, mientras que el bundle ejecutado es **2.53.1**. El bundle demuestra que una cadena WPE moderna desacoplada de GTK puede ejecutar el contrato HTML en Linux, pero **no demuestra identidad binaria, ABI ni comportamiento exacto de 2.52.6**.

Para usar exactamente 2.52.6 se necesitaría un bundle oficial 2.52.6, un paquete reproducible de esa versión o completar la build local 2.52.6 existente. Los harnesses ya admiten ambos escenarios: el smoke WebDriver registra `browserVersion` desde el driver y la matriz no sustituye la versión observada por una cadena fija.

## Cambios de harness publicados

`run_wpe_webdriver_smoke.py` valida hashes de fixtures, crea la sesión WebDriver, ejecuta los tres documentos y emite PASS por capacidad. `run_wpe_smoke.sh` acepta `--webdriver-driver` y `--webdriver-browser`. `run_runtime_matrix.sh` acepta `WPE_WEBDRIVER` y `WPE_BROWSER`, ejecuta el smoke real y conserva GTK/offscreen como resultados separados. `diagnose_wpe_minibrowser.py` acepta `--bundle-root` para inspeccionar los ejecutables `bin/`, README y loader.

## Límites

El resultado PASS es para el bundle público WPE 2.53.1 sobre Linux x86-64 en host, en modo headless, con el backend FDO incluido. No prueba PS4, OpenOrbis, WebKit 2.52.6 exacto ni un backend no-Linux. No se usaron SDK Sony, módulos SPRX, JSCBRIDGE, exploits, offsets, payloads, ROP/JOP ni ABI privada.
