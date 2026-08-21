# PS4 BD-J: contrato histórico del compiler receiver y puente a native usermode

## Alcance

Este informe analiza únicamente fuentes públicas y código/documentación histórica. No usa runtime retail 13.52, PUPs, dumps ni artefactos privados, y no ejecuta exploits, payloads, JAR/ELF/BIN ni código contra hardware.

La conclusión distingue estrictamente `DIRECT_HISTORICAL`, `STRONG_INDIRECT`, `HYPOTHESIS`, `UNVERIFIED_13.52` y `BLOCKED`.

## 1. Contrato histórico de `CompilerAgentRequest`

El informe público de HackerOne #1379975 publica el siguiente contrato histórico para el hilo “compiler receiver”:

```c
typedef struct {
    uint8_t cmd;                 // 0x00
    uint64_t arg0;               // 0x08
    uint64_t arg1;               // 0x10
    uint64_t arg2;               // 0x18
    uint64_t arg3;               // 0x20
    uint64_t arg4;               // 0x28
    uintptr_t runtime_data;       // 0x30
    uintptr_t compiler_data;      // 0x38
    uint64_t data1;               // 0x40
    uint64_t data2;               // 0x48
    uint64_t unk;                 // 0x50
} CompilerAgentRequest;           // 0x58
```

El flujo publicado es:

```c
CompilerAgentRequest req;
while (CompilerAgent::readn(s, &req, sizeof(req)) > 0) {
    uint8_t ack = 0xAA;
    CompilerAgent::writen(s, &ack, sizeof(ack));
    if (req.compiler_data != 0) {
        memcpy(req.compiler_data + 0x28, &req, sizeof(req));
        /* procesamiento posterior no publicado íntegramente */
    }
}
```

La evidencia permite fijar estos puntos:

| Elemento | Estado histórico |
|---|---|
| Tamaño | `0x58` bytes. |
| Campo de control | `cmd` en `0x00`. |
| Cinco argumentos | `arg0`–`arg4` en `0x08`–`0x28`. |
| Datos de runtime | `runtime_data` en `0x30`. |
| Datos del compilador | `compiler_data` en `0x38`. |
| Campos adicionales | `data1` `0x40`, `data2` `0x48`, `unk` `0x50`. |
| Transporte | Descriptor abstracto `s` consumido por `readn`/`writen`. |
| Confirmación | ACK de un byte `0xAA`. |
| Escritura | Copia de `sizeof(req)` a `compiler_data + 0x28` si el puntero no es cero. |

El contrato público **no** fija el número de socket, endpoint, familia de socket, proceso propietario del descriptor, autenticación, framing adicional, endianess negociado, comandos válidos ni validación de rangos. Tampoco publica el código completo de la rutina posterior a `memcpy`.

### Interpretación de seguridad

Históricamente, `compiler_data` era tratado como un puntero de confianza suministrado al receiver. La copia transforma esa confianza en una primitiva de escritura direccionada cuando el proceso atacante puede influir en el contenido recibido y en el destino. El informe relaciona el destino con memoria JIT, pero esto es un hecho histórico de la cadena de 9.00, no una propiedad demostrada de 13.52.

## 2. `JitCompilerReceiverImpl` frente a `JitDefaultImpl`

La búsqueda en los checkouts locales y las fuentes públicas consultadas no encontró implementaciones completas identificables con los nombres exactos **`JitCompilerReceiverImpl`** y **`JitDefaultImpl`**. Las páginas públicas exponen el contrato nativo del receiver y la cadena de explotación, pero no una comparación de esas dos clases.

Por ello no es válido afirmar que:

- `JitCompilerReceiverImpl` sea exactamente el adaptador que abre el descriptor `s`;
- `JitDefaultImpl` sea un fallback seguro o una implementación puramente Java;
- una de ellas exista sin cambios en 13.52;
- sus métodos, firmas, campos u offsets sean los mismos que los del precedente publicado.

La comparación queda **BLOCKED** por ausencia de código fuente o decompilación verificable. El dato que falta es el código de ambas implementaciones o un inventario de clases que muestre sus firmas y relaciones.

## 3. APIs legítimas frente al protocolo privado

`AccessController.doPrivileged`, reflexión y `sun.misc.Unsafe` son APIs/clases Java que históricamente ayudan a preparar el estado del proceso. Sin embargo, el compiler receiver no es una API Java estándar: es un protocolo privado entre componentes nativos/JVM.

