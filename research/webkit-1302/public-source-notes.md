# Notas de fuentes públicas — Vue After Free / PS4 13.02

Fecha de consulta: 2026-08-26.

Fuente principal: [owendswang/vue-after-free-lite](https://github.com/owendswang/vue-after-free-lite), fork basado en Vuemony/vue-after-free.

El README visible declara que el userland exploit funciona de 5.05 a 13.02 tal cual, pero que el repositorio ofrece jailbreak funcional sólo hasta 13.00. La propia FAQ responde que en 13.02 o superior sólo funciona el userland y que los archivos del repositorio no permiten jailbreak por encima de 13.00.

Clasificación local: `DIRECT_PUBLIC_DOCUMENTATION` para el alcance declarado; `USERLAND_CORROBORATED` para ejecución userland 13.02; `NOT_KERNEL_VERIFIED` para cualquier salto a kernel; `NO_FULL_JAILBREAK_13_02` para la cadena completa.

La página muestra además un commit reciente titulado “Improve NetCtrl stability and success rate...” y una estructura con `src`, `payloads`, `bd-j`, `requirements.txt` y `package.json`. Esto demuestra que NetCtrl forma parte del árbol público consultado, pero no demuestra por sí mismo compatibilidad funcional con 13.02.
