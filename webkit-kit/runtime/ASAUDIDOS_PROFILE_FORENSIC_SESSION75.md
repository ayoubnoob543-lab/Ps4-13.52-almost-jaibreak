# Revisión pública del perfil de ASaudidos — Sesión 75

## Perfil

URL: https://x.com/ASaudidos

El perfil visible se identifica como `MasterMaind ..`, usuario `@ASaudidos`, cuenta verificada, creada en febrero de 2026. La descripción pública indica “Vulnerability Research • Reverse Engineering • 0days”. El perfil mostraba 44 posts y una publicación fijada.

## Publicación fijada

URL: https://x.com/ASaudidos/status/2087654852793192698
Fecha visible: 12 de agosto.

Texto visible ampliado: el autor afirma que PlayStation resolvió su reporte, que su nombre aparece públicamente en HackerOne Hacktivity, que recibió una recompensa de $10k y que hubo una vulnerabilidad real, reporte responsable, validación, fix y recompensa. Enlaza `https://hackerone.com/playstation/hacktivity?type=team` y muestra una imagen de Hacktivity.

La publicación fijada **no muestra ni menciona** un programa de authoring BD-J, `bdj-sdk`, `classes.zip`, `libSceNKWebKit`, `libkernel_web`, una ISO, un comando, un repositorio de código o una herramienta de extracción. Sólo demuestra la afirmación pública de un reporte validado y una corrección/recompensa; no permite identificar la primitive ni el programa utilizado.

## Otras publicaciones visibles

Una publicación reciente dice que el autor estuvo centrado en un “new discovery” y afirma haber confirmado una “new bug class” en 13.50 y 13.52, pero el texto aparece truncado en la vista del perfil.

Otra publicación del 18 de agosto menciona que durante una prueba llegó a un “kernel bug” y ocurrió un kernel panic, pero el texto visible también está truncado. Esto es una afirmación del autor y no prueba por sí sola el programa utilizado ni una cadena reproducible.

Una publicación del 13 de agosto contiene una felicitación/respuesta relacionada con `@gezine_dev`, pero no aporta nombres de herramientas en el texto visible.

## Estado de evidencia

Clasificación del dato de la herramienta usada: `UNVERIFIED`.

La siguiente pieza mínima para identificarla es el post/vídeo concreto de BD-J/13.52 o una respuesta que muestre el nombre del programa, un enlace a un repositorio o una pantalla legible. La publicación fijada no contiene esa información.

## Post sobre el descubrimiento en 13.50/13.52

URL: https://x.com/ASaudidos/status/2091136042141208618
Fecha visible: 22 de agosto de 2026, 12:10 PM.

El texto completo afirma que el autor confirmó una “new bug class” en 13.50 y 13.52, mientras las pruebas en vivo se realizan en 12.02. Dice que el reporte ya fue enviado a Sony mediante HackerOne y que no publicará “the exact component trigger or technical path” hasta que el asunto esté parcheado y la divulgación sea aprobada. Añade que el trabajo avanza desde confirmar el comportamiento hasta hacerlo fiable y probar la cadena completa, y que después adjuntará un vídeo mostrando el proceso desde el trigger inicial hasta la activación exitosa de HEN.

Este post es evidencia directa de que el autor declara no publicar todavía el componente exacto, el trigger ni la ruta técnica. No menciona ningún programa concreto, SDK, herramienta de authoring, comando, repositorio o nombre de archivo. Tampoco prueba por sí mismo que la afirmación sea técnicamente correcta ni identifica la primitive.

Clasificación: existencia pública del post y su contenido `DIRECT` como evidencia de lo que el autor escribió; herramienta utilizada `UNVERIFIED`; componente/trigger/ruta técnica `UNVERIFIED`; vídeo prometido pero no adjunto en este post `UNVERIFIED`.

## Post enlazado por el usuario: 2084139516877574245

URL: https://x.com/ASaudidos/status/2084139516877574245

