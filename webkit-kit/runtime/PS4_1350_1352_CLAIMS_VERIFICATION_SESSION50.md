# Verificación de claims PS4 13.50→13.52 — sesión 50

## Conclusión ejecutiva

El texto aportado mezcla un hecho oficial con varias explicaciones no demostradas. La fuente oficial citada indirectamente sólo dice que PS4 13.52 incluye correcciones de seguridad. No proporciona funciones, offsets, diff binario ni nombres de vulnerabilidades.

## Evidencia

### 1. Notas de 13.52

Games.gg reproduce la nota oficial de Sony como: "Hemos realizado algunas correcciones de seguridad en el software del sistema". Esto confirma que el firmware es security-focused, pero no especifica kernel UAF, malloc/free, WebKit ni checksums.

Fuente: https://games.gg/es/news/lanzamiento-de-ps4-firmware-1352-notas-completas-del-parche

Clasificación: `DIRECT_PUBLIC_FOR_SECURITY_FIX_ONLY`.

### 2. Exploit chart

ConsoleMods lista exploits públicos hasta 13.00/13.04 y deja 13.50 y 13.52+ sin userland/kernel exploit público. La tabla no aporta un diff técnico de 13.50→13.52.

Fuente: https://consolemods.org/wiki/PS4:Exploit_Chart

Clasificación: `DOCUMENTED_ONLY` para el estado público; no prueba qué cambió internamente.

### 3. PS4 Wee Tools

El README describe herramientas para dumps NOR/Syscon. El changelog documenta soporte hasta 13.04. No es un extractor de PUP/WebKit ni aporta hashes de COREOS/eMMC específicos de 13.52.

Fuente: https://github.com/andy-man/ps4-wee-tools

Clasificación: `DIRECT_PUBLIC_SCOPE`, pero `UNVERIFIED` para cualquier afirmación concreta sobre checksums 13.52.

### 4. Reddit / videos

Los posts y vídeos describen UAF, parches y posibles bugs, pero no aportan el diff binario, funciones, offsets, hashes de módulos o una extracción verificable de `libSceNKWebKit.sprx`.

Clasificación: `DOCUMENTED_ONLY` / `UNVERIFIED`.

## Matriz de claims

| Claim | Estado |
|---|---|
| 13.52 incluye correcciones de seguridad | `DIRECT_PUBLIC` |
| 13.50 tenía un UAF kernel concreto | `DOCUMENTED_ONLY / UNVERIFIED` |
| Sony modificó específicamente malloc/free para cerrar ese UAF | `UNVERIFIED` |
| 13.52 parchó funciones WebKit concretas | `UNVERIFIED` sin módulo/diff |
| 13.52 cambió checksums COREOS/eMMC | `UNVERIFIED` con las fuentes revisadas |
| PS4 Wee Tools puede descifrar WebKit/PUP | `REFUTED_BY_PROJECT_SCOPE` |
| El PUP 13.52 que tenemos es consistente | `DIRECT_LOCAL`, hash/SLB2 verificados |

## Qué sí cambia para nuestra investigación

La evidencia pública confirma que el supuesto cambio 13.50→13.52 es de seguridad, pero no nos da el diferencial exacto. Para demostrarlo necesitamos un diff binario comparable de los mismos módulos o snapshots 13.50 y 13.52. El PUP aislado de 13.52 no permite inferir qué función cambió.

No se ejecutó ningún exploit, payload, binario ni hardware.
