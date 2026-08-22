# Revisión estática de `ps4-ipv6-uaf` — sesión 72

## Fuentes

- Repositorio: https://github.com/ChendoChap/ps4-ipv6-uaf
- Rama 6.70–6.72: https://github.com/ChendoChap/ps4-ipv6-uaf/tree/6.70-6.72

Las páginas se consultaron de forma pasiva. No se descargó ni ejecutó código, payload ni binario.

## Contenido

La rama `6.70-6.72` contiene JavaScript y archivos HTML/ROP (`expl.js`, `index.html`, `rop.js`, `syscalls.js`, `userland.js`), no módulos binarios WebKit ni `libkernel_web.sprx`. El README del repositorio lo describe como una implementación del exploit IPv6 UAF para firmware 7.00–7.02 y enumera ramas históricas de 5.05 a 7.02.

El README también menciona dependencias históricas de la cadena, como el exploit WebKit, métodos ROP y tablas de syscalls. Esa información es útil para entender qué artefactos debían acompañar a una cadena de firmware concreta, pero no constituye un dump de `libSceNKWebKit` ni evidencia sobre 13.52.

La página enumera modificaciones de kernel asociadas al exploit histórico, incluyendo cambios de mapeo de memoria, resolución dinámica y otras funciones de kernel. No se usan aquí para construir una cadena ni se consideran evidencia aplicable a 13.52.

## Valor para el objetivo actual

El repositorio confirma que las ramas públicas de explotación históricas separaban el código JavaScript/ROP de los módulos binarios y de las tablas específicas de firmware. Sirve como referencia de organización y procedencia, pero no aporta archivos `webkit.bin`, `webkit.elf`, `libSceNKWebKit.sprx` o `libkernel_web.sprx`.

## Clasificación

| Hallazgo | Clasificación |
|---|---|
| Rama pública específica 6.70–6.72 | `DIRECT_HISTORICAL` |
| Código JS/ROP y tablas de firmware | `DIRECT_HISTORICAL` |
| Módulos WebKit binarios en el repositorio | `DISCARDED` |
| Evidencia específica de PS4 13.52 | `DISCARDED` |
| Utilidad para entender la separación código/módulos | `INDIRECT_13.52` |
| Ruta operativa o exploit reutilizable | `DISCARDED` |

## Conclusión

`ps4-ipv6-uaf` no resuelve el bloqueo de WebKit 13.52. Su valor es histórico: confirma que el código de una cadena pública y los dumps de módulos podían distribuirse por separado y que cada firmware requería datos específicos. No se debe trasladar ninguna tabla ni offset a 13.52.

## Referencias

[1] [ChendoChap/ps4-ipv6-uaf](https://github.com/ChendoChap/ps4-ipv6-uaf)

[2] [Rama 6.70–6.72](https://github.com/ChendoChap/ps4-ipv6-uaf/tree/6.70-6.72)
