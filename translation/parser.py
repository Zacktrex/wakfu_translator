import re

CHANNEL_COLORS = {
    "Vicinity": "#FFFFFF",
    "Trade": "#FFA500",
    "Recruitment": "#FF1493",
    "Politics": "#00FF00",
    "Private": "#1E90FF",
    "Group": "#800080",
    "Guild": "#FFA500",
    "Alliance": "#87CEFA",
    "Team": "#FFFF00",
    "Game Log": "#1D7906",
    "Ankama Discussion": "#1E90FF"
}

# Pre-compiled regex patterns for performance
TIMESTAMP_PATTERN = re.compile(r"^\d{1,2}:\d{2}:\d{2}(?:,\d{1,3})?\s*-\s*")
TIMESTAMP_MATCH_PATTERN = re.compile(r"^(\d{1,2}:\d{2}:\d{2}(?:,\d{1,3})?)\s*-\s*(.*)")
COLOR_CODE_PATTERN = re.compile(r'\|c([0-9A-Fa-f]{6})(.*?)\|r')


def should_exclude_from_general(line: str) -> bool:
    """
    Check if a line should be excluded from General tab.
    Returns True if line contains Fight Log or Game Log.
    """
    from constants import EXCLUDED_CHANNELS
    return any(f"[{channel}]" in line for channel in EXCLUDED_CHANNELS)


def parse_line(line):
    line = TIMESTAMP_PATTERN.sub("", line).strip()
    # Skip Fight Log entries entirely
    if "[Fight Log]" in line:
        return None, None
    if line.startswith("[") and "]" in line:
        line = line.split("]", 1)[1].strip()
    if ":" in line:
        sender, message = line.split(":", 1)
        return sender.strip(), message.strip()
    return None, line.strip()

def parse_wakfu_colors(line):
    ts_color = "#FFD700"
    default_color = "#FFFFFF"
    ts_match = TIMESTAMP_MATCH_PATTERN.match(line)
    if ts_match:
        timestamp, rest = ts_match.groups()
    else:
        timestamp, rest = "", line

    color = next((c for ch, c in CHANNEL_COLORS.items() if ch.lower() in rest.lower()), default_color)
    rest = COLOR_CODE_PATTERN.sub(
                  lambda m: f"<font color='#{m.group(1)}'>{m.group(2)}</font>", rest)

    html = "<span style='padding:2px'>"
    if timestamp:
        html += f"<font color='{ts_color}'>[{timestamp}]</font> "
    html += f"<span style='color:{color}'>{rest}</span></span>"
    return html
