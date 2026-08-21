# Investigación independiente del compiler-agent/JIT de BD-J

## Alcance y clasificación

Este informe analiza únicamente el contrato histórico del compiler receiver y sus dos adaptadores JIT públicos conservados localmente. No descarga PUPs, dumps o firmware privado, no ejecuta exploits/protocolos/artefactos y no interactúa con hardware.

Las categorías son:

- **DIRECT_13.52**: evidencia verificable que identifica bytes, metadata o comportamiento de PS4 13.52.
- **INDIRECT_13.52**: evidencia temporal o de soporte que aproxima 13.52, pero no identifica el contrato actual.
- **HISTORICAL_ONLY**: evidencia directa de una revisión histórica o del cliente público antiguo.
- **HYPOTHESIS**: posibilidad técnica que requiere una condición no demostrada.
- **DISCARDED**: hipótesis incompatible con la evidencia disponible.

## Resultado ejecutivo

El contrato histórico del receiver queda reconstruido con alta precisión: recibe una estructura de `0x58` bytes, devuelve un ACK de un byte `0xAA` y, si `compiler_data` no es nulo, copia la petición a `compiler_data + 0x28`. La implementación pública histórica `JitCompilerReceiverImpl` añade la obtención de símbolos, localización de `BufferBlob::create`, descubrimiento del descriptor/socket del compiler-agent, reserva de memoria JIT y copia por chunks.

La ruta alternativa `JitDefaultImpl` no usa el compiler-agent: resuelve APIs legítimas `sceKernelJitCreateSharedMemory`, `sceKernelJitCreateAliasOfSharedMemory` y `sceKernelJitMapSharedMemory`, crea alias RW/RX y copia datos mediante `memcpy`. Es una API JIT legítima separada del protocolo privado.

No se encontró evidencia **DIRECT_13.52** del receiver, del descriptor, de la estructura vigente ni de las clases `JitCompilerReceiverImpl`/`JitDefaultImpl` en ese firmware. El primer punto no demostrado es la existencia y accesibilidad del **compiler-agent/descriptor** en PS4 13.52; antes de eso no se puede inferir compatibilidad a partir del layout histórico.

## 1. Contrato histórico de `CompilerAgentRequest`

La estructura publicada por el reporte de PlayStation #1379975 es:

```c
typedef struct {
    uint8_t  cmd;                 // 0x00
    uint64_t arg0;                // 0x08
    uint64_t arg1;                // 0x10
    uint64_t arg2;                // 0x18
    uint64_t arg3;                // 0x20
    uint64_t arg4;                // 0x28
    uintptr_t runtime_data;       // 0x30
    uintptr_t compiler_data;      // 0x38
    uint64_t data1;               // 0x40
    uint64_t data2;               // 0x48
    uint64_t unk;                 // 0x50
} CompilerAgentRequest;           // 0x58
```

El receiver histórico publicado se comporta conceptualmente así:

```c
CompilerAgentRequest req;
while (CompilerAgent::readn(s, &req, sizeof(req)) > 0) {
    uint8_t ack = 0xAA;
    CompilerAgent::writen(s, &ack, sizeof(ack));
    if (req.compiler_data != 0)
        memcpy(req.compiler_data + 0x28, &req, sizeof(req));
}
```

| Campo | Offset | Evidencia histórica |
|---|---:|---|
| `cmd` | `0x00` | Campo de control publicado |
| `arg0`–`arg4` | `0x08`–`0x28` | Cinco argumentos de 64 bits |
| `runtime_data` | `0x30` | Puntero/dato asociado al runtime |
| `compiler_data` | `0x38` | Puntero usado por la copia posterior |
| `data1` | `0x40` | Campo adicional |
| `data2` | `0x48` | Campo adicional |
| `unk` | `0x50` | Campo no identificado |
| Tamaño total | `0x58` | Tamaño publicado |
| ACK | 1 byte, `0xAA` | Confirmación publicada |

El contrato público no especifica familia de socket, endpoint, proceso propietario del descriptor, autenticación, endianess negociado, comandos válidos, framing adicional ni validaciones de rangos. Tampoco publica íntegramente el procesamiento posterior a `memcpy`. Por tanto, sólo el layout y el patrón de ACK/copia están confirmados históricamente.

## 2. `JitCompilerReceiverImpl`: contrato del cliente histórico

El archivo local `historical_JitCompilerReceiverImpl.java` identifica la implementación como un adaptador que usa el protocolo vulnerable del runtime compiler-agent. Sus elementos relevantes son:

| Elemento | Comportamiento histórico |
|---|---|
| Reserva | `MAX_CODE_SIZE = 24 * 1024 * 1024`; el comentario indica que se reservan 8 MiB para el JIT Java de un total de 32 MiB de memoria de código |
| Tamaño de request | `COMPILER_AGENT_REQUEST_SIZE = 0x58` |
| ACK | `ACK_MAGIC_NUMBER = 0xAA` |
| Símbolos | `sceKernelGetModuleInfo`, `read`, `write` |
| Handles | `API.LIBKERNEL_MODULE_HANDLE` para resolver los símbolos |
| Metadata | `SCE_KERNEL_MODULE_INFO_SIZE = 0x160` |
| Descubrimiento de módulo | Obtiene base y tamaño del módulo BD-J desde offsets del buffer de información |
| Helper JIT | Busca una secuencia asociada a `BufferBlob::create` |
| Socket | Busca otra secuencia asociada al hilo sender del compiler-agent y lee el descriptor mediante una expresión RIP-relative |
| Copia | Divide el buffer en chunks, pone `dest + i - 0x28` en `req` en `0x38`, escribe `0x58` bytes y espera ACK |

