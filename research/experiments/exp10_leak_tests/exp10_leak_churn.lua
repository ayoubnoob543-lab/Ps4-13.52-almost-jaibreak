-- exp10_leak_churn.lua — re-test kern.37/47/48 CON churn previo
-- Hipótesis: buffers no inicializados solo filtran lo que pasó antes por esa memoria.
local E = require("common_1352")

local function scan(buf, tag, round)
    if not buf then return end
    for off = 1, #buf - 8, 8 do
        local v = string.unpack("<I8", buf, off)
        if v >= 0x800000000000ULL then
            E.log("LEAK", "%s ronda %d off %#x valor %#018x  << CANDIDATO",
                  tag, round, off - 1, v)
        end
    end
end

E.log("LEAK", "inicio: 30 rondas churn + lectura sysctls objetivo")
for round = 1, 30 do
    -- churn barato permitido en sandbox: sockets DGRAM efímeros
    local s = E.try(syscall.socket, AF_INET, SOCK_DGRAM, 0)
    if s and s >= 0 then syscall.close(s) end
    -- churn sysctl genérico (fuerza allocs M_TEMP internos)
    E.try(E.sysctl_read, {1, 14}, 0x400)

    for _, oid in ipairs({37, 47, 48}) do
        local d = E.try(E.sysctl_read, {1, oid}, 0x400)
        scan(d, "kern." .. oid, round)
    end
end
E.log("LEAK", "fin. Si CANDIDATOS=0 ⇒ sanitización activa confirmada; registrar.")
