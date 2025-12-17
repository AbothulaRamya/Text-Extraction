""""import cv2
import pytesseract
import os
import re
from gtts import gTTS
from django.conf import settings
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from difflib import SequenceMatcher
import language_tool_python
from googletrans import Translator, LANGUAGES
import requests
from .models import UploadedMedia

# Set the path for Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Initialize tools
translator = Translator()
grammar_tool = language_tool_python.LanguageTool('en-US')

# Function to check similarity between phrases
def is_similar(a, b, threshold=0.5):
    return SequenceMatcher(None, a, b).ratio() > threshold

# Function to clean redundant and meaningless text
def clean_and_deduplicate_text(text):
    phrases = text.split(". ")
    cleaned_phrases = []
    
    for phrase in phrases:
        phrase = phrase.strip()
        if not phrase:
            continue  # Skip empty phrases
        
        is_duplicate = any(is_similar(phrase, cleaned) for cleaned in cleaned_phrases)
        
        if not is_duplicate:
            cleaned_phrases.append(phrase)

    return ". ".join(cleaned_phrases).strip() + "."

# Extract text from an image
def extract_text_from_image(image_path):
    try:
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(gray, lang='eng')
        return clean_and_deduplicate_text(text)
    except Exception as e:
        print(f"Error extracting text from image: {e}")
        return ""

# Extract text from video frames
def extract_text_from_video(video_path, frame_interval=100):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return "Error: Unable to open video file."

    phrases = []
    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        if frame_count % frame_interval == 0:
            try:
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                _, thresh_frame = cv2.threshold(gray_frame, 128, 255, cv2.THRESH_BINARY)
                text = pytesseract.image_to_string(thresh_frame, lang='eng')
                phrases.append(text)
            except Exception as e:
                print(f"Error processing frame {frame_count}: {e}")

    cap.release()
    return clean_and_deduplicate_text(". ".join(phrases)) if phrases else "No text could be extracted."

# Translate text into the required language
def translate_text(text, target_language='en'):
    try:
        translated = translator.translate(text, dest=target_language)
        return translated.text
    except requests.exceptions.Timeout:
        print("Error: Translation timed out")
        return text
    except Exception as e:
        print(f"Error in translation: {e}")
        return text

# Generate audio from translated text
def generate_audio(text, lang='en'):
    try:
        tts = gTTS(text=text, lang=lang)
        audio_filename = "translated_audio.mp3"
        audio_path = os.path.join(settings.MEDIA_ROOT, audio_filename)
        tts.save(audio_path)
        return settings.MEDIA_URL + audio_filename
    except Exception as e:
        print(f"Error generating audio: {e}")
        return None

# Unified upload view for images and videos
def upload_video(request):
    video_url = None
    image_url = None
    extracted_text = None
    translated_text = None
    audio_url = None
    languages = [(key, LANGUAGES[key].capitalize()) for key in LANGUAGES.keys()]

    if request.method == "POST":
        target_language = request.POST.get("target_language", "en")
        fs = FileSystemStorage(location=settings.MEDIA_ROOT)

        if request.FILES.get("video"):
            video_file = request.FILES["video"]
            filename = fs.save(video_file.name, video_file)
            video_url = settings.MEDIA_URL + filename
            video_path = os.path.join(settings.MEDIA_ROOT, filename)
            extracted_text = extract_text_from_video(video_path)
        
        elif request.FILES.get("image"):
            image_file = request.FILES["image"]
            filename = fs.save(image_file.name, image_file)
            image_url = settings.MEDIA_URL + filename
            image_path = os.path.join(settings.MEDIA_ROOT, filename)
            extracted_text = extract_text_from_image(image_path)
        
        if extracted_text:
            translated_text = translate_text(extracted_text, target_language)
            audio_url = generate_audio(translated_text, target_language)

        return render(request, 'upload_video.html', {
            'video_url': video_url,
            'image_url': image_url,
            'extracted_text': extracted_text,
            'translated_text': translated_text,
            'audio_url': audio_url,
            'languages': languages
        })
        
    return render(request, 'upload_video.html', {'languages': languages})

# View for displaying uploaded media
def media_display(request):
    try:
        media_files = UploadedMedia.objects.latest('uploaded_at')  # Get the latest upload
    except UploadedMedia.DoesNotExist:
        media_files = None  # Handle case where no media is uploaded yet

    return render(request, 'media_display.html', {'media': media_files})
def home(request):
    return render(request, 'home.html')

"""
import cv2
import pytesseract
import os
import re
from gtts import gTTS
from django.conf import settings
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from difflib import SequenceMatcher
import language_tool_python
from googletrans import Translator, LANGUAGES
import requests
from .models import UploadedMedia

# Set the path for Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Initialize tools
translator = Translator()
#grammar_tool = language_tool_python.LanguageTool('en-US')

