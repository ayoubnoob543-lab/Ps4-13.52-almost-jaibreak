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

## Prototipo `homebrew/`

El prototipo seguro de `homebrew/` está implementado como una frontera C portable con adaptación host. No incorpora WebKit retail, módulos `.sprx`, SDK Sony, offsets, gadgets, ROP/JOP, exploits ni payloads.

| Componente | Estado | Evidencia |
|---|---|---|
| Contrato C portable del runtime | AVAILABLE | `homebrew/include/orbis_webkit_stub.h` |
| Adaptador host seguro | AVAILABLE | `homebrew/src/orbis_webkit_stub.c` |
| Smoke executable host | AVAILABLE | `homebrew/src/homebrew_smoke.c` y build local |
| Makefile reproducible host | AVAILABLE | `homebrew/Makefile` |
| Fuente OSS WebKit/JSC de referencia | AVAILABLE | Corpus fijado en `PS4OSSCode.HEAD` |
| OpenOrbis toolchain instalado en sandbox | MISSING | No se detectaron `clang`, `ld.lld`, CMake ni Ninja |
| OpenOrbis sysroot/headers target | MISSING | No presentes en el entorno |
| ABI y runtime Orbis autorizados | UNKNOWN | No demostrables desde OSS |
| Backend gráfico/compositor PS4 | MISSING | No se implementa ni se inventa |
| Event loop, sandbox, filesystem y allocator target | MISSING | Requieren contrato target legítimo |
| `libSceNKWebKit.sprx` 13.52 | MISSING | Bytes verificables no disponibles |
| `libkernel_web.sprx` 13.52 | MISSING | Bytes verificables no disponibles |
| `libSceLibcInternal.sprx` 13.52 | MISSING | Bytes verificables no disponibles |
| Compatibilidad real con firmware 13.52 | UNKNOWN | No hay build ni prueba en hardware |

El smoke host sólo demuestra la coherencia del adaptador. No se promueve a `PS4_HOMEbrew_BUILD_PASS` ni a `WEBKIT_RETAIL_1352_CONFIRMED`.
