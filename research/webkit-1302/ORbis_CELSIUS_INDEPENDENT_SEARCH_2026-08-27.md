# Búsqueda independiente Orbis 13.02/13.04 y Celsius/Jordy

Punto de partida: rama `research/webkit-disk-1302`, commit `d42bf9c`.

## Alcance A: Orbis 13.02/13.04

Buscar únicamente dumps, proyectos IDA/Ghidra/Binary Ninja, pseudocódigo, disassembly, call graphs o análisis de kernel que permitan identificar `ffs_mountfs`, `ffs_reload` o la función situada en `0x001512A7`. No se recopilarán tablas genéricas de offsets.

## Alcance B: Celsius/Jordy

Buscar únicamente copias históricas del bootstrap/PoC, imágenes UFS/FFS y artefactos atribuidos a autores originales, incluyendo material eliminado, mirrors, commits antiguos, gists, pastes y archivos enlazados desde publicaciones originales. No se reauditará `ps4-suid-scanner`.

## Criterio de independencia

Un fork, espejo o publicación que conserve el mismo hash, commit, texto o blob se clasificará como derivado, no como corroboración independiente. Las afirmaciones sin artefacto serán `SOURCE_ONLY`; los bytes, hashes o proyectos analizables se clasificarán por separado de sus claims.

## Registro

Cada hallazgo se documentará como: artefacto | URL/origen | fecha | hash | firmware | relación con Celsius | pieza que aporta | procedencia.
