# MARKER-RECLAIM — análisis estático exhaustivo (2026-08-24)

Pregunta central: ¿el MARKER que `kqueue_scan()` aloca en cada kevent() puede
reutilizar la celda liberada de K1 y servir como primitiva de observación de
memoria residual / punteros kernel?

**VEREDICTO EJECUTIVO:** el MARKER reutiliza la celda estructuralmente, pero
`knote_alloc()` aplica `M_ZERO` SIEMPRE (kern_event.c L2165–2169): el slot llega
puesto a cero. No hay residuos, no hay punteros filtrables, y el bucle de scan
salta los markers sin llamar `f_event` ni hacer copyout. La hipótesis como
*observador* queda REFUTADA a nivel fuente FreeBSD 9.1. Sobrevive como
*estabilizador inerte* y como habilitador de la cadena double-free.

---

## 1. Anatomía exacta del MARKER (fuente: kern_event.c F9.1 archivado)

```c
L1345  marker = knote_alloc(1);
L1348  marker->kn_status = KN_MARKER;          /* único campo semántico */
L1385  TAILQ_INSERT_TAIL(&kq->kq_head, marker, kn_tqe);   /* toca 0x18–0x27 */
...
L1498  knote_free(marker);
```

```c
L2165  knote_alloc(int waitok) {
L2167      return uma_zalloc(knote_zone,
L2168          (waitok ? M_WAITOK : M_NOWAIT) | M_ZERO);   /* ← SIEMPRE cero */
```

## 2. Tamaño y comparación con knote

`knote_zone = uma_zcreate("KNOTE", sizeof(struct knote), ...)` (L2159) ⇒
MARKER ocupa **exactamente sizeof(struct knote)**. Cálculo desde `sys/event.h`
F9.1: SLIST(8)+SLIST(8)+ptr(8)+TAILQ(16)+kq(8)+kevent(32)+status(4)+sfflags(4)+
sdata(8)+union(8)+fop(8)+hook(8)+hookid(8) = **0x80**.

✅ Coincide BYTE A BYTE con la medición en hardware del investigador
(`analysis/kqueue_uaf_1352_observations_v2_2026-08-24.json`) y con el header
F9.0 citado en el writeup de Cryptogenic (PS4 5.05 BPF), que anota
`kn_fop @ offset 0x68`. Triple fuente, cero discrepancias.

## 3. Campos inicializados vs sin tocar

| Offset | Campo | Estado tras alloc + setup |
|---|---|---|
| todo | — | **0x00 por M_ZERO** (L2168) |
| 0x18–0x27 | kn_tqe | escrito por TAILQ_INSERT_TAIL |
| 0x50 | kn_status | KN_MARKER (0x20) |
| resto | — | permanecen 0 |

Conclusión: **no existe ventana residual**. Ni `kn_kq`, ni `kn_fop`, ni
`kn_kevent` contienen bytes previos de K1.

## 4. ¿Puede reclamar la celda recién liberada?

Estructuralmente SÍ (misma UMA zone, política LIFO por CPU-bucket en F9):
una llamada `kevent()` inmediatamente posterior al `close()` tiene alta
probabilidad de recibir la celda de K1 como su marker. **Pero el contenido que
deja es cero**, así que la reutilización no aporta observación.

## 5. Semántica del scan ante markers (por qué tampoco filtra间接amente)

En el bucle (L1393–1402): si el primer elemento tiene `kn_status==KN_MARKER` y
no es el propio → el scan **duerme** (`KQ_FLUXWAIT`) sin invocar `f_event` ni
copiar `kn_kevent`. Los markers jamás llegan al copyout ⇒ ni siquiera la
ventana 0x30–0x4F sale a userland. Vía de filtración por procesamiento:
cerrada.

## 6. Tabla de hipótesis

| HIPÓTESIS | EVIDENCIA | FUENTE | ESTADO |
|---|---|---|---|
| MARKER ocupa celda liberada de knote_zone | misma zona UMA; LIFO esperado | kern_event.c L183/L2165 | CONFIRMADO_FREEBSD (estructural) |
| MARKER tamaño == knote == 0x80 | uma_zcreate sizeof(knote); medición HW coincide | fuente + HW investigador + Cryptogenic | CONFIRMADO_FREEBSD + coherente PS4 |
| MARKER conserva datos residuales de K1 | `\|M_ZERO` incondicional | L2167–68 | **REFUTADO** (base F9.1) |
| MARKER → residual data observable | slot siempre en cero; loop salta markers | L1393–1402 | **REFUTADO** |
| MARKER → kernel pointer | sin residuo y sin copyout de markers | ídem | **REFUTADO** |
| MARKER → KASLR leak | depende de las dos anteriores | derivado | **REFUTADO** como vía directa |
| MARKER → control de campos de knote | cero control: campos fijos por el propio scan | L1348/L1385 | **REFUTADO** como control directo |
| MARKER como estabilizador inerte del walk (sin side-effects de user_filterops) | markers se saltan sin procesar | L1393 | HIPÓTESIS — REQUIRES_HARDWARE |
| MARKER como pieza de cadena double-free (roadmap §2a) | doble-liberación no depende de contenido | técnica estándar (Cryptogenic 5.05) | HIPÓTESIS — REQUIRES_HARDWARE |

## 7. Referencias públicas relevantes encontradas

- **Cryptogenic — "PS4 5.05 BPF Double Free Kernel Exploit Writeup"** (exploit-db
  45045): confirma independientemente el layout de `struct knote` en PS4
  (`kn_fop@0x68`) y documenta la cadena clásica sobre este objeto:
  double-free → *allocator poisoning* → fake-knote spray → `f_detach` hijack →
  JOP/ROP. En 5.05 el fake-knote vivía en el heap WebKit (pre-SMAP). En 13.52,
  con SMEP/SMAP activos, esa variante directa no aplica: haría falta contenido
  controlado EN ZONA KERNEL (véase roadmap §2c).
- **CVE-2026-58083 / FreeBSD-SA-26:50.kqueue** (mismo lote 2026-07-29 que el
  semctl): UaF en copia de knotes durante `fork()` con timer-filters; lista
  activa corrupta; escalada potencial. Alcance Orbis desconocido (¿fork()
  alcanzable desde sandbox?): REQUIRES_HARDWARE.
- **venglin/exploits kqueue.txt**: race check/use en kevent() FreeBSD ≤6.1 —
  precedente histórico de la familia.

## 8. Qué queda pendiente exclusivamente para hardware

1. ¿El kernel Orbis 13.52 mantiene `M_ZERO` en su `knote_alloc`? (diff imposible
   sin bytes retail; por defecto asumir SÍ por herencia).
2. ¿Doble-liberación vía dup()/close produce corrupción de freelist observable?
3. ¿Algún otro subsistema comparte zona con knote en Orbis?
4. Comportamiento real del walk con markers ajenos bajo carreras.

---

**Nota metodológica:** la refutación de esta hipótesis es progreso válido según
la regla de progreso del lab («o una vía técnica descartada con una razón
verificable»). El presupuesto de investigación se redirige íntegro a §2a
(double-free) y §1b/1c (mapa del heap vía SETALL-oracle).
