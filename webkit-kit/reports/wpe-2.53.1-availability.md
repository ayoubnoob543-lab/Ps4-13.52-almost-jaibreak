# WPE WebKit 2.53.1: disponibilidad del bundle

## Estado

```text
WPE_2531_BUNDLE = NOT_AVAILABLE_IN_THIS_ENVIRONMENT
WPE_2531_DIAGNOSTIC = NOT_RUN
WPE_2531_RUNTIME = NOT_RUN
WPE_2531_HTML_SMOKE = NOT_RUN
WPE_2531_COMPARISON = NOT_RUN
```

Se buscó un bundle oficial en `/tmp`, `/home/ubuntu`, `Downloads`, `/tmp/wpe-builds` y el árbol `bin` de la build WPE 2.52.6. No se encontró `MiniBrowser`, `WPEWebDriver` ni `libWPEWebKit-2.0.so` de la versión 2.53.1. Solo están disponibles el prefijo local `libwpe` 1.16.3, `WPEBackend-fdo` 1.16.1 y la build incompleta 2.52.6, que se preservó intacta.

El checkout actualizado contiene los runners versionados `diagnose_wpe_minibrowser.py`, `run_wpe_headless.py`, `compare_wpe_smoke.py` y `render_wpe_report.py`; se materializaron únicamente desde Git mediante sparse-checkout. Se ejecutaron el diagnóstico y el runner en modo autodetección, y ambos devolvieron `NOT_RUN` porque no encontraron el bundle.
No se descargó otra build grande, no se recompiló WebKit y no se ejecutaron assertions ni comparación funcional WPE 2.53.1. Por tanto, no existe evidencia funcional 2.53.1 en este entorno; el bloqueo real restante es exclusivamente la ausencia de `MiniBrowser`/`WPEWebDriver`/`libWPEWebKit` 2.53.1.

## Comando pendiente

Cuando el bundle esté disponible, ejecutar desde la raíz del repositorio:

```sh
python3 webkit-kit/tools/diagnose_wpe_minibrowser.py \
  /ABSOLUTE/PATH/bin/MiniBrowser \
  --prefix /ABSOLUTE/PATH \
  --output wpe-2531-diagnostic.json

python3 webkit-kit/tools/run_wpe_headless.py \
  --minibrowser /ABSOLUTE/PATH/bin/MiniBrowser \
  --prefix /ABSOLUTE/PATH \
  --headless \
  --output wpe-2531-run.json

python3 webkit-kit/tools/compare_wpe_smoke.py \
  wpe-2531-run.json \
  --output wpe-2531-comparison.json

python3 webkit-kit/tools/render_wpe_report.py \
  wpe-2531-run.json \
  wpe-2531-comparison.json \
  --output wpe-2531-validation-report.md
```

El bundle debe proporcionar al menos `bin/MiniBrowser`, `lib/libWPEWebKit-2.0.so*`, `lib/libwpe-1.0.so*`, `lib/libWPEBackend-fdo-1.0.so*`, sus dependencias dinámicas y un prefijo coherente. El resultado 2.53.1 se mantendrá separado de cualquier estado 2.52.6.
