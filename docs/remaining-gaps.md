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

## NUEVA BRECHA TÉCNICA (kernel 11.02 real descargado y verificado)

Artefacto: `~/fl_verify/deep/kernel1102/11.02/kernel.bin` (44 MB,
sha256 `451f8735…` ✓, NO commiteado por regla no-blobs).
Tabla numerada extraída: `research/results/orbis1102_syscall_numbers_verified.txt`
(680 entradas, punteros→strings verificados).

| Incógnita nueva | Estado | Método propuesto |
|---|---|---|
| Localizar array `sysent[]` en binario stripado | DESCONOCIDO — layout Sony≠F9 stock (no hay runs {int,ptr} de 16B) | RE offline: probar layouts 24/32B, buscar por handlers conocidos (exit→sigthread), o anclar via llamadas desde sys_ioctl |
| Desensamblar handler __semctl (GETALL/SETALL) para verificar patrón CVE-2026-58087 EN BINARIO ORBIS | HIPÓTESIS→verificable offline una vez localizado sysent | capstone sobre sy_call del índice correspondiente |
| ¿Claves de cifrado PUP accesibles desde kernel x86? | HIPÓTESIS (SAMU probablemente las retiene) | strings/xrefs alrededor de sbl/pup_update.c module |