El cliente valida algunos prerrequisitos locales: símbolos no nulos, éxito de `sceKernelGetModuleInfo`, presencia de las secuencias binarias, tamaño máximo y respuesta exacta `0xAA`. Estas validaciones pertenecen al **adaptador histórico del cliente**, no prueban que el receiver nativo validara el puntero recibido.

El contrato es especialmente frágil porque depende de:

1. nombres/exportaciones de símbolos;
2. layout de `SceKernelModuleInfo` y offsets del módulo;
3. patrones de instrucciones para localizar `BufferBlob::create` y el descriptor;
4. estructura de `0x58` bytes;
5. semántica del campo `compiler_data`;
6. memoria JIT direccionable con la misma relación `dest - 0x28`;
7. descriptor/socket accesible desde el proceso BD-J.

Toda esta sección es **HISTORICAL_ONLY**.

## 3. `JitDefaultImpl`: API JIT legítima

La implementación alternativa `historical_JitDefaultImpl.java` no utiliza el compiler receiver. Resuelve mediante `dlsym` tres APIs:

```text
sceKernelJitCreateSharedMemory
sceKernelJitCreateAliasOfSharedMemory
sceKernelJitMapSharedMemory
```

Después crea una región compartida, un alias con permisos RW, un mapeo RX y copia desde el alias RW hacia la región RX mediante `memcpy`. El uso de una región RW y otra RX es una arquitectura explícita de alias de memoria; no es equivalente al protocolo privado de escritura mediante `compiler_data`.

| Ruta | Naturaleza | Dependencia |
|---|---|---|
| `JitDefaultImpl` | API JIT legítima | Exportaciones `sceKernelJit*`, permisos y semántica de memoria vigentes |
| `JitCompilerReceiverImpl` | Protocolo privado histórico | Descriptor, layout, receiver, `BufferBlob::create`, patrón de socket y copia direccionada |

La existencia histórica de las APIs `sceKernelJit*` no demuestra que estén exportadas o accesibles en 13.52. Esa afirmación sería **HYPOTHESIS**.

## 4. Validaciones y posibles mitigaciones

El receiver publicado no muestra validaciones de:

- que `compiler_data` apunte a una región perteneciente al compilador;
- que `compiler_data + 0x28` esté dentro de un buffer asignado;
- que el destino sea RW o RX autorizado;
- que `cmd` y los argumentos estén dentro de un conjunto válido;
- que el descriptor proceda del runtime legítimo;
- que exista autenticación o identidad del emisor;
- que el tamaño recibido sea distinto de `sizeof(req)` sólo cuando corresponda;
- que la operación de copia no cruce límites de la región de memoria.

Una mitigación en cualquiera de estos puntos rompería la primitiva histórica. También la romperían:

| Mitigación posible | Punto roto | Estado para 13.52 |
|---|---|---|
| Validación de puntero/intervalo de `compiler_data` | Escritura direccionada | **HYPOTHESIS** |
| Cambio de layout/tamaño/endianness | Interpretación del request | **HYPOTHESIS** |
| Eliminación o cierre del descriptor | Acceso al receiver | **HYPOTHESIS** |
| Autenticación del canal | Entrada no confiable | **HYPOTHESIS** |
| Sustitución por copia a buffer interno | `memcpy` hacia destino externo | **HYPOTHESIS** |
| Separación estricta de permisos JIT | Conversión de escritura a código ejecutable | **HYPOTHESIS** |
| Eliminación del compiler-agent | Toda la ruta privada | **HYPOTHESIS** |
| Cambio de patrones de `BufferBlob::create` o sender thread | Adaptador no encuentra helpers/socket | **HYPOTHESIS** |

No existe evidencia pública que asigne alguna de estas mitigaciones concretamente a PS4 13.52.

## 5. Cambios públicos y alcance temporal

Las reproducciones públicas de la divulgación indican que la cadena `bd-jb` fue probada en PS4 9.00 y que TheOfficialFloW comunicó que fue corregida en PS4 9.50. Esto es evidencia temporal de que el conjunto histórico completo no debe asumirse presente después de 9.50, pero no identifica cuál componente fue cambiado ni cómo se modificó el receiver [1] [2] [3].

No se encontró un commit público de Sony, un changelog o una decompilación que documente específicamente:

- un nuevo tamaño de `CompilerAgentRequest`;
- validaciones de `compiler_data`;
- cierre/autenticación del descriptor;
- eliminación de `JitCompilerReceiverImpl`;
- sustitución por `JitDefaultImpl`;
- cambios de `BufferBlob::create`;
- cambios de permisos RW/RX;
- la presencia o ausencia del compiler-agent en PS4 13.52.

