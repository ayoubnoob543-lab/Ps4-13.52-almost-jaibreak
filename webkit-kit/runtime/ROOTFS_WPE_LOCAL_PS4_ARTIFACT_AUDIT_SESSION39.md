# Auditoría local del entorno WPE/rootfs frente a artefactos PS4 13.52

## Alcance y método

Se inspeccionaron en modo sólo lectura:

```text
/home/ubuntu/wpe-artifacts-2526/arch/rootfs
/home/ubuntu/wpe-artifacts-2526/db-extract
```

Se registraron nombres, rutas, tamaños, permisos, UID/GID, fechas de modificación, enlaces simbólicos, tipos mediante `file`, SHA-256 de archivos legibles y strings de texto relevantes. Se consultaron los montajes sin desmontarlos. Los montajes dinámicos `proc`, `sys`, `dev` y `run` bajo el rootfs se excluyeron del inventario de archivos persistentes, pero se conservaron como información de montaje.

No se ejecutó ningún binario del rootfs, no se ejecutaron exploits/PoC/payloads y no se interactuó con hardware.

## Cantidad de material

| Árbol | Archivos regulares | Bytes | Symlinks |
|---|---:|---:|---:|
| `arch/rootfs` | 37.277 | 1.441.490.154 | 9.230 |
| `db-extract` | 14.910 | 17.471.073 | 0 |

El inventario completo reproducible se generó fuera del repositorio como `/home/ubuntu/rootfs_local_audit_manifest.json`. El script utilizado fue `/home/ubuntu/rootfs_local_audit.py`; ambos son auxiliares locales y no constituyen artefactos PS4.

## Artefactos WPE/Linux confirmados

El rootfs contiene un paquete WPE WebKit `2.52.6-1` y binarios ELF Linux x86-64. Ejemplos relevantes:

| Ruta | Tamaño | SHA-256 | Tipo/Build ID |
|---|---:|---|---|
| `usr/lib/libWPEWebKit-2.0.so.1.9.10` | 133.528.480 B | registrado en el manifest local | ELF shared object WPE; contiene rutas `/usr/src/debug/wpewebkit/wpewebkit-2.52.6` |
| `usr/lib/wpe-webkit-2.0/MiniBrowser` | 2.534.112 B | `a2c569e96a4e00a61b849eba6f4c592c43a4071767cc63d39effada41eca1d37` | ELF64 PIE x86-64; Build ID `55f35b0dcddb3ed1733fb5e28f5d4ebe6b652aba` |
| `usr/lib/wpe-webkit-2.0/WPEWebProcess` | 4.544 B | `163fae04346ee415b7812d52fa13066f18553e5d03aa861f019fcbd1ac33421d` | ELF64 PIE x86-64; Build ID `f11258799e2454959d692f2cd6a22bc43e27b087` |
| `usr/lib/libWPEBackend-fdo-1.0.so.1.10.2` | 88.632 B | `6dfb7b1943569e9bb650d49ddfddb7d97ebddf3be0f6034752b002a92c6b9995` | ELF64 x86-64; Build ID `a5010358baacc73b70bd4b05c9b3e783396309e2` |
| `usr/lib/libwpe-1.0.so.1.9.6` | 47.152 B | `e0c42f2405d63bc05c8b59bc63f3ba0469c56e2d37e5ecf6c3256746859f44b8` | ELF64 x86-64; Build ID `ef1373a302253ddaa4acb0c9ee58752c03dd7c7a` |
| `var/cache/pacman/pkg/wpewebkit-2.52.6-1-x86_64.pkg.tar.zst` | 38.898.907 B | `99f09e0a1e62069d1715ee9840d18202b07c4fcdbe5c6ba79b178cb93cf59faf` | Zstandard package |
| `var/lib/pacman/local/wpewebkit-2.52.6-1/desc` | metadata | `2d7ca9a312f7d8f75fafc6e55a483ee03b27d043f53f1a38a23bdf0d7ca3d81d` | package `wpewebkit`, version `2.52.6-1` |

Los enlaces `libWPEWebKit-2.0.so.1` y similares son symlinks Linux; no se consideran evidencia PS4.

