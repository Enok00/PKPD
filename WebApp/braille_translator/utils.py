"""
Utility functions for extracting text from various document formats
and translating to Braille
"""
import os
from pathlib import Path


def extract_text_from_txt(file_path):
    """Extract text from .txt file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except UnicodeDecodeError:
        # Try with different encoding
        with open(file_path, 'r', encoding='latin-1') as file:
            return file.read()


def extract_text_from_pdf(file_path):
    """Extract text from PDF file"""
    try:
        import PyPDF2
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    except ImportError:
        return "Error: PyPDF2 library not installed. Please install it with: pip install PyPDF2"
    except Exception as e:
        return f"Error extracting PDF text: {str(e)}"


def extract_text_from_docx(file_path):
    """Extract text from Word document"""
    try:
        from docx import Document
        doc = Document(file_path)
        text = []
        for paragraph in doc.paragraphs:
            text.append(paragraph.text)
        return '\n'.join(text)
    except ImportError:
        return "Error: python-docx library not installed. Please install it with: pip install python-docx"
    except Exception as e:
        return f"Error extracting DOCX text: {str(e)}"


def extract_text_from_file(file_path):
    """
    Extract text from supported file formats
    Returns: tuple (text, error_message)
    """
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


def text_to_braille_liblouis(text, grade=1):
    """
    Convert text to Braille using liblouis library (more accurate)
    grade: 1 for Grade 1 Braille, 2 for Grade 2 Braille
    """
    try:
        import louis
        
        # Select the appropriate translation table
        if grade == 2:
            table = "en-us-g2.ctb"  # English Grade 2
        else:
            table = "en-us-g1.ctb"  # English Grade 1
        
        braille = louis.translateString([table], text)
        return braille
    except ImportError:
        # Fallback to basic translation if louis is not installed
        return text_to_braille(text) + "\n\n(Note: Install 'louis' library for more accurate Grade 2 Braille translation)"
    except Exception as e:
        # Fallback to basic translation if there's an error
        return text_to_braille(text) + f"\n\n(Note: Error using liblouis: {str(e)})"
