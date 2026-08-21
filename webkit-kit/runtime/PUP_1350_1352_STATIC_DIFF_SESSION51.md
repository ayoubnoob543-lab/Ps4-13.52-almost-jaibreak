# PS4 PUP 13.50 → 13.52 — diferencial estático

| Campo | 13.50 | 13.52 | Delta |
|---|---:|---:|---:|
| `size` | 503293952 | 503310848 | +16896 |
| `size_in_sectors` | 982996 | 983029 | +33 |
| `declared_container_bytes` | 503293952 | 503310848 | +16896 |

| Entrada | Tamaño 13.50 | Tamaño 13.52 | Delta | SHA-256 13.50 | SHA-256 13.52 |
|---|---:|---:|---:|---|---|
| `PS4UPDATE1.PUP` | 326026471 | 326026951 | +480 | `8adf0cfbe6bac3932d6e8473591d00d90fb496e5ad894729d296752c4830fb3b` | `fd5e6c16398e628b3f258bce5f395c9fda687011a1a985d4b507928f54e6b580` |
| `PS4UPDATE2.PUP` | 177266167 | 177282367 | +16200 | `e0c736ab95e071cf83b02deeef4a19a03389bdc0b7b67a409c29ee28fe17e511` | `44cd0c0e85b5912150112df99867357c3822a90f366198d11e2ec4c1e10adee7` |

## Interpretación

Los dos PUP son contenedores SLB2 válidos y coherentes. Ambas entradas internas cambian de tamaño y hash entre 13.50 y 13.52, pero permanecen opacas. Esto demuestra un diferencial de bytes de los paquetes internos, no qué módulo o función cambió.

No se descifró, desempaquetó ni ejecutó contenido. Para atribuir el cambio a WebKit, kernel, BD-J o checksums concretos todavía se necesita metadata interna legible o una extracción autorizada de los módulos comparables.
