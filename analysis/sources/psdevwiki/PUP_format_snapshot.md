# Formato interno del PUP PS4 — documentación psdevwiki (snapshot 2026-08-24)

Fuente: https://www.psdevwiki.com/ps4/PUP (última edición wiki: 2026-06-28).
Capturado vía resultados de búsqueda (la wiki bloquea fetch automatizado).
Transcripción literal de las estructuras relevantes para el lab.

## ScePupHeader (cabecera de cada fragmento PUP interno)

```c
struct ScePupHeader {
  uint32_t magic;            // 0x00 - PS4PUPMAGIC "\x4F\x15\x3D\x1D"
  uint16_t version;          // 0x04 - Big Endian (?)
  uint16_t unknown_one;      // 0x06
  uint16_t unknown_two;      // 0x08
  uint16_t flags;            // 0x0A
  uint16_t header_size;      // 0x0C
  uint16_t metadata_size;    // 0x0E

  // From this point on, the header is encrypted...
  uint16_t file_size;        // 0x10   (nota wiki: u16; ver observación abajo)
  uint16_t segment_count;    // 0x18
  uint16_t metadata_entries; // 0x1A
  uint32_t unknown_three;    // 0x1C
}; // Size: 0x20
```

Observación propia: los offsets 0x10–0x1F con esos tipos no cuadran entre sí
(u16 file_size en 0x10 y segment_count en 0x18 implican hueco); la captura real
(nuestro mock) muestra un u64 de tamaño en 0x10 y segment_count u16 en 0x18,
coherente con el binario. La wiki probablemente simplificó. Punto a reverificar
cuando exista una cabecera descifrada real.

## ScePupSegmentHeader (32 B por segmento)

```c
struct ScePupSegmentHeader {
  uint64_t flags;               // Id = flags >> 20 ; bit0 = IS_INFO ;
                                // bit3 = comprimido ; bit11 = blocked
  uint64_t offset;
  uint64_t compressed_size;
  uint64_t uncompressed_size;
};
```

## ScePupMetadataEntry (0x50 B — ¡material criptográfico POR SEGMENTO!)

```c
struct ScePupMetadataEntry {
  char aes128_key[0x10];   // clave AES128 de descifrado del segmento
  char aes128_iv [0x10];   // IV AES128
  char digest   [0x20];    // ?HMAC-?SHA256 digest
  char digest_key[0x10];   // clave HMAC-SHA256
};
```

"Nota wiki": la tabla de metadatos sigue a la estructura info y contiene material
criptográfico (claves intermedias para descifrar/verificar segmentos). Cada
segmento debe tener su entrada.

## Reglas de cifrado (wiki)
- El cifrado se aplica a los segmentos POST-compresión.
- Segmentos sin bloquear = copia directa o descompresión.
- Los primeros 0x10 bytes del header son claros; desde ahí, header+metadata
  CIFRADOS ("can be seen by using the system as an oracle to decrypt PUPs").

## Contenido por fragmento (wiki)
- PS4UPDATE1 = "core": kernel x86/GameOS, usermode, Bluray, EAP, EMC, Syscon,
  SAM y otros firmwares del SPI flash.
- PS4UPDATE2 = partición system_ex (aplicaciones de sistema).
- Todos los fragmentos contienen EULA, orbis_swu y watermark.

## Índices de entrada (selección; tabla completa en la wiki)

| ID | Componente | Destino sflash/partición | Per-console |
|---|---|---|---|
| 5 | COREOS → secure_modules.bin | — | No (universal) |
| 6 | SYSTEM → system_fs_image.img | da0x4 system (SAMU HDD Key) | No |
| 7 | EAP KERNEL | da0x2 | No |
| 9 | PREINST | preinst fs | No |
| 12 | SYSTEM_EX | da0x5 | No |
| 512/514 | ORBIS_SWU.SELF / (Encrypted SELF) | — | No |
| 4/45/49/50 | SECURE LOADER (por SOCUID: CXD90026G…CXD90055GB) | sflash0s1.cryptx2/b | **Sí** |
| 3337(0xD07)… | SYSCON FW etc. | sc_fw_update0 | Universal |

Nota: los dispositivos `.cryptx2b` confirman que las particiones del Secure
Loader van cifradas por consola (SOCUID), mientras COREOS/SYSTEM/EAP son
universales.
