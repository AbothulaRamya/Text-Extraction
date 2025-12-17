from PIL import Image
import pytesseract
from googletrans import Translator
from langdetect import detect

# Extract text from image
def extract_text(image_path, lang='eng'):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image, lang=lang)
    return text

# Detect the language of text
def detect_language(text):
    return detect(text)

# Translate text to target language
def translate_text(text, target_lang='en'):
    translator = Translator()
    translation = translator.translate(text, dest=target_lang)
    return translation.text
