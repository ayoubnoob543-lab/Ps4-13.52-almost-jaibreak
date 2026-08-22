# Referencia estática: JIT/WebKit y límites del WebProcess en PS4

## Fuentes

- CTurt, “Hacking the PS4, part 3”: https://cturt.github.io/ps4-3.html
- CTurt, “Hacking the PS4, part 2”: https://cturt.github.io/ps4-2.html

Las páginas se consultaron como documentación pública. No se ejecutó ni adaptó ningún código operativo.

## Hallazgos técnicos

La documentación histórica afirma que JavaScriptCore utiliza JIT y que PS4 expone una interfaz de memoria JIT mediante dos syscalls personalizadas, `sys_jitshm_create` y `sys_jitshm_alias`, junto con wrappers de `libkernel` como `sceKernelJitCreateSharedMemory`. También indica que `libSceJitBridge.sprx` fue analizado para entender la relación entre esas llamadas.

El punto más importante para nuestro objetivo es la frontera de seguridad: la propia fuente separa “código nativo ejecutado dentro del proceso WebKit” de un escape de sandbox o ejecución de kernel. Además, declara que Sony aplica comprobaciones de privilegio en el kernel y que sólo ciertos procesos pueden usar JIT. Por tanto, la existencia histórica de JIT no equivale a una primitive WebKit en 13.52 ni a un jailbreak.

La documentación de la arquitectura del navegador también distingue el proceso WebKit/WebProcess de otros procesos del navegador y describe restricciones de acceso entre procesos. Esto ayuda a interpretar correctamente cualquier dump: un módulo o string observado en WebKit no demuestra acceso a handles, memoria o archivos pertenecientes a otro proceso.

## Valor para el análisis de módulos

La referencia confirma que `libSceJitBridge.sprx`, `libkernel_web.sprx` y JavaScriptCore son componentes relacionados históricamente en la ruta de ejecución nativa del WebProcess. Esto hace que `libSceJitBridge.sprx` sea un candidato de dependencia adicional si aparece en un dump legítimo. Nucleus ya enumeraba `libSceJitBridge.sprx` y `libSceJscCompiler.sprx` como módulos de sistema PS4, pero ninguno de los dos artefactos está disponible localmente.

No hay evidencia en estas páginas sobre PS4 13.52, sobre `CSSFontFace` en esa versión ni sobre una primitive concreta posterior a 11.50. Las afirmaciones se clasifican como históricas.

## Clasificación

| Hallazgo | Clasificación |
|---|---|
| PS4 tuvo una interfaz JIT asociada a `libSceJitBridge` | `DIRECT_HISTORICAL` |
| JIT implica por sí solo escape de sandbox | `DISCARDED` |
| WebProcess y otros procesos tienen límites de acceso | `DIRECT_HISTORICAL` |
| `libSceJitBridge` existe sin cambios en 13.52 | `UNVERIFIED` |
| La misma ruta JIT funciona en 13.52 | `UNVERIFIED` |
| Utilidad de buscar `libSceJitBridge` junto a WebKit | `INDIRECT_13.52` |

## Conclusión

Esta fuente sí identifica una dependencia histórica relevante para el puente WebKit → código nativo: `libSceJitBridge`/wrappers JIT. Pero también confirma por qué no debe confundirse con una explotación completa: el código nativo permanece dentro del WebProcess y las comprobaciones de privilegio del kernel son una frontera separada. Para 13.52 todavía faltan el módulo WebKit y la evidencia de que la interfaz JIT esté disponible o haya cambiado.

## Referencias

[1] [CTurt — Hacking the PS4, part 3](https://cturt.github.io/ps4-3.html)

[2] [CTurt — Hacking the PS4, part 2](https://cturt.github.io/ps4-2.html)
