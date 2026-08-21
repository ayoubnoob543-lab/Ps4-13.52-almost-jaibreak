# Investigación profunda del workaround FontFace atribuido a ufm42

## Resultado principal

Los posts públicos de Dr.Yenyen dicen que ufm42 encontró un workaround para que el exploit FontFace funcionase en PS4 13.52 y mencionan ayuda de arabpixell con pruebas y offsets. Sin embargo, los enlaces asociados no conducen a un repositorio, commit, testcase o módulo legible de 13.52.

## Perfiles y repositorios revisados

`ufm42` mantiene públicamente `wobkot`, `kexp`, `cobolt`, `Netflix-N-Hack` y otros proyectos. `wobkot` sigue sin entrada 13.52 en la tabla pública y sus forks auditados son equivalentes.

`ArabPixel` mantiene `WebKitty`, un host de exploits PS4. Su README declara explícitamente:

- CSSFontFace + Lapse/NetCtrl: 9.00–11.02;
- PSFree + Lapse: 7.00–9.60;
- Bad Hoist + exploit 6.7x: 6.70–6.72.

Aunque agradece a ufm42 y menciona CSSFontFace NetCtrl/Lapse, no declara soporte 13.52 ni publica una entrada 13.52. `WebKitty` es un host/colección de cadenas históricas, no un dump de `libSceNKWebKit.sprx`.

El repositorio `Feyzee61/ps4jb` también queda limitado a 5.05, 6.72 y 7.00–9.60.

## Clasificación

| Elemento | Clasificación |
|---|---|
| Claim de workaround FontFace 13.52 en X/Reddit | DOCUMENTED_ONLY |
| Participación de arabpixell en pruebas/offsets | DOCUMENTED_ONLY |
| `wobkot` como implementación 13.52 | DISCARDED |
| `WebKitty` como implementación 13.52 | DISCARDED |
| Código público del workaround 13.52 | UNVERIFIED / no localizado |
| Primitive controlable 13.52 | UNVERIFIED |
| Native usermode 13.52 | UNVERIFIED |

## Conclusión

La investigación agotó los repositorios públicos directamente vinculados a los autores y hosts. Existe un claim técnico más fuerte que un simple vídeo, pero el artefacto que permitiría reproducirlo no está publicado en las fuentes revisadas. El bloqueo exacto sigue siendo `libSceNKWebKit.sprx` de 13.52, un testcase/commit del workaround o un dump parcial con procedencia y hash.
