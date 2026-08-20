# Ejecución real de WPE WebKit 2.52.6

## Alcance

Esta ejecución utilizó exclusivamente el paquete binario público Arch Linux `wpewebkit 2.52.6-1` x86_64 y su userspace Arch aislado. No se ejecutó CMake/Ninja, no se tocó `/tmp/wpewebkit-2.52.6-build`, y no se utilizaron resultados GTK ni WPE 2.53.1 para declarar capacidades de 2.52.6.

## Identidad verificada

| Elemento | Resultado |
|---|---|
| MiniBrowser | ELF x86-64, Build ID `55f35b0dcddb3ed1733fb5e28f5d4ebe6b652aba` |
| MiniBrowser SHA-256 | `a2c569e96a4e00a61b849eba6f4c592c43a4071767cc63d39effada41eca1d37` |
| WPEWebDriver | ELF x86-64, Build ID `3fb7e9b322fde2d7dc4626cf634faeead30c28a2` |
| libWPEWebKit | `libWPEWebKit-2.0.so.1.9.10`, Build ID `40d28b84c551f2f8d6aa3b3272a63d599d84c1c0` |
| glibc userspace | Arch glibc 2.44 |
| Fixtures | page1/page2/page3 hashes coinciden con `fixture-manifest.json` |

## Pruebas realizadas

`MiniBrowser --help` terminó con **PASS** y confirmó `--headless`, `--automation` y `--use-legacy-api`. `WPEWebDriver --status` terminó con **PASS** y devolvió `{"ready":true,"message":"No sessions"}`. La inspección ELF/loader también terminó con **PASS** dentro del chroot.

El arranque headless directo con el sandbox original terminó **BLOCKED** por:

```text
bwrap: Failed to make / slave: Invalid argument
Connection: failed to receive credentials: Expecting to read a single byte for receiving credentials but read zero bytes
```

La prueba directa del host Ubuntu, fuera del chroot, terminó **BLOCKED** porque el paquete requiere símbolos/glibc más nuevos. La salida observada por el runner fue `GLIBC_PRIVATE`/glibc incompatible; por eso el paquete nunca se ejecutó directamente contra las bibliotecas Ubuntu.

Se verificó el kernel del sandbox: los user namespaces no están disponibles para bubblewrap (`No permissions to create a new namespace`). Como experimento reversible únicamente dentro del chroot, se sustituyó temporalmente `bwrap` por un wrapper que conserva el binario original como `bwrap.real` y ejecuta el proceso final sin namespaces. El wrapper corrigió el error inmediato de `bwrap`, pero el proceso WPE quedó esperando y la sesión WebDriver no completó el handshake dentro del timeout. El stream real de argumentos de bubblewrap muestra que WPE solicita, entre otros, `--unshare-pid`, `--unshare-net`, `/proc`, `/dev`, `/tmp`, `/etc`, `/sys` y un seccomp descriptor; por tanto, un no-op wrapper no constituye una ejecución equivalente ni se considera PASS.

También se probó `--use-legacy-api`; terminó **BLOCKED** por el mismo mecanismo de sandbox original. No se siguieron repitiendo variantes idénticas.

## Ejecución de runners

| Runner | Estado | Evidencia |
|---|---|---|
| `diagnose_wpe_minibrowser.py` | **PASS parcial** | ELF, loader y bibliotecas presentes; ejecución directa fuera del chroot bloqueada por glibc |
| `run_wpe_headless.py` | **BLOCKED** | El runner host no puede cargar el loader Arch; salida sin assertions |
| `compare_wpe_smoke.py` | **NOT_RUN/BLOCKED** | No recibió assertions WPE reales |
| `render_wpe_report.py` | **PASS** | Generó el informe basado únicamente en el JSON real, marcando capacidades como no ejecutadas |
| page1→page2→page3 | **BLOCKED** | No se creó sesión WebDriver funcional |
| DOM/CSS/Flex/Grid/JS/eventos/forms/SVG/imagen/Canvas/storage/navegación/historial | **NOT_RUN** | No hay assertions del engine 2.52.6 |

JSON del runner headless: `385e8bc8b80593bbff5c448f3043a20b0ef20a988ae61d9ed5422cc140f6c50a`.

## Conclusión

El engine WPE 2.52.6 y MiniBrowser están disponibles y verificados como binarios correctos. El bloqueo restante está fuera del engine: el sandbox actual no permite user namespaces y bubblewrap necesita esa capacidad para crear el entorno de procesos WPE. El shim sin namespaces no es suficiente porque no reproduce los mounts, seccomp, PID/network namespaces ni handshake esperado.

El siguiente paso mínimo es ejecutar el mismo chroot en una VM/host Linux que permita `CLONE_NEWUSER`, `CLONE_NEWPID`, `CLONE_NEWNET` y las operaciones de mount requeridas por bubblewrap. No es necesario reconstruir WebKit.

Estados obligatorios:

```text
WPE_2526_ARTIFACT       = PASS
WPE_2526_ELF_LOADER     = PASS
WPE_2526_WEBDRIVER_BASE = PASS
WPE_2526_MINIBROWSER    = BLOCKED_RUNTIME_SANDBOX
WPE_2526_HTML_SMOKE     = NOT_RUN
WPE_2526_CAPABILITIES   = NOT_RUN
WPE_2531_REFERENCE      = SEPARATE
```
