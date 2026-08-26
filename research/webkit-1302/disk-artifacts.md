# WebKit y disco/artefactos 13.02

## Objetivo

Construir un corpus específico de 13.02 que permita responder, con evidencia, tres preguntas separadas:

1. ¿Qué superficie WebKit/BD-J permite alcanzar ejecución userland?
2. ¿Qué artefactos de disco, ISO, JAR, BDJO o PUP son sólo transportes y cuáles contienen código relevante?
3. ¿Qué bytes del sistema 13.02 son necesarios para validar offsets y el salto a kernel R/W?

## Capas de artefactos

| Capa | Ejemplos | Qué demuestra | Qué no demuestra |
|---|---|---|---|
| BD-J/disco | ISO, BDMV, JAR, BDJO, clases Java | Transporte, carga y superficie BD-J | Kernel exploit o offsets kernel |
| WebKit | HTML/JS, Vue After Free, fixtures | Ejecución userland y primitives JavaScript | Privilegios kernel |
| Userland PS4 | `libkernel_web`, `libkernel_sys`, libc, manifests | Wrappers, syscalls y layout de módulos | Kernel retail |
| PUP | SLB2, entradas, hashes, tamaños | Integridad del contenedor y metadata | Módulos descifrados si no se descifra |
| Kernel | `system_fs_image.img`, kernel ELF/raw, dumps | Offsets, funciones y parches de build exacta | Persistencia o jailbreak completo por sí solo |

## Pipeline recomendado

### A. Adquisición

Registrar URL o fuente, fecha UTC, commit/release, tamaño, SHA-256 y licencia. No usar `latest` como identidad de evidencia. Si el artefacto es un adjunto o asset mutable, copiarlo a un directorio de evidencia con nombre versionado.

### B. Identificación

Determinar si el objeto es ISO/UDF, JAR/ZIP, BDJO, PUP/SLB2, SELF/SPRX, ELF o raw. Guardar la salida de `file`, cabeceras y hashes. La identificación de contenedor no debe presentarse como identificación del módulo interno.

### C. Extracción estática

Para disco, listar ISO/UDF y extraer sólo metadata y archivos necesarios; no ejecutar clases ni binarios recuperados. Para PUP, validar SLB2, tamaños y hashes de entradas. Para ELF/SELF, registrar program headers, secciones disponibles, arquitectura y build ID cuando exista.

### D. Correlación

Relacionar cada offset con un artefacto y una build. La correlación debe marcar si la fuente es independiente o si varios repositorios comparten el mismo origen. Un valor compartido por tres forks no constituye tres confirmaciones.

### E. Validación

Elevar a `VERIFIED` sólo tras una comprobación sobre bytes de 13.02 o una ejecución controlada con resultado observable. Mantener `SOURCE_ONLY` cuando sólo exista una tabla o afirmación pública.

## Artefactos ya localizados en el laboratorio

| Artefacto | Ubicación | Uso en esta rama |
|---|---|---|
| Tabla local de offsets | `research/results/slopos/1302.h` | Referencia `SOURCE_ONLY`; requiere segunda fuente o bytes. |
| Offsets integrados | `kpayload/source/offsets/1302.c`, `kpayload/include/offsets/1302.h` | Comparar qué valores consume el payload. |
| Vue/WebKit corpus | `webkit-kit/`, `experiments/`, `research/` | Separar userland de kernel. |
| ISO y scanners históricos | `scanner_1304.iso`, `goldhen/` | Comparación de pipeline; no asumir 13.02. |
| PUP y manifests 13.52 | raíz y `analysis/` | Metodología de parsing; no evidencia 13.02. |

## Lista de artefactos faltantes

| Faltante | Prioridad | Razón |
|---|---:|---|
| Kernel retail 13.02 o dump equivalente | P0 | Validar los diez parches restantes y las tablas kernel. |
| `system_fs_image.img` 13.02 con procedencia | P0 | Candidata a contener módulos y kernel, aunque pueda estar cifrada. |
| Logs de ejecución Netctrl/ucred en 13.02 | P0 | Confirmar o descartar el salto userland → kernel. |
| Segunda fuente independiente de SLOPOS 13.02 | P1 | Resolver si la tabla es corroborada o sólo replicada. |
| Build/manifest exacto de WebKit 13.02 | P1 | Vincular userland con una build concreta. |
| ISO/BD-J 13.02 identificado y hasheado | P1 | Reproducir la vía de entrada disco sin mezclarla con el kernel. |

## Restricciones de seguridad y reproducibilidad

Esta rama documenta investigación y análisis estático. No debe ejecutar payloads recuperados automáticamente, modificar una consola, descargar artefactos desde URLs mutables sin hash ni publicar binarios generados sin revisión. Todo experimento de hardware debe tener un protocolo separado, consentimiento del propietario del dispositivo y logs mínimos suficientes para reproducir el resultado sin publicar datos sensibles.
