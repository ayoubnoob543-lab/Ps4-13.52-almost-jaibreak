# REGLAS PERMANENTES DEL PROYECTO — aplican SIEMPRE, sin recordatorios

Vigencia: permanente para todo el trabajo sobre este repositorio
(`ayoubnoob543-lab/firmware-lab`) y sus artefactos asociados en Termux.
Establecidas por el propietario el 2026-08-24.

## 1. Jerarquía de almacenamiento

- **GitHub = BACKUP.**
- **Termux (`~/firmware-lab` y rutas de artefactos listadas abajo) = copia de
  trabajo principal.**

## 2. Flujo obligatorio tras cada cambio importante

1. Guardar los archivos en Termux.
2. Hacer commit.
3. Hacer push a GitHub.
4. **Comprobar que el push terminó correctamente** (verificar línea del remote,
   no asumir éxito).
5. Conservar los archivos importantes también en Termux.

## 3. Política de borrado

- **NUNCA borrar automáticamente archivos importantes del proyecto local.**
- Solo se pueden eliminar sin preguntar: temporales, cachés, duplicados exactos,
  builds regenerables y archivos intermedios trivialmente reproducibles.
- **Antes de borrar cualquier archivo grande**, informar obligatoriamente:
  - nombre
  - tamaño
  - finalidad
  - espacio que se recuperaría
  …y **esperar confirmación explícita** del propietario.

## 4. Artefactos protegidos en Termux (hasta orden contraria del propietario)

El PUP original y todo artefacto necesario para reproducir el análisis NO se
borran ni se mueven fuera de Termux. Inventario mínimo protegido:

| Artefacto | Ruta | Nota |
|---|---|---|
| PUP 13.52 reconstruido y verificado | `~/fl_pup/out/PS4SYS_13.52.rebuilt.PUP` (503 MB, sha256 `daa44e91…`) | == PS4SYS_CRC[DC9D6197] |
| PUP 13.50 reconstruido | `~/fl_pup/out/PS4SYS_13.50.rebuilt.PUP` (503 MB, `04585405…`) | comparativa |
| PUPs internos tallados | `~/fl_pup/out/PS4UPDATE1.PUP` / `PS4UPDATE2.PUP` (hashes fd5e6c16 / 44cd0c0e) | verificados |
| Chunks fuente del PUP | `~/fl_pup/parts/` (~961 MB) | reproducibles desde rama git pero costosos: tratar como protegidos |
| Dump libkernel_sys dual-anclado | `~/firmware-lab/libkernel_sys_13.52.bin` + `lk_dump*.bin` | núcleo del lab |
| Dumps libkernel ELF multi-FW | `~/firmware-lab/research/libkernel/*.elf` + copias en `~/fl_verify/` | comparativa versiones |
| Compiler 11.02 verificado | `~/fl_verify/compiler_1102.self` | evidencia mast1c0re |
| Toolkit Luac0re + release verificada | `~/fl_verify/Luac0re_2.4.zip` (`43e94351…`) + `~/fl_verify/luac0re/` | vía userland |
| Fuentes FreeBSD 9.1 archivadas | `analysis/sources/freebsd-9.1/` | base del análisis estático |

## 5. Aplicación

Estas reglas se aplican en cada tarea sin necesidad de que el propietario las
recuerde. Ante conflicto entre rapidez y estas reglas, ganan las reglas.
