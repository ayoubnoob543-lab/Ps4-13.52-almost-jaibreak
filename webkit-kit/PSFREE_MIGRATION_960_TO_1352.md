# Migración estática PSFree 9.60 → PS4 13.52

## Regla principal

El código de `zacke0815/ps4-9.04_webkitJB` en el commit `e9046aa49b44584ef1a8bbdbc63e8a77d0709e1d` se usa como **referencia de arquitectura y flujo**, no como fuente de offsets válidos para 13.52. Esta rama no ejecuta ni adapta una cadena de explotación.

## Clasificación

| Área | Reutilizable | Específico de 9.60 | Requisito 13.52 | Estado 13.52 |
|---|---|---|---|---|
| Representación `Int64`/punteros | Sí, con validación de ABI | Tamaño y endianess asumidos | Confirmar ABI x86-64 de la build | `STRUCTURAL` |
| Lectura/escritura abstracta | Sí como interfaz de análisis | Primitivas concretas dependen de exploit | Probar sólo con fixture controlado | `NO_RUNTIME_IMPLEMENTATION` |
| Descubrimiento de bases | Concepto reutilizable | Imports, vtables y anclas dependen del binario | Disponer de módulos 13.52 y sus hashes | `MISSING` |
| Resolución de imports | Algoritmo abstracto | Offsets de import slots son target-specific | Analizar SELF/SPRX 13.52 | `MISSING` |
| ROP/JOP | Sólo como documentación histórica | Gadgets y offsets son enteramente target-specific | Requiere bytes y autorización; no se generan | `UNVERIFIED` |
| `libkernel_web`/libc | Separación de capas reutilizable | Símbolos y offsets de 9.60 no se transfieren | Módulos 13.52 exactos | `MISSING` |
| Syscalls y estructuras kernel | Idea de resolver por símbolos/tabla | Valores, layouts y entry points dependen del firmware | Bytes kernel/libkernel 13.52 | `UNVERIFIED` |
| Payload/loader | No se migra | Es operacional y específico de target | Fuera del alcance de esta base segura | `NOT_INCLUDED` |

## Valores que sí pueden derivarse legítimamente

El repositorio local contiene `libkernel_sys_13.52.bin` con SHA-256 `ef15204fee6f9f3e37892a4d29d779ed90ec4b70025b652d64625d76419b6a9c`. Ese blob permite análisis estático de sus propios bytes y validación de patrones, pero no demuestra los módulos WebKit ni permite rellenar automáticamente offsets de exploit.

Las tablas públicas `SYSENT`/`pmap_protect` y los archivos `13.52.js` se clasifican como `STRUCTURAL/UNVERIFIED` porque no están corroborados por una imagen retail del kernel objetivo.

## Valores que deben permanecer ausentes

Deben permanecer `MISSING` o `UNVERIFIED` hasta obtener bytes de la misma build: bases de `libSceNKWebKit.sprx`, `libkernel_web.sprx` y `libSceLibcInternal.sprx`; import slots; GOT/vtables; gadgets; estructuras de objetos; offsets de syscalls; Build ID; hashes de módulos y relación exacta entre módulos.

## Herramienta

`tools/analyze_psfree_reference.py` produce un inventario JSON de hashes, líneas relevantes y categorías, sin importar módulos JavaScript ni emitir cadenas operativas. Su salida debe usarse como material de revisión, no como configuración de ejecución.
