# Roadmap de cierre de brechas — kernel 13.52 (UAF knote + CVE-2026-58087)

Estado de entrada: UAF reproducible en hardware; sin leak, sin control de `kn_fop`,
sin R/W. Este documento mapea cada brecha a técnicas candidatas CONCRETAS con su
fundamento en las fuentes FreeBSD 9.1 archivadas (`analysis/sources/freebsd-9.1/`),
ordenadas por relación costo/información. Nada aquí está demostrado en consola;
cada técnica lleva su experimento de validación y métrica de éxito.

---

## Brecha 1 — KASLR leak

Bloqueo actual: 760 KB examinados, 0 punteros. Sanitización confirmada en
`kinfo_proc`; `kern.37/47/48` devuelven datos "aleatorios".

### 1a. Re-test de kern.37/47/48 CON churn previo (costo: mínimo)
Los buffers no inicializados solo filtran lo que pasó antes por esa memoria.
Protocolo: generar presión de kernel (crear/destruir cientos de procesos/hilos,
montar/desmontar, abrir/cerrar cientos de fds y sockets) e INMEDIATAMENTE leer los
tres sysctls en bucle. Métrica: aparición de valores estables en rango kernel
(≥0x800000000000) repetidos entre lecturas. Si tras churn siguen en cero,
descartarlos definitivamente.

### 1b. Disclosure residual por GETALL (Exp 1a del plan) — candidato principal
El `copyout` con count viejo devuelve la cola NO sobrescrita de un buffer M_TEMP
recién liberado/reutilizado. La pregunta clave es QUÉ objetos ricos en punteros
pasan por M_TEMP con tamaño ≈ al array. Sondeo propuesto: variar `count` (16…256
semáforos) para barrer buckets de tamaño, y ejecutar entre carreras cargas que
allocen M_TEMP: resolución de paths (`kern.proc.pathname` de PIDs ajenos), sysctls
de cadena, `shm_open`/unlink, creación masiva de procesos. Métrica: bytes residuales
con forma 0x8xxxxxxxxxxx / 0xFFFFFFFF8xxxxxxx estables entre intentos.

### 1c. Oráculo SETALL (Exp 1b) dirigido
Ventaja sobre 1a: lectura byte-a-byte posicional con ERANGE como marcador de
contenido >0x7FFF. Permite MAPEAR el heap adyacente sin crash: barrer `count` del
set pequeño y registrar en qué offsets aparece ERANGE (contorno de objetos vivos).
Ese mapa, combinado con churn, localiza vecinos puntero-ricos para 1a.

### 1d. Probe de routing sockets (fuera de plan anterior)
CVE-2026-3038 (rtsock, ≤13.04 según wiki, "possible privilege escalation") sugiere
que rtsock existía y era defectuoso recientemente. Probar `socket(PF_ROUTE,...)`:
si no está bloqueado en 13.52, RTM_GET/TAIL de F9 devuelve estructuras cuyo
tratamiento histórico ha filtrado punteros en otros BSD. Métrica: disponibilidad +
dump hex de mensajes route buscando valores en rango kernel.

---

## Brecha 2 — Control de kn_fop (o alternativa)

Bloqueo actual: reclaim tipado reinicializa (`kn_fop=&user_filterops`,
`kn_hook=NULL`). El slot vive en `knote_zone` UMA dedicada ⇒ ningún malloc ajeno
lo reclama.

### 2a. Doble-liberación vía dup() — la vía clásica UMA (prioritaria)
`dup(pipe_fd)` antes del cierre crea DOS descriptores hacia el mismo pipe.
Secuencia propuesta:
```text
kq_A registra K1(EVFILT_READ, fd)
dup(fd → fd2)
close(fd)      → knlist_remove libera K1 (ventana UAF abierta)
spray EVFILT_USER → K2 ocupa el slot
close(fd2)     → el segundo cierre recorre la knlist de K1 ya liberada
                 → posible segunda liberación del MISMO slot (double-free UMA)
```
Double-free en UMA ⇒ dos dueños lógicos de una celda ⇒ asignaciones solapadas con
CONTENIDO controlado por una parte y SEMÁNTICA de knote por otra. Es la escalera
clásica FreeBSD y no requiere vencer la reinicialización: la rodea.
Métrica: detectar doble-procesamiento del mismo índice / corrupción de lista
(crash con firma distinta al UAF simple).

### 2b. Confusión cruzada de filtros (sin leak)
Reclaim con knote de OTRO filtro (VNODE/PROC/AIO si accesibles): `kn_fop` apunta a
otro `filterops` legítimo pero `kn_ptr`/campos se interpretan con el tipo equivocado.
EVFILT_PROC guarda `proc*` en kn_ptr; procesado como READ-knote de pipe recorre
buffers con semántica de file*. Confusiones de este tipo producen derefs
explotables sin conocer direcciones. Requiere verificar qué filtros acepta el
kernel Orbis sobre qué tipos de fd (sondeo por attach/error).

### 2c. Enumeración de zonas candidatas (necesita consola)
Spray sistemático de cada alocator de ~0x80 B disponible tras el reclaim fallido y
observación de estabilidad/corrupción. Si algún objeto NO-knote comparte zona con
knotes en Orbis (Sony pudo unificar), ahí hay control de bytes. Sin binario kernel
esto se sondea en ciego con la métrica del 2a.

---

## Brecha 3 — R/W estable

Depende de 1+2. Encadenado realista una vez existan:

```text
leak (brecha 1)  → base kernel + dirección del knote vecino
write (2a o Exp2 GETALL-OOB) → sobrescribir kn_fop PARCIAL (bytes bajos)
   ↓
redirigir f_event dentro de .text conocido (sin necesitar ROP completo)
   ↓
stack pivot a cadena fijada por kn_sdata/kn_kevent (controlado por el atacante)
   ↓
R/W arbitrario → parcheo de cred (UID 0) + syscalls habilitadas → HEN
```

Nota SMEP: redirigir `f_event` directo a memoria de usuario fallará si SMEP está
activo (esperable); por eso el objetivo intermedio es texto del kernel con pivot,
no código usuario. La parcialidad del write u16 (techo 0x7FFF por semval) alcanza
para desviar los 2 bytes bajos de un puntero existente hacia gadgets cercanos —
técnica estándar de partial overwrite.

## Brecha 4 — semctl presente en Orbis 13.52

Experimento único (Exp 0 del plan): sondeo con SIGSYS handler de
`semget/semctl/semop/msgget/shmget`. Lectura de resultados:
| Resultado | Interpretación |
|---|---|
| ENOSYS constante | cárcel sin PR_ALLOW_SYSVIPC ⇒ vía muerta (documentar) |
| EINVAL/EINVAL variados | IPC vivo ⇒ avanzar Exp 1 |
| SIGSYS | filtrado por syscall-layer ⇒ probar shim vía entry userland alternativo |
Confirmación secundaria: `msgget/shmget` comparten gate; si shm vive y sem muere,
Sony quitó sem específicamente.

## Orden de ejecución recomendado

```text
Exp0 (gate) → 1c mapa de heap → 1a/1b leak hunt con churn → 1d rtsock probe
→ 2a double-free (si 1 da base) → 2b confusiones → Exp2 write forense
→ composición R/W → cred/HEN
```

Regla del lab: cada paso se documenta con errnos, bytes crudos y traces; nada entra
al README sin evidencia asociada.
