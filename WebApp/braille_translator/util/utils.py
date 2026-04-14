"""
Utility functions for extracting text from various document formats
and translating to Braille
"""
import base64
import binascii
from pathlib import Path
from uuid import uuid4

import PyPDF2
from docx import Document
from django.core.files.base import ContentFile
from django.utils.text import slugify


def extract_text_from_txt(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except UnicodeDecodeError:
        # Try with different encoding
        with open(file_path, 'r', encoding='latin-1') as file:
            return file.read()


def extract_text_from_pdf(file_path):
    try:
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error extracting PDF text: {str(e)}"


def extract_text_from_docx(file_path):
    try:
        doc = Document(file_path)
        text = []
        for paragraph in doc.paragraphs:
            text.append(paragraph.text)
        return '\n'.join(text)
    except Exception as e:
        return f"Error extracting DOCX text: {str(e)}"


def extract_text_from_file(file_path):
    file_extension = Path(file_path).suffix.lower()
    
    try:
        if file_extension == '.txt':
            return extract_text_from_txt(file_path), None
        elif file_extension == '.pdf':
            text = extract_text_from_pdf(file_path)
            if text.startswith("Error"):
                return None, text
            return text, None
        elif file_extension in ['.docx', '.doc']:
            text = extract_text_from_docx(file_path)
            if text.startswith("Error"):
                return None, text
            return text, None
        else:
            return None, f"Unsupported file format: {file_extension}"
    except Exception as e:
        return None, f"Error processing file: {str(e)}"


def camera_image_to_content_file(image_data, title):
    """Convert a browser camera data URL into a Django ContentFile."""
    if not image_data:
        return None, "No camera image was captured."

    if "," not in image_data:
        return None, "Invalid camera image data."

    header, encoded_image = image_data.split(",", 1)

    if "image/" not in header or ";base64" not in header:
        return None, "Unsupported camera image format."

    image_format = header.split("image/")[-1].split(";")[0].lower()
    if image_format == "jpeg":
        image_format = "jpg"

    try:
        decoded_image = base64.b64decode(encoded_image)
    except (ValueError, binascii.Error):
        return None, "Could not decode the captured image."

    file_stem = slugify(title or "camera-capture") or "camera-capture"
    file_name = f"{file_stem}-{uuid4().hex}.{image_format}"
    return ContentFile(decoded_image, name=file_name), None


# Braille mapping (Grade 1 Braille)
BRAILLE_MAP = {
    'a': '⠁', 'b': '⠃', 'c': '⠉', 'd': '⠙', 'e': '⠑',
    'f': '⠋', 'g': '⠛', 'h': '⠓', 'i': '⠊', 'j': '⠚',
    'k': '⠅', 'l': '⠇', 'm': '⠍', 'n': '⠝', 'o': '⠕',
    'p': '⠏', 'q': '⠟', 'r': '⠗', 's': '⠎', 't': '⠞',
    'u': '⠥', 'v': '⠧', 'w': '⠺', 'x': '⠭', 'y': '⠽', 'z': '⠵',
    
    # Numbers (preceded by number sign ⠼)
    '1': '⠼⠁', '2': '⠼⠃', '3': '⠼⠉', '4': '⠼⠙', '5': '⠼⠑',
    '6': '⠼⠋', '7': '⠼⠛', '8': '⠼⠓', '9': '⠼⠊', '0': '⠼⠚',
    
    # Punctuation
    '.': '⠲', ',': '⠂', '?': '⠦', '!': '⠖', ';': '⠆',
    ':': '⠒', '-': '⠤', '(': '⠐⠣', ')': '⠐⠜',
    '"': '⠐⠦', "'": '⠄', '/': '⠸⠌',
    
    # Space and newline
    ' ': ' ', '\n': '\n', '\t': '  ',
}


def text_to_braille(text):
    if not text:
        return ""
    
    braille_text = []
    
    # Capital letter indicator
    CAPITAL_SIGN = '⠠'
    
    for char in text:
        if char.isupper():
            # Add capital sign before uppercase letters
            braille_text.append(CAPITAL_SIGN)
            braille_text.append(BRAILLE_MAP.get(char.lower(), char))
        else:
            braille_text.append(BRAILLE_MAP.get(char, char))
    
    return ''.join(braille_text)


