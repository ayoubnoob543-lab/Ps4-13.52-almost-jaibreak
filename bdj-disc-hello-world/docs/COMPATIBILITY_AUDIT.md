# Static compatibility audit

## Resultado

La imagen generada contiene un BDJO que referencia exactamente `org.homebrew.MyXlet`, y el JAR contiene esa clase junto con sus clases internas. La comprobación de cadenas del BDJO produjo `MATCH`.

El bytecode se inspeccionó con JDK8 sin ejecutarlo. Las referencias simbólicas del Xlet apuntan a `javax.tv.xlet.Xlet`, `javax.tv.xlet.XletContext`, `org.havi.ui.HScene` y `org.havi.ui.HSceneFactory`, que están presentes en los stubs públicos usados durante la compilación.

El JAR contiene una firma JAR válida con `META-INF/MANIFEST.MF`, `META-INF/SIG-BD00.SF` y `META-INF/SIG-BD00.RSA`. La plantilla BDMV incluye `BDMV/index.bdmv`, `MovieObject.bdmv`, el BDJO, playlist, clip info, stream, fuentes y certificados de la plantilla pública del SDK.

## Hashes observados

| Artefacto | Tamaño | SHA-256 |
|---|---:|---|
| `build/bdj-hello-world.iso` | 16,777,216 bytes | `ad043fc4a1ac6ecd1a9a5cabb876e6daa849d52e5ec1afb3de29822dff148fdb` |
| `build/discdir/BDMV/JAR/00000.jar` | 4,320 bytes | `7cff985677ca0511afeaf35b89f0f7eb0e192708ddb39030734979269fcc7065` |
| `build/discdir/BDMV/BDJO/00000.bdjo` | 166 bytes | `d32325af03d55c054fe7766cc96a8bb14cd10a0c5dc06a3a58938f04427cdea5` |

## Límites

Esta auditoría no emula el reproductor BD-J propietario de PlayStation y no ejecuta el JAR ni la ISO. Por ello confirma consistencia de authoring y referencias, pero no confirma que una PS4 13.52 acepte la imagen o muestre el Xlet. Esa comprobación sólo puede realizarse mediante una prueba autorizada en el equipo objetivo.

La imagen no contiene explotación, código nativo, acceso a kernel, carga dinámica ni lógica para eludir el sandbox.
