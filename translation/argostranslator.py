import argostranslate.package
import argostranslate.translate
import threading

from translation.parser import parse_line
from constants import MAX_TRANSLATION_CACHE_SIZE, MODEL_INSTALL_TIMEOUT

# Cache installed language pairs to avoid repeated checks
_installed_pairs = set()
_installation_lock = threading.Lock()
# Translation cache to avoid re-translating same messages
_translation_cache = {}
_cache_lock = threading.Lock()

def ensure_argos_model(from_code="en", to_code="es"):
    """
    Ensure Argos Translate model for the given language pair is installed.
    Downloads and installs it if necessary (only once).
    """
    pair_key = f"{from_code}-{to_code}"
    
    # Quick check if already installed
    if pair_key in _installed_pairs:
        return
    
    with _installation_lock:
        # Double-check after acquiring lock
        if pair_key in _installed_pairs:
            return
            
        installed_languages = argostranslate.translate.get_installed_languages()

        # Check if translation exists
        from_lang = next((lang for lang in installed_languages if lang.code == from_code), None)
        to_lang = next((lang for lang in installed_languages if lang.code == to_code), None)

        if from_lang and to_lang:
            try:
                translation = from_lang.get_translation(to_lang)
                if translation:  # Already installed
                    _installed_pairs.add(pair_key)
                    return
            except Exception:
                pass  # Translation not installed yet

        # If not installed, update package index and install in background
        def _install_model():
            try:
                argostranslate.package.update_package_index()
                available_packages = argostranslate.package.get_available_packages()
                package_to_install = next(
                    (pkg for pkg in available_packages if pkg.from_code == from_code and pkg.to_code == to_code),
                    None
                )
                if package_to_install:
                    argostranslate.package.install_from_path(package_to_install.download())
                    _installed_pairs.add(pair_key)
            except Exception as e:
                print(f"Model installation error ({from_code}->{to_code}): {e}")
        
        # Run installation in background thread
        install_thread = threading.Thread(target=_install_model, daemon=True)
        install_thread.start()
        # Wait for installation to complete (with timeout)
        install_thread.join(timeout=MODEL_INSTALL_TIMEOUT)


def translate_text_via_argos(line, from_code="en", to_code="es", sender="Unknown"):
    """
    Translate a given text using Argos Translate, similar to Ollama flow.
    Returns a tuple: (sender, translated_text)
    """
    if not line.strip():
        return None, None

    # Check cache first
    cache_key = f"{from_code}:{to_code}:{line}"
    with _cache_lock:
        if cache_key in _translation_cache:
            return _translation_cache[cache_key]

    try:
        # Ensure the translation model is installed
        ensure_argos_model(from_code, to_code)
        sender, message = parse_line(line)
        if not message:
            return sender, None
        # Perform translation
        translated_text = argostranslate.translate.translate(message, from_code, to_code)
        result = (sender, translated_text)
        
        # Cache the result
        with _cache_lock:
            # Evict oldest entries if cache is full
            if len(_translation_cache) >= MAX_TRANSLATION_CACHE_SIZE:
                # Remove first 20% of entries
                keys_to_remove = list(_translation_cache.keys())[:MAX_TRANSLATION_CACHE_SIZE // 5]
                for key in keys_to_remove:
                    del _translation_cache[key]
            _translation_cache[cache_key] = result
        
        return result
    except Exception as e:
        return None, f"[Argos Translation Error]: {e}"

# # Example usage
# if __name__ == "__main__":
#     sender, translated = translate_text_via_argos("Hello World!", from_code="en", to_code="es", sender="")
#     print(f"{sender}: {translated}")
#     sender, translated = translate_text_via_argos("Hello World!", from_code="en", to_code="es", sender="")
#     print(f"{sender}: {translated}")
#     # Output: Protic: ¡Hola Mundo!