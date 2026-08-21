# Recomendación de ruta para obtener evidencia WebKit 13.52 — sesión 70

## Fuentes públicas revisadas

1. **MODDED WARFARE, vídeo del 4 de agosto de 2026**: https://www.youtube.com/watch?v=mWX9uj0mKIQ. El título y la descripción afirman que existen bugs de userland WebKit para PS4 hasta 13.52 y enlazan al repositorio `ntfargo/CSSFontFace-Exploit`, además de referencias a publicaciones X. La fuente demuestra una afirmación pública y una ruta documental hacia un repositorio, pero no aporta por sí sola un módulo retail, hash de `libSceNKWebKit.sprx`, offsets ni una primitive reproducible en nuestro entorno. Clasificación: `DOCUMENTED_ONLY`.

2. **Vídeo de TheeEvolutionYT del 23 de julio de 2026**: https://www.youtube.com/watch?v=ZG-SGV4c-kQ. El título y la descripción afirman que un bug BD-J userland afecta a 13.52 y que falta un bug de kernel estable para un jailbreak completo. Esto confirma una afirmación pública sobre una fase userland, no la disponibilidad de los bytes del runtime ni la primitive concreta. Clasificación: `DOCUMENTED_ONLY`.

3. **Feyzee61/psfree_lapse**: https://github.com/Feyzee61/psfree_lapse. El README identifica soporte para PS4 7.00–9.60, no 13.52, y declara que los binarios de payload se excluyen. Es útil como precedente de cómo una implementación pública separa WebKit, kernel y payload, pero no es una fuente de WebKit 13.52. Clasificación: `HISTORICAL_ONLY` para nuestro objetivo.

4. **Reddit, “Updating a PS4 4.73 to 13.52 so you don't have to”**: https://www.reddit.com/r/ps4homebrew/comments/1vk06yc/updating_a_ps4_473_to_13_52_so_you_dont_have_to/. La página contiene comentarios sobre configuraciones de reversión y pruebas entre firmwares, pero no presenta un artefacto WebKit 13.52 verificable. Clasificación: `DOCUMENTED_ONLY`/`UNVERIFIED`.

## Recomendación

La ruta más rápida y legítima no es intentar obtener claves desde los PUP raw ni ejecutar payloads. Es solicitar o localizar un artefacto público ya divulgado con procedencia técnica suficiente: `libSceNKWebKit.sprx` 13.52, un dump parcial autorizado que lo contenga, o una cabecera/tabla `.PUP.dec` obtenida mediante un método legítimo. El primer paso de validación debe ser SHA-256, arquitectura, formato, Build ID, tamaño, procedencia y cadena de custodia; sólo después se ejecutaría el correlador estático.

El repositorio CSSFontFace enlazado por la fuente pública puede ser útil como **referencia de código y testcase**, pero no debe tratarse como evidencia de que el binario retail 13.52 contiene la misma implementación. El fork PSFree revisado tampoco debe usarse como fuente para 13.52, porque declara soporte 7.00–9.60.

## Ranking de rutas

| Ruta | Valor | Riesgo de falso positivo | Dependencia |
|---|---|---:|---|
| Artefacto retail público con hash/procedencia | Muy alto | Bajo | Que exista y sea verificable |
| Extracción autorizada de una cabecera/tabla `.PUP.dec` | Muy alto | Bajo | Acceso legítimo a la salida del sistema/oracle |
| Repositorio de exploit/testcase como referencia estructural | Medio | Alto | No demuestra equivalencia retail |
| Inferir claves/offsets desde bytes raw | Bajo | Muy alto | No recomendado |
| Copiar WebKitGTK/WPE al objetivo PS4 | Bajo para retail | Muy alto | ABI/sysroot/backend ausentes |

## Conclusión

La evidencia pública nueva mejora la ruta documental hacia CSSFontFace/WebKit userland 13.52, pero no cierra el puente hacia el runtime retail. El artefacto mínimo que debemos conseguir es una muestra binaria o metadata descifrada con procedencia verificable; mientras no exista, el laboratorio y el correlador pueden prepararse, pero la presencia de una vulnerabilidad concreta en 13.52 queda `UNVERIFIED`.
