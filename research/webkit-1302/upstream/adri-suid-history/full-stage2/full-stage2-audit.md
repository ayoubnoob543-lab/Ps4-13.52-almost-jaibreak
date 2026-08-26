# Auditoría del supuesto “full stage 2” de `ps4-suid-scanner`

**Fecha de corte:** 26 de agosto de 2026.
**Método:** análisis Git, búsqueda de copias públicas y lectura estática. No se ejecutó JavaScript, exploit, payload ni cadena de corrupción.

## Conclusión

El supuesto commit sí existe como objeto Git público. Su SHA es `1089382ec1e0000e9557b7748d39b57952bbc4f3`, fue creado el 9 de agosto de 2026 a las 00:35:29 UTC por Adrián García Casado y tiene como único padre `96a79482d249fdbc6101bc641241488de66c313d`. Su mensaje es:

> Replace skeleton with full stage 2: persistent r/w + ROP for 13.04

El commit elimina `stage2_jordy.js` de 194 líneas y añade `jordy_stage2.js` de 302 líneas. Por tanto, **sí existió una versión posterior al skeleton y su contenido es recuperable**. Sin embargo, el calificativo “full” no corresponde a una implementación completa: el archivo deja sin resolver precisamente los pasos que conectarían la primitive JavaScript con kernel R/W y Celsius.

| Elemento | Resultado | Clasificación |
|---|---|---|
| Existencia del commit 1089382 | Confirmada por API, página GitHub y raw file. | **VERIFIED** |
| Relación padre 96a7948 → 1089382 | Confirmada; el segundo reemplaza el archivo del primero. | **VERIFIED** |
| Archivo posterior de 302 líneas | Recuperado; SHA-256 `e07e8fee72cae298010304349acdd1876a35bf46e9f0e814585ee7f9f9d47528`. | **VERIFIED** |
| “Full stage 2” como implementación funcional | No confirmado; contiene placeholders y TODOs críticos. | **SOURCE_ONLY / MISLEADING TITLE** |
| Primitive JavaScript userland | Helpers presentes, pero dependen de un contexto Jordy externo. | **SOURCE_ONLY** |
| Kernel R/W | No implementado ni demostrado. | **INVALID como prueba funcional** |
| Mount UFS/FFS y Celsius | Sólo comentarios; no hay llamada implementada ni imagen UFS. | **HYPOTHESIS / UNVERIFIED** |
| Copia independiente externa | No encontrada. Los mirrors identificados son copias del mismo commit. | **UNVERIFIED** |

## 1. Linaje Git

