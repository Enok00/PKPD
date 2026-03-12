"""
Utility functions for extracting text from various document formats
and translating to Braille
"""
from pathlib import Path
import PyPDF2
from docx import Document


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


# Braille Unicode mapping (Grade 1 Braille)
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
    """
    Convert regular text to Braille Unicode characters (Grade 1 Braille)
    This is a basic implementation. For more advanced Grade 2 Braille,
    consider using the 'louis' library (liblouis)
    """
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


