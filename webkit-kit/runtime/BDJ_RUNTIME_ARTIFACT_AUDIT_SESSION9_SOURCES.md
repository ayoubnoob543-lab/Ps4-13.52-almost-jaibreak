# Fuentes nuevas de disponibilidad/procedencia — Sesión 9

## ASaudidos / MasterMaind

La página pública `https://twitter-thread.com/t/2081061116025692373` reproduce un hilo de @ASaudidos del 25-07-2026 titulado “update on ps4 bd-j exploit progress (firmware 12.02)”. El texto afirma que la cadena userland funciona en 12.02, 13.02, 13.50 y 13.52; también afirma que Sony eliminó el grant original de `sunjce_provider.jar` en una actualización reciente, pero que la vulnerabilidad usada por esa cadena es distinta y permanece sin parchear. Describe resultados como control de registros, pivot de stack, invocación de syscalls y ejecución nativa dentro del proceso BD-J.

Esto es una **declaración pública atribuida al investigador**, no un artefacto. No aporta `rt.jar`, `bdjstack.jar`, hash, manifest, clase, método, símbolo, diff ni repositorio del runtime. Clasificación: `DOCUMENTED_ONLY` para la afirmación; `UNVERIFIED` para cualquier implementación concreta de 13.52.

## GBAtemp

La página `https://gbatemp.net/threads/ps4-exploit-guide.497858/page-1392` contiene un estado comunitario que enumera “BD-JB: 13.50 (Gezine unreleased patched in 13.52)”. La misma página identifica la ruta histórica `file:///app0/bdjstack/lib/ext` y recomienda fuentes públicas de firmware, pero no ofrece bytes BD-J 13.52, hash ni manifest. Clasificación: `WEAK_INDIRECT`/`DOCUMENTED_ONLY`.

## Implicación para disponibilidad

Estas fuentes reducen la incertidumbre sobre afirmaciones públicas, pero no cambian la disponibilidad de artefactos. La auditoría local y los repositorios públicos revisados siguen sin contener `rt.jar`, `bdjstack.jar`, `sunjce_provider.jar`, `enhanced-stubs.zip` ni una librería JVM/BD-J de 13.52. No se descargaron PUPs, discos, dumps ni firmware propietario.
