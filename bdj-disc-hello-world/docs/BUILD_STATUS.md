# Build status

## Situación exacta

| Ítem | Estado |
|---|---|
| ISO generada | **Sí** (`build/bdj-hello-world.iso`, 16 MiB, UDF 2.50) |
| Validación Linux (estructura UDF/BDMV) | **Sí** — estática, sin ejecución |
| Carga en PS4 | **Desconocido** — no se ha probado en el reproductor BD-J propietario |
| Hardware test PS4 13.52 | **Pendiente** (`UNVERIFIED`) |
| Hello World = vulnerabilidad | **No** |
| Primitive de seguridad | **No** |
| Escape del sandbox | **No** |
| Ejecución nativa | **No** |
| Acceso al kernel | **No** |
| Impacto Bug Bounty | **No** (sin condición vulnerable ni impacto reproducible) |

## Qué sí tenemos

- ISO BD-J reproducible
- JAR firmado (`BDMV/JAR/00000.jar`)
- BDJO coherente que referencia `org.homebrew.MyXlet`
- Código fuente del Xlet benigno
- Makefile reproducible
- Hashes y metadatos estáticos
- Documentación y paquete textual para revisión

Eso prueba que el disco está **bien construido**, no que contenga un exploit ni que la PS4 13.52 lo acepte.

## Qué no tenemos / no afirmamos

- **No sabemos si carga en la PS4.** La ISO sólo se ha validado en Linux a nivel de estructura UDF/BDMV. No se ha probado en el reproductor BD-J propietario de PS4.
- **Hello World no es una vulnerabilidad.** Sólo demuestra que un Xlet benigno puede inicializarse y dibujar una interfaz *si* la consola lo acepta. Eso es comportamiento normal de BD-J.
- **No hay primitive de seguridad.** No se ha demostrado corrupción de memoria, confusión de tipos, UAF, lectura arbitraria, escritura arbitraria ni ejecución de código.
- **No hay escape del sandbox.** El Xlet no intenta ni demuestra acceso a permisos elevados, rutas protegidas, USB arbitrario, procesos o bibliotecas nativas.
- **No hay ejecución nativa.** No hay ELF, payload, carga dinámica ni llamada a código nativo.
- **No hay acceso al kernel.** El proyecto no contiene ni prueba una cadena hacia kernel execution.
- **No hay evidencia específica de PS4 13.52.** El SDK y la plantilla son públicos y genéricos; no equivalen al runtime propietario de PS4 13.52.
- **No hay impacto para Bug Bounty.** Sin una condición vulnerable y un impacto reproducible, Sony no tendría base para aceptar un reporte como vulnerabilidad.

## Artefactos confirmados (estático)

| Artefacto | SHA-256 |
|---|---|
| `build/bdj-hello-world.iso` | `ad043fc4a1ac6ecd1a9a5cabb876e6daa849d52e5ec1afb3de29822dff148fdb` |
| `build/discdir/BDMV/JAR/00000.jar` | `7cff985677ca0511afeaf35b89f0f7eb0e192708ddb39030734979269fcc7065` |
| `build/discdir/BDMV/BDJO/00000.bdjo` | `d32325af03d55c054fe7766cc96a8bb14cd10a0c5dc06a3a58938f04427cdea5` |

## Flags

- `iso_generated`: `true`
- `hardware_tested`: `false`
- `mode`: `static-only`
- Compatibilidad PS4 13.52: `UNVERIFIED`
- Native usermode / jailbreak / kernel: **fuera de alcance**
