# Toolkit de experimentos kernel 13.52 (Luac0re/Lua)

Instrumentación para ejecutar el plan de `docs/research-plan-1352-kernel.md` y el
roadmap `docs/gap-closure-roadmap-1352.md` en consola real. Compatible con la API
de Luac0re (syscall wrappers resueltos por patrón en libkernel).

## Checklist que atiende

- [✓] UAF — ya reproducido por el investigador
- [✓] reclaim — ya demostrado (EVFILT_USER)
- [?] corrupción controlable → **exp20/21 + Exp 2 del plan** (GETALL OOB write,
      contenido u16 ≤0x7FFF; destructivo, ejecutar al final)
- [✗] info leak → **exp10** (churn+kern.37/47/48) y **exp21** (residual copyout)
- [✗] KASLR → depende del leak; partial overwrite no requiere base completa
      (ver roadmap §3)
- [✗] kernel R/W → composición según roadmap §3, tras leak+corrupción
- [✗] ejecución → etapa final (pivot con campos kevent controlados)

## Uso

1. Cargar Luac0re (juego Star Wars Racer Revenge, savedata resignada).
2. Copiar `common_1352.lua` junto a los scripts.
3. Orden:
   - `exp00_gate.lua` — SOLO UNA VEZ. Decide si toda la vía semctl vive o muere.
   - `exp10_leak_churn.lua` — seguro, repetible sin riesgo.
   - Par de carrera (dos conexiones simultáneas):
     conexión A: `exp20_race_attacker.lua`; conexión B: `exp21_race_victim.lua`.
4. Registrar TODAS las salidas (log_server) en `analysis/` del lab.

## Reglas
- exp20/21 son inocuos: carrera perdida = EINVAL silencioso.
- El OOB write (Exp 2 del plan) NO está aquí: es destructivo; se ejecuta solo tras
  mapear con exp21 y bajo decisión explícita del investigador.
