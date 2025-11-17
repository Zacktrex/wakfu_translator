import os, time
from collections import deque
from queue import Queue
from settings import load_settings
from translation.parser import parse_wakfu_colors, should_exclude_from_general, TIMESTAMP_PATTERN
from signals import ui_signals
from PyQt5.QtWidgets import QTextEdit
from constants import MAX_DISPLAYED_LINES

# Use bounded deque instead of unbounded set to prevent memory leak
displayed_lines = deque(maxlen=MAX_DISPLAYED_LINES)
message_queue = Queue()

# Tracked players cache - updated via signal
_tracked_players_cache = {}

def update_tracked_players(players_dict):
    """Signal handler to update tracked players in worker"""
    global _tracked_players_cache
    _tracked_players_cache = players_dict

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
                        
                        # Skip Fight Log and Game Log entirely
                        if should_exclude_from_general(line):
                            displayed_lines.append(line)
                            continue
                        
                        if not line or line in displayed_lines:
                            continue
                        
                        displayed_lines.append(line)
                        
                        # Extract sender name
                        sender_name = extract_player_name(line)
                        
                        # Check if sender is a tracked player (case-insensitive exact match)
                        is_tracked = False
                        source_lang = None
                        if sender_name and _tracked_players_cache:
                            sender_lower = sender_name.lower()
                            for tracked_name, lang in _tracked_players_cache.items():
                                if tracked_name.lower() == sender_lower:
                                    is_tracked = True
                                    source_lang = lang
                                    break
                        
                        # If tracked player, queue for translation with metadata
                        if is_tracked:
                            message_queue.put((line, source_lang, sender_name))
                        
                        # Send to General tab (excluding Fight/Game Log)
                        ui_signals.append_text.emit(line)

                        # Send only to player tab matching the sender (use cached tabs)
                        tabs = ui_signals.chat_ui.tabs.get_cached_tabs()
                        for tab in tabs:
                            player_name = tab.property("player_name")
                            if player_name and sender_name and player_name.lower() in sender_name.lower():
                                ui_signals.append_text_to_tab.emit(tab, line, False)

            except Exception as e:
                ui_signals.status_text.emit(f"⚠️ Error reading chat log: {e}")

        time.sleep(settings.get("check_interval", 2))


def extract_player_name(line):
    """
    Extract player name from chat line.
    Handles formats like: [Channel] PlayerName: message
    """
    # Remove timestamp if present
    line = TIMESTAMP_PATTERN.sub("", line).strip()
    
    # Check for channel prefix like "[Vicinity]" or "[Trade]"
    if line.startswith("[") and "]" in line:
        parts = line.split("]", 1)
        if len(parts) > 1:
            rest = parts[1].strip()
            # Now check if there's a player name with colon
            if ":" in rest:
                player_name = rest.split(":")[0].strip()
                return player_name
    
    return None
    return None