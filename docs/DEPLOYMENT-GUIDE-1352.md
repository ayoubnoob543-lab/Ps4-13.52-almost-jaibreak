# GUÍA DE DESPLIEGUE — PS4 13.52 desde Android/Termux

## Lo que necesitas comprar/adquirir

| Item | Dónde | Precio aprox | Para qué |
|---|---|---|---|
| Star Wars Racer Revenge (CUSA03474 USA o CUSA03492 EU) | PS Store digital | ~5€ | Ejecución inicial via savedata exploit |
| Cuenta PSN activa en la consola | Ya la tienes | Gratis | Para instalar el juego |
| Cable/Red entre teléfono y PS4 | WiFi compartido del móvil | Gratis | Para enviar payloads |

## Lo que YA tienes (preparado en este repo)

| Fichero | Función |
|---|---|
| `tools/pupdec_unpack.py` | Desempaquetador .dec completo con AES128 |
| `tools/pup_dec_full_unpacker.py` | Versión extendida |
| `tools/pupdec_validate_log.py` | Validador 33/33 |
| `tools/kernel_payload_generator.py` | Generador de payload paramétrico |
| `research/experiments/exp30_ioctl_mock/` | Protocolo ioctl capturado |
| Luac0re 2.4 (descargado, hash verificado) | Framework Lua/JIT para ejecutar payloads |

## PASO A PASO COMPLETO

### FASE 0 — Preparación (desde el teléfono)

```bash
# En Termux:
cd ~/firmware-lab
# Todo el toolkit ya está aquí y validado

# Extraer Luac0re si no lo hiciste antes:
cd ~/fl_verify/deep/payloads
unzip -o ps4-payloads-bin.zip -d luacore_ready/
```

### FASE 1 — Instalar el juego en la PS4

1. Enciende la PS4 (FW 13.52, sin jailbreak)
2. Ve a PlayStation Store
3. Busca "Star Wars Racer Revenge" (o "Super Star Wars" — también compatible)
4. Compralo/descargalo (~5€)
5. NO lo ejecutes todavía

### FASE 2 — Resignar la savedata

⚠️ **ESTE ES EL ÚNICO PASO QUE REQUIERE AYUDA EXTERNA**

La savedata modificada debe estar firmada para TU cuenta PSN específica.
Opciones sin tener otra PS4 hackeada:

**Opción A** — Servicio online de resigning:
- Busca "PS4 save resign service" en comunidades de PS4 homebrew
- Algunos usuarios con consolas hackeadas ofrecen este servicio gratis
- Envíales: tu account ID (visible en Settings → Account Management)
- Ellos te devuelven la savedata firmada

**Opción B** — Apollo Save Tool:
- Requiere PS4 ya hackeada (no es tu caso actualmente)
- Si conoces a alguien con una PS4 hackeada, puede usar Apollo

**Opción C** — Esperar a que la comunidad publique una versión
que no requiera resigning (los desarrolladores están trabajando en ello)

### FASE 3 — Importar savedata a la PS4

1. Copia la savedata firmada a un USB (FAT32, MBR)
2. En la PS4: Settings → Application Saved Data Management → Saved Data in USB Storage Device → Copy to System Storage
3. Selecciona el usuario correspondiente
4. Confirma la importación

### FASE 4 — Configurar red entre teléfono y PS4

1. Conecta ambos dispositivos a la MISMA red WiFi
   (puede ser el hotspot de tu propio teléfono)

2. Anota la IP local de tu teléfono:
   ```bash
   # En Termux:
   ifconfig wlan0 | grep inet
   # Ejemplo: 192.168.1.100
   ```

3. Verifica que la PS4 puede alcanzar esa IP:
   ```bash
   # Desde Termux, haz ping a la IP de la PS4:
   ping 192.168.1.XXX  # (IP de la PS4 en tu red)
   ```

### FASE 5 — Ejecutar el exploit

1. En Termux, inicia el servidor de payloads:
   ```bash
   cd ~/firmware-lab/research/experiments/exp30_ioctl_mock
   python3 -m http.server 8080 --bind 0.0.0.0
   ```
   
2. En la PS4, abre el juego Star Wars Racer Revenge
3. El juego cargará la savedata modificada
4. El exploit se activará automáticamente
5. La PS4 se conectará al servidor de payloads en tu teléfono

6. Desde Termux, envía los payloads:
   ```bash
   # Usando los scripts incluidos en Luac0re:
   python3 ws.py --ps4-ip=192.168.1.XXX --port=8513
   ```

### FASE 6 — Post-explotación

Una vez dentro:

```text
Tienes ejecución NATIVA USERLAND en la PS4 13.52

Puedes hacer:
  ✓ Ejecutar payloads Lua/JavaScript
  ✓ Acceder al filesystem (con permisos del proceso)
  ✓ Ejecutar FTP server para explorar archivos
  ✓ Investigar estructuras del kernel accesibles

NO puedes hacer:
  ✗ GoldHEN / HEN (necesita kernel R/W)
  ✗ Instalar homebrew PKG
  ✗ Descifrar PUP directamente
  ✗ Acceder a particiones SAMU-cifradas
```

## Qué hacer con acceso userland

Con ejecución userland puedes:

1. **Dumpear módulos accesibles**: libkernel.sprx, libSceLibcInternal.sprx
   → Estos son útiles para comparación con nuestros dumps 11.02/12.xx

2. **Probar las vulnerabilidades kernel documentadas**:
   - semctl TOCTOU (syscall 510): ¿el kernel 13.52 tiene SysV?
   - kqueue UAF: confirmar la ventana double-free
   - Si alguna da kernel R/W ⇒ jailbreak completo

3. **Extraer información del sistema**: versión exacta, build strings,
   configuración, módulos cargados

## IMPORTANTE

Este proceso NO da jailbreak completo. Da ejecución userland que permite
INVESTIGAR. Para jailbreak completo necesitas un kernel exploit adicional.

Las vulnerabilidades kernel candidatas para 13.52 están documentadas en
`docs/remaining-gaps.md` (semctl TOCTOU es la más prometedora).
