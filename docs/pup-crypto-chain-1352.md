# Cadena criptográfica del PUP 13.52 — estado verificado (2026-08-24)

Leyenda: ✅CONFIRMADO · ❓DESCONOCIDO · 🔶parcial/inferido

```text
PS4UPDATE.PUP (SLB2/BLS externo)          ✅ PLANO — parseado y hash-verificado
   │  bls_header 32B + bls_entry 48B ×N     ✅ entradas: UPDATE1@1024(326MB),
   ▼                                        UPDATE2@326028288(177MB)
PS4UPDATE1.PUP / PS4UPDATE2.PUP           ✅ tallados, sha256 fd5e6c16/44cd0c0e ✓
   │
   ├─ ScePupHeader 0x20
   │    ├─ 0x00–0x0F claro                ✅ CONFIRMADO (magic 4F153D1D + campos)
   │    └─ 0x10–0x1F CIFRADO              ✅ CONFIRMADO (entropía + hexdump)
   │        file_size / segment_count /
   │        metadata_entries viven aquí   ❓ valores desconocidos sin clave
   │
   ├─ Tabla de segmentos (ScePupSegmentHeader 32B c/u)   ← DENTRO de la zona cifrada
   │    flags(u64, Id=flags>>20) offset csize usize       ❓ contenido real desconocido
   │
   ├─ Segmentos especiales 0xE*/0xF* = tabla ScePupMetadataEntry   ✅ FUNCIÓN confirmada
   │    (0x50B c/u: aes128_key[16] aes128_iv[16] digest[32] digest_key[16])
   │    ❓ sus bytes: cifrados como el resto
   │
   ├─ Segmentos de datos (ID5 secure_modules, ID6 system_fs→KERNEL RETAIL,
   │  ID7 EAP, ID12 SYSTEM_EX, 512/514 orbis_swu.self…)  ✅ IDs/nombres confirmados
   │    cifrado POST-compresión            ✅ (wiki) · AES128 con clave de metadata
   │                                       ❓ requiere tabla descifrada
   ▼
ioctl /dev/pup_update0 (en consola, kernel)   ✅ mecanismo capturado (8 frames)
   │  DECRYPT_HDR→cabecera; VERIFY×2; DECRYPT_SEG/BLOK×N
   ▼
SAMU (HSM) ejecuta AES con key-slots internos ✅ arquitectura (psdevwiki/CTurt/marcan)
   │  claves NUNCA x86-visibles               ✅ consenso escena, nunca refutado
   ▼
*.PUP.dec  ⚠️ CONTIENE la tabla metadata EN CLARO   ✅ por flujo de decrypt.c
   │        (fwrite(header_data) tras descifrar ⇒ AES128 keys/IVs por segmento
   │         quedan en claro dentro del .dec)
   ▼
Unpacker offline (Zer0xFF/prosperity) funcionan SOLO sobre .dec  ✅
```

## La brecha exacta

| Pieza | Estado |
|---|---|
| Clave que cifra cabecera interna (4832 B) | ❓ REQUIERE una sesión console-oracle (kernel-exec) — luego es estática para ese fichero |
| Per-segment AES128 keys/IVs | ✅ VIAJAN DENTRO DEL FICHERO (en metadata); accesibles tras abrir la cabecera |
| Descifrado offline posterior | ✅ posible con AES128 estándar + zlib (sin SAMU, sin consola) |

Corrección importante a informes previos: "SAMU nunca da claves" es cierto,
pero **no impide el descifrado offline** porque las claves operativas viajan
dentro del propio PUP (cifradas una sola vez bajo la clave de cabecera).
El SAMU protege esa única capa.
