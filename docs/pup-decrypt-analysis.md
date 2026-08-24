# Análisis del descifrado PUP — ¿es posible desde Termux? (2026-08-24)

Respuesta corta: **NO existe implementación pública del descifrado sin consola**,
porque el algoritmo y las claves viven DENTRO del kernel/SBL de Sony. Lo que sí
existe y quedó **portado a Termux y probado**: toda la capa de orquestación
(`tools/pup_orchestrator.py`), que es la parte no criptográfica del payload.

## 1. Dónde está la rutina real de descifrado

NO está en ninguno de los repos descargados. El payload `ps4-pup_decrypt` (idc)
solo ORQUESTRA: delega cada operación al dispositivo de kernel `/dev/pup_update0`
mediante ioctls:

| Opcode | Operación | Estructura de args |
|---|---|---|
| `0xC0184401` | descifrar cabecera interna | buf(8), len(8), type(4)+pad |
| `0xC0184402` | verificar segmento (additional=1) | idx(2)+pad, buf, len |
| `0xC0184403` | verificar segmento (additional=0) | ídem |
| `0xC0184404` | descifrar segmento | idx(2)+pad, buf, len |
| `0xC0284405` | descifrar bloque con tabla | entry_idx, block_idx, block_buf, block_len, table_buf, table_len |

## 2. Dependencias rastreadas

```
decrypt_pups()
 ├─ open("/dev/pup_update0", O_RDWR)      ← DEPENDENCIA KERNEL (única crítica)
 ├─ BLS/SLB2 parse (bls_header/bls_entry) ← portable (portado ✓)
 └─ decrypt_pup_data()
     ├─ pup_file_header (16B claro)       ← portable (portado ✓)
     ├─ ioctl decrypt_header              ← kernel
     ├─ pup_segment[] walk + block tables ← portable (lógica portada ✓)
     └─ ioctl decrypt_segment/block       ← kernel
```
Adicionales del payload (no-cripto): `printfsocket` (log por socket),
libPS4 runtime — irrelevantes fuera de consola.

## 3. Criptografía vs dependencia PS4

- **Algoritmo criptográfico: 100% dentro del kernel/SBL de Sony**
  (`SceSblUpdateMgr`/driver sbl). AES + derivación de claves NO públicos.
- **Dependencia PS4 estricta:** el nodo `/dev/pup_update0` (su apertura ya
  requiere contexto que el sandbox no da; por eso el payload corre en modo
  kernel tras exploit).
- **Portable (y portado):** formato BLS/SLB2, cabecera interna de 16 B en claro,
  cálculo de región cifrada (`unk_0C+unk_0E`), clasificación de segmentos por
  flags (0xE0000000 firma adicional, 0xF0000000 watermark, bit 0x800 tabla de
  bloques, bit 0x8 comprimido), aritmética de bloques
  (`block_size = 1<<((flags>>12&0xF)+12)`).

## 4. Adaptación Termux realizada

`tools/pup_orchestrator.py`: réplica fiel del flujo de `decrypt.c` con los
ioctls sustituidos por stubs que fallan con diagnóstico explícito. Probado sobre
el PUP 13.52 reconstruido (hash verificado): produce orden de trabajo completo
con fronteras cifradas exactas — cabeceras internas cifradas de 4816 B
(UPDATE1) y 1232 B (UPDATE2).

## 5. La dependencia PS4 que falta, EXACTAMENTE

```
/dev/pup_update0  — character device cuyo handler en el kernel:
                    · valida contexto (solo ejecución kernel/confiable)
                    · implementa AES-CBC con claves derivadas embebidas en SBL
                    · mantiene estado por segmento/bloque entre ioctls
```

Sin ejecución kernel en 13.52 ese device es irrecuperable. No es un binario
que se pueda "portar": ES parte del firmware objetivo.

## 6. ¿Claves/IVs/tablas en el código?

**NO.** Verificado sobre las 831 líneas del payload: cero tablas de claves, cero
IVs, cero constantes de derivación. (Las únicas "claves" del ecosistema
descargado son placeholders ingenuos en PFU: `(seed+i)%256`, sin relación con
Sony.)

## 7. Implementaciones públicas independientes

- `ps4-pup-unpacker` (C++): parser del formato POST-descifrado (tablas en
  claro). Útil después; no descifra.
