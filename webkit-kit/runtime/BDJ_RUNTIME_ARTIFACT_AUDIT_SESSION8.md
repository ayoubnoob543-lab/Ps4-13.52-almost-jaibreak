# Auditoría de artefactos BD-J/JVM — Sesión 8

## Alcance

Esta auditoría revisa únicamente el corpus local y los repositorios públicos ya presentes en el workspace, buscando evidencia de `rt.jar`, `bdjstack.jar`, `app0/bdjstack/bdjstack.jar`, `app0/bdjstack/lib/rt.jar`, componentes JVM/BD-J, compiler-agent, `RootCertManager` y `BdjPolicyImpl`. No se ejecutaron exploits, payloads, ELF/BIN/PUPs ni artefactos de PS4.

## Resultado ejecutivo

No se encontró ningún `rt.jar`, `bdjstack.jar`, `sunjce_provider.jar`, `RootCertManager.class/.java`, `BdjPolicyImpl.class/.java` ni snapshot del runtime BD-J de PS4 13.52 en los workspaces auditados.

El corpus contiene **código cliente y documentación histórica**, no el runtime Sony. Los repositorios públicos examinados en sesiones previas —`TheOfficialFloW/bd-jb`, BlueLoader, BD-JB-1250, BDJ-SDK y BDJPlus— muestran cómo se espera interactuar con el runtime, pero no versionan los JAR del sistema PS4. Los JAR del runtime aparecen como dependencias extraídas de un entorno de consola o como bibliotecas que el SDK espera externamente.

## Búsqueda local

Se inspeccionaron estas ubicaciones sin modificar sus archivos:

| Ubicación | Resultado |
|---|---|
| `/home/ubuntu/ps4-bdj-trust-audit` | No hay `rt.jar`, `bdjstack.jar` ni fuentes de `RootCertManager`/`BdjPolicyImpl`; sólo notas, capturas, código cliente histórico y el harness pasivo |
| `/home/ubuntu/firmware-lab-runtime` | No hay artefactos BD-J/JVM; el repositorio contiene documentación WebKit/WPE y herramientas estáticas |
| `/home/ubuntu/firmware-lab-bundle` | No hay artefactos BD-J/JVM identificables |
| `/home/ubuntu/firmware-lab-audit` | No hay artefactos BD-J/JVM identificables |

La búsqueda por nombre exacto no encontró:

```text
rt.jar
bdjstack.jar
sunjce_provider.jar
RootCertManager.java / .class
BdjPolicyImpl.java / .class
```

Tampoco se encontró una ruta local que extraiga esos archivos desde un PUP, `system_ex`, un filesystem PS4 o un dump. No se intentó descifrar ni extraer contenido protegido.

## Corpus público disponible

### `TheOfficialFloW/bd-jb`

Checkout local pasivo: `evidence/bd-jb-src`, HEAD `8a31b642375f320681aebf5c1fbb00b06c321fb4`, 62 commits visibles. Contiene código Java y payload nativo del proyecto, incluyendo adaptadores de `Unsafe`, `ClassLoader$NativeLibrary` y clientes históricos de JIT/compiler-agent. No contiene `rt.jar`, `bdjstack.jar`, `sunjce_provider.jar`, `RootCertManager` ni `BdjPolicyImpl` del sistema PS4.

Clasificación: **STRUCTURAL / HISTORICAL**, no evidencia directa del runtime 13.52.

### BlueLoader y BD-JB-1250

Estos proyectos públicos usan clases BD-J y dependen de bibliotecas del runtime o de un SDK externo. Su estructura permite identificar nombres de paquetes y contratos de integración, pero no aporta los JAR Sony de la consola ni un hash de una copia 13.52.

Clasificación: **STRUCTURAL / DOCUMENTED_ONLY**.

### BDJ-SDK y BDJPlus

El SDK proporciona stubs y herramientas de desarrollo; BDJPlus muestra carga de módulos/JAR y delegación de una fase de escape a componentes externos. Ninguno constituye una copia del bootclasspath o del runtime nativo de PS4.

Clasificación: **PUBLIC_SDK / STRUCTURAL**, no evidencia 13.52.

## Artefactos disponibles y hashes

| Artefacto | Disponible | Procedencia | Hash/identidad |
|---|---|---|---|
| `rt.jar` PS4 13.52 | No | — | MISSING |
| `bdjstack.jar` PS4 13.52 | No | — | MISSING |
| `sunjce_provider.jar` PS4 13.52 | No | — | MISSING |
| `RootCertManager` | Sólo capturas públicas de código, no bytes | Publicación pública; no archivo fuente verificable | Capturas previamente registradas; no hash del código |
| `BdjPolicyImpl` | No hay bytes locales | Referencias históricas/documentales | MISSING |
| `TheOfficialFloW/bd-jb` | Sí, código fuente público | GitHub | HEAD `8a31b642375f320681aebf5c1fbb00b06c321fb4` |
| Harness BD-J pasivo | Sí en workspace aislado, no es runtime | Trabajo local de sesión previa | No es evidencia 13.52 |

La ausencia de un JAR no se convierte en un resultado negativo sobre la implementación de PS4. Sólo significa que el corpus actual no permite analizarlo.

## Preguntas que siguen sin resolver

1. Qué clases y métodos contiene exactamente el `rt.jar` de PS4 13.52.
2. Si `bdjstack.jar` 13.52 contiene las mismas clases, firmas y layouts que las versiones históricas.
3. Si `RootCertManager` y `BdjPolicyImpl` cambiaron sólo en digest/política o también en classloading y permisos.
4. Qué exporta la JVM nativa y qué interfaces existen entre BD-J, compiler-agent y bibliotecas del sistema.
5. Si la demo pública atribuida a ASaudidos usó una ruta Java normal, una política privilegiada, Ixc, reflection, JIT u otra capacidad no documentada.

## Siguiente paso mínimo

El siguiente paso mínimo es obtener de forma autorizada una copia ya accesible de `rt.jar`, `bdjstack.jar` o un snapshot de filesystem/runtime de PS4 13.52 con procedencia verificable. Bastaría inicialmente con un manifiesto de nombres, tamaños, fechas y SHA-256; para responder las preguntas técnicas se necesitarían además los bytes de los JAR y, si la investigación llega a la frontera nativa, metadata estática del módulo JVM/BD-J correspondiente.

El PUP exterior por sí solo no se considera un artefacto analizable en este informe: parsing de contenedor, extracción, descifrado y disponibilidad de un módulo ya accesible son capas distintas. No se realizó ninguna operación criptográfica ni de extracción protegida.

## Estado de publicación

Este archivo es el único cambio nuevo previsto para la publicación de la Sesión 8. No se añaden binarios, workspaces temporales, dumps ni material protegido.

## Referencias públicas

[1]: https://github.com/TheOfficialFloW/bd-jb "TheOfficialFloW/bd-jb"

[2]: https://github.com/kimariin/BlueLoader "BlueLoader"

[3]: https://github.com/ayasns/BD-JB-1250 "BD-JB-1250"

[4]: https://github.com/john-tornblom/bdj-sdk "BDJ-SDK"
