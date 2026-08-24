# Investigación de claves PUP (2026-08-24) — basada en evidencia

Pregunta: ¿dónde está la clave que descifra la cabecera interna del PUP 13.52
y puede obtenerse sin consola?

## Evidencia recopilada
1. RETAIL.md (idc): MD5 de .dec verificados en consola 1.76 para FW 1.75–4.xx+
   ⇒ el descifrado es determinista y validable; se hacía EN CONSOLA ya en 2017.
2. decrypt.c: la tabla de segmentos/metadata solo existe tras ioctl DECRYPT_HDR;
   el tool escribe la cabecera DESCIFRADA al .dec ⇒ los .PUP.dec contienen las
   AES128 keys/IVs por segmento EN CLARO (estructura psdevwiki, 0x50 B/entrada).
3. prosperous (PS5)/Zer0xFF/prosperity: procesan SOLO .dec — nadie implementa
   el descifrado offline.
4. SAMU/HSM: CTurt+marcan+psdevwiki — claves no extraíbles del procesador
   seguro; interacción sí posible.

## Respuestas a A–H
A) clave pública conocida: NO encontrada para ninguna FW PS4/PS5.
B) derivable: NO hay KDF pública documentada para esta capa.
C) almacenada en metadata: las claves POR-SEGMENTO sí viajan en metadata
   (cifradas); la clave de CABECERA no aparece en el fichero.
D) específica del firmware: la de cabecera lo parece (cambia por update);
   las per-segmento son únicas por fichero (viajan en él).
E) dependiente de consola: la de cabecera NO lo es según diseño (la misma
   consola 1.76 descifraba updates futuros ⇒ clave estable/compartida),
   pero esto es inferencia del flujo, no documento Sony → HIPÓTESIS fuerte.
F) derivada de SOCUID: aplica a SECURE LOADER/particiones .cryptx2b
   (per-console), no hay evidencia que afecte a la cabecera del update.
G) solamente SAMU: la operación de descifrado sí pasa por SAMU/SBL; la clave
   como material probablemente resida allí ⇒ REQUIRES console-oracle.
H) combinación: modelo más consistente = clave de cabecera estática-por-FW
   protegida en SBL/SAMU; per-segment keys dentro del fichero.

## Conclusión operativa
Un único acceso console-oracle en 13.52 (kernel exec + payload adaptado)
produce: .dec completo + tabla metadata clara ⇒ capacidad offline permanente
de descifrar/desempaquetar ESE firmware desde Termux (AES128-CBC + zlib,
formato documentado). Sin ese acceso, no existe ruta legítima conocida.
