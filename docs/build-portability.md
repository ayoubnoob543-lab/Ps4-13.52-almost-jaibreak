# Portabilidad del pipeline de build (`build.sh`)

## Alcance

`build.sh` construye el HEN del laboratorio: `kpayload/` → `installer/` → `hen.bin`
(514784 B con los PRX actuales). Este documento describe la adaptación que hace el
pipeline ejecutable tanto en hosts x86_64 nativos (CI Ubuntu original) como en hosts
ARM64 sin binutils multi-arquitectura (por ejemplo Termux/aarch64), sin alterar la
semántica del payload.

## Qué estaba roto en hosts no-x86_64

| Síntoma | Causa raíz |
|---|---|
| `error: unsupported argument 'btver2' to option '-march='` | Los Makefiles asumían gcc x86_64 nativo; en ARM64 el driver apunta a aarch64 |
| `ld.lld: discarding .shstrtab section is not allowed` | `kpayload/linker.x` descartaba `*(*)` en `/DISCARD/`; GNU ld lo toleraba, lld no |
| `fatal error: 'asm/types.h' file not found` | Cabeceras del sistema incompletas en el entorno (fix de entorno, no del repo) |
| Colisión `elf64_phdr`/`elf64_shdr` | `<elf.h>` uapi de linux choca con `elf_helper.h`; el include en `hooks.h` era legacy sin uso |
| `typedef redefinition` de `wchar_t`, asm rechazado en el SDK | El submódulo pineado mezcla estilos que GNU as/gcc aceptaban y LLVM no |

## Estrategia de adaptación

1. **Detección de modo x86_64** (`kpayload/Makefile`, `installer/Makefile`):
   - Modo `native`: el compilador acepta `-march=btver2 -m64` tal cual (hosts x86_64;
     flags idénticos al histórico, salida inalterada).
   - Modo `cross-clang`: se añade `--target=x86_64-unknown-freebsd13.0 -fuse-ld=lld`,
     se usa `llvm-objcopy`/`llvm-ar` si existen y **se omite `-masm=intel`** porque el
     asm inline de este árbol es AT&T y el IAS de clang no tolera mezclar dialectos.
   - Si nada es viable, el build falla con mensaje explícito (sin builds silenciosos
     para la arquitectura equivocada).
2. **libPS4.a desde copia parcheada** (`installer/build/sdk-libps4/`): el submódulo
   permanece intacto y pineado; la regla copia su árbol, aplica `installer/patches/*`
   y compila ahí. Parches mínimos, cada uno documentado en su cabecera:
   - `types.h`: `wchar_t` vuelve al tipo builtin `int` (ABI-correcto; clang lo
     predefine y rechaza el typedef divergente).
   - `syscall.h`: el macro `SYSCALL` pasa a un único bloque asm con `.intel_syntax`
     embebida y `mov` en lugar de `movq` (el IAS de LLVM no mantiene estado de
     dialecto entre strings ni admite `movq reg,imm` en intel).
   - `syscall.s`: mismos ajustes de mnemónico.
3. **linker.x**: `.shstrtab 0 : { *(.shstrtab) }` antes del descarte comodín.
   Sección non-alloc: irrelevante para `objcopy -O binary`, compatible GNU/lld.
4. **Leniencia de warnings heredados**: `-Wno-error=int-conversion` etc., porque los
   compiladores modernos promueven a error patrones C-legacy del código de research
   (p. ej. `NULL` donde va `int`). Sin cambios semánticos.
5. **Shebangs**: `#!/usr/bin/env bash`. En Android/Termux invocar como
   `bash build.sh` (no existe `/usr/bin/env` a nivel raíz del sistema).

## Herramientas de análisis estático

`tools/analyze_xref_versions.py` ahora prueba `objdump` y `llvm-objdump` y cae a
Capstone si ningún binario sabe desensamblar x86-64 (los binutils restringidos por
arquitectura antes mataban la herramienta). Los tests de smoke GTK del host
(`test_modern_webkitgtk`, `test_homebrew_jsc`) hacen skip con razón explícita cuando
faltan `webkit2gtk-4.1` / `javascriptcoregtk-4.1` / `xvfb-run`; siguen activos en CI.

## Verificación en este entorno (ARM64 + clang 21.1.8, 2026-08-24)

```text
bash build.sh                 -> exit 0, hen.bin generado
unittest discover -s tests    -> 31 tests OK (4 skipped justificados)
tools/check_env.sh            -> ENV_PREFLIGHT_PASS (mode=cross-clang)
```

Rebuild local del payload registrado en `ARTIFACTS.md` (hash `38bf58bb…`); el
artefacto canónico `hen.bin` (`32570b6e…`) no se modifica: otro compilador produce
bytes distintos y la identidad del artefacto histórico se preserva.

## Límites

Compilar aquí demuestra que el pipeline es reproducible como *procesamiento de
código*; no valida ABI de consola, offsets de kernel ni ejecución en hardware. La
validez de offsets sigue gobernada por las clasificaciones de evidencia del README.
