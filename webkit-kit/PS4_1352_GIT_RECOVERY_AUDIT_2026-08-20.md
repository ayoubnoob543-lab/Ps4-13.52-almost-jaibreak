# Auditoría de recuperación por historial Git — PS4 WebKit 13.52

## Alcance

Este ciclo no repitió la auditoría de `libkernel_sys_13.52.bin`, `lk_dump1.bin`, `lk_dump2.bin` o `lk_dump3.bin`, no ejecutó smoke WPE y no repitió búsquedas públicas de módulos WebKit. La vía nueva fue exclusivamente la recuperación local mediante refs, reflogs, commits no alcanzables, árboles y blobs Git.

## Método reproducible

```sh
git reflog --all --date=iso
git fsck --full --no-reflogs --unreachable
git log --all --name-status -- webkit-kit analysis
git ls-tree -r --name-only origin/webkit-ps4-1352-kit
```

Los blobs no alcanzables de tamaño razonable se inspeccionaron únicamente como bytes/texto estático con `git cat-file` y `strings`; no se ejecutaron ni se cargaron como ELF/SELF.

## Resultado

El reflog mostró commits locales anteriormente reescritos o integrados mediante rebase, pero todos correspondían a documentación WPE o al pipeline estático ya publicado:

| Commit no alcanzable | Contenido | Resultado |
|---|---|---|
| `0480a252...` | Evidencia del paquete WPE 2.52.6 | **PORTABLE/NO RETAIL** |
| `078f867...` | Delta de búsqueda pública 13.52 | **DOCUMENTED_ONLY** |
| `bb59aaa...` | Pipeline ELF/SELF estructural | **PORTABLE** |

La búsqueda de blobs no alcanzables por cadenas `libSceNKWebKit`, `libkernel_web`, `libSceLibcInternal`, `13.52`, `NXDP`, `ORBISDMP`, `orbisstate` y `eboot.bin` no encontró ningún blob candidato. No apareció un árbol antiguo, tag, rama, manifest, ruta de extracción ni hash oculto que apuntara a bytes retail WebKit 13.52.

## Contradicción resuelta

El reflog sí contiene commits que ya no son alcanzables desde la rama actual, pero eso no significa que el workspace haya conservado artefactos target. La inspección de sus árboles y blobs demostró que son informes y herramientas, no `SPRX`, `SELF`, `ELF`, `eboot.bin` o dumps. Por tanto, la recuperación Git no aporta bytes nuevos.

## Estado de evidencia

| Elemento | Clasificación |
|---|---|
| Reflogs/commits históricos del kit | **VERIFIED_METADATA** |
| Pipeline estático recuperable | **PORTABLE** |
| Artefacto retail `libSceNKWebKit.sprx` 13.52 | **MISSING** |
| `libkernel_web.sprx` 13.52 | **MISSING** |
| `libSceLibcInternal.sprx` 13.52 | **MISSING** |
| SELF/ELF/eboot correlacionado | **MISSING** |
| NXDP/ORBISDMP/orbisstate correlacionado | **MISSING/UNVERIFIED** |
| Build ID/GOT/vtables/offsets target | **MISSING/UNVERIFIED** |

## Conclusión

La vía local de historial Git, reflogs y objetos huérfanos queda agotada para este checkout y no recupera el primer artefacto retail WebKit 13.52. La infraestructura útil quedó preservada: inventarios, manifests, parser ELF/SELF estructural y clasificación de evidencia. El siguiente avance exige una fuente externa autorizada o un backup propio que contenga al menos un módulo retail 13.52 con procedencia y hash.

No se añadieron binarios grandes, no se modificaron artefactos históricos y no se ejecutó ningún binario PS4.
