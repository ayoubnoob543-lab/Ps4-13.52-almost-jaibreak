# Auditoría de `pmap_protect` para PS4 13.52

## Decisión conservadora

`0x58570` es el candidato estructural más fuerte para la entrada de función `pmap_protect`, pero permanece `UNVERIFIED` frente al kernel retail porque no existe un binario 13.52 con bytes correspondientes.

`0x59DF0` también permanece `UNVERIFIED`. Su procedencia es más débil para esta build porque aparece repetido en una tabla multi-firmware sin una medición binaria específica de 13.52.

La evidencia disponible permite ordenar candidatos, no confirmar la dirección. Ningún valor debe marcarse como `DIRECT_BYTES` o `CONFIRMED_1352` hasta inspeccionar el kernel objetivo y demostrar prologue, referencias y mapeo archivo/dirección.

## Fuente primaria de 13.52

Repositorio: <https://github.com/ps4-linux/ps4-linux-loader>

Archivo: `linux/magic.h`

Commit de soporte 13.52: `9acef9f`, mensaje `PS4 13.52 support + edid fix`, autor ArabPixel, 2026-07-25.

El bloque exacto es:

```c
#elif defined PS4_13_52 //ArabPixel from 12.02
#define kern_off_pmap_extract 0x573D0
#define kern_off_pmap_protect 0x58570
#define kern_off_sysent 0x1102b70
#define kern_off_kernel_pmap_store 0x1b2c3a0
```

El mismo bloque define `printf`, `copyin`, `copyout`, `copyinstr` y otras funciones. El valor no es un sitio de parche relativo: `kernel.h` declara `pmap_protect` como puntero a función y `kernel.c` lo resuelve mediante `RESOLVE(pmap_protect)`, lo invoca con `kernel_pmap_store` y escanea los primeros `0x500` bytes de la función para localizar el patrón de parche W^X.

## SLOPOS

Repositorio: <https://github.com/alferdoss/SLOPOS-offsets>

Commit: `42273e2180cae9aa0c1a67332994d75e1baa713c`.

Archivo: `ps4/1352.h`, etiquetado `PS4 13.52 — kexec offsets: ArabPixel`:

```c
#define kern_off_pmap_protect 0x58570
#define kern_off_sysent       0x1102B70
```

SLOPOS documenta que su bloque kexec procede de `ps4-linux/ps4-linux-loader` (`magic.h` y `fw_offsets.h`). Por ello es una segunda publicación coherente con la fuente primaria, aunque comparte esa procedencia.

## Scene-Collective

Repositorio: <https://github.com/Scene-Collective/ps4-hen>

Commit: `2beb4cfcef1d416a32d6fb7b35f01189e9eb62e2`, mensaje `Add 13.52 support`.

`installer/include/offsets.h` define:

```c
#define K1352_PMAP_PROTECT   0x00059DF0
#define K1352_PMAP_PROTECT_P 0x00059E37
#define K1352_PMAP_STORE     0x01B2C3A0
```

El código del installer local usa `K1352_PMAP_PROTECT` como dirección de la función `pmap_protect`, `K1352_PMAP_STORE` como `kernel_pmap_store` y `K1352_PMAP_PROTECT_P` como una entidad distinta usada en el parche. Por tanto, `K1352_PMAP_PROTECT_P` no se sustituye por `0x58570` y permanece en `0x00059E37`.

El historial de Scene muestra que `0x59DF0` fue añadido para 13.52 junto con la tabla de macros, pero el mismo valor ya estaba repetido para 11.50, 11.52, 12.00, 12.02, 12.50, 12.52, 13.00, 13.02, 13.04 y 13.50. La fuente no aporta una medición específica de 13.52 para ese valor.

## Comprobación semántica

Los valores son comparables como posibles direcciones de la función `pmap_protect`, no como función frente a parche:

| Componente | Uso | Valor |
|---|---|---:|
| `ps4-linux-loader` `PS4_13_52` | Entrada de función `pmap_protect` | `0x58570` |
| SLOPOS `ps4/1352.h` | Entrada de función kexec | `0x58570` |
| Scene/local `K1352_PMAP_PROTECT` anterior | Dirección usada por el installer como función | `0x59DF0` |
| Scene/local `K1352_PMAP_PROTECT_P` | Offset/sitio de parche separado | `0x59E37` |

La evidencia pública disponible es suficiente para priorizar `0x58570` como candidato `STRUCTURAL`, no para resolverlo como `DIRECT_BYTES`. Esto no constituye una prueba de ejecución en una PS4 física 13.52 ni verifica todos los parches dependientes.
