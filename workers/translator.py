import time
from collections import deque
from PyQt5.QtCore import QTime
from settings import load_settings
from translation.argostranslator import translate_text_via_argos
from signals import ui_signals
from workers.file_reader import message_queue
from PyQt5.QtWidgets import QTextEdit
from translation.parser import parse_line

translated_lines = deque(maxlen=1000)


# workers/translator.py
def translator_worker(stop_event):
    settings = load_settings()
    translated_lines = deque(maxlen=1000)

    while not stop_event.is_set():
        try:
            line = message_queue.get(timeout=1)
        except Exception:
            continue

        timestamp = QTime.currentTime().toString("HH:mm:ss")
        # For each player tab
        for tab in ui_signals.chat_ui.tabs.findChildren(QTextEdit):
            player_name = tab.property("player_name")
            if not player_name:
                continue  # skip General tab

            sender, message = parse_line(line)
            if not message:
                continue

            # Only translate if the sender matches the tab name
            if sender and player_name.lower() in sender.lower():
                tab_source_lang = tab.property("source_lang") or "en"  # <-- get per-tab
                sender_name, translated = translate_text_via_argos(
                    line,
                    from_code=tab_source_lang,
                    to_code=settings.get("target_lang", "en"),
                    sender="",
                )

                if translated and line not in translated_lines:
                    translated_lines.append(line)
                    ui_signals.append_text_to_tab.emit(
                        tab, f"[{timestamp}] {sender_name}: {translated}", True
                    )
