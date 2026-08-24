# Matriz de fuentes/herramientas PS4-PUP (2026-08-24)

| Fuente | Qué hace | Requiere PS4 | ¿Nuevo hoy? |
|---|---|---|---|
| idc/ps4-pup_decrypt (+RETAIL.md hashes MD5 .dec 1.75–4.xx) | orquesta ioctls en consola | SÍ (kernel) | validación futura |
| SocraticBliss fork | ídem + safe.PUP→entryname.dec, probado ≤5.05 | SÍ | variante |
| andy-man (probado ≤11.05), EchoStretch, Scene-Collective, dcac8, vvsx87/PPPwn, Creeeeger/PS4-dec(CI), PSTools/ps4_unjail(+encryptsrv) | ídem | SÍ | familia |
| zecoxao/ps5-pup-decrypt(-elf) | ídem PS5; pup_segment=40B (flags2 extra); checkheaders static_asserts | SÍ (PS5) | diff estructural |
| fail0verflow/prosperous | framework Lua PS5: kernel.lua+pup_decrypt.lua vía /dev/pup_update0 | SÍ (PS5 kernel) | arquitectura referencia |
| Force67/prosperity (delta/formats/pup_object.cpp) | parser/emulador sobre .dec; sniff ext; zlib bloques | NO (sobre .dec) | implementación formato |
| Zer0xFF/ps4-pup-unpacker | unpacker .dec (Linux/OSX/Win) | NO | mapa IDs |
| PFU-PupFileUnpacker | GUI python; crypto naive | NO | — |
| ps4-wee-tools | toolbox on-console; SAMU boot flag | SÍ | superficie SAMU |
| psdevwiki/PUP (ed.06-28) | formato+indices completos | NO | ✅ fuente clave nueva |
| RuxaXa pup-update0-samu-model | modelo mailbox→SAMU | NO | modelo testable |
