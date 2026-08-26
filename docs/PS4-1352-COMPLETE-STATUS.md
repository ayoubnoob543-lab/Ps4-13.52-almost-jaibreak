# PS4 FW 13.52 — ESTADO COMPLETO DEL PROYECTO (2026-08-25)

## Resumen en una frase

Todo lo determinable sin consola está hecho y documentado. La cadena completa
para 13.52 existe como diseño; le falta UN archivo (payload kernel 13.02/13.52)
que solo puede producirse con UNA sesión console-oracle.

## Inventario completo

### Herramientas creadas (funcionales, probadas)

| Herramienta | Función | Estado |
|---|---|---|
| `tools/pupdec_unpack.py` | Desempaquetador .dec offline | ✅ selftest OK |
| `tools/pup_dec_full_unpacker.py` | Versión completa con AES128 opcional | ✅ selftest OK |
| `tools/pupdec_validate_log.py` | Validador contra log de consola real | ✅ 33/33 |
| `tools/pup_orchestrator.py` | Orquestador del PUP SLB2 | ✅ probado |
| `tools/kernel_payload_generator.py` | Generador paramétrico de payload kernel | ✅ probado |
| `research/experiments/exp30_ioctl_mock/` | Captura protocolo ioctl con mock | ✅ 8 ioctls |
| `research/run.sh` | Pipeline autónomo con parada HW | ✅ |

### Vulnerabilidades documentadas

| Vulnerabilidad | FW | Clase |
|---|---|---|
| UAF kqueue/knote | **13.52** | CONFIRMADO_HW (autor-reportado) |
| Triple-free ucred vía netcontrol(99) | ≤13.00 | Código fuente público analizado |
| CVE-2026-58087 semctl TOCTOU | kernel 11.02 confirma SysV; 13.02 = HIPÓTESIS | CONFIRMADO_OTRA_VERSION |
| exFAThax v2 | parcheado en 13.52 | REFUTADO_13.52 |
| BD-J sunjce | parcheado en 13.52 | REFUTADO_13.52 |

### Formato PUP 13.52 — lo que sabemos sin descifrar

| Estructura | Offset | Tamaño | Contenido |
|---|---|---|---|
| SLB2 header | 0x00000000 | 32 B | magic "SLB2", 2 entradas |
| bls_entry[0] | 0x00000020 | 48 B | UPDATE1 @1024, 326 MB |
| bls_entry[1] | 0x00000050 | 48 B | UPDATE2 @326028288, 177 MB |
| ScePupHeader UPD1 | 0x00000400 | 16 B claro + 4816 B cifrado |
| ScePupHeader UPD2 | 0x1EC0C840 | 16 B claro + 1232 B cifrado |

La región cifrada de cada cabecera contiene la tabla de segmentos y las
entradas `ScePupMetadataEntry` (0x50 B) con AES128 key+IV+HMAC-SHA256 por
segmento. Sin descifrar esa cabecera no se puede acceder a ningún contenido.

## Cadena para construir el jailbreak 13.52

```text
PASO 1 [REQUIRES CONSOLE]
   Ejecutar kqueue UAF en PS4 13.52
   → userland code execution

PASO 2 [REQUIRES CONSOLE]
   Ejecutar payload adaptado de ps4-pup_decrypt
   → /dev/pup_update0 ioctl → produce PS4UPDATE1.PUP.dec

PASO 3 [OFFLINE — tools/pupdec_unpack.py YA LO HACE]
   Parsear .dec → extraer segmentos → tabla metadata EN CLARO
   → AES128 keys/IVs visibles → system_fs_image.img descifrable

PASO 4 [OFFLINE]
   Montar system_fs_image.img (FAT32/exFAT)
   → kernel retail binario visible
   → offsets 13.52 calculables por diff con 13.00

PASO 5 [OFFLINE — tools/kernel_payload_generator.py YA LO HACE]
   Generar payload kernel 13.02/13.52 con offsets reales
   → jailbreak completo reproducible offline
```

## Lo que falta EXACTAMENTE

Una sola cosa: **que alguien ejecute los pasos 1–2 en una consola 13.52**.
Todo lo demás está construido, validado y esperando.
