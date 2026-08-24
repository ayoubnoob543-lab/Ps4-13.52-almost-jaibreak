-- exp00_gate.lua — Exp 0: ¿sobreviven semsys/kqueue al sandbox UID=1?
-- Ejecutar con Luac0re ya inicializado. No modifica estado del sistema.
local E = require("common_1352")

E.log("GATE", "inicio sondeo de wrappers e invocación viva")

-- 1) presencia de stubs en libkernel (evidencia estática en consola)
for name, num in pairs(E.PROBE) do
    local has = E.has_wrapper(num)
    E.log("GATE", "wrapper %-8s (%3d): %s", name, num,
          has and string.format("0x%x", syscall.syscall_wrapper[num]) or "AUSENTE")
end

local avail = E.resolve_available()

-- 2) invocación viva segura: semget(IPC_PRIVATE, 8, IPC_CREAT|0666)
if avail.semget then
    local semid = E.try(syscall.semget, E.IPC_PRIVATE, 8,
                        E.IPC_CREAT + 0x1B6) -- 0666
    if semid and semid >= 0 then
        E.log("GATE", "semget OK -> semid=%d ⇒ SysV SEM vivo", semid)
        -- GETALL con buffer de 8 u16 para validar __semctl end-to-end
        if avail.__semctl then
            local argp = malloc(8)
            write64(argp, malloc(16))
            local r = E.try(syscall.__semctl, semid, 0, E.GETALL, read64(argp))
            E.log("GATE", "__semctl(GETALL) -> %s", to_hex(r or 0))
        end
        if avail.semop then
            local r = E.try(syscall.semop, semid, malloc(8), 0) -- nsops=0 no-op
            E.log("GATE", "semop(no-op) -> %s", to_hex(r or 0))
        end
        syscall.__semctl(semid, 0, E.IPC_RMID, 0)
        E.log("GATE", "set %d eliminado (limpieza)", semid)
    else
        E.log("GATE", "semget falló: %s (¿prison sin SYSVIPC?)",
              semid and ("errno " .. tostring(-semid)) or "excepción")
    end
else
    E.log("GATE", "semget SIN wrapper ⇒ vía semctl muerta en este kernel")
end

-- 3) kqueue/kevent vivos (control positivo conocido)
if avail.kqueue then
    local kq = E.try(syscall.kqueue)
    E.log("GATE", "kqueue() -> %s", kq and tostring(kq) or "error")
    if kq and kq >= 0 then syscall.close(kq) end
end

E.log("GATE", "fin. Registrar esta salida completa en el lab.")
