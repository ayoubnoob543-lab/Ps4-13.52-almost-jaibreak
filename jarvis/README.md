# JARVIS — agente de escritorio local para Windows

JARVIS es un agente de escritorio modular que conversa con un modelo local de Ollama y puede observar la pantalla, controlar ratón y teclado, gestionar aplicaciones, trabajar con archivos y proyectos, ejecutar PowerShell/Git y asistir en tareas de programación. La interfaz y el historial se ejecutan localmente; no se incluyen APIs de pago ni telemetría.

> **Importante:** este programa puede controlar el equipo y ejecutar comandos. En modo normal solicita confirmación para borrados, PowerShell/Git y acciones sensibles. El botón **STOP** interrumpe el bucle del agente, pero no puede deshacer una acción ya completada.

## Instalación con PowerShell

Abre PowerShell en la carpeta `jarvis` y ejecuta:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.install.ps1
```

Si ya tienes Python 3.11 o posterior:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Instala [Ollama para Windows](https://ollama.com/download/windows), abre una consola y descarga un modelo de texto. Para visión, descarga también uno compatible:

```powershell
ollama serve
ollama pull llama3.2:3b
ollama pull llava:7b
```

En otra consola, ejecuta:

```powershell
.run.ps1
```

También puedes iniciar directamente:

```powershell
.\.venv\Scripts\python.exe .\main.py
```

## Primer inicio y configuración

El primer inicio pregunta cómo llamarte y qué nombre quieres dar al asistente. Los valores se guardan en `config.json`. El modelo, la URL de Ollama, el límite de pasos, el directorio de trabajo, la confirmación de acciones y la voz se pueden cambiar allí o desde la pestaña **Configuración**.

El directorio por defecto para rutas relativas es la carpeta del proyecto JARVIS. Para trabajar en otro proyecto, establece `agent.workspace_root` a una ruta absoluta de Windows, por ejemplo `C:\\Users\\Ana\\source\\repos\\mi-proyecto`.

## Arquitectura

| Módulo | Responsabilidad |
|---|---|
| `agent/` | Bucle OBSERVE → PLAN → ACT → VERIFY → REPAIR → DONE, cliente Ollama y memoria local. |
| `computer/` | Capturas, ratón, teclado, aplicaciones, procesos, PowerShell, archivos y Git. |
| `coding/` | Espacio de trabajo para proyectos; las operaciones de código usan lectura/escritura, Git y ejecución controlada. |
| `voice/` | TTS local con pyttsx3 y STT opcional con sounddevice/faster-whisper. |
| `ui/` | Interfaz PySide6, chat, estado, historial y STOP. |
| `data/` | Conversación, acciones y capturas; permanece local. |

Cada ciclo de acción registra fase, herramienta, argumentos, resultado, éxito y hora en `data/actions.jsonl`. La conversación se conserva en `data/conversation.json`. El sistema no oculta procesos y las llamadas a Ollama apuntan por defecto a `127.0.0.1`.

## Visión y voz

La herramienta `screenshot` guarda `data/screenshots/latest.png`. La arquitectura del cliente Ollama admite mensajes con imágenes y selecciona `ollama.vision_model` cuando se solicita visión; el catálogo actual prioriza acciones de escritorio y puede ampliarse con una herramienta de análisis visual sin cambiar la interfaz. La voz es opcional: TTS funciona con `pyttsx3`; STT requiere instalar `faster-whisper`, que descarga el modelo indicado en su primera utilización.

## Seguridad y operación

El modo normal (`autonomous_mode: false`) pide confirmación antes de borrar, ejecutar PowerShell/Git y controlar aplicaciones. El modo autónomo puede activarse únicamente desde la configuración. La lista `blocked_commands` identifica comandos especialmente destructivos y fuerza confirmación aunque se cambie otra opción. Se recomienda usar una cuenta de Windows sin privilegios administrativos y probar primero en una carpeta de trabajo.

## Comprobación

```powershell
.\.venv\Scripts\python.exe -m compileall .
.\.venv\Scripts\python.exe -m pytest -q
```

## Solución de problemas

Si aparece “No encuentro Ollama”, inicia `ollama serve` y verifica `http://127.0.0.1:11434/api/tags`. Si PyAutoGUI no puede controlar el escritorio, revisa permisos de accesibilidad/seguridad de Windows y que la sesión tenga un escritorio interactivo. Si un modelo no admite visión, JARVIS continúa funcionando en texto con el modelo principal.
