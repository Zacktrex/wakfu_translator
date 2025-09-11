import time
from collections import deque
from PyQt5.QtCore import QTime
from settings import load_settings
from translation.translator import translate_text_via_ollama
from signals import ui_signals
from workers.file_reader import message_queue

translated_lines = deque(maxlen=1000)



# workers/translator.py
def translator_worker(stop_event):
    from settings import load_settings
    from translation.translator import translate_text_via_ollama
    from signals import ui_signals
    from workers.file_reader import message_queue
    from PyQt5.QtCore import QTime
    from collections import deque

    settings = load_settings()
    translated_lines = deque(maxlen=1000)

    while not stop_event.is_set():
        try:
            line = message_queue.get(timeout=1)
        except Exception:
            continue

        sender, translated = translate_text_via_ollama(
            line, settings.get("target_lang", "en"), settings.get("model_name", "")
        )
        if translated and line not in translated_lines:
            translated_lines.append(line)
            timestamp = QTime.currentTime().toString("HH:mm:ss")
            ui_signals.append_text.emit(f"[{timestamp}] {sender or 'Unknown'}: {translated}")



