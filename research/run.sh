#!/usr/bin/env bash
set -uo pipefail
cd "$(dirname "$0")"
echo "== Pipeline 13.52: etapa LOCAL (segura) =="
python3 experiments/exp01b_integrity/run_local.py > logs/exp01b.stdout.log 2> logs/exp01b.stderr.log || true
python3 experiments/exp01a_static_stubs/run_local.py > logs/exp01a.stdout.log 2> logs/exp01a.stderr.log || true
python3 experiments/exp00_gate/run_local.py      > logs/exp00.stdout.log  2> logs/exp00.stderr.log  || true
python3 analysis/classify.py                    > logs/classify.stdout.log 2>logs/classify.stderr.log || true

echo "== Etapa CONSOLA (requiere PS4 13.52 real) =="
if [ -n "${PS4_RUNTIME:-}" ]; then
  echo "PS4_RUNTIME detectado: ejecutar exp10/exp20/exp21 (Luac0re) — no automatizado aquí"
else
  echo "STOP: sin hardware PS4 disponible. Experimentos exp10/exp20/exp21 quedan en REQUIRES_HARDWARE." | tee results/REQUIRES_HARDWARE.txt
fi
echo "== resumen =="
cat results/pipeline_summary.json 2>/dev/null
