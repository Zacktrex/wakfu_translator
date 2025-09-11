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

def parse_line(line):
    line = re.sub(r"^\d{1,2}:\d{2}:\d{2}(?:,\d{1,3})?\s*-\s*", "", line).strip()
    if line.startswith("[") and "]" in line:
        line = line.split("]", 1)[1].strip()
    if ":" in line:
        sender, message = line.split(":", 1)
        return sender.strip(), message.strip()
    return None, line.strip()

def parse_wakfu_colors(line):
    ts_color = "#FFD700"
    default_color = "#FFFFFF"
    ts_match = re.match(r"^(\d{1,2}:\d{2}:\d{2}(?:,\d{1,3})?)\s*-\s*(.*)", line)
    if ts_match:
        timestamp, rest = ts_match.groups()
    else:
        timestamp, rest = "", line

    color = next((c for ch, c in CHANNEL_COLORS.items() if ch.lower() in rest.lower()), default_color)
    rest = re.sub(r'\|c([0-9A-Fa-f]{6})(.*?)\|r',
                  lambda m: f"<font color='#{m.group(1)}'>{m.group(2)}</font>", rest)

    html = "<span style='padding:2px'>"
    if timestamp:
        html += f"<font color='{ts_color}'>[{timestamp}]</font> "
    html += f"<span style='color:{color}'>{rest}</span></span>"
    return html