Por ello, la afirmación “la cadena fue mitigada antes de 13.52” es **INDIRECT_13.52** sólo en el sentido de que la divulgación pública dice que el conjunto fue corregido en 9.50. La forma exacta de la mitigación es **UNVERIFIED**.

## 6. Matriz de conclusiones

| Hallazgo | Clasificación | Razón |
|---|---|---|
| Request de `0x58` bytes con `compiler_data` en `0x38` | **HISTORICAL_ONLY** | Publicado por #1379975 y reproducido por fuentes secundarias |
| ACK `0xAA` | **HISTORICAL_ONLY** | Publicado en el flujo del receiver |
| Copia a `compiler_data + 0x28` | **HISTORICAL_ONLY** | Publicada explícitamente; no prueba conservación posterior |
| `JitCompilerReceiverImpl` usa `read`, `write`, `sceKernelGetModuleInfo` | **HISTORICAL_ONLY** | Archivo histórico local verificable |
| Descubrimiento por firmas de `BufferBlob::create` y sender thread | **HISTORICAL_ONLY** | Código adaptador histórico |
| `JitDefaultImpl` usa `sceKernelJit*` y alias RW/RX | **HISTORICAL_ONLY** | Código adaptador histórico |
| El protocolo privado y la API JIT legítima son rutas distintas | **HISTORICAL_ONLY** | Contratos de las dos implementaciones |
| El conjunto histórico fue corregido en 9.50 | **INDIRECT_13.52** | Reproducciones públicas citan la comunicación de TheOfficialFloW |
| El receiver actual de 13.52 mantiene el layout | **HYPOTHESIS** | Sin bytes/metadata 13.52 |
| 13.52 valida `compiler_data` | **HYPOTHESIS** | Mitigación posible, no documentada |
| 13.52 elimina el compiler-agent | **HYPOTHESIS** | Mitigación posible, no documentada |
| Existe `JitCompilerReceiverImpl` en 13.52 | **HYPOTHESIS** | Nombre histórico no es evidencia de presencia |
| El vídeo público de BD-J 13.52 demuestra esta ruta | **DISCARDED** | No muestra símbolos, contrato, logs ni primitive JIT |
| El JIT legítimo `sceKernelJit*` equivale al receiver vulnerable | **DISCARDED** | Son mecanismos distintos |

## 7. Primer punto que podría romperse

El primer punto técnico que debe comprobarse para 13.52 es el **descriptor/receiver**, no la memoria JIT. Aunque `Unsafe`, `dlsym` o APIs JIT existieran, la cadena no podría usar el contrato histórico si el proceso BD-J no puede obtener el descriptor correcto o si el receiver ya no acepta la estructura antigua.

El segundo punto es el layout: una diferencia en tamaño, offsets, endianess, framing o interpretación de `compiler_data` invalida el adaptador histórico. El tercer punto es la validación del destino y de los permisos de memoria.

## 8. Evidencia mínima faltante

Para confirmar o descartar compatibilidad con 13.52 se necesita, como mínimo, una fuente pública verificable que revele uno de los siguientes elementos:

1. código/decompilación del receiver o de su proceso propietario;
2. metadata de una clase/módulo que muestre el descriptor, socket, símbolos y tamaño de request;
3. una comparación de firmware que identifique la mitigación concreta;
4. un inventario de `sceKernelJit*`, `BufferBlob::create`, `read`, `write` y `sceKernelGetModuleInfo` en la build 13.52.

Sin uno de esos elementos, no puede determinarse si 13.52 conserva, modifica o elimina la ruta histórica.

## Conclusión

El contrato histórico queda **DIRECT/HISTORICAL**: `0x58` bytes, `compiler_data` en `0x38`, ACK `0xAA`, copia a `+0x28`, descriptor abstracto y un adaptador que localiza socket/helpers mediante símbolos y firmas. `JitDefaultImpl` es una ruta JIT legítima distinta basada en `sceKernelJit*`.

La evidencia pública de que `bd-jb` fue corregido en 9.50 es **INDIRECT_13.52**, pero no identifica la mitigación. No hay evidencia **DIRECT_13.52**. El primer punto no demostrado es la disponibilidad y semántica del compiler receiver/descriptor en 13.52; el segundo es la validez del layout. La ruta histórica debe permanecer **UNVERIFIED**, no confirmada ni descartada para 13.52.

## Referencias

[1]: https://hackerone.com/reports/1379975 "PlayStation report #1379975: bd-j exploit chain"

[2]: https://www.psx-place.com/threads/update-2-thefl0w-discloses-blu-ray-disc-java-sandbox-escape-vulnerabilities-ps3-ps4-ps5.37554/ "PSX-Place reproduction of the BD-JB disclosure"

[3]: https://habr.com/ru/articles/671088/ "Habr reproduction of the PlayStation BD-J exploit chain"

[4]: https://elhacker.info/Books/BOOKS%20PART%206/hardwear_io_bd_jb-.pdf "Public BD-JB presentation material"
