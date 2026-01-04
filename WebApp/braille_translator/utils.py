"""
Utility functions for extracting text from various document formats
and translating to Braille
"""
import os
from pathlib import Path
import PyPDF2
from docx import Document
import cv2
import numpy as np
from PIL import Image


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


# Braille to text mapping (reverse of BRAILLE_MAP)
BRAILLE_TO_TEXT = {v: k for k, v in BRAILLE_MAP.items()}


def braille_to_text(braille_string):
    """
    Convert Braille Unicode characters back to regular text
    """
    if not braille_string:
        return ""
    
    regular_text = []
    capital_next = False
    
    i = 0
    while i < len(braille_string):
        char = braille_string[i]
        
        # Check for capital sign
        if char == '⠠':
            capital_next = True
            i += 1
            continue
        
        # Check for number sign (need to handle multi-character numbers)
        if char == '⠼' and i + 1 < len(braille_string):
            # Get the next braille character for the number
            next_char = braille_string[i + 1]
            # Number braille pattern is ⠼ followed by a letter braille
            number_braille = '⠼' + next_char
            text_char = BRAILLE_TO_TEXT.get(number_braille, '')
            regular_text.append(text_char)
            i += 2
            continue
        
        # Regular character translation
        text_char = BRAILLE_TO_TEXT.get(char, char)
        
        if capital_next and text_char.isalpha():
            text_char = text_char.upper()
            capital_next = False
        
        regular_text.append(text_char)
        i += 1
    
    return ''.join(regular_text)


