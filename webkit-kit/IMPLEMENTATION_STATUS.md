# Estado de implementación del kit WebKit/JSC

## Componentes añadidos

`tools/run_host_regression.py` ejecuta el harness ECMAScript seguro con Node. Su resultado es exclusivamente `HOST_ECMASCRIPT_SMOKE`; no demuestra que el motor sea WebKit de PS4 ni carga módulos retail.

`tools/structural_signatures.py` genera hashes del archivo, metadata ELF básica, hashes de cadenas imprimibles y ventanas de bytes. Es una firma estructural de baja dependencia. No desensambla, no resuelve offsets, no genera gadgets y deja `semantic_identity=UNVERIFIED`.

`tools/compare_signatures.py` compara dos salidas mediante similitud Jaccard de tokens/ventanas. Un resultado sólo puede clasificarse como `CANDIDATE_STRUCTURAL_ONLY`.

`tools/make_triple_manifest.py` crea un manifest de `libSceNKWebKit.sprx`, `libkernel_web.sprx` y `libSceLibcInternal.sprx`. Los archivos ausentes quedan `MISSING`; `common_build_id` permanece `MISSING` hasta que exista evidencia coherente.

`tools/kit_health.py` busca marcadores de secretos y políticas inseguras. No ejecuta JavaScript PS4, payloads ni binarios.

## Uso

```bash
python3 webkit-kit/tools/run_host_regression.py
python3 webkit-kit/tools/structural_signatures.py archivo-a -o a.signatures.json
python3 webkit-kit/tools/structural_signatures.py archivo-b -o b.signatures.json
python3 webkit-kit/tools/compare_signatures.py a.signatures.json b.signatures.json
python3 webkit-kit/tools/make_triple_manifest.py /ruta/al/conjunto -o triple-manifest.json
python3 webkit-kit/tools/kit_health.py
```

## Estado actual

El host dispone de Node, por lo que el smoke test ECMAScript puede ejecutarse. No hay Clang/LLD, CMake, Ninja, Docker ni SDK/ABI retail detectados en el entorno auditado. El repositorio no contiene los tres módulos WebKit 13.52; por ello no puede generar firmas target, Build ID común, GOT/imports reales, vtables retail ni offsets confirmados.

OpenOrbis permanece como una ruta separada para una aplicación homebrew legítima cuando el usuario aporte el toolchain. Este kit no incluye loader de jailbreak, exploit, payload, escape de sandbox ni redistribución de módulos propietarios.

## Criterios de promoción

Una coincidencia estructural no se promueve a `CONFIRMED` sin bytes target, SHA-256, formato/segmentos, Build ID o metadata equivalente y procedencia coherente. Los offsets absolutos permanecen deshabilitados por diseño.
