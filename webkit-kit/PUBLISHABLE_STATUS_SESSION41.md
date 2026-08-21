# Estado publicable del kit WebKit/BD-J PS4 13.52

## Alcance

Este documento consolida el material seguro que puede versionarse: documentación, manifests, hashes, parsers, correladores, tests sintéticos y demos WPE/Linux no explotativas. No incluye payloads operativos, exploits armados, claves, credenciales ni binarios nuevos de procedencia dudosa.

## Progreso por área

| Área | Avance | Base verificable |
|---|---:|---|
| Infraestructura WPE/Linux | 100% | Rootfs WPE 2.52.6, MiniBrowser, WebDriver, fixtures y smoke ya validados |
| Tooling de análisis | 95% | Parsers de artefactos, manifests, hashes y correladores versionados |
| Corpus upstream/Sony | 90% | WebKit-601-1300, commits upstream y comparaciones estructurales documentadas |
| Material BD-J de laboratorio | 25% | `scanner_1304.iso` con UDF/BDJO/JAR, atribuido a 13.04 por nombre/metadata |
| Evidencia WebKit retail PS4 13.52 | 0% directa | No hay `libSceNKWebKit.sprx`, SELF/ELF WebKit ni snapshot retail verificable |
| Evidencia indirecta de WebKit 13.52 | 15% | Referencias, commits, rangos y diagnósticos, sin bytes retail |
| Primitive de memoria PS4 13.52 | 0% | No demostrada |
| Native usermode PS4 13.52 | 0% | No demostrado |

Los porcentajes de infraestructura y tooling no se suman como evidencia de firmware. Una coincidencia estructural en WPE o WebKit-601-1300 conserva estado `UNVERIFIED` para 13.52.

## Metas operativas separadas

### Disco BD-J

El repositorio conserva `scanner_1304.iso`, una imagen UDF con `BDJO`, `00000.bdjo`, `00000.jar` y clases BD-J. Es adecuada como artefacto de laboratorio para estudiar estructura y carga normal, pero no es una imagen identificada como 13.52. La carga real en hardware no está verificada y no se publica ninguna cadena de escape o payload.

Para una prueba legítima específica de 13.52 faltaría una imagen BD-J de esa versión o metadata que establezca su compatibilidad. Para estudiar WebKit/JavaScriptCore faltaría además el runtime correspondiente; una ISO BD-J no lo contiene automáticamente.

### Navegador

La demo Linux/WPE 2.52.6 está completa para su objetivo: `MiniBrowser`, `WPEWebDriver`, `/status`, page1→page2→page3 y assertions DOM/CSS/JS ya fueron validados. Esto prueba WPE/Linux, no el navegador retail PS4.

La ejecución del navegador PS4 13.52 sigue requiriendo `libSceNKWebKit.sprx` o equivalente, ABI/headers de la build, integración del WebProcess y procedencia verificable de la misma versión.

## Material que se versiona

Se incorporan sólo documentos, código de análisis y tests. Los binarios grandes y artefactos de runtime permanecen fuera de Git o sólo se referencian mediante hashes. `scanner_1304.iso` ya era un archivo existente del repositorio y no se vuelve a copiar ni modificar.

## Clasificación

- `DIRECT_BYTES`: archivo local disponible con hash; no implica firmware correcto.
- `VERIFIED_METADATA`: metadata o manifest verificable.
- `STRUCTURAL`: código o patrón comparable sin procedencia retail.
- `WPE_LINUX_ONLY`: evidencia exclusiva del laboratorio Linux.
- `MISSING`: bytes o runtime no presentes.
- `UNVERIFIED`: cualquier conclusión específica de PS4 13.52 sin bytes/procedencia suficiente.

## Validación prevista

```text
py_compile: PASS requerido
unittest: PASS requerido
pytest, si está disponible: PASS requerido
git diff --check: PASS requerido
git status: limpio tras push
```

No se ejecutan binarios analizados, clases BD-J, exploits, PoC ni payloads.
