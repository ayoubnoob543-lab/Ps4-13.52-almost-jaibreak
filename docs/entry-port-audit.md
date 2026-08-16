# Auditoría de portabilidad de entrada hacia PS4 13.52

## Candidata más cercana

La candidata histórica más cercana es **HenLoader LP 1.0**, release `10f5c4b181f565ab5474266c6f6061769042aa7a`. Su propia descripción limita la cadena a `Lapse (9.00-12.02) + Poops (9.00-12.52)` e incluye GoldHEN 2.4b18.7. La ISO publicada mide 1,69 MB y tiene SHA-256 `0cd1f34fb31668f89eee64f30535f735c2425ee6317f32346955e793cbc71e1b`.

Es la candidata más próxima por usar BD-J y una ISO de entrada, pero no es una portabilidad directa: su kernel chain termina en 12.52 y el repositorio local necesita una entrada que entregue `installer.bin` y seleccione/ejecute offsets de 13.52.

## Comparación con 13.52

| Componente | HenLoader/Poops 12.52 | Rama local 13.52 | Evidencia para un port |
|---|---|---|---|
| Entrada | BD-J ISO | No hay ISO/HTML/loader 13.52 | No suficiente |
| Kernel chain | Lapse/Poops | No hay kernel chain pública 13.52 | No suficiente |
| WebKit/ROP | Específico de la cadena anterior | No hay gadgets 13.52 completos | No suficiente |
| Kernel offsets | Tabla de la cadena 12.52 | Tabla 13.52 pública parcial/cruzada | No basta para reconstruir la entrada |
| Loader/payload | Payload HEN propio | `installer.bin` de esta rama | Formatos y ABI no demostrados equivalentes |
| Caché/recursos | Empaquetados en la ISO | No existe caché web | No transportable por copia |
| Detección de firmware | Menú/cadena HenLoader | `get_offsets_for_fw(1352)` en kpayload | Selección local correcta, entrada ausente |

**Mast1c0re** no es una alternativa directa. Su repositorio público describe ejecución mediante un guardado de un juego de PS2 y escape del emulador; no es BD-J/WebKit y no documenta una forma de entregar este `installer.bin` ni una cadena de kernel 13.52.

## Auditoría de offsets y dependencias

Los 89 campos de `kpayload/source/offsets/1352.c` coinciden exactamente con la tabla pública de Scene-Collective consultada. El bloque `PS4_13_52` de `ps4-linux-loader` confirma directamente varios campos comparables, incluidos `printf`, `pmap_protect = 0x58570`, `sysent = 0x1102B70` y `kernel_pmap_store = 0x1B2C3A0`. No se encontró una fuente pública completa que permita reconstruir los gadgets WebKit, estructuras de userland, primitive de escape y transporte de payload necesarios para un port de la entrada.

## Decisión

No se creó una variante experimental. Copiar HenLoader, `scanner_1304.iso`, los gadgets 13.50 o `jordy_stage2.js` y cambiar etiquetas de firmware produciría un artefacto que parecería 13.52 sin una cadena verificable. No hay cambios experimentales que revertir.

El build actual permanece intacto y compilable. El bloqueo no es un offset aislado: falta una **entrada/loader/kernel chain pública completa y específica de 13.52** que conecte el arranque del usuario con este `installer.bin`. La validación en hardware sólo puede comenzar después de obtener esa cadena o una implementación pública equivalente.

## Referencias

1. [GoldHEN/henloader_lp, release 1.0](https://github.com/GoldHEN/henloader_lp/releases/tag/1.0)
2. [McCaulay/mast1c0re](https://github.com/McCaulay/mast1c0re)
3. [ConsoleMods Exploit Chart](https://consolemods.org/wiki/PS4:Exploit_Chart)
4. [ConsoleMods BD-JB](https://consolemods.org/wiki/PS4:BD-JB)
5. [Scene-Collective/ps4-hen, 13.52 commit](https://github.com/Scene-Collective/ps4-hen/commit/2beb4cfcef1d416a32d6fb7b35f01189e9eb62e2)