def preprocess_braille_image(image_path):
    """
    Preprocess braille image for better OCR results
    Returns: preprocessed image as numpy array
    """
    try:
        # Read image
        img = cv2.imread(image_path)
        
        if img is None:
            return None, "Failed to read image"
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Resize if image is too large (helps with processing speed)
        height, width = gray.shape
        max_dimension = 2000
        if max(height, width) > max_dimension:
            scale = max_dimension / max(height, width)
            new_width = int(width * scale)
            new_height = int(height * scale)
            gray = cv2.resize(gray, (new_width, new_height))
        
        # Apply bilateral filter to reduce noise while keeping edges sharp
        bilateral = cv2.bilateralFilter(gray, 9, 75, 75)
        
        # Apply adaptive thresholding
        # Try both methods and use the one that detects more reasonable contours
        thresh1 = cv2.adaptiveThreshold(
            bilateral, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        thresh2 = cv2.adaptiveThreshold(
            bilateral, 255, cv2.ADAPTIVE_THRESH_MEAN_C, 
            cv2.THRESH_BINARY, 15, 3
        )
        
        # Also try Otsu's thresholding
        _, thresh3 = cv2.threshold(bilateral, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Count contours in each to pick the best one
        contours1, _ = cv2.findContours(cv2.bitwise_not(thresh1), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours2, _ = cv2.findContours(cv2.bitwise_not(thresh2), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours3, _ = cv2.findContours(cv2.bitwise_not(thresh3), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Choose the threshold with reasonable number of contours
        counts = [(len(contours1), thresh1), (len(contours2), thresh2), (len(contours3), thresh3)]
        # Pick the one with moderate number of contours (not too few, not too many)
        counts.sort(key=lambda x: abs(x[0] - 100))  # Target around 100 dots
        thresh = counts[0][1]
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(thresh, None, 10, 7, 21)
        
        # Morphological operations to clean up
        kernel = np.ones((2, 2), np.uint8)
        denoised = cv2.morphologyEx(denoised, cv2.MORPH_CLOSE, kernel)
        
        return denoised, None
    except Exception as e:
        return None, f"Error preprocessing image: {str(e)}"


def detect_braille_dots(image_path):
    """
    Detect braille dots in an image and attempt to recognize braille characters
    This implementation uses contour detection and pattern matching.
    For production use, consider specialized braille OCR libraries or trained ML models.
    
    Returns: (braille_text, regular_text, notes)
    """
    try:
        # Preprocess image
        processed_img, error = preprocess_braille_image(image_path)
        
        if error:
            return "", "", error
        
        notes = []
        notes.append("✓ Image preprocessing completed successfully")
        
        # Detect dots using contour detection
        contours, _ = cv2.findContours(
            cv2.bitwise_not(processed_img), 
            cv2.RETR_EXTERNAL, 
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        # Filter contours by size and shape to get actual dots
        dots = []
        min_area = 3
        max_area = 1000
        
        # First pass: collect all potential dots
        potential_dots = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if min_area < area < max_area:
                # Check circularity (braille dots are roughly circular)
                perimeter = cv2.arcLength(contour, True)
                if perimeter > 0:
                    circularity = 4 * np.pi * area / (perimeter * perimeter)
                    # Only accept reasonably circular shapes
                    if circularity > 0.3:  # Relaxed threshold
                        M = cv2.moments(contour)
                        if M["m00"] != 0:
                            cx = int(M["m10"] / M["m00"])
                            cy = int(M["m01"] / M["m00"])
                            potential_dots.append((cx, cy, area))
        
        # If we found dots, filter by area to remove outliers
        if potential_dots:
            areas = [d[2] for d in potential_dots]
            median_area = sorted(areas)[len(areas) // 2]
            
            # Keep dots within reasonable size range of median
            for dot in potential_dots:
                if median_area * 0.2 < dot[2] < median_area * 5:
                    dots.append(dot)
        
        notes.append(f"✓ Detected {len(dots)} potential braille dots")
        
        if len(dots) == 0:
            notes.append("\n⚠ No braille dots detected in the image.")
            notes.append("Tips:")
            notes.append("  • Ensure the image has good contrast")
            notes.append("  • Use higher resolution (300 DPI+)")
            notes.append("  • Check lighting conditions")
            return "", "No braille dots detected", "\n".join(notes)
        
        # Sort dots by position (top to bottom, left to right)
        dots.sort(key=lambda d: (d[1], d[0]))
        
        # Group dots into braille cells (6 dots in 2x3 pattern)
        cells = group_dots_into_cells(dots)
        notes.append(f"✓ Grouped dots into {len(cells)} potential braille cells")
        
        # Recognize braille characters from cells
        braille_chars = []
        recognized_chars = []
        
        for cell in cells:
            braille_char, text_char = recognize_braille_cell(cell)
            if braille_char:
                braille_chars.append(braille_char)
                recognized_chars.append(text_char)
        
        braille_text = ''.join(braille_chars)
        regular_text = ''.join(recognized_chars)
        
        if braille_text:
            notes.append(f"✓ Recognized {len(braille_chars)} braille characters")
            notes.append("\n📋 Results:")
            notes.append(f"  Braille: {braille_text}")
            notes.append(f"  Text: {regular_text}")
        else:
            notes.append("\n⚠ Could not recognize braille patterns")
            notes.append("This may be due to:")
            notes.append("  • Non-standard braille spacing")
            notes.append("  • Image quality issues")
            notes.append("  • Unusual braille format")
        
        notes.append("\n💡 Note: For production-grade OCR, consider:")
        notes.append("  • Specialized braille OCR APIs")
        notes.append("  • Google Cloud Vision API")
        notes.append("  • Custom trained deep learning models")
        
        return braille_text, regular_text, "\n".join(notes)
        
    except Exception as e:
        return "", "", f"❌ Error processing braille image: {str(e)}"


def group_dots_into_cells(dots, cell_width=None, cell_height=None):
    """
    Group detected dots into braille cells (2 columns x 3 rows)
    Automatically determines cell size based on dot spacing
    Returns list of cells, where each cell contains dot positions
    """
    if not dots or len(dots) < 2:
        return [[dot] for dot in dots] if dots else []
    
    # Auto-detect cell dimensions if not provided
    if cell_width is None or cell_height is None:
        # Calculate average distances between nearby dots
        distances_x = []
        distances_y = []
        
        sorted_x = sorted(dots, key=lambda d: d[0])
        sorted_y = sorted(dots, key=lambda d: d[1])
        
        for i in range(len(sorted_x) - 1):
            dx = sorted_x[i + 1][0] - sorted_x[i][0]
            if 5 < dx < 200:  # Reasonable dot spacing
                distances_x.append(dx)
        
        for i in range(len(sorted_y) - 1):
            dy = sorted_y[i + 1][1] - sorted_y[i][1]
            if 5 < dy < 200:
                distances_y.append(dy)
        
        if distances_x:
            avg_x = sum(distances_x) / len(distances_x)
            cell_width = avg_x * 3  # Approximate cell width
        else:
            cell_width = 60
        
        if distances_y:
            avg_y = sum(distances_y) / len(distances_y)
            cell_height = avg_y * 4  # Approximate cell height
        else:
            cell_height = 100
    
    cells = []
    used_dots = set()
    
    # Sort dots by position (left to right, top to bottom)
    sorted_dots = sorted(enumerate(dots), key=lambda x: (x[1][1] // (cell_height // 2), x[1][0] // (cell_width // 2)))
    
    for idx, dot in sorted_dots:
        if idx in used_dots:
            continue
        
        # Start a new cell with this dot
        cell_dots = [dot]
        used_dots.add(idx)
        x, y, _ = dot
        
        # Find other dots that belong to this cell
        for other_idx, other_dot in enumerate(dots):
            if other_idx in used_dots:
                continue
            
            ox, oy, _ = other_dot
            
            # Check if this dot is within the cell bounds
            if abs(ox - x) <= cell_width and abs(oy - y) <= cell_height:
                cell_dots.append(other_dot)
                used_dots.add(other_idx)
        
        if cell_dots:
            cells.append(cell_dots)
    
    return cells


def recognize_braille_cell(cell_dots):
    """
    Recognize a braille character from a group of dots
    Returns: (braille_unicode, text_character)
    """
    if not cell_dots:
        return ' ', ' '
    
    # Only process cells with reasonable number of dots (1-6 for standard braille)
    if len(cell_dots) > 8:  # Too many dots, likely noise
        return '?', '?'
    
    # Calculate the bounding box of the cell
    xs = [d[0] for d in cell_dots]
    ys = [d[1] for d in cell_dots]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    
    # Determine which dots are present in the 2x3 grid
    # Standard braille cell layout:
    #  1  4
    #  2  5
    #  3  6
    
    width = max_x - min_x if max_x > min_x else 1
    height = max_y - min_y if max_y > min_y else 1
    
    # Create a pattern based on dot positions
    pattern = [False] * 6  # 6 dots in braille cell
    
    # More robust position mapping
    for dot in cell_dots:
        x, y, _ = dot
        # Normalize positions (0.0 to 1.0)
        rel_x = (x - min_x) / width if width > 0 else 0.5
        rel_y = (y - min_y) / height if height > 0 else 0.5
        
        # Determine which position this dot occupies
        # Left column (0) or right column (1)
        col = 0 if rel_x < 0.5 else 1
        
        # Top (0), middle (1), or bottom (2) row
        if rel_y < 0.33:
            row = 0
        elif rel_y < 0.67:
            row = 1
        else:
            row = 2
        
        # Map to braille dot number (1-6, but we use 0-5 for array)
        dot_num = row + (col * 3)
        if 0 <= dot_num < 6:
            pattern[dot_num] = True
    
    # Map pattern to braille character
    # Extended pattern matching for better coverage
    braille_patterns = {
        # Letters a-j (no dots 3 or 6)
        (True, False, False, False, False, False): ('⠁', 'a'),
        (True, True, False, False, False, False): ('⠃', 'b'),
        (True, False, False, True, False, False): ('⠉', 'c'),
        (True, False, False, True, False, True): ('⠙', 'd'),
        (True, False, False, False, False, True): ('⠑', 'e'),
        (True, True, False, True, False, False): ('⠋', 'f'),
        (True, True, False, True, False, True): ('⠛', 'g'),
        (True, True, False, False, False, True): ('⠓', 'h'),
        (False, True, False, True, False, False): ('⠊', 'i'),
        (False, True, False, True, False, True): ('⠚', 'j'),
        
        # Letters k-t (add dot 3)
        (True, False, True, False, False, False): ('⠅', 'k'),
        (True, True, True, False, False, False): ('⠇', 'l'),
        (True, False, True, True, False, False): ('⠍', 'm'),
        (True, False, True, True, False, True): ('⠝', 'n'),
        (True, False, True, False, False, True): ('⠕', 'o'),
        (True, True, True, True, False, False): ('⠏', 'p'),
        (True, True, True, True, False, True): ('⠟', 'q'),
        (True, True, True, False, False, True): ('⠗', 'r'),
        (False, True, True, True, False, False): ('⠎', 's'),
        (False, True, True, True, False, True): ('⠞', 't'),
        
        # Letters u-z (add dots 3 and 6)
        (True, False, True, False, True, False): ('⠥', 'u'),
        (True, True, True, False, True, False): ('⠧', 'v'),
        (False, True, False, True, True, True): ('⠺', 'w'),
        (True, False, True, True, True, False): ('⠭', 'x'),
        (True, False, True, True, True, True): ('⠽', 'y'),
        (True, False, True, False, True, True): ('⠵', 'z'),
        
        # Special characters
        (False, False, False, False, False, False): (' ', ' '),
        (False, False, True, False, True, True): ('⠴', '"'),
        (False, False, False, True, False, False): ('⠈', '\''),
        (False, True, False, False, False, False): ('⠂', ','),
        (False, True, True, False, False, True): ('⠲', '.'),
        (False, True, False, False, True, False): ('⠢', '?'),
        (False, False, True, True, False, False): ('⠌', '/'),
    }
    
    pattern_tuple = tuple(pattern)
    result = braille_patterns.get(pattern_tuple)
    
    if result:
        return result
    
    # If no exact match, return unknown but with the actual pattern detected
    dots_present = sum(pattern)
    if dots_present == 0:
        return ' ', ' '
    
    # Return unknown with some braille char
    return '•', '?'


def translate_braille_image(image_path):
    """
    Main function to translate braille image to text
    Returns: (braille_text, translated_text, processing_notes)
    """
    try:
        # Check if image exists
        if not os.path.exists(image_path):
            return "", "", "Image file not found"
        
        # Detect braille in image
        braille_text, regular_text, notes = detect_braille_dots(image_path)
        
        return braille_text, regular_text, notes
        
    except Exception as e:
        return "", "", f"Error translating braille image: {str(e)}"

