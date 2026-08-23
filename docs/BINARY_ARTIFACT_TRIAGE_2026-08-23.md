# Triage de artefactos binarios — análisis estático por API (2026-08-23)

Método: solo lectura vía GitHub API (sin clonar, sin ejecutar, sin descifrar). Hashes calculados sobre los blobs reales de git.

## 1. Partes PUP 13.50 vs 13.52 (artifacts/pup_chunks_1350_1352/)

Comparación de los 52 SHA-256 del manifiesto PUP_PARTS_MANIFEST_1350_1352.json por índice de parte:

| Resultado | Valor |
|---|---|
| Partes idénticas entre versiones | 0 |
| Partes diferentes | 26/26 |

Conclusión: las imágenes PS4SYS están cifradas de extremo a extremo (el README de artifacts lo confirma: no se han descifrado); cualquier cambio de contenido altera todo el ciphertext posterior. La localización de cambios por ventanas de 20 MB es imposible sin descifrar el PUP. Vía cerrada mientras no existan claves/volcado descifrado.

## 2. Inventario y hashes (calculados hoy sobre blobs git)

| Archivo | Bytes | SHA-256 |
|---|---|---|
| lk_dump1.bin | 159744 | d4a9a642f85446785469750532d9353c9010ebec4373b8e9c4c06d594536da57 |
| lk_dump2.bin | 159744 | e044d0e5303596df94f86190d34bee6dda8e87f9a51578d067e8d1650ca15e8d |
| lk_dump3.bin | 159744 | e31dd16ddc488851c98bc1782cfe919ece1cab2c141bd0ef7c8a9ef82fb9fdf2 |
| libkernel_sys_13.52.bin | 479232 | ef15204fee6f9f3e37892a4d29d779ed90ec4b70025b652d64625d76419b6a9c |
| hen.bin | 499680 | 32570b6e54c9531dc8a7d75ef4da6557d440bf69c4b765a85a77d428db3a4b73 |

## 3. Estructura de libkernel_sys_13.52.bin (verificada por hash)

libkernel_sys_13.52.bin == cat(lk_dump1, lk_dump2, lk_dump3):

| Región | Rango | Contenido identificado |
|---|---|---|
| R1 = lk_dump1 | 0x00000–0x27000 | Tabla de stubs de syscall x86-64: patrón `48 c7 c0 NN NN 00 00 / 49 89 ca / 0f 05 / 72 01 / c3`. 210 stubs contados por firma `4989ca0f057201c3`. Primeros números visibles: 0x1b2, 0x1b3 |
| R2 = lk_dump2 | 0x27000–0x4E000 | Código de módulo: rutas `/system/common/lib/libSceSysmodule.sprx`, errores `orbis_rtld_*_module_info`, áreas nombradas del kernel (SCE_KERNEL_HEAP_AREA, SCE_KERNEL_JIT_SHM_AREA, SCE_KERNEL_PROC_IMAGE_AREA…), internos pthread/TCB |
| R3 = lk_dump3 | 0x4E000–0x75000 | Metadatos: registros repetitivos de estructura fija compatibles con tablas .eh_frame/unwinding; 1 sola cadena ≥8 chars en toda la región |

hen.bin: blob crudo de código x86-64 (prólogo endbr64/push visibles), payload userland sin cifrar.

## 4. Alcance y limitaciones

- Análisis exclusivamente estático/catálogo: sin ejecución, sin ingeniería inversa profunda, sin desarrollo de explotación.
- Los dumps son userland (stubs de libkernel mapeados en proceso); NO contienen código de kernel.
- Utilidad: mapa de referencia para comparar contra futuras versiones de firmware y para validar procedencia de artefactos.