El binario principal contiene rutas de depuración y strings `WPEWebKit`, `MiniBrowser` y `libWPEWebKit-2.0.so.1`, consistentes con WPE WebKit 2.52.6. Es evidencia de laboratorio Linux, no de WebKit retail PS4.

## Búsqueda de nombres y strings PS4/WebKit

Se buscaron las cadenas:

```text
libSceNKWebKit
libkernel_web
JavaScriptCore
WebKit
CSSFontFace
CSSFontFaceSet
FontFaceSet
MarkedVector
SerializedScriptValue
CloneDeserializer
CloneSerializer
JSCell
m_objectPool
m_gcBuffer
13.52
13.50
13.00
WebKit-601-1300
WebKit-616-1300
```

Las coincidencias de `WebKit` y `JavaScriptCore` se concentran en cabeceras públicas WPE, binarios WPE y rutas de depuración `wpewebkit-2.52.6`. No apareció ninguna ruta `libSceNKWebKit`, `libkernel_web`, `sprx`, `SELF`, `PUP`, `system_ex` o `orbis` atribuible a PS4.

Las coincidencias de texto en `db-extract` corresponden principalmente a nombres de paquetes Linux, descripciones de paquetes y dependencias del rootfs. Los nombres de paquetes `wpewebkit-2.52.6`, `webkit2gtk-4.1-2.52.6` y `webkitgtk-6.0-2.52.6` identifican distribución Linux/WPE, no Sony PS4.

## Montajes y permisos

El rootfs tiene montajes dinámicos de laboratorio para `proc`, `sys`, `dev`, `dev/pts`, `dev/shm`, `dev/hugepages`, `dev/mqueue` y `run`. No se desmontó ninguno.

Se encontró al menos un archivo no legible sin elevar permisos (`etc/.pwd.lock`) y un symlink de pseudo-filesystem no legible (`proc/1/cwd`). No se cambiaron permisos ni se utilizó `sudo`. Estos bloqueos afectan únicamente a partes del inventario dinámico y no constituyen evidencia PS4.

## Correlación con las familias congeladas

El correlador de familias debe apuntar a un árbol fuente concreto, no al workspace completo, porque los informes y JSON contienen literalmente los nombres de las familias y producirían falsos positivos. El entorno auditado contiene headers y binarios WPE 2.52.6, pero no una extracción fuente completa equivalente al árbol Sony retail.

Resultado conceptual de la correlación sobre este entorno:

| Familia | Resultado válido para PS4 13.52 | Motivo |
|---|---|---|
| MarkedVector/GC | `UNVERIFIED` | cualquier código/metadata disponible es WPE/Linux o documentación; no hay procedencia PS4 |
| CloneSerializer/CloneDeserializer/objectPool | `UNVERIFIED` | no hay módulo ni fuente retail PS4; los nombres aislados no bastan |
| CSSFontFace | `UNVERIFIED` | el rootfs contiene WPE 2.52.6, pero no layout Sony 13.52 |

Los strings o rutas de depuración WPE no deben convertirse en `MATCH` de PS4. Un resultado `MATCH` futuro en una fuente WPE sería sólo una coincidencia de familia; `status_13_52` debe seguir siendo `UNVERIFIED`.

## Conclusión

El entorno conserva un rootfs Linux/WPE 2.52.6 real y suficientemente grande para el laboratorio, con binarios ELF x86-64, paquete WPE y Build IDs. No apareció ningún artefacto PS4 WebKit/JSC, ni módulo `libSceNKWebKit`, ni SELF/SPRX, ni snapshot Sony, ni metadata que vincule el contenido con PS4 13.52.

Por tanto, este entorno no permite avanzar en la reconstrucción del runtime real 13.52. Sólo permite usar WPE 2.52.6 como referencia Linux no equivalente. Sigue siendo necesaria una extracción real de PS4 13.52 o un artefacto público Sony con procedencia, ruta, tamaño y SHA-256 verificables.

## Validación

- Inventario recursivo: completado.
- SHA-256 y tipos: completados para archivos legibles.
- `py_compile`: PASS para scripts de auditoría y correlación.
- Tests existentes: 31 PASS, 2 SKIPPED.
- `git diff --check`: PASS.
- Ejecución de binarios: NOT RUN.
- Exploits/PoC/payloads: NOT RUN.
- Hardware: NOT USED.
- Commit/push: no realizados.