La cadena histórica puede separarse así:

| Capa | Función | Naturaleza |
|---|---|---|
| `AccessController`/privilegios | Permitir operaciones que el sandbox normalmente rechazaría. | API Java histórica. |
| Reflexión | Alcanzar clases, campos o métodos internos. | API Java histórica; nombres/layout dependen del runtime. |
| `Unsafe` | Leer/escribir memoria y manipular referencias en el precedente. | API no estándar y runtime-dependiente. |
| `ClassLoader$NativeLibrary.findEntry` | Resolver símbolos mediante una ruta nativa histórica. | Implementación interna, no contrato BD-J portable. |
| Compiler receiver | Recibir estructura, ACK y copiar hacia un destino controlado. | Protocolo privado nativo. |
| JIT memory | Región donde el resultado podía convertirse en instrucciones ejecutables. | Dependencia de JVM/mitigaciones/memoria. |

La existencia de una API legítima no implica que el proceso BD-J pueda abrir el descriptor del compiler receiver ni que el descriptor esté accesible desde Java. Esa frontera —cómo se obtiene el descriptor y qué implementación lo conecta con JIT— es una dependencia imprescindible no publicada.

## 4. Variantes y mitigaciones públicas

La evidencia primaria pública confirma que Sony parcheó o mitigó partes de la cadena BD-J histórica en firmwares posteriores a 9.00. También existen mitigaciones Java históricas relevantes, como el commit OpenJDK `020204a972d9be8a3b2b9e75c2e8abea36d787e9`, que modifica la construcción de objetos durante deserialización mediante dominios de protección e intersección de privilegios.

No se encontró un commit, advisory o writeup público que documente para PS4 13.52:

- el tamaño actual de `CompilerAgentRequest`;
- validación de `compiler_data`;
- cierre o autenticación del descriptor;
- cambios en `JitCompilerReceiverImpl` o `JitDefaultImpl`;
- eliminación del JIT o cambio RW→RX;
- modificación de `NativeLibrary.findEntry`;
- un compiler-agent alternativo.

PSX-Place y Habr corroboran el mismo layout y flujo de HackerOne, pero son reproducciones/traducciones, no implementaciones independientes. Por tanto, elevan la confianza en el precedente publicado, no en su conservación posterior.

## 5. Rutas alternativas a native usermode

La deserialización privilegiada de `userprefs` y `com.oracle.security.Service.newInstance`/`ProviderAdapter` son rutas históricas alternativas para obtener construcción o reflexión privilegiada. No proporcionan por sí solas un entrypoint nativo. JNI/`loadLibrary` y callbacks propietarios son posibilidades abstractas sin evidencia PS4 13.52. UDF es una superficie de kernel separada y no constituye un puente Java→native usermode.

El candidato más fuerte sigue siendo el **compiler receiver**, porque el informe público conecta explícitamente su copia con memoria JIT y ejecución de payloads. La deserialización y `ProviderAdapter` sólo podrían ser rutas de preparación de privilegios o classloading.

## 6. Tabla de evaluación

