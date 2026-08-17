# Porting estático de PSFree 8.50/8.52 hacia PS4 13.52

## Alcance y límite de seguridad

Este documento audita código y tablas históricas de PSFree, Vue-After-Free y el loader de Linux. El objetivo es identificar contratos conceptuales, dependencias de build y requisitos de verificación. No implementa ni valida una cadena JOP/ROP funcional, no ejecuta JavaScript, no aplica parches kernel y no demuestra compatibilidad runtime en 13.52.

La revisión de PSFree está fijada en el commit `368d82aa40d3017c220757ce315761adb5f06678`. El clon actual contiene un cargador firmware específico para `0x800`–`0x900` (`rop/900.mjs`); no contiene una tabla WebKit independiente para 8.50/8.52. Las referencias a 8.03 aparecen en comentarios y en el flujo de dumping. Los datos 8.50/8.52 disponibles en el corpus proceden principalmente de Vue-After-Free, no de un dump WebKit 8.50/8.52.

## Resumen de clasificación

| Categoría | Significado en esta auditoría |
|---|---|
| `PORTABLE` | Algoritmo o contrato conceptual reutilizable, pero sus entradas deben recalcularse. |
| `FIRMWARE_DEPENDENT` | Campo, offset, ABI interno, vtable, segmento o gadget que depende de la build. |
| `OBSOLETE` | Dato histórico que no debe portarse como valor a 13.52. |
| `REQUIRES_REANALYSIS` | Debe localizarse por bytes/XREFs en la imagen objetivo. |
| `UNVERIFIED` | Mención o tabla sin bytes de la build objetivo. |

## 1. Estructuras WebKit/JSC

Las constantes de `PSFree/module/offset.mjs` son las siguientes. Aunque algunas coinciden con layouts conocidos de WebKit/JSC, el propio uso está documentado alrededor de WebKit PS4 8.03; no son offsets confirmados para 13.52.

| Componente | Referencia histórica PSFree | Uso | Hipótesis 13.52 | Qué verificar | Prioridad |
|---|---:|---|---|---|---:|
| `JSC::JSObject::m_cell` | `0x00` | Cabecera del objeto | `FIRMWARE_DEPENDENT` | Bytes de un objeto conocido y vtable/mapa de clase | Alta |
| `JSC::JSObject::m_butterfly` | `0x08` | Acceso a propiedades fuera de línea | `FIRMWARE_DEPENDENT` | Layout de `JSObject` y representación de butterfly | Alta |
| `JSC::JSObject` inline properties | `0x10` | Inicio de JSValues inline | `FIRMWARE_DEPENDENT` | `sizeof(JSObject)` y número de inline slots | Alta |
| `JSC::JSArrayBufferView::m_vector` | `0x10` | Convertir una vista en lectura/escritura de memoria | `REQUIRES_REANALYSIS` | Firma de clase, m_mode y manejo GC en WebKit 13.52 | Crítica |
| `JSArrayBufferView::m_length` | `0x18` | Tamaño usado por `make_buffer` | `REQUIRES_REANALYSIS` | Bytes de un TypedArray/ArrayBufferView de 13.52 | Crítica |
| `JSArrayBufferView::m_mode` | `0x1c` | Diferenciar modos de TypedArray | `REQUIRES_REANALYSIS` | Enum y layout de `JSArrayBufferView` objetivo | Alta |
| `WTF::StringImpl::m_length` | `0x04` | Manipulación del tamaño de cadena | `REQUIRES_REANALYSIS` | Layout de `StringImpl` y representación 8-bit/16-bit | Crítica |
| `WTF::StringImpl::m_data` | `0x08` | Redirección temporal de datos | `REQUIRES_REANALYSIS` | Bytes de `StringImpl` en la build objetivo | Crítica |
| `StringImpl` inline data | `0x14` | Marker/string spray | `REQUIRES_REANALYSIS` | Umbral y almacenamiento inline de la build | Alta |
| `StringImpl` size | `0x18` | Tamaño asumido por el spray | `REQUIRES_REANALYSIS` | Constructor/destructor y allocator de 13.52 | Alta |
| `JSHTMLTextAreaElement::m_wrapped` | `0x18` | Obtención del `HTMLTextAreaElement` nativo | `REQUIRES_REANALYSIS` | Herencia JSObject→wrapper y vtable en WebKit 13.52 | Crítica |
| `JSHTMLTextAreaElement` size | `0x20` | Tamaño histórico | `UNVERIFIED` | `sizeof` real de la clase en 13.52 | Alta |
| `CustomGetterSetter` | `JSFunction + 0x28`, getter en `+0x08` | Resolver getter nativo de `scrollLeft` | `FIRMWARE_DEPENDENT` | Layout de `JSCustomGetterSetterFunction` y XREF a getter | Crítica |
| Butterfly | `m_butterfly` indirecto | Propiedades fuera de línea/fake object | `REQUIRES_REANALYSIS` | Estructura de butterfly, capacidad y punteros de 13.52 | Crítica |
| Vtable | `HTMLTextAreaElement* + 0` | Identificar módulo y disparar getter histórico | `REQUIRES_REANALYSIS` | Vtable real y entrada getter en `.relro` de 13.52 | Crítica |

