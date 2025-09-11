from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QDoubleSpinBox, QSpinBox, QFileDialog
)
from settings import load_settings, save_settings


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.resize(500, 320)

        self.settings = load_settings()
        layout = QVBoxLayout(self)

        # Chat log path + browse
        chat_layout = QHBoxLayout()
        chat_label = QLabel("Chat Log Path:")
        self.chat_input = QLineEdit(self.settings.get("chat_log", ""))
        self.chat_browse = QPushButton("Browse...")
        self.chat_browse.clicked.connect(self.browse_chat_log)
        chat_layout.addWidget(chat_label)
        chat_layout.addWidget(self.chat_input)
        chat_layout.addWidget(self.chat_browse)
        layout.addLayout(chat_layout)

        # Model name input
        model_layout = QHBoxLayout()
        model_label = QLabel("Model Name:")
        self.model_input = QLineEdit(self.settings.get("model_name", ""))
        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_input)
        layout.addLayout(model_layout)

        # Transparency
        trans_layout = QHBoxLayout()
        trans_label = QLabel("Transparency:")
        self.transparency_input = QDoubleSpinBox()
        self.transparency_input.setRange(0.1, 1.0)
        self.transparency_input.setSingleStep(0.05)
        self.transparency_input.setValue(float(self.settings.get("transparency", 0.85)))
        self.transparency_input.setDecimals(2)
        trans_layout.addWidget(trans_label)
        trans_layout.addWidget(self.transparency_input)
        layout.addLayout(trans_layout)

        # Check interval
        interval_layout = QHBoxLayout()
        interval_label = QLabel("Check Interval (s):")
        self.interval_input = QSpinBox()
        self.interval_input.setRange(1, 60)
        self.interval_input.setValue(int(self.settings.get("check_interval", 2)))
        interval_layout.addWidget(interval_label)
        interval_layout.addWidget(self.interval_input)
        layout.addLayout(interval_layout)

        # Check last lines
        last_lines_layout = QHBoxLayout()
        last_lines_label = QLabel("Check Last Lines:")
        self.last_lines_input = QSpinBox()
        self.last_lines_input.setRange(10, 500)
        self.last_lines_input.setValue(int(self.settings.get("check_last_lines", 40)))
        last_lines_layout.addWidget(last_lines_label)
        last_lines_layout.addWidget(self.last_lines_input)
        layout.addLayout(last_lines_layout)

        # Target language
        lang_layout = QHBoxLayout()
        lang_label = QLabel("Target Language:")
        self.lang_input = QComboBox()
        self.lang_input.setEditable(True)
        langs = ["en", "fr", "es", "de", "ja", "ko", "zh"]
        self.lang_input.addItems(langs)
        self.lang_input.setCurrentText(self.settings.get("target_lang", "en"))
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.lang_input)
        layout.addLayout(lang_layout)
        # --- Restart notice ---
        self.restart_label = QLabel(
            "⚠️ Any changes here require restarting the app to take effect."
        )
        self.restart_label.setStyleSheet("color: orange; font-weight: bold;")
        layout.addWidget(self.restart_label)

        # Buttons
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.cancel_btn = QPushButton("Cancel")
        btn_layout.addStretch(1)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        # Connections
        self.save_btn.clicked.connect(self.save)
        self.cancel_btn.clicked.connect(self.reject)

    def browse_chat_log(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Chat Log File", "", "Log Files (*.log);;All Files (*)"
        )
        if path:
            self.chat_input.setText(path)

    def save(self):
        self.settings["chat_log"] = self.chat_input.text().strip()
        self.settings["model_name"] = self.model_input.text().strip()
        self.settings["transparency"] = self.transparency_input.value()
        self.settings["check_interval"] = self.interval_input.value()

        self.settings["check_last_lines"] = self.last_lines_input.value()
        self.settings["target_lang"] = self.lang_input.currentText().strip()
        save_settings(self.settings)
        self.accept()
