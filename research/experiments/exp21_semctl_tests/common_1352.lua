-- common_1352.lua — helpers compartidos para experimentos kernel 13.52
-- Requiere Luac0re cargado (syscall/memory/global ya inicializados)

EXP1352 = {}

-- Syscalls objetivo NO presentes en SYSCALL_TABLE stock de Luac0re
EXP1352.PROBE = {
    kqueue   = 362,  -- 0x16A
    kevent   = 363,  -- 0x16B
    __semctl = 220,
    semget   = 221,
    semop    = 222,
    msgget   = 225,
    shmget   = 231,
}

-- Constantes FreeBSD/Orbis
EXP1352.IPC_PRIVATE = 0
EXP1352.IPC_CREAT   = 0x200     -- 01000 octal
EXP1352.IPC_RMID    = 0
EXP1352.GETVAL      = 5
EXP1352.GETALL      = 6
EXP1352.SETALL      = 9
EXP1352.SEMVMX      = 0x7FFF

function EXP1352.log(tag, fmt, ...)
    print(string.format("[1352][%s] %s", tag, string.format(fmt, ...)))
end

-- ¿Existe el wrapper de esta syscall en libkernel? (sin lanzar error)
function EXP1352.has_wrapper(num)
    return syscall.syscall_wrapper and syscall.syscall_wrapper[num] ~= nil
end

-- Resolver solo las que existan; devuelve tabla {nombre=true}
function EXP1352.resolve_available()
    local ok_list = {}
    for name, num in pairs(EXP1352.PROBE) do
        if EXP1352.has_wrapper(num) then
            ok_list[name] = true
        end
    end
    return ok_list
end

-- Invocación defensiva: devuelve ret o nil+errno_string
function EXP1352.try(fn, ...)
    local ok, a, b, c = pcall(fn, ...)
    if not ok then return nil, "THREW:" .. tostring(a) end
    return a, b, c
end

-- sysctl genérico F9: name=mib array, old_len
function EXP1352.sysctl_read(mib, old_len)
    local namelen = #mib
    local namebuf = malloc(namelen * 4)
    for i, v in ipairs(mib) do
        write32(namebuf + (i - 1) * 4, v)
    end
    local oldp = malloc(old_len)
    local oldlenp = malloc(8)
    write64(oldlenp, old_len)
    local ret = syscall.sysctl(namebuf, namelen, oldp, oldlenp, 0, 0)
    local got = read64(oldlenp)
    if ret and ret < 0 then return nil, -ret end
    return read_buffer(oldp, got), got
end

return EXP1352
