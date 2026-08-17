# CSSFontFace → PS4 13.52: auditoría y migración estática

## Alcance

Este documento continúa el laboratorio desde `0a2e731` y analiza el repositorio público [ntfargo/CSSFontFace-Exploit](https://github.com/ntfargo/CSSFontFace-Exploit) sin ejecutar su JavaScript ni atribuir compatibilidad runtime a PS4 13.52.

El README del repositorio distingue tres conceptos que no deben mezclarse:

| Concepto | Declaración pública | Clasificación |
|---|---:|---|
| Alcance de la vulnerabilidad CSSFontFace | PS4 6.00–13.52 | `DOCUMENTATION` / `UNVERIFIED` para la cadena 13.52 |
| Implementación CSSFontFace de este repositorio | PS4 6.00–11.02 | `CONFIRMED` como código histórico del repositorio |
| Implementación de kernel incluida | PS4 7.00–11.02 | `CONFIRMED` como tabla histórica; no transferible a 13.52 |

El propio README explica que WebKit PS4 11.5x–latest rediseñó el manejo de propiedades de CSSFontFace e introdujo `m_propertiesOrCSSConnection`; también declara que la primitiva de lectura/escritura basada en `m_featureSettings` deja de ser utilizable por encima de los rangos soportados. Esta afirmación es una guía de migración, no bytes de WebKit 13.52.

## Procedencia auditada

| Elemento | Valor |
|---|---|
| Repositorio | `ntfargo/CSSFontFace-Exploit` |
| Commit auditado | `221baa6e7349b96a6fd299808a25a4178e47741c` |
| `README.md` SHA-256 | `860db9e43151442f43324093d16fe9bbcb2224be83bb2c3ef3412fb9104f6a27` |
| `public/src/ps4/constants.js` SHA-256 | `c832a6f7ba08b729a291a5807caf5f2caffac52823e32ca8bca6dbba3252e329` |
| `public/src/ps4/userland.js` SHA-256 | `dc1ae1fd99829511818dd0ecde813e75287f804b4543af4186d09ab875d5c2a4` |
| Tabla pública detectada | FW 6.00, 6.20, 6.50, 6.51, 6.70, 7.00, 7.50, 7.51, 8.00, 8.03, 8.50, 9.00, 9.03, 9.50, 10.00, 10.50, 11.00 y 11.02 |
| Entrada 11.50 | Ausente |
| Entrada 13.52 | Ausente |

El inventario se obtiene con `tools/analyze_cssfontface_constants.py`, que trata `constants.js` como texto y no importa ni ejecuta el exploit.

## Qué es transferible

La siguiente arquitectura es portable como metodología, pero no como offsets:

| Componente | Qué puede conservarse | Clasificación |
|---|---|---|
| Retención/creación de objetos FontFace y coordinación con `document.fonts` | Modelo conceptual del ciclo UAF | `PORTABLE` |
| Separación entre vtable, objeto falso, vista de memoria y ARW | Organización del análisis | `PORTABLE` |
| Resolución de base WebKit desde una vtable observada | Procedimiento, si se dispone de bytes/vtable 13.52 | `PORTABLE` como método; `FIRMWARE_DEPENDENT` en valores |
| Resolución de libc/libkernel mediante imports como `__imp_strerror` y `__imp___error` | Método de correlación de módulos | `PORTABLE` como método; `FIRMWARE_DEPENDENT` en offsets |
| Gadgets ROP concretos | No se conservan; deben redescubrirse en la imagen objetivo | `OBSOLETE` fuera de su build |
| `wk_CSSFontFace_vtable` | Debe localizarse en bytes y validarse con XREFs | `FIRMWARE_DEPENDENT` |
| Campos de objeto CSSFontFace | Deben reconstruirse en 13.52 | `FIRMWARE_DEPENDENT` |
| `m_featureSettings` como primitive ARW | No puede asumirse después del rediseño 11.5x+ | `OBSOLETE` para la cadena pública; `UNVERIFIED` como posibilidad alternativa |

## Layouts observados en la tabla pública

La tabla no es uniforme. Los campos y tamaños de CSSFontFace cambian de forma significativa:

| Firmware | `sizeof` | Campos CSSFontFace visibles | Observación |
|---|---:|---|---|
| 6.00 | `0x128` | `m_families`, `m_featureSettings` buffer/size/capacity, `m_clients`, `m_wrapper`, `m_status`, `m_thread`, `m_function` | Layout antiguo que sustenta la primitive histórica |
| 6.50 | `0x120` | `m_clients`, `m_wrapper`, `m_status` | Parte del layout se hereda o deja de estar explícita |
| 7.00 | `0xe8` | `m_clients`, `m_wrapper`, `m_status`, `m_thread`, `m_function` | Cambio grande de tamaño y posiciones |
| 9.00 | `0xb8` | `m_clients`, `m_wrapper`, `m_status`, `m_thread`, `m_function` | Nuevo layout; `ArrayBuffer` también cambia |
| 10.00/10.50 | no siempre explícito | `m_clients`, `m_wrapper`, `m_status` y vtable/gadgets por minor | La tabla usa herencia/fallback del proxy |
| 11.00/11.02 | vtable/gadgets explícitos; campos no completos | Parte de los campos se resuelve por fallback a 10.x | No equivale a una tabla 11.50+ |
| 11.50–13.52 | ausente | ausente | Requiere imagen WebKit objetivo |

La ausencia de `wk_CSSFontFace_m_propertiesOrCSSConnection` en `constants.js` es significativa: el repositorio no modela el nuevo campo que su README identifica para 11.5x–latest. No se debe rellenar ese campo con un delta ni con valores de otra versión.

## Dependencias de `userland.js`

El flujo histórico utiliza explícitamente los siguientes datos dependientes del firmware:

| Uso | Campos/valores | Clasificación para 13.52 |
|---|---|---|
| Crear objeto falso y sobrevivir a `CSSFontFaceSet::add/remove` | vtable, `m_clients`, `m_wrapper`, `m_status`, `m_thread`, `m_function` | `FIRMWARE_DEPENDENT` |
| Construir vistas de `ArrayBuffer` | `wk_ArrayBuffer_m_contents_m_data`, `wk_ArrayBuffer_m_contents_m_sizeInBytes` | `FIRMWARE_DEPENDENT` |
| Detectar base de WebKit | vtable conocida menos puntero observado | Método `PORTABLE`; offset `UNVERIFIED` |
| Resolver libc | `wk___imp_strerror` menos `c_strerror` | `FIRMWARE_DEPENDENT` |
| Resolver libkernel | `wk___imp___error` menos `k__error` | `FIRMWARE_DEPENDENT` |
| Preparar pivot y ROP | Gadgets `wk_*`, cambios por `version.major` | `OBSOLETE` sin bytes 13.52 |
| Pasar de WebKit a libkernel_sys | Requiere `libkernel_web` y una cadena de imports/relocations coincidente | `UNVERIFIED` |

El archivo `userland.js` contiene ramas por major firmware, pero esas ramas no constituyen una prueba de 13.52: el código no contiene una entrada 13.52 en la tabla de constantes ni una imagen objetivo.

## Cambio estructural 11.50+

La evidencia pública disponible permite afirmar únicamente lo siguiente:

1. WebKit 11.5x–latest introdujo `m_propertiesOrCSSConnection` en el manejo de propiedades de CSSFontFace.
2. La primitive histórica de serialización/lectura-escritura mediante `m_featureSettings` deja de ser válida según el README del autor.
3. El repositorio no incluye la definición de layout 11.50+ ni una tabla 13.52.
4. Por tanto, para 13.52 deben reconstruirse el tamaño del objeto, la posición de todos los campos usados, la relación entre `m_propertiesOrCSSConnection` y `m_featureSettings`, la vtable y los XREFs de los métodos de CSSFontFace.

No se puede determinar estáticamente, sin bytes de WebKit 13.52, si el UAF subyacente sigue produciendo una primitive alternativa, si cambió sólo el layout, o si la cadena quedó inutilizable por otra mitigación.

## Relación con el ancla `libkernel_sys` 13.52

El dump `libkernel_sys_13.52.bin` sigue siendo válido como ancla independiente:

```text
SHA-256: ef15204fee6f9f3e37892a4d29d779ed90ec4b70025b652d64625d76419b6a9c
```

Sus wrappers y syscalls no proporcionan por sí mismos la vtable CSSFontFace, los imports de `libkernel_web`, los límites `.text`/`PT_SCE_RELRO` ni gadgets WebKit. La conexión sólo podrá elevarse por encima de `UNVERIFIED` con bytes de WebKit/libkernel_web de la misma build y referencias de importación o relocación que conduzcan al dump 13.52.

## Artefactos 13.52 encontrados en este ciclo

No se encontró ni se validó ningún binario nuevo de:

- `libSceNKWebKit.sprx`;
- `libkernel_web.sprx`;
- `libSceLibcInternal.sprx`;
- `eboot`/SELF relacionado;
- dump `.text`/`PT_SCE_RELRO`;
- tabla de símbolos WebKit 13.52.

La documentación de [PS4 Developer Wiki — Vulnerabilities](https://www.psdevwiki.com/ps4/Vulnerabilities) sólo sirve como contexto y no contiene hashes ni bytes 13.52.

## Herramienta añadida

Se añadió `tools/analyze_cssfontface_constants.py`.

Uso reproducible:

```bash
python3 tools/analyze_cssfontface_constants.py \
  /ruta/a/CSSFontFace-Exploit/public/src/ps4/constants.js \
  --out /tmp/cssfontface_constants_report.json
```

La herramienta produce el hash del archivo, firmwares detectados, presencia de campos y clasificación de cada registro. Marca explícitamente 13.52 como `ABSENT_FROM_PUBLIC_TABLE` y no promueve ningún valor histórico.

## Estado

| Bloqueo | Estado |
|---|---|
| Lógica conceptual CSSFontFace | `PORTABLE` como metodología |
| Layout 6.00–11.02 | `CONFIRMED` en el repositorio auditado |
| Cambio `m_propertiesOrCSSConnection` 11.5x+ | `DOCUMENTATION`; necesita bytes para validación estructural |
| Layout CSSFontFace 13.52 | `UNVERIFIED` |
| Primitive `m_featureSettings` en 13.52 | `OBSOLETE` para la cadena pública; no se descarta una primitive alternativa sin bytes |
| Vtable/gadgets 13.52 | `UNVERIFIED` |
| Conexión WebKit → libkernel_sys 13.52 | `UNVERIFIED` |
| Jailbreak o runtime 13.52 | No demostrado |

## Siguiente artefacto de mayor impacto

El artefacto prioritario sigue siendo un dump de `libSceNKWebKit.sprx` 13.52 con `.text`, `PT_SCE_RELRO`, build ID o al menos segmentos y bytes. En segundo lugar, un `libkernel_web.sprx` 13.52 o un SELF/eboot que conserve imports/relocations. Sin uno de esos artefactos no es legítimo reconstruir offsets ni declarar que CSSFontFace es utilizable en 13.52.
