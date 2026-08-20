# WPE WebKit 2.53.1: disponibilidad del bundle

## Estado

```text
WPE_2531_BUNDLE = BLOCKED_EXPECTED_SHA_NOT_FOUND
WPE_2531_DIAGNOSTIC = NOT_RUN
WPE_2531_RUNTIME = NOT_RUN
WPE_2531_HTML_SMOKE = NOT_RUN
WPE_2531_COMPARISON = NOT_RUN
```

Se comprobó el almacenamiento local/persistente disponible en `/home/ubuntu/Downloads`, `/home/ubuntu/upload`, `/home/ubuntu/wpe-bundles`, `/home/ubuntu/.cache/wpe`, `/tmp/wpe-bundles` y `/tmp/wpe-builds`. No apareció ningún bundle recuperable. La build `/tmp/wpewebkit-2.52.6-build` se preservó intacta y no se modificó.

La fuente oficial de WPE identifica el tarball de fuentes 2.53.1 en [wpewebkit.org/releases/wpewebkit-2.53.1.tar.xz](https://wpewebkit.org/releases/wpewebkit-2.53.1.tar.xz), pero ese archivo no es el bundle universal con `MiniBrowser` y `WPEWebDriver`. El índice oficial de bundles es `https://wpewebkit.org/built-products/x86_64/release/nightly/MiniBrowser/`. Su `LAST-IS` actual apunta a:

```text
MiniBrowser_wpe_319501@main.tar.xz
SHA-256 actual = 388b167c6a171b3ab6549863e4cc4cb1520c13c56d150268fac161e0ef35b722
```

El SHA-256 exigido por esta tarea es:

```text
d25e7f19ca68113de5ec29344889717f3796cabff64ea8b05fd3bcd3ecb3b4f7
```

Se consultaron los 60 ficheros `.sha256sum` del índice nightly actual y el valor esperado **no apareció**. Por seguridad y reproducibilidad, no se descargó el bundle actual: descargarlo habría incumplido la verificación exacta solicitada. No se descargó otro artefacto alternativo, no se recompiló WebKit y no se ejecutó un runtime cuyo SHA no coincidiera.

## Evidencia disponible

| Elemento | Estado |
|---|---|
| Bundle persistente recuperable | **NOT_FOUND** |
| `MiniBrowser` WPE 2.53.1 | **NOT_FOUND** |
| `WPEWebDriver` WPE 2.53.1 | **NOT_FOUND** |
| `libWPEWebKit-2.0.so*` WPE 2.53.1 | **NOT_FOUND** |
| SHA esperado en índice oficial nightly actual | **NOT_FOUND** |
| `libwpe` local 1.16.3 | **AVAILABLE** en `/tmp/wpe-prefix` |
| `WPEBackend-fdo` local 1.16.1 | **AVAILABLE** en `/tmp/wpe-prefix` |
| Build WPE 2.52.6 | **PRESERVED**, no tocada |

No existe una ruta persistente de bundle que pueda documentarse honestamente. La ruta esperada, una vez proporcionado el artefacto correcto, será `/home/ubuntu/wpe-bundles/wpewebkit-2.53.1/`; el archivo debe conservarse fuera de Git y su manifiesto debe registrar el SHA exacto antes de extraerlo.

## Comando pendiente cuando exista el artefacto correcto

```sh
mkdir -p /home/ubuntu/wpe-bundles/wpewebkit-2.53.1
sha256sum -c /home/ubuntu/wpe-bundles/wpewebkit-2.53.1/MiniBrowser_wpe_*.sha256sum
python3 webkit-kit/tools/diagnose_wpe_minibrowser.py \
  /home/ubuntu/wpe-bundles/wpewebkit-2.53.1/MiniBrowser \
  --prefix /home/ubuntu/wpe-bundles/wpewebkit-2.53.1 \
  --output wpe-2531-diagnostic.json
python3 webkit-kit/tools/run_wpe_headless.py \
  --minibrowser /home/ubuntu/wpe-bundles/wpewebkit-2.53.1/MiniBrowser \
  --prefix /home/ubuntu/wpe-bundles/wpewebkit-2.53.1 \
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

Hasta que el archivo exacto esté disponible y pase el SHA indicado, los estados funcionales permanecen `NOT_RUN`.