El commit padre [`96a79482d249fdbc6101bc641241488de66c313d`](https://github.com/adri22235/ps4-suid-scanner/commit/96a79482d249fdbc6101bc641241488de66c313d) fue creado a las 00:26:47 UTC del mismo día. Su mensaje es “Add stage 2 skeleton: Jordy r/w -> ROP -> Celsius for 13.04” y añade `stage2_jordy.js` con 194 líneas.

El commit hijo [`1089382ec1e0000e9557b7748d39b57952bbc4f3`](https://github.com/adri22235/ps4-suid-scanner/commit/1089382ec1e0000e9557b7748d39b57952bbc4f3) fue creado ocho minutos después. Su diff es estructuralmente claro: elimina el skeleton y añade un archivo de nombre distinto, `jordy_stage2.js`, con 302 líneas. No es un commit fantasma ni únicamente un mensaje sin objeto asociado.

La referencia `refs/heads/main` apunta actualmente a `1089382ec1e0000e9557b7748d39b57952bbc4f3`. El tag `v2.0`, en cambio, apunta al commit `3fd35a4e475698b59dae40794901a56126a38c52`, de 29 de julio de 2026, cuyo único cambio visible es un asset `hen.bin` y cuyo árbol no contiene `jordy_stage2.js` ni `stage2_jordy.js`. Por ello, `v2.0` no es una versión posterior del stage 2.

| Ref/commit | Fecha | Contenido | Relación |
|---|---:|---|---|
| `96a7948` | 2026-08-09 00:26 | `stage2_jordy.js`, skeleton de 194 líneas. | Padre |
| `1089382` | 2026-08-09 00:35 | `jordy_stage2.js`, 302 líneas. | Commit investigado |
| `main` | Actual | Apunta a `1089382`. | Ref activa |
| `v2.0` → `3fd35a4` | 2026-07-29 | `hen.bin` y archivos del scanner. | Rama/tag separado; no contiene stage 2 |

## 2. Comparación estática del archivo posterior

### Primitive de lectura/escritura

El archivo posterior contiene `setVector()`, `read8`, `read16`, `read32`, `read64`, `write8`, `write32` y `write64`. Estas funciones redirigen el `m_vector` de un `Uint8Array` supuesto mediante `g_candidate`, `g_scratchBytes` y `g_scratchWords`. La implementación no crea el bug de WebKit ni demuestra que esos objetos existan en el contexto real: los recibe como argumentos desde una integración Jordy que no está incluida en el commit.

La presencia de estos helpers acredita que el autor escribió una capa de acceso de memoria JavaScript prevista para una primitive previa. No acredita kernel R/W. Para que llegara al kernel, todavía tendría que existir una vulnerabilidad userland/kernel separada y una demostración de que la dirección pasada a `setVector()` puede apuntar fuera del proceso.

### Base de WebKit

`findWebkitBase()` lee un supuesto vtable desde `targetAddress`, pero no conoce el offset del vtable de `JSC::JSUint8Array`. El código conserva literalmente:

> `TODO: Determine JSUint8Array vtable offset for 13.04`

y termina con:

> `return 0; // placeholder`

Además, `targetAddress` no está definido en el archivo original; se presupone que Jordy lo proporcionará. La función no devuelve una base válida para 13.04.

### Base de libkernel

`findLibkernelBase()` menciona una entrada GOT aproximada para `pthread_create` en `webkit_base + 0x3ce1000`, pero no proporciona el slot exacto, el símbolo/NID verificado ni una lectura efectiva. Termina con:

> `TODO: Find exact GOT offset`
> `return 0; // placeholder`

La base de libkernel no se puede obtener desde este código.

### ROP y `dlsym`

`buildRopChain()` crea un array y añade algunos gadgets WebKit 13.04. Pero la entrada para `sceKernelDlsym` usa valor cero como dirección del string y no contiene una dirección de llamada a `dlsym`:

> `p(G.POP_RSI_RET); v(0); // TODO: string address`
> `// TODO: dlsym address`

La cadena no contiene una llamada materializada a `mount`, una dirección de función, una ruta de montaje ni una estructura de argumentos completa.

### Mount UFS/FFS y Celsius

La referencia central aparece sólo en comentarios:

> `// call mount → triggers ffs_mountfs → Celsius`

El archivo no construye la imagen UFS malformada, no define el mount point, no resuelve `mount`, no prepara flags válidos, no muestra los campos de `struct fs` y no aporta dirección o bytes de `ffs_mountfs()`. Por tanto, no hay nueva evidencia técnica que relacione un offset 13.02 con la función FFS.

### ROP pivot y kernel R/W

`executeRop()` describe una estrategia basada en una página JIT y una callback, pero no escribe una cadena en memoria ni redirige control. Termina registrando:

> `TODO: Implement execution pivot`

`stage2_run()` llama primero a `findWebkitBase()`. Como esa función devuelve cero, la ejecución entra en la rama de error, imprime bytes de diagnóstico, restaura el estado y retorna. Así, el flujo normal del archivo no alcanza siquiera la construcción efectiva de una cadena ROP.

## 3. Diferencias respecto al skeleton

El commit 1089382 aporta más detalle de diseño y convierte el nombre del archivo, pero no elimina las incertidumbres fundamentales del skeleton. Las diferencias principales son la adición de helpers `read16/read64/write8/write32/write64`, una conversión parcial a 64 bits mediante enteros JavaScript, gadgets nominales, cinco constantes de kernel y una organización en cinco pasos. No se observa una implementación completa de ninguno de estos componentes decisivos: resolución de bases, `dlsym`, llamada a `mount`, pivot o parche de kernel.

| Componente | Skeleton 96a7948 | “Full” 1089382 | Evaluación |
|---|---|---|---|
| Helpers R/W | Parciales/esquemáticos. | Más completos, con read/write de varios tamaños. | Aumento de código, no prueba de alcance. |
| Base WebKit | Placeholder. | Sigue siendo `return 0`. | No implementada. |
| Base libkernel | Placeholder. | Sigue siendo `return 0`. | No implementada. |
| Gadgets ROP | Declarativos. | Más gadgets declarativos. | No basta para ejecutar ROP. |
| `dlsym` | No resuelto. | String y dirección siguen TODO. | No implementado. |
| Mount UFS/FFS | Conceptual. | Sigue siendo comentario. | No implementado. |
| ROP pivot | Conceptual. | Sigue siendo TODO. | No implementado. |
| Kernel R/W | Afirmado en comentarios. | Afirmado en comentarios. | No demostrado. |

## 4. Forks, mirrors y copias

La enumeración pública de forks devuelve cuatro repositorios asociados. Tres contienen una copia de `jordy_stage2.js`: el repositorio original, `ayoubnoob543-lab/ps4-suid-scanner` y `ke5adb/ps4-suid-scanner`. Los tres archivos tienen el mismo SHA-256 `e07e8fee72cae298010304349acdd1876a35bf46e9f0e814585ee7f9f9d47528` y el mismo commit histórico `1089382` en su historial del archivo. No son fuentes independientes.

`kishan9601743105-oss/ps4-suid-scanner` y `OptiTronOffical/ps4-suid-scanner` contienen los archivos del scanner, offsets y gadgets, pero no `jordy_stage2.js` ni `stage2_jordy.js` en el árbol auditado. No se encontró allí una implementación alternativa del stage 2.

El resultado de búsqueda de código de GitHub para la cadena distintiva `TODO: Implement execution pivot` devuelve sólo el repositorio original. La búsqueda de `filename:jordy_stage2.js` devuelve el original y la copia de `firmware-lab`; esta última es un artefacto generado en el commit `0d6221d3d9cb1009d1383a36445e26d6faa502bd` de la propia investigación, no un mirror histórico externo. Su versión usa BigInt y añade mensajes explícitos de “INCOMPLETE”; debe clasificarse como **DERIVED/LOCAL RESEARCH ARTIFACT**.

## 5. Wayback, cachés y referencias externas

Las consultas CDX de Wayback para `github.com/adri22235/ps4-suid-scanner/*` y para las rutas raw de `jordy_stage2.js` devolvieron arrays vacíos en la consulta realizada. No se encontró un snapshot anterior o alternativo en Wayback.

Las búsquedas exactas del SHA, del mensaje “Replace skeleton with full stage 2” y del nombre `jordy_stage2.js` sólo devolvieron el repositorio de GitHub y sus copias. No apareció una publicación independiente en Reddit, blog, X, Discord indexado o mirror que contuviera una variante técnica del archivo.

La ausencia de resultados no prueba que nunca existiera una copia privada, borrada o no indexada. Sólo establece que no se localizó una copia pública independiente en las fuentes consultadas.

## 6. ¿Contiene información nueva sobre Celsius/13.02?

Sí contiene información nueva sobre la **intención de integración**: el autor pretendía mantener viva la primitive `m_vector`, resolver bases WebKit/libkernel, construir ROP, llamar a `mount` con una imagen UFS malformada y, después, modificar `PRISON0`/`ROOTVNODE`. También confirma que se reutilizan valores de kernel 13.04 como `PRISON0 = 0x0111FA18`, `ROOTVNODE = 0x02136E90`, `ALLPROC = 0x01B28538` y `SYSENT = 0x01102B70`.

No contiene información nueva verificable sobre la implementación de `ffs_mountfs()` en Orbis. No aporta offset de `ffs_mountfs`, bytes, firma, pseudocódigo, `struct fs` de Sony, imagen UFS, primitive de kernel, log de hardware ni comparación 13.02→13.04/13.50. Los offsets que aparecen son generales y no resuelven la procedencia material de Celsius.

## 7. Veredicto final

El “full stage 2” **sí existió como commit y archivo**, por lo que la conclusión anterior de que el SHA era simplemente inaccesible debe corregirse. La evidencia correcta es que GitHub conserva el objeto y su contenido.

Pero el archivo no es una implementación completa. Es una especificación parcialmente codificada de una cadena futura: la primitive userland se asume, la base WebKit no se resuelve, la base libkernel no se resuelve, `dlsym` no se resuelve, `mount` sólo aparece en comentarios, la imagen UFS no existe en el archivo, el pivot ROP no está implementado y el flujo aborta antes de ejecutar la cadena.

En consecuencia, el commit no demuestra Celsius, no demuestra que `ffs_mountfs()` vulnerable exista en Orbis 13.02 y no demuestra kernel R/W en 13.02. Su valor probatorio es **VERIFIED como evidencia de intención de desarrollo y de arquitectura propuesta**, pero **INVALID como PoC funcional**.

La pieza que seguiría faltando es un commit o artefacto que reemplace los TODOs con direcciones y lógica verificables, acompañado de un contexto Jordy completo y una prueba estática reproducible. Para confirmar Celsius específicamente, además haría falta el código/bytes de la ruta Orbis `mount → UFS/FFS → ffs_mountfs`, o un log de hardware que demuestre que la imagen UFS alcanza la corrupción y entrega una primitive fuera del proceso.

## Referencias

[1]: https://github.com/adri22235/ps4-suid-scanner/commit/1089382ec1e0000e9557b7748d39b57952bbc4f3 "Commit 1089382: Replace skeleton with full stage 2"

[2]: https://github.com/adri22235/ps4-suid-scanner/commit/96a79482d249fdbc6101bc641241488de66c313d "Commit padre 96a7948: stage 2 skeleton"

[3]: https://raw.githubusercontent.com/adri22235/ps4-suid-scanner/1089382ec1e0000e9557b7748d39b57952bbc4f3/jordy_stage2.js "Archivo raw jordy_stage2.js del commit 1089382"

[4]: https://github.com/adri22235/ps4-suid-scanner/releases/tag/v2.0 "Tag v2.0"

[5]: https://github.com/adri22235/ps4-suid-scanner/network/members "Forks públicos del repositorio"

[6]: https://github.com/ayoubnoob543-lab/firmware-lab/blob/0d6221d3d9cb1009d1383a36445e26d6faa502bd/jordy_stage2.js "Variante local derivada en firmware-lab"

[7]: https://web.archive.org/ "Wayback Machine, consulta CDX sin snapshots relevantes"