- PFU-PupFileUnpacker: heurístico, sin cripto real.
- Herramientas PS3-PUP: formato distinto, no aplicables.
- **Conclusión:** todo descifrador PS4 público conocido depende del dispositivo
  de kernel; consistente con `RETAIL.md` del propio repo ("updates decrypted on
  a 1.76 retail system" = EN CONSOLA).

## 8–9. Prueba sobre material existente y criterios de validez

Ejecutado (ver §4). Criterios para aceptar cualquier salida futura como
válida: (a) cabecera descifrada debe parsear como `pup_header` coherente
(segment_count>0, tamaños cuadren), (b) segmentos deben extraerse completos,
(c) hashes comparables contra `RETAIL.md`/listados históricos cuando existan,
(d) archivos internos deben mostrar magia estructural válida (SELF/ELF/etc.).

## 10. Reparto Termux vs PS4

| Parte | ¿Termux? |
|---|---|
| Parseo SLB2/BLS externo, tallado, hash | ✅ hecho |
| Cabecera interna clara (16 B) + región cifrada medida | ✅ hecho |
| Orquestación completa + órdenes de trabajo | ✅ hecho (`pup_orchestrator.py`) |
| Descifrado header/segmento/bloque | ❌ REQUIRES_PS4_KERNEL |
| Enumeración de segmentos internos | ❌ depende del descifrado de tabla |
| Obtención de módulos (kernel, WebKit, libkernel retail) | ❌ ídem |

## Implicancia estratégica

La pieza exacta que falta no es código: **es ejecución kernel en 13.52**.
La investigación UAF kqueue/knote es, hoy, el único camino público conocido
hacia ella. Al conseguirla, `ps4-pup_decrypt` adaptado (mismo flujo, mismo PUP
ya tallado y verificado) cerraría el círculo: kernel retail dump → offsets
13.52 verificables → objetivos del lab.

---

## BARRIDO EXHAUSTIVO DE ALTERNATIVAS (2026-08-24 tarde)

Búsqueda en GitHub/X/wiki de CUALQUIER implementación que descifre PUP sin
`/dev/pup_update0`. Resultado completo:

| Herramienta | Plataforma | Mecanismo | ¿Offline? |
|---|---|---|---|
| idc/ps4-pup_decrypt (+ forks Creeeeger, andy-man, Scene-Collective, dcac8, vvsx87) | PS4 | ioctl /dev/pup_update0 desde modo kernel | ❌ |
| PSTools/ps4_unjail | PS4 | variante del mismo payload (unjail primero) | ❌ |
| zecoxao/ps5-pup-decrypt(-elf) | PS5 | mismo dispositivo, opcodes PS5 | ❌ |
| **fail0verflow/prosperous** (`pup_decrypt.lua`) | **PS5** | Lua sobre exploit kernel; MISMOS `/dev/pup_update0` con opcodes desplazados (0xC0104401..06); syscalls vía primitivas kernel.lua | ❌ |
| PFU / pup-py3 / Dextura unpacker | PC | parseo heurístico/post-descifrado | ⚠️ sin descifrado |

**Conclusión del barrido:** las DOS plataformas (PS4 y PS5) resuelven el
descifrado exactamente igual — delegando al dispositivo del kernel — y ambas
necesitan ejecución privilegiada previa. No existe decryptor offline público
porque las claves viven en el SBL/kernel y jamás se han publicado para 13.xx.

## La pieza que falta, formulada con precisión final

```text
Componente ausente: acceso efectivo a /dev/pup_update0 (o equivalente funcional)
  ├── Vía clásica: ejecución kernel (payload idc)      ← requiere cerrar UAF→R/W
  ├── Vía PS5-style: kernel R/W + ioctl desde Lua      ← ídem
  └── Vía extracción de claves: dump kernel 13.52      ← REQUIRES_KERNEL_DUMP
```

Alternativa teórica restante: si algún día aparece un dump de kernel 13.52,
las claves del update-manager podrían extraerse estáticamente y escribirse un
decryptor Termux real. Ese dump es EL mismo artefacto AUSENTE que persigue el
lab desde el día uno — ahora con TRES motivos para perseguirlo.

Cadena completa cuando exista R/W kernel:
UAF → R/W → abrir pup_update0 (o extraer claves) → descifrar PUP 13.52
→ kernel retail dump verificable → offsets 13.52 → objetivos del lab cerrados.
