# Inventario de artefactos mast1c0re / vías de entrada 13.52 (2026-08-24)

## Contexto

El objetivo prioritario del lab es un artefacto retail 13.52 verificable
(WebKit/kernel). La vía candidata es la cadena mast1c0re (CTurt 2022) portada a
13.52. Este documento inventaria qué existe públicamente, qué se descargó y qué
falta para una ejecución real, sin inflar afirmaciones.

## Piezas encontradas y verificables

| Pieza | Origen | Hash / tamaño | Estado |
|---|---|---|---|
| Notas de investigación 13.52 | `Suchi96/mast1c0re-13_52-test` (`mast1c0re_13.52_research.docx`) | 14379 B | Offsets libkernel verificados estáticamente 8/8 (ver `analysis/mast1c0re_1352_offset_corroboration_2026-08-24.json`) |
| Compiler binario | `Suchi96/ps411_02stuff/ps2-emu-compiler.self` | 2055140 B; `e3654841…` | Claims estáticas verificadas byte-exacto (`analysis/mast1c0re_compiler_1102_verification_2026-08-24.json`) |
| Framework Luac0re 2.4 | `Gezine/Luac0re` release `2.4` (`Luac0re_2.4.zip`) | 88506067 B | Descargado localmente; incluye imagen de juego con save para CUSA03474/CUSA03492 |
| Saves craftadas Bully | `Suchi96/CanisCanemEdit` (`VMC0.card`, `VMC1.card`, `.psu`) | 8650752 B c/u | Referenciadas, no commitadas por tamaño |
| Dumps EE | `Suchi96/EE_DumpTest/PS2_EEdump.zip` | 8703669 B | Material de research PS2 |
| Dumps libkernel multi-FW | `Suchi96/ps4libkernel{9_00,11_02,12_00,12_52}` | ~454592 B ELF c/u | Hashes en `analysis/mast1c0re_compiler_1102_verification_2026-08-24.json` |

SHA-256 del release descargado:

```text
Luac0re_2.4.zip -> 43e94351c35fcd0b2d624ecdd8498b0980442416bdaebe4c864bbd6d5aacfa38
                   (88506067 B; asset oficial de github.com/Gezine/Luac0re releases tag 2.4)
```

## Qué aporta Luac0re 2.4 (Gezine)

- Variación de mast1c0re que usa el intérprete **Lua 5.3 embebido en ps2emu**
  (juego: *Star Wars Racer Revenge*, CUSA03474 USA / CUSA03492 EU).
- Desde 2.0 incluye **exploit JIT**: ejecución nativa userland arbitraria en los
  últimos firmwares PS4/PS5 **sin necesidad de kernel exploit**.
- Flujo práctico: comprar el juego digital → sustituir/resignar la savedata
  incluida (guía `remote_lua_loader SETUP`) → cargar payloads Lua por red
  (`payload_sender.py`) o shellcode JIT.
- El repo trae además shellcode JIT para entradas **Poops** y **P2JB**, y un
  `kexp_2026_05_25.bin` orientado a PS5 (elfldr-ps5 0.23).

## Cadena 13.52 realista hoy (si se dispone de consola)

```text
PS4 13.52 + Star Wars Racer Revenge (digital)
  → savedata resignada con los ficheros de Luac0re
  → arranque del juego → Lua/JIT → ejecución nativa userland
  → [opcional investigación] dumpear módulos accesibles desde el proceso
```

## Lo que NO resuelve esta vía (sin cambios)

1. **No hay kernel exploit público para 13.52**: ni Luac0re ni mast1c0re dan
   acceso kernel ⇒ **no hay HEN/GoldHEN** por este camino.
2. La resignación de savedata exige otra consola con HEN o un servicio externo.
3. Las claims de ejecución en hardware del doc de Suchi96 siguen siendo
   autor-reportadas; este laboratorio solo ha validado las partes estáticas.

## Clasificación

Todo lo anterior es infraestructura de entrada userland y material de
comparación: `STRUCTURAL_CORROBORATED` para offsets verificados,
`VERIFIED_METADATA` para hashes de terceros. Ningún byte nuevo de kernel o
WebKit retail 13.52 ha aparecido públicamente a fecha de hoy.
