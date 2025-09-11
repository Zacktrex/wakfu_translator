try:
    import ollama
    OLLAMA_AVAILABLE = True
except Exception:
    ollama = None
    OLLAMA_AVAILABLE = False

from translation.parser import parse_line
from settings import DEFAULT_SETTINGS

def translate_text_via_ollama(line, target_lang, model_name):
    if not OLLAMA_AVAILABLE:
        return None, "[Ollama Not Available]"

    sender, message = parse_line(line)
    if not message:
        return None, None

    model_name = model_name or DEFAULT_SETTINGS["model_name"]
    prompt = f"Translate this into {target_lang}. ONLY return translated text:\n\n{message}"
    try:
        resp = ollama.chat(model=model_name, messages=[{"role": "user", "content": prompt}])
        translated = resp.get("message", {}).get("content", "").strip()
        return sender or "Unknown", translated
    except Exception as e:
        return None, f"[Translation Error]: {e}"
