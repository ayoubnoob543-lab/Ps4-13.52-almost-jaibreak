# BRECHAS RESTANTES — cierre offline total (2026-08-24)

Toda brecha restante converge en UN hito: **una sesión console-oracle en 13.52**
(kernel-exec + payload pup_decrypt adaptado). Tras ella, TODO lo demás se
resuelve OFFLINE desde Termux con herramientas ya creadas/documentadas:

1. .dec producido ⇒ tabla segmentos+metadata AES128 en claro (offset 0x20…)
2. Descifrado segmentos offline (AES128+IV de metadata + zlib) — implementable
   en Termux con cryptography/lzma (sin PS4)
3. system_fs_image.img extraído ⇒ montar FAT32/exFAT ⇒ kernel retail + módulos
   ⇒ offsets 13.52 verificables ⇒ cierra objetivos del lab
4. Con kernel retail: validar/refutar sysvsem(220/221/222), kqueue UAF window,
   semctl CVE-2026-58087 en binario real

Sin consola NO queda ninguna incógnita resoluble por vías públicas conocidas:
barridos GitHub/X/wiki/foros agotados (ver source-matrix y offline_scan.json).

Clasificación final de la cadena: ver docs/pup-crypto-chain-1352.md.
