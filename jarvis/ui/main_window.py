from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any

from PySide6.QtCore import QObject, QThread, Signal, Slot, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QCheckBox, QDialog, QDialogButtonBox, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QListWidget, QMainWindow, QMessageBox, QPushButton, QPlainTextEdit, QSpinBox, QSplitter, QTabWidget, QVBoxLayout, QWidget)

class FirstRunDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent); self.setWindowTitle("Configurar JARVIS"); self.setMinimumWidth(420)
        self.user = QLineEdit(); self.assistant = QLineEdit("JARVIS")
        form = QFormLayout(); form.addRow("¿Cómo quieres que te llame?", self.user); form.addRow("Nombre del asistente", self.assistant)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel); buttons.accepted.connect(self.accept); buttons.rejected.connect(self.reject)
        layout = QVBoxLayout(self); layout.addWidget(QLabel("Primera configuración")); layout.addLayout(form); layout.addWidget(buttons)

class Worker(QObject):
    finished = Signal(str); status = Signal(str); event = Signal(object)
    def __init__(self, engine, prompt): super().__init__(); self.engine, self.prompt = engine, prompt
    @Slot()
    def run(self):
        self.engine.on_status = self.status.emit; self.engine.on_event = self.event.emit
        self.finished.emit(self.engine.run(self.prompt))

class MainWindow(QMainWindow):
    confirmation_requested = Signal(str, object)

    def __init__(self, config: dict[str, Any], engine, voice, config_path: Path):
        super().__init__(); self.config, self.engine, self.voice, self.config_path = config, engine, voice, config_path; self.thread = None
        self.setWindowTitle(f"{config.get('assistant_name', 'JARVIS')} · Asistente local"); self.resize(1200, 760)
        self.engine.on_confirmation = self.request_confirmation
        self.confirmation_requested.connect(self.show_confirmation)
        self._build(); self._apply_style()

    def _build(self):
        central = QWidget(); root = QVBoxLayout(central); self.setCentralWidget(central)
        header = QHBoxLayout(); self.title = QLabel(self.windowTitle()); self.title.setObjectName("title"); self.status = QLabel("● Listo"); self.stop = QPushButton("STOP"); self.stop.clicked.connect(self.engine.stop); header.addWidget(self.title); header.addStretch(); header.addWidget(self.status); header.addWidget(self.stop); root.addLayout(header)
        split = QSplitter(Qt.Horizontal); root.addWidget(split, 1)
        left = QWidget(); ll = QVBoxLayout(left); self.chat = QPlainTextEdit(); self.chat.setReadOnly(True); self.input = QPlainTextEdit(); self.input.setPlaceholderText("Escribe una tarea para JARVIS… (Ctrl+Enter para enviar)"); self.input.setMaximumHeight(110); send = QPushButton("Enviar"); send.clicked.connect(self.send); self.input.keyPressEvent = self._key_event
        ll.addWidget(self.chat, 1); ll.addWidget(self.input); ll.addWidget(send); split.addWidget(left)
        right = QTabWidget(); actions = QWidget(); al = QVBoxLayout(actions); self.action_list = QListWidget(); al.addWidget(QLabel("Historial local de acciones")); al.addWidget(self.action_list); right.addTab(actions, "Acciones")
        settings = QWidget(); form = QFormLayout(settings); self.model = QLineEdit(self.config["ollama"]["model"]); self.max_steps = QSpinBox(); self.max_steps.setRange(1, 100); self.max_steps.setValue(int(self.config["agent"]["max_steps"])); self.auto = QCheckBox(); self.auto.setChecked(bool(self.config["agent"].get("autonomous_mode", False))); save = QPushButton("Guardar configuración"); save.clicked.connect(self.save_config); form.addRow("Modelo Ollama", self.model); form.addRow("Máximo de pasos", self.max_steps); form.addRow("Modo autónomo", self.auto); form.addRow(save); right.addTab(settings, "Configuración")
        split.addWidget(right); split.setSizes([800, 400])
        self._welcome()

    def _welcome(self):
        name = self.config.get("user_name") or "usuario"
        self.chat.appendPlainText(f"{self.config.get('assistant_name', 'JARVIS')}: Hola, {name}. Estoy ejecutándome localmente y listo para ayudarte.")
        for row in self.engine.memory.recent_actions(): self.action_list.addItem(f"{row.get('timestamp','')} · {row.get('phase')} · {row.get('tool')} · {'OK' if row.get('success') else 'ERROR'}")

    def _key_event(self, event):
        if event.key() == Qt.Key_Return and event.modifiers() & Qt.ControlModifier: self.send()
        else: QPlainTextEdit.keyPressEvent(self.input, event)

    def send(self):
        prompt = self.input.toPlainText().strip()
        if not prompt or self.thread and self.thread.isRunning(): return
        self.input.clear(); self.chat.appendPlainText(f"Tú: {prompt}"); self.status.setText("● Pensando…"); self.engine.reset_stop()
        self.thread = QThread(); worker = Worker(self.engine, prompt); worker.moveToThread(self.thread); self.thread.started.connect(worker.run); worker.status.connect(self.set_status); worker.event.connect(self.on_event); worker.finished.connect(self.on_finished); worker.finished.connect(self.thread.quit); self.thread.finished.connect(worker.deleteLater); self.thread.start()

    def request_confirmation(self, message: str) -> bool:
        decision = {"value": False}; done = threading.Event()
        self.confirmation_requested.emit(message, (decision, done)); done.wait(timeout=300)
        return bool(decision["value"])

    @Slot(str, object)
    def show_confirmation(self, message: str, payload: object):
        decision, done = payload
        answer = QMessageBox.question(self, "Confirmación requerida", message, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        decision["value"] = answer == QMessageBox.Yes
        done.set()

    @Slot(str)
    def set_status(self, value): self.status.setText(f"● {value.capitalize()}")
    @Slot(object)
    def on_event(self, event): self.action_list.insertItem(0, f"{event.timestamp} · {event.phase} · {event.tool} · {'OK' if event.success else 'ERROR'}")
    @Slot(str)
    def on_finished(self, text): self.chat.appendPlainText(f"{self.config.get('assistant_name','JARVIS')}: {text}\n"); self.status.setText("● Listo");

    def save_config(self):
        self.config["ollama"]["model"] = self.model.text().strip() or self.config["ollama"]["model"]; self.config["agent"]["max_steps"] = self.max_steps.value(); self.config["agent"]["autonomous_mode"] = self.auto.isChecked(); self.config_path.write_text(json.dumps(self.config, ensure_ascii=False, indent=2), encoding="utf-8"); self.engine.config = self.config; QMessageBox.information(self, "JARVIS", "Configuración guardada.")

    def _apply_style(self):
        self.setStyleSheet("""QMainWindow,QWidget{background:#101318;color:#e8edf2}QPlainTextEdit,QListWidget,QLineEdit,QSpinBox{background:#171c23;border:1px solid #2b3542;border-radius:8px;padding:8px;color:#e8edf2}QPushButton{background:#2563eb;color:white;border:0;border-radius:7px;padding:9px 16px;font-weight:600}QPushButton:hover{background:#3b82f6}#title{font-size:20px;font-weight:700}QTabWidget::pane{border:1px solid #2b3542;border-radius:8px}QTabBar::tab{padding:9px 16px}""")
