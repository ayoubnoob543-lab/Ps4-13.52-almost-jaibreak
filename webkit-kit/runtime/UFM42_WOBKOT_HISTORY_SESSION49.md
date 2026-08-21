# Historial de ufm42/wobkot — sesión 49

## Resultado principal

Se enumeraron ramas, tags, commits y forks públicos de `ufm42/wobkot` mediante GitHub API y se compararon los archivos fuente de los tres forks públicos.

Repositorio original:

- URL: https://github.com/ufm42/wobkot
- Rama: `main`
- Tags: ninguno
- Ramas adicionales: ninguna
- Último commit: `0d0cce9c4e1203eb04fdcd736781b38492978f7b`
- Último push: 2026-08-05 16:20:59 UTC

Commits relevantes:

- `2f96abf1796bf05e913b298c9932284b6cac38d3` — 2026-07-25 — `full chain exploit added`
- `bba4e8fdc5b59b781e0d26eea49bdbf8f748fe34` — 2026-07-03 — `update rop implementation for gadgets compatibility`
- `f0ab54dd8a8d1e8393ab1f7d6f2f3e010f1bec81` — 2026-07-01 — `add 10.xx support`
- `bfd5246ab9fbb5f4d065175296bba68d23007b96` — 2026-07-01 — rediseño de offsets y reducción de spray

Forks públicos:

- `ke5adb/wobkot`
- `Retr0H4x/wobkot`
- `Hiruika006/wobkot`

Cada fork expone únicamente la rama `main`. Los tres forks tienen el mismo SHA de `constants.js`:

`52c6af4a7f75c87238345ad6f6e0761a04e3c54a052ed68a5363461a5a92ef72`

También coinciden sus hashes de `userland.js` (`0d5fc478...`) y `kernel.js` (`949f9d12...`).

## Firmware

La tabla completa de `constants.js` contiene parches hasta `1102.bin`. No aparecen literales `13.52`, `1352`, `13_52` ni `1352.bin`. Los únicos `KPATCH` son:

`600.bin`, `620.bin`, `650.bin`, `670.bin`, `700.bin`, `750.bin`, `800.bin`, `850.bin`, `900.bin`, `903.bin`, `950.bin`, `1000.bin`, `1050.bin`, `1100.bin`, `1102.bin`.

La búsqueda fue realizada tanto sobre el repositorio original como sobre los tres forks y no encontró una entrada 13.52.

## Conclusión

El historial y los forks confirman un proyecto público real de userland/chain WebKit, pero no contienen soporte público 13.52. No existe una rama, tag o fork visible que añada los offsets o parches necesarios. La demo pública 13.52 debe corresponder a material no publicado, un host diferente o una adaptación privada.

No se ejecutó código, payload, binario ni hardware.