# Function to check similarity between phrases
def is_similar(a, b, threshold=0.5):
    return SequenceMatcher(None, a, b).ratio() > threshold

# Function to clean redundant and meaningless text
def clean_and_deduplicate_text(text):
    phrases = text.split(". ")
    cleaned_phrases = []
    
    for phrase in phrases:
        phrase = phrase.strip()
        if not phrase:
            continue  # Skip empty phrases
        
        is_duplicate = any(is_similar(phrase, cleaned) for cleaned in cleaned_phrases)
        
        if not is_duplicate:
            cleaned_phrases.append(phrase)

    return ". ".join(cleaned_phrases).strip() + "."

# Function to remove unwanted phrases and characters
def remove_unwanted_phrases(text):
    unwanted_phrases = [
        "TOP", "HEADLINES", "NDTV", "SUMMIT", "PRESIDENT", "PUTIN", "LAWMAKER", "SAFORI"
    ]
    
    for phrase in unwanted_phrases:
        text = re.sub(rf'\b{re.escape(phrase)}\b', '', text, flags=re.IGNORECASE)
    
    text = re.sub(r'[^a-zA-Z0-9., ]+', ' ', text)  # Remove unnecessary characters
    return text.strip()

# Function to refine text cleaning
def refine_text(text):
    text = clean_and_deduplicate_text(text)
    text = remove_unwanted_phrases(text)
    return text

# Extract text from an image
def extract_text_from_image(image_path):
    try:
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(gray, lang='eng')
        return refine_text(text)
    except Exception as e:
        print(f"Error extracting text from image: {e}")
        return ""

# Extract text from video frames
def extract_text_from_video(video_path, frame_interval=100):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return "Error: Unable to open video file."

    phrases = []
    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        if frame_count % frame_interval == 0:
            try:
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                _, thresh_frame = cv2.threshold(gray_frame, 128, 255, cv2.THRESH_BINARY)
                text = pytesseract.image_to_string(thresh_frame, lang='eng')
                phrases.append(text)
            except Exception as e:
                print(f"Error processing frame {frame_count}: {e}")

    cap.release()
    return refine_text(". ".join(phrases)) if phrases else "No text could be extracted."

# Translate text into the required language
def translate_text(text, target_language='en'):
    try:
        translated = translator.translate(text, dest=target_language)
        return translated.text
    except requests.exceptions.Timeout:
        print("Error: Translation timed out")
        return text
    except Exception as e:
        print(f"Error in translation: {e}")
        return text

# Generate audio from translated text
def generate_audio(text, lang='en'):
    try:
        tts = gTTS(text=text, lang=lang)
        audio_filename = "translated_audio.mp3"
        audio_path = os.path.join(settings.MEDIA_ROOT, audio_filename)
        tts.save(audio_path)
        return settings.MEDIA_URL + audio_filename
    except Exception as e:
        print(f"Error generating audio: {e}")
        return None

# Unified upload view for images and videos
def upload_video(request):
    video_url = None
    image_url = None
    extracted_text = None
    translated_text = None
    audio_url = None
    languages = [(key, LANGUAGES[key].capitalize()) for key in LANGUAGES.keys()]

    if request.method == "POST":
        target_language = request.POST.get("target_language", "en")
        fs = FileSystemStorage(location=settings.MEDIA_ROOT)

        if request.FILES.get("video"):
            video_file = request.FILES["video"]
            filename = fs.save(video_file.name, video_file)
            video_url = settings.MEDIA_URL + filename
            video_path = os.path.join(settings.MEDIA_ROOT, filename)
            extracted_text = extract_text_from_video(video_path)
        
        elif request.FILES.get("image"):
            image_file = request.FILES["image"]
            filename = fs.save(image_file.name, image_file)
            image_url = settings.MEDIA_URL + filename
            image_path = os.path.join(settings.MEDIA_ROOT, filename)
            extracted_text = extract_text_from_image(image_path)
        
        if extracted_text:
            translated_text = translate_text(extracted_text, target_language)
            audio_url = generate_audio(translated_text, target_language)

        return render(request, 'upload_video.html', {
            'video_url': video_url,
            'image_url': image_url,
            'extracted_text': extracted_text,
            'translated_text': translated_text,
            'audio_url': audio_url,
            'languages': languages
        })
        
    return render(request, 'upload_video.html', {'languages': languages})

# View for displaying uploaded media
def media_display(request):
    try:
        media_files = UploadedMedia.objects.latest('uploaded_at')  # Get the latest upload
    except UploadedMedia.DoesNotExist:
        media_files = None  # Handle case where no media is uploaded yet

    return render(request, 'media_display.html', {'media': media_files})

def home(request):
    return render(request, 'home.html')
