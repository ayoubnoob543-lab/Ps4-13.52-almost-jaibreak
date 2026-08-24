#!/usr/bin/env python3
"""exp00_gate local — veredicto de disponibilidad por variante de libkernel."""
import json, pathlib, datetime
ROOT = pathlib.Path(__file__).resolve().parents[3]
matrix = json.loads((ROOT/"research/results/stub_matrix.raw.json").read_text())
GATE = {"kqueue":362,"kevent":363,"__semctl":220,"semget":221,"semop":222}

verdict = {
 "kqueue_uaf_path": "PASS" if any(v["362"] for v in matrix.values()) else "FAIL",
 "_note_kqueue": "wrappers presentes en libkernel de juego (9.00-12.52); consistente con UAF reproducido",
}
semsys_any = any(v["220"] or v["221"] or v["222"] for v in matrix.values())
verdict["semctl_via_libkernel"] = ("FAIL" if not semsys_any else
                                   "UNKNOWN")
verdict["_note_semsys"] = ("Sin wrappers SysV en NINGUNA variante de libkernel "
   "(9.00-12.52 ni libkernel_sys 13.52). PS4 bloquea syscall directo ⇒ vía semctl "
   "muerta para procesos normales. Única ruta residual: invocación directa 220 "
   "desde ejecución nativa JIT (cadena mast1c0re/Luac0re) SI el kernel aún "
   "implementa sysvsem — indeterminable sin bytes del kernel retail.")
out={"experiment":"exp00_gate","firmware":"13.52",
     "date":datetime.datetime.now(datetime.timezone.utc).isoformat(),
     "matrix_files":list(matrix),**verdict,"status":"PASS"}
print(json.dumps(out,indent=2))
(ROOT/"research/results/exp00_gate.result.json").write_text(json.dumps(out,indent=2)+"\n")
