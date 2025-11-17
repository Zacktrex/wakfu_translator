from PyQt5.QtCore import QObject, pyqtSignal

class UISignals(QObject):
    append_text = pyqtSignal(str)
    status_text = pyqtSignal(str)
    # Add is_ai parameter for AI tab messages
    append_text_to_tab = pyqtSignal(object, str, bool)
    # Signal for tracked players updates
    tracked_players_updated = pyqtSignal(dict)

# Instantiate it so other modules can import
ui_signals = UISignals()
