# GoldHEN v2.4b18 — infraestructura de referencia de loader/payload

## Qué es

GoldHEN es el Homebrew Enabler para PS4 mantenido por [SiSTRo](https://github.com/SiSTR0) bajo la
organización [`GoldHEN`](https://github.com/GoldHEN/GoldHEN). El código fuente es privado; las
releases públicas se distribuyen como binarios firmados por su autor. Este laboratorio integra la
release **pública** `2.4b18` como material de referencia estática y como infraestructura de carga
para firmwares soportados, no como evidencia 13.52.

## Contenido integrado

| Elemento | Ruta | Origen |
|---|---|---|
| Payload principal (`goldhen.bin`) | `goldhen/goldhen.bin` | Asset oficial `GoldHEN_v2.4b18.7z` |
| Archivo original íntegro | `goldhen/archive/GoldHEN_v2.4b18.7z` | Release `2.4b18` de GitHub |
| Stage2 PPPwn v1.03 (9.00–11.00) | `goldhen/pppnw_stage2/` | Incluido dentro del asset oficial |
| Documentación del autor | `goldhen/*.md` | Incluido dentro del asset oficial |
| Manifest reproducible | `goldhen/MANIFEST.json` | Generado localmente (SHA-256/tamaño por archivo) |
| Loader Lapse/Poops (fuente) | `third_party/henloader_lp` | Submódulo de `GoldHEN/henloader_lp` |

Todos los hashes y tamaños están registrados en `goldhen/MANIFEST.json`. El hash del archivo
original (`d0c84c79f65df5afc79a00c578f33ab1aa70aeb9c205f1e789895dc7d4fca38d`) permite verificar
la descarga contra la release oficial en cualquier momento.

## Firmwares soportados (declarados por el autor)

- `goldhen.bin` v2.4b18: **5.05, 6.71/6.72, 9.00, 9.60, 10.00/10.01, 10.50, 10.70/10.71, 11.00**.
- `third_party/henloader_lp` (HenLoader): exploit *Lapse* para **9.00–12.02** y exploit *Poops*
  (BD-JB de TheFlow) para **9.00–13.00**.
- Las versiones más recientes del payload (por ejemplo `2.4b18.7`) no tienen release pública en
  GitHub; se distribuyen vía Ko-fi del autor y no forman parte de este corpus verificable.

## Relación con el objetivo 13.52

**GoldHEN no soporta FW 13.52.** Ningún byte de este directorio valida offsets del kernel
13.52 ni constituye evidencia de jailbreak 13.52. Su clasificación es
`DIRECT_BYTES_EXTERNAL_RELEASE` para los binarios publicados (identidad del artefacto, no del
firmware objetivo) y `STRUCTURAL_REFERENCE` para documentación y stage2.

Usos válidos dentro del lab:

1. Comparación estructural de tablas de payload/resolver entre HENs versionados.
2. Referencia de formato de stage2/kernel-loader para la metodología de carga.
3. Infraestructura de prueba en firmwares ≤ 13.00 vía HenLoader (Lapse/Poops), fuera del alcance
   de la validación 13.52.

## Observaciones verificables de esta descarga

- Los stage2 de PPPwn vienen agrupados por binario idéntico: `stage2_10.00.bin` =
  `stage2_10.01.bin` y `stage2_10.50.bin` = `stage2_10.70.bin` = `stage2_10.71.bin`
  (SHA-256 iguales en `MANIFEST.json`). Es coherente con builds compartidas entre revisiones
  menores de firmware.
- El asset oficial incluye `CHANGELOG.md` que declara soporte hasta 11.00; cualquier soporte
  superior proviene exclusivamente del loader externo (`henloader_lp`) o de releases no públicas.

## Cómo verificar la procedencia

```bash
sha256sum goldhen/archive/GoldHEN_v2.4b18.7z
# esperado: d0c84c79f65df5afc79a00c578f33ab1aa70aeb9c205f1e789895dc7d4fca38d
python3 - <<'EOF'
import json, hashlib, os
m = json.load(open("goldhen/MANIFEST.json"))
for e in m["files"]:
    h = hashlib.sha256(open(os.path.join("goldhen", e["path"]), "rb").read()).hexdigest()
    assert h == e["sha256"], e["path"]
print("OK:", len(m["files"]), "archivos verificados")
EOF
```

## Uso práctico (firmware ≤ 13.00, fuera del alcance 13.52)

- USB FAT32/exFAT con tabla MBR; renombrar `goldhen.bin` a `payload.bin` en la raíz y ejecutar el
  loader correspondiente (BD-J/Lapse/Poops o host WebKit según firmware).
- Tras la primera carga, GoldHEN copia el payload a `/data` en la consola; actualizaciones
  posteriores se aplican sobrescribiendo `payload.bin` en el USB.
