from __future__ import annotations

import threading
from typing import Callable

class VoiceService:
    def __init__(self, config: dict):
        self.config = config.get("voice", {})
        self._tts = None
        self._model = None
        if self.config.get("tts_enabled"):
            try:
                import pyttsx3
                self._tts = pyttsx3.init()
                self._tts.setProperty("rate", int(self.config.get("tts_rate", 175)))
            except Exception:
                self._tts = None

    def speak(self, text: str) -> None:
        if not self._tts: return
        self._tts.say(text); self._tts.runAndWait()

    def listen_once(self, on_text: Callable[[str], None], seconds: int = 8) -> None:
        def worker() -> None:
            try:
                import sounddevice as sd
                import numpy as np
                samplerate = 16000
                audio = sd.rec(int(seconds * samplerate), samplerate=samplerate, channels=1, dtype="float32")
                sd.wait()
                if self._model is None:
                    from faster_whisper import WhisperModel
                    self._model = WhisperModel(self.config.get("stt_model", "base"), device="cpu", compute_type="int8")
                segments, _ = self._model.transcribe(np.squeeze(audio), language="es")
                text = " ".join(segment.text.strip() for segment in segments).strip()
                if text: on_text(text)
            except ImportError:
                on_text("STT opcional no instalado. Instala faster-whisper para activar el micrófono local.")
            except Exception as exc:
                on_text(f"Error de voz: {exc}")
        threading.Thread(target=worker, daemon=True).start()
