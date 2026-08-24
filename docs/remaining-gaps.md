# BRECHAS RESTANTES (estado tras barrido offline completo — 2026-08-24)

| Brecha | Estado | Ruta para cerrarla |
|---|---|---|
| Cabecera interna cifrada (4832/1248 B) | Contiene las AES128 keys+IVs POR SEGMENTO (formato público) | Una sola clave estática por-FW la abre ⇒ REQUIRES consola con kernel-exec UNA vez (extraer y publicar = desbloqueo permanente para todos) |
| Tabla de segmentos real 13.52 | Dentro de la cabecera cifrada | ídem |
| Kernel retail 13.52 | Dentro de system_fs_image.img (ID 6) dentro de UPDATE1 | ídem |
| WebKit/libkernel_web retail | ídem (system fs) | ídem |
| sysvsem en kernel 13.52 | REQUIRES_KERNEL_BYTES | ídem |
| Ventana double-free kqueue | REQUIRES_HARDWARE (consola) | experimentos exp20/21 |
| Leak KASLR | REQUIRES_HARDWARE | Exp 1a/1b |