### Observaciones estructurales

La operación `addrof`/`fakeobj` no depende sólo de un número. Requiere que la representación de JSValue, la cabecera de `JSObject`, el butterfly y la gestión de GC mantengan contratos compatibles. En 13.52 deben verificarse por bytes y comportamiento estático de las funciones correspondientes; no es válido aplicar una resta o delta desde 8.50/8.52.

`make_buffer()` cambia temporalmente `m_vector` y `m_length` de un TypedArray. El comentario del código explica que se elige un TypedArray oversize para evitar ciertos caminos de GC. La estrategia conceptual es `PORTABLE`, pero los offsets y las reglas de `m_mode` son `REQUIRES_REANALYSIS`.

El flujo de cadenas usa `StringImpl::m_data`, `m_length` y almacenamiento inline. El hecho de que el spray use strings de 8 bits y `Error(...).message` para obtener una nueva representación es una hipótesis específica de la implementación WebKit histórica. Para 13.52 deben verificarse allocator, longitud de `JSString`, flags de `StringImpl` y destrucción.

## 2. Resolución de módulos

### 2.1 Descubrimiento de la base

`PSFree/module/memtools.mjs` implementa `find_base()` mediante una búsqueda por páginas de 16 KiB y dos firmas históricas: una firma de inicio de `.text` y otra de `PT_SCE_MODULE_PARAM` en `.data`. El algoritmo de caminar páginas es `PORTABLE`; las firmas y el tamaño de página son `FIRMWARE_DEPENDENT` o deben confirmarse para la imagen objetivo.

| Operación | 8.50/8.52 | 13.52 | Clasificación |
|---|---|---|---|
| Tamaño de página de PS4 | `0x4000` | No debe asumirse sin contexto de módulo | `REQUIRES_REANALYSIS` |
| Firma `.text` | `55 48 89 e5 41 56 41 53 48 83...` | Buscar en bytes reales | `REQUIRES_REANALYSIS` |
| Firma `.data`/module param | Comentada para 8.00/8.03: `0x20`, `0x3c13f4bf`, `0x2` | Buscar en `PT_SCE_MODULE_PARAM` real | `REQUIRES_REANALYSIS` |
| Búsqueda hacia atrás/adelante | Escaneo por páginas | Reutilizable si se adapta al formato | `PORTABLE` |

La existencia de un patrón de prólogo no prueba por sí misma la identidad del módulo. En 13.52 el resultado debe comprobarse con límites de segmento, cabeceras o referencias internas.

### 2.2 `libSceNKWebKit.sprx`

El flujo de `send.mjs` obtiene un `HTMLTextAreaElement` y sigue `JSHTMLTextAreaElement + 0x18` hasta el objeto DOM; desde allí lee la vtable y busca su base. El offset `0x18` es histórico y `FIRMWARE_DEPENDENT`. La idea de usar una vtable nativa en `PT_SCE_RELRO` como ancla es `PORTABLE`, pero requiere una vtable 13.52.

### 2.3 `libkernel_web.sprx`

En el código histórico se usa un import de `__stack_chk_fail` en `libwebkit_base + 0x8d8`. La resolución del stub RIP-relative es portable, pero `0x8d8` es un offset absoluto de WebKit histórico y no se debe llevar a 13.52. El procedimiento correcto es:

```text
obtener imagen WebKit 13.52
→ localizar un import conocido por bytes/XREFs
→ resolver FF 25 disp32 o relocación equivalente
→ validar que el destino cae en un módulo ejecutable con límites coherentes
→ calcular base de libkernel_web sólo después de esa validación
```

Estado del offset histórico `0x8d8`: `OBSOLETE` como valor de 13.52; método de resolución: `PORTABLE`.

### 2.4 `libSceLibcInternal.sprx`

El flujo histórico utiliza `strlen` en `libwebkit_base + 0x918`. Al igual que `0x8d8`, el algoritmo de resolver el import es portable, pero `0x918` es `FIRMWARE_DEPENDENT` y `OBSOLETE` como candidato 13.52. `memcpy` es una alternativa metodológica, no una dirección transferible.

### 2.5 Relación con `libkernel_sys` 13.52

El dump local `libkernel_sys_13.52.bin` está confirmado por SHA-256, pero no es WebKit ni `libkernel_web`. Las funciones encontradas en él no permiten inferir los imports de WebKit. La correlación correcta sigue siendo:

