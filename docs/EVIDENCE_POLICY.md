# Política de evidencia

## Etiquetas permitidas

| Etiqueta | Uso |
|---|---|
| `VERIFIED` | Bytes o ejecución reproducible sobre el firmware exacto, con hash y método registrados. |
| `VERIFIED_METADATA` | Contenedor, tamaño, hash o estructura verificados, sin afirmar el contenido interno. |
| `CORROBORATED` | Apoyo independiente o comprobación parcial; todavía no equivale a validación completa. |
| `SOURCE_ONLY` | Tabla, código, README, commit o claim público sin validación independiente del objetivo. |
| `HISTORICAL_ONLY` | Evidencia correcta para otra versión, no transferible automáticamente. |
| `UNVERIFIED` | Hipótesis plausible sin prueba suficiente. |
| `MISSING` | Artefacto o prueba necesaria no disponible. |
| `NOT_REPRODUCIBLE` | La cadena o resultado no puede repetirse con el corpus actual. |

## Reglas

Una etiqueta `VERIFIED` siempre debe acompañarse de versión exacta, fuente, commit o URL, tamaño, SHA-256, método y resultado. Una coincidencia de offset en dos forks no es independencia si ambos derivan del mismo origen. Un hash de un contenedor no valida módulos cifrados dentro de él. Un crash no es un leak; un leak no es escritura arbitraria; escritura arbitraria no es jailbreak.

Las palabras “funciona”, “confirmado”, “completo”, “soporte” y “jailbreak” deben especificar si se refieren a userland, un parser, un host-side smoke test, una build o hardware real. Si no se puede especificar, usar `UNVERIFIED`.

## Métricas

No se usarán porcentajes agregados de progreso en README o documentos de estado. Los porcentajes mezclaban cobertura, compilabilidad, cantidad de bytes y probabilidad de éxito. El estado se expresará como una matriz de componentes con etiquetas y bloqueadores concretos.

## Hardware y artefactos sensibles

Los experimentos con consola requieren una nota de alcance, riesgo, firmware, build, fecha y log. El repositorio no ejecuta automáticamente exploits ni payloads recuperados. No se publican claves, credenciales, dumps propietarios o artefactos sin procedencia legal y técnica.