El post responde a Jose Coixao, que pregunta: “can you send a Hello World notification with your bdjb on 13.52 as proof?”. ASaudidos responde únicamente “check it” y adjunta un vídeo de 1:07. El fotograma visible muestra una interfaz de PS4 con Blu-ray Disc seleccionado; no se ve el nombre de un programa de authoring ni un comando de terminal en ese fotograma.

En la misma página aparece una respuesta de `@Sonic_Iso` que pregunta “but your system settings show 13.52?” y adjunta una captura. En la captura se lee parcialmente una consola titulada:

`BD-J Xlet initialized - GUI ready`
`Firmware: 13.50`
`BD-J Vuln Probe - PS4 13.50`
`--> Vuln Probe <--`
`--> PROBE COMPLETE <--`
`SM: com.sony.bdjb...security.BdJSecurityManager ...`
`java.home: blocked`

La resolución disponible corta las líneas inferiores y no permite leer el nombre completo de la clase, el programa que produjo la consola ni los métodos ejecutados. Tampoco demuestra que el vídeo de ASaudidos use exactamente esa misma herramienta: la captura pertenece a la respuesta de otra cuenta.

Conclusión de herramienta: `UNVERIFIED`. Evidencia directa del post: existe un Xlet BD-J/GUI y un vídeo de 1:07 que muestra la interfaz PS4/Blu-ray; no hay nombre visible de `bdj-sdk`, `classes.zip`, `BDSigner`, `makefs`, `gh` ni de otro programa. La pregunta de Jose confirma el término `bdjb` en el contexto de la demostración, pero no revela la primitive ni la herramienta usada.

## Estado del medio de vídeo

Al abrir el medio adjunto desde el post, X lo identifica como vídeo de `01:08` y muestra controles de reproducción. En la vista pública disponible no aparece título interno, nombre de archivo, descripción adicional ni texto que identifique el programa. El frame visible continúa mostrando la interfaz de PS4/Blu-ray; no se observa una terminal o IDE legible en esa vista.

La duración y la existencia del vídeo son `DIRECT`; el programa utilizado y el componente técnico siguen `UNVERIFIED`.

## Repositorio `iaceene/HENloader_Source`

URL: https://github.com/iaceene/HENloader_Source

El README identifica el proyecto como “HENloader LP – SOURCE”, un loader BD-J basado en Blu-ray que combina Lapse, Poopsploit y GoldHEN. Declara compatibilidad de 9.00 a 12.52 según el exploit, no 13.52. El árbol público contiene `InitXlet.java`, `MessagesOutputStream.java`, `Screen.java`, `bluray.InitXlet.perm` y los directorios `api/`, `external/` y `sandbox/`.

El README hace visible una comprobación de seguridad: imprime “Priviledge escalation failure, unsupported firmware?” cuando `System.getSecurityManager()` no queda anulado; si pasa esa condición, llama a componentes internos de offsets de kernel. Esto confirma que el proyecto es un loader de explotación y no un simple harness BD-J legítimo. No se ejecutó ningún archivo ni se siguieron sus instrucciones de uso.

El propio README atribuye el entorno BD-J a `kimariin`, la consola Java a `sleirsgoevy`, Lapse a Gezine y Poops a `theflow0`, e incluye enlaces a releases y payloads. Esos créditos pueden ayudar a reconstruir procedencia, pero no prueban que ASaudidos utilizara este repositorio. Tampoco aparece en el README el texto exacto `BD-J Vuln Probe - PS4 13.50` ni una atribución a ASaudidos.

Clasificación: existencia y contenido del repositorio `DIRECT`; compatibilidad declarada 9.00–12.52 `DOCUMENTED_ONLY`; relación con el programa de ASaudidos `UNVERIFIED`; compatibilidad 13.52 `DISCARDED` como afirmación del README, porque el propio proyecto declara un límite de 12.52; primitive o ruta técnica de ASaudidos `UNVERIFIED`.