```text
WebKit 13.52 con imports reales
→ libkernel_web/libc de la misma build
→ libkernel_sys 13.52 sólo mediante imports, wrappers o evidencia binaria
```

No existe actualmente el primer artefacto de esta cadena, por lo que la conexión WebKit→libkernel_sys permanece `UNVERIFIED`.

## 3. JOP/ROP: clasificación estática

La tabla `rop/900.mjs` contiene offsets absolutos relativos a una build histórica. La función `init_gadget_map()` suma cada offset a una base; esto prueba que la tabla es un mapa de build y no un detector de gadgets.

| Grupo | Ejemplos históricos | Función | Método de migración 13.52 | Estado |
|---|---|---|---|---|
| Carga de registros | `pop rax/rbx/rcx/rdx/rsi/rdi; ret` | Preparar argumentos | Buscar secuencias exactas o equivalentes y verificar contexto | `REQUIRES_REANALYSIS` |
| Carga extendida | `pop r8`…`pop r15` | ABI System V para argumentos 5–8 | Buscar bytes con prefijos REX y `ret` | `REQUIRES_REANALYSIS` |
| Lectura/escritura | `mov rax,[rax]; ret`, `mov [rdi],rax; ret`, variantes dword | Primitivas auxiliares | Localizar por bytes/XREFs; confirmar seguridad de contexto | `REQUIRES_REANALYSIS` |
| Control de stack | `pop rsp; ret`, `leave; ret` | Pivot/retorno | Sólo tras validar stack y vtable de 13.52 | `REQUIRES_REANALYSIS` |
| JOP específico | `jop2`–`jop5` | Dispatcher y pivot histórico | No hay patrón semántico suficiente; reconstruir cadena | `FIRMWARE_DEPENDENT` |
| JOP de textarea | `ta_jop1`–`ta_jop3` | Entrada desde getter/vtable | Recalcular a partir de getter y vtable reales | `FIRMWARE_DEPENDENT` |
| libc | `getcontext`, `setcontext` | Guardar/restaurar contexto | Resolver export/import en libc 13.52 | `FIRMWARE_DEPENDENT` |
| libkernel | `__error` | Obtener errno | Resolver símbolo/import en libkernel de la build | `FIRMWARE_DEPENDENT` |
| Epílogo | `leave; ret` | Restaurar stack | Buscar patrón, validar prologo/epílogo | `REQUIRES_REANALYSIS` |

Los gadgets con comentarios de bytes, por ejemplo `58 c3`, `48 8b 00 c3` o `48 89 07 c3`, son candidatos localizables por patrón. Sin embargo, una coincidencia de dos o cuatro bytes puede aparecer en una instrucción no alineada. La migración debe comprobar límites de instrucción, referencias y efecto sobre el ABI; no basta con `indexOf`.

Los gadgets JOP con offsets largos son más frágiles: aunque sus instrucciones puedan existir en 13.52, la relación entre dispatcher, memoria de punteros, vtable y registros puede haber cambiado. Se marcan `REQUIRES_REANALYSIS`, no `PORTABLE`.

Existe una inconsistencia interna que debe conservarse como advertencia: `rop/900.mjs` escribe el getter `scrollLeft` en `0x1b8`, mientras `Chain900` contiene un comentario que menciona `0x1c8`; el código ejecutable usa `0x1b8`. Esta discrepancia no resuelve cuál es la entrada válida en 13.52 y debe verificarse contra el vtable dump de la build objetivo.

## 4. ABI y runtime conceptual

| Elemento | Estado conceptual | Dependencia que debe verificarse en 13.52 |
|---|---|---|
| `Memory`, `Addr`, `Int` | `PORTABLE` como abstracciones | Representación de punteros, NaN-boxing/JSValue y conversiones |
| `BufferView`/`View1/2/4` | `PORTABLE` como wrappers | `JSArrayBufferView` y `m_vector/m_length/m_mode` |
| `gc_alloc`, sprays y GC | `FIRMWARE_DEPENDENT` | Allocator, tamaños de slots y presión del GC |
| `addrof`/`fakeobj` | `PORTABLE` como objetivo conceptual | Butterfly, vtable, JSValue y controles de tipo |
| `ArrayBuffer`/TypedArray | `FIRMWARE_DEPENDENT` | Caminos fast/slow, ownership y destrucción |
| System V AMD64 | `STRUCTURAL` | Registros de argumentos y frame layout; confirmar wrapper/entrypoint |
| `eval` argument offset `0x30` | Histórico 8.03 | `REQUIRES_REANALYSIS` en 13.52 |
| `page_size=0x4000` | Históricamente PS4 | Confirmar desde módulo/OS de la build, no desde WebKit aislado |
| `gc()`/`sleep()` | `PORTABLE` como control de presión | Timing y comportamiento de la build objetivo |