| Mecanismo | Evidencia histórica | Evidencia 13.52 | Mitigación conocida | Dependencias imprescindibles | Qué lo refutaría | Confianza |
|---|---|---|---|---|---|---|
| `CompilerAgentRequest`/receiver | Estructura `0x58`, ACK `0xAA`, `compiler_data` en `0x38`, copia a `+0x28`, publicada por HackerOne. | Ninguna. | Posible validación de punteros, cambio de ABI, cierre del descriptor o eliminación del receiver; no documentado para 13.52. | Receiver accesible, framing/descriptor, layout vigente, memoria JIT direccionable y ejecutable. | Código/metadata 13.52 que elimine o valide la ruta. | `DIRECT_HISTORICAL / UNVERIFIED_13.52` |
| `JitCompilerReceiverImpl` | No hay código público verificable con ese nombre. | Ninguna. | Desconocida. | Clase, firmas y relación con receiver. | Inventario o código que muestre ausencia. | `BLOCKED` |
| `JitDefaultImpl` | No hay código público verificable con ese nombre. | Ninguna. | Desconocida. | Clase y selección del backend JIT. | Igual. | `BLOCKED` |
| `Unsafe` + objetos/memoria | Documentado en presentación BD-JB y reimplementaciones históricas. | Ninguna. | Restricción de reflexión, eliminación de `Unsafe`, cambios de layout. | Clase presente, acceso a `theUnsafe`, métodos y layout compatibles. | Runtime sin clase/campo/métodos o con checks nuevos. | `DIRECT_HISTORICAL / UNVERIFIED_13.52` |
| `NativeLibrary.findEntry` | Documentado como vía histórica a `sceKernelDlsym`. | Ninguna. | Cambio de clase, firma, visibilidad o resolución. | Clase interna, reflexión, biblioteca cargada y símbolo. | Ausencia o método incompatible. | `DIRECT_HISTORICAL / UNVERIFIED_13.52` |
| Deserialización privilegiada | `UserPreferenceManagerImpl` + `ObjectInputStream` en #1379975. | Ninguna. | OpenJDK `020204a…` y posibles filtros/validaciones. | Archivo controlable, gadget, constructor y protección relajada. | Filtro/constructor protegido. | `DIRECT_HISTORICAL / UNVERIFIED_13.52` |
| `Service.newInstance`/`ProviderAdapter` | Código reportado en #1379975. | Ninguna. | Validación de registro o cambios de proveedor. | Clases propietarias, accessor sustituible y constructor público. | Clase ausente o validación no evadible. | `DIRECT_HISTORICAL / HYPOTHESIS` |
| JNI/`loadLibrary`/callbacks | Sólo contratos Java SE y precedentes generales. | Ninguna. | Perfil BD-J/política y ausencia de bibliotecas. | JNI exportado, biblioteca aceptada y callback. | No hay clase, símbolo o biblioteca accesible. | `HYPOTHESIS` |

## 7. Relación hipotética con BD-J userland 13.52

La demostración pública de BD-J userland 13.52, sin código ni trazas, no permite saber si alcanzó `AllPermission`, desactivó el SecurityManager, obtuvo acceso a `Unsafe`, llamó a `NativeLibrary`, alcanzó un compiler receiver o sólo ejecutó Java dentro del sandbox.

La hipótesis técnicamente más fuerte es que, si la demostración llegó a native usermode, tuvo que conservarse una interfaz equivalente a la cadena **privilegios → internals JVM → acceso a memoria/símbolos → mecanismo de ejecución**. El compiler receiver histórico es el candidato más fuerte porque tiene un contrato de escritura explícito, pero no se puede inferir su conservación en 13.52.

## Pieza exacta faltante

Para demostrar o refutar el puente en 13.52 se necesita al menos uno de estos artefactos legítimos:

1. Código/decompilación verificable de `JitCompilerReceiverImpl` y `JitDefaultImpl`.
2. Metadata de la JVM/BD-J que identifique el descriptor, canal, símbolos y tamaño actual de la estructura.
3. Un diff de runtime que muestre validación de `compiler_data`, cierre del receiver o cambios RW→RX.
4. Un stack trace/log/captura técnica donde aparezcan el compiler-agent, `NativeLibrary`, `Unsafe` o el símbolo de resolución.

Sin alguno de esos elementos, el máximo demostrable es el contrato histórico de 9.00 y una relación hipotética con 13.52.

## Conclusión

El candidato técnicamente más fuerte investigable sin runtime privado es **CompilerAgentRequest/compiler receiver**, no porque se haya demostrado en 13.52, sino porque es la única fuente pública que especifica una estructura, transporte abstracto, ACK y escritura direccionada conectada explícitamente con memoria JIT.

La comparación `JitCompilerReceiverImpl` frente a `JitDefaultImpl` queda bloqueada por ausencia de código público verificable. La pieza de mayor valor es una decompilación o manifest de la JVM/BD-J que revele esas clases y el contrato vigente. Hasta obtenerla, la clasificación correcta para 13.52 es **UNVERIFIED**, no A ni B.

## Referencias

[1]: https://hackerone.com/reports/1379975 — PlayStation report #1379975, bd-j exploit chain.

[2]: https://www.psx-place.com/threads/update-2-thefl0w-discloses%22blu-ray-disc-java-sandbox-escape-vulnerabilities-ps3-ps4-ps5.37554/ — PSX-Place reproduction and discussion of the disclosure.

[3]: https://habr.com/ru/articles/671088/ — Habr translation/reproduction of the chain.

[4]: https://elhacker.info/Books/BOOKS%20PART%206/hardwear_io_bd_jb-.pdf — Public BD-JB presentation.

[5]: https://github.com/openjdk/jdk/commit/020204a972d9be8a3b2b9e75c2e8abea36d787e9 — OpenJDK deserialization-construction mitigation.
