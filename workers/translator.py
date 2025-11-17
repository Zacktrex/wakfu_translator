import time
from collections import deque
from PyQt5.QtCore import QTime
from settings import load_settings
from translation.argostranslator import translate_text_via_argos
from signals import ui_signals
from workers.file_reader import message_queue
from PyQt5.QtWidgets import QTextEdit
from translation.parser import parse_line
from constants import MAX_TRANSLATED_LINES, MESSAGE_QUEUE_TIMEOUT

translated_lines = deque(maxlen=MAX_TRANSLATED_LINES)

# Settings cache - reload only on signal
_settings_cache = None

def _load_settings_cache():
    global _settings_cache
    _settings_cache = load_settings()

# Load settings once at startup
_load_settings_cache()


# workers/translator.py
def translator_worker(stop_event):
    global _settings_cache
    translated_lines = deque(maxlen=MAX_TRANSLATED_LINES)

    while not stop_event.is_set():
        try:
            # Now expecting tuple: (line, source_lang, sender_name) or old format (str)
            queue_item = message_queue.get(timeout=MESSAGE_QUEUE_TIMEOUT)
            
            # Handle both old format (str) and new format (tuple)
            if isinstance(queue_item, tuple):
                line, source_lang, sender_name = queue_item
            else:
                # Fallback for compatibility (old player tab system)
                line = queue_item
                source_lang = None
                sender_name = None
                
        except Exception:
            continue

        # Use cached settings (updated only on settings save signal)
        settings = _settings_cache or load_settings()
        timestamp = QTime.currentTime().toString("HH:mm:ss")
        
        # Handle tracked player translation (new system)
        if source_lang and sender_name:
            sender, message = parse_line(line)
            if not message:
                continue
            
            target_lang = settings.get("target_lang", "en")
            
            # Skip if source == target language
            if source_lang == target_lang:
                continue
            
            # Translate using tracked player's language
            _, translated = translate_text_via_argos(
                message,
                from_code=source_lang,
                to_code=target_lang,
                sender="",
            )

            if translated and line not in translated_lines:
                translated_lines.append(line)
                
                # Format: [time] PlayerName (fr→en): translated message
                formatted = f"[{timestamp}] {sender_name} ({source_lang}→{target_lang}): {translated}"
                
                # Send translated message to General tab only
                ui_signals.append_text.emit(formatted)
            continue
        
        # Handle old player tab system (if queue_item was just a string)
        # Use cached tab list instead of findChildren for performance
        tabs = ui_signals.chat_ui.tabs.get_cached_tabs()
        for tab in tabs:
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
