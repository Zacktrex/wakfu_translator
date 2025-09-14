import argostranslate.package
import argostranslate.translate

from translation.parser import parse_line

def ensure_argos_model(from_code="en", to_code="es"):
    """
    Ensure Argos Translate model for the given language pair is installed.
    Downloads and installs it if necessary (only once).
    """
    installed_languages = argostranslate.translate.get_installed_languages()

    # Check if translation exists
    from_lang = next((lang for lang in installed_languages if lang.code == from_code), None)
    to_lang = next((lang for lang in installed_languages if lang.code == to_code), None)

    if from_lang and to_lang:
        try:
            translation = from_lang.get_translation(to_lang)
            if translation:  # Already installed
                return
        except Exception:
            pass  # Translation not installed yet

    # If not installed, update package index and install
    argostranslate.package.update_package_index()
    available_packages = argostranslate.package.get_available_packages()
    package_to_install = next(
        (pkg for pkg in available_packages if pkg.from_code == from_code and pkg.to_code == to_code),
        None
    )
    if package_to_install:
        argostranslate.package.install_from_path(package_to_install.download())


def translate_text_via_argos(line, from_code="en", to_code="es", sender="Unknown"):
    """
    Translate a given text using Argos Translate, similar to Ollama flow.
    Returns a tuple: (sender, translated_text)
    """
    if not line.strip():
        return None, None

    try:
        # Ensure the translation model is installed
        print("Ensuring Argos model is installed...", from_code, to_code)
        ensure_argos_model(from_code, to_code)
        sender, message = parse_line(line)
        # Perform translation
        translated_text = argostranslate.translate.translate(message, from_code, to_code)
        return sender, translated_text
    except Exception as e:
        return None, f"[Argos Translation Error]: {e}"

# # Example usage
# if __name__ == "__main__":
#     sender, translated = translate_text_via_argos("Hello World!", from_code="en", to_code="es", sender="")
#     print(f"{sender}: {translated}")
#     sender, translated = translate_text_via_argos("Hello World!", from_code="en", to_code="es", sender="")
#     print(f"{sender}: {translated}")
#     # Output: Protic: ¡Hola Mundo!