El supuesto más delicado es que la representación de `JSValue` y los tamaños de objetos continúen siendo compatibles. PSFree depende de acceso a punteros mediante `readp`, de estructuras TypedArray y de un modo de coerción/GC concreto. En 13.52 cada una de esas condiciones debe marcarse como `REQUIRES_REANALYSIS` hasta disponer de bytes y pruebas estáticas de la build.

## 5. Qué se puede migrar sin offsets 13.52

Se puede migrar de forma legítima la arquitectura de herramientas: parser de segmentos, detección de imports RIP-relative, búsqueda de límites, extracción de vtables, clasificación de patrones, separación de módulos y generación de informes. También se pueden conservar los wrappers conceptuales `Memory`/`Addr`/`BufferView` como interfaces, sin afirmar que su implementación sea válida.

No se pueden migrar como valores: `0x8d8`, `0x918`, `0x18` de `JSHTMLTextAreaElement`, `0x10/0x18/0x1c` de `JSArrayBufferView`, `0x1b8`/`0x1c8` de la vtable, `0x30` de `ExecState`, offsets de gadgets de `rop/900.mjs`, ni cualquier base WebKit/libc/libkernel histórica.

## 6. Plan de porting por fases

### Fase 0 — Proveniencia y formato

Obtener una imagen WebKit 13.52 legalmente disponible, conservar SHA-256, tamaño, formato real, cabeceras y segmentos. Rechazar archivos sin firmware/procedencia verificable.

### Fase 1 — Segmentos y bases

Parsear `.text`, `PT_SCE_RELRO`, `.data` y parámetros de módulo. Ejecutar búsqueda de límites y comparar firmas únicamente dentro de la imagen. Registrar cada base como `DIRECT_BYTES` sólo si procede de un artefacto hashado; de lo contrario, `REQUIRES_REANALYSIS`.

### Fase 2 — Layouts JSC/WebCore

Reconstruir `JSObject`, `JSArrayBufferView`, `StringImpl`, `JSHTMLTextAreaElement`, `CustomGetterSetter` y butterfly mediante constructores, accesores, vtables y XREFs. Comparar con 8.03 y 8.50/8.52 como referencias estructurales, no mediante deltas.

### Fase 3 — Imports y módulos

Localizar `__stack_chk_fail`, `strlen` o `memcpy` por tabla de imports, stubs RIP-relative y XREFs. Obtener `libkernel_web` y `libSceLibcInternal` de la misma build. Relacionar después con `libkernel_sys` 13.52; no utilizar el ancla final para inventar módulos ausentes.

### Fase 4 — Gadgets

Generar candidatos por patrones de instrucciones, validar alineación, límites, referencias y efectos de registros. Separar gadgets de entrada, load/store, pivot, contexto y retorno. No generar una cadena operativa sin validación autorizada en una imagen 13.52.

### Fase 5 — Integración estática

Integrar la configuración validada en `webkit_1352_migration.json`, producir una matriz con evidencia por patrón y ejecutar tests negativos sobre blobs equivocados para evitar falsos positivos.

### Fase 6 — Evidencia runtime autorizada

Sólo si el propietario aporta un entorno autorizado y evidencia reproducible, comprobar compatibilidad runtime de los componentes. Esta fase queda fuera del análisis estático actual.

## Estado final

| Componente | Estado hacia 13.52 |
|---|---|
| Algoritmos PSFree de búsqueda/imports | `PORTABLE` |
| Layouts históricos 8.00–8.03 | `STRUCTURAL`, no transferibles directamente |
| Referencias 8.50/8.52 de Vue/kernel | `UNVERIFIED`/`STRUCTURAL`, no equivalentes a WebKit 13.52 |
| Estructuras WebKit 13.52 | `REQUIRES_REANALYSIS` |
| Bases WebKit/libkernel/libc 13.52 | `UNVERIFIED` |
| Gadgets 13.52 | `UNVERIFIED` |
| Cadena explotable | No preparada ni demostrada |

La pieza de mayor impacto sigue siendo un dump verificable de `libSceNKWebKit.sprx` 13.52 con `.text` y `PT_SCE_RELRO`. Sin ese artefacto no existe una base técnica para afirmar que los layouts o la cadena histórica de 8.50/8.52 son compatibles con 13.52.

## Referencias

[1]: https://github.com/kmeps4/PSFree/tree/368d82aa40d3017c220757ce315761adb5f06678 "PSFree, commit auditado"
[2]: https://github.com/Vuemony/vue-after-free/tree/6e37d510c7383aac2378b7215aefd14c1defd8d1 "Vue-After-Free, commit auditado"
[3]: https://github.com/ps4-linux/ps4-linux-loader/commit/9acef9fbf79097a2bb39d6c9c17228198bc445cc "ps4-linux-loader v25, soporte estructural 13.52"
