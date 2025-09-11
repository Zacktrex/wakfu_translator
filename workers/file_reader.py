import os, time
from collections import deque
from queue import Queue
from settings import load_settings
from translation.parser import parse_wakfu_colors
from signals import ui_signals
from PyQt5.QtWidgets import QTextEdit  # <--- add this

displayed_lines = set()
message_queue = Queue()

import os, time

# workers/file_reader.py
def file_reader_worker(stop_event, settings, ui_signals):
    chat_log = settings.get("chat_log", "")
    last_warned = False

    while not stop_event.is_set():
        if not os.path.exists(chat_log):
            if not last_warned:
                ui_signals.status_text.emit("⚠️ Chat log file not found. go to settings to set it and restart the app if its first run.")
                last_warned = True
            time.sleep(settings.get("check_interval", 2))
            continue
        else:
            if last_warned:
                ui_signals.status_text.emit(f"✅ Chat log file found: {chat_log}")
                last_warned = False

            try:
                with open(chat_log, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()[-settings.get("check_last_lines", 40):]
                    for line in lines:
                        line = line.strip()
                        if not line or line in displayed_lines:
                            continue
                        displayed_lines.add(line)
                        message_queue.put(line)  # send it to translator

                        # Extract sender/player from line
                        sender_name = extract_player_name(line)  # implement this function

                        # Send to General tab
                        ui_signals.append_text.emit(line)

                        # Send only to player tab matching the sender
                        for tab in ui_signals.chat_ui.tabs.findChildren(QTextEdit):
                            player_name = tab.property("player_name")
                            if player_name and sender_name and player_name.lower() == sender_name.lower():
                                ui_signals.append_text_to_tab.emit(tab, line, False)

            except Exception as e:
                ui_signals.status_text.emit(f"⚠️ Error reading chat log: {e}")

        time.sleep(settings.get("check_interval", 2))



def extract_player_name(line):
    # Example format: "[PlayerName] message"
    if line.startswith("[") and "]" in line:
        return line.split("]")[0][1:]
    return None