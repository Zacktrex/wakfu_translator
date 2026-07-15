from pathlib import Path
from argostranslate import package, translate
import os

# Path to your downloaded Argos model
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "en_es.argosmodel"

def install_model():
    """Install the Argos translation model if available."""
    if not MODEL_PATH.exists():
        print(f"Model file not found: {MODEL_PATH}")
        return False

    try:
        package.install_from_path(MODEL_PATH)
        print("✅ Model installed successfully.")
        return True
    except Exception as e:
        print(f"❌ Error installing model: {e}")
        return False


def get_translation():
    """Get the English -> Spanish translation object."""
    installed_languages = translate.get_installed_languages()

    print("\nInstalled Languages:")
    for lang in installed_languages:
        print(f" - {lang}")

    english = next((lang for lang in installed_languages if lang.name == "English"), None)
    spanish = next((lang for lang in installed_languages if lang.name == "Spanish"), None)

    if english is None or spanish is None:
        raise Exception("English or Spanish language package not installed.")

    translator = english.get_translation(spanish)
    if translator is None:
        raise Exception("Could not create the translation object.")

    return translator


def test_translation():
    """Run some test translations."""
    translator = get_translation()

    test_sentences = [
        "Hello World!",
        "How are you?",
        "This is a test.",
        "I love Python.",
        "Good morning!"
    ]

    print("\nTranslations:")
    print("-" * 40)

    for sentence in test_sentences:
        translated = translator.translate(sentence)
        print(f"EN: {sentence}")
        print(f"ES: {translated}")
        print("-" * 40)


if __name__ == "__main__":
    install_model()
    test_translation()