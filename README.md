# PKPD – Braille Translator Web App

A Django-based web application for translating text documents and images to/from Braille.

## Required Libraries

Install all required Python libraries using the provided `requirements.txt`:

```bash
pip install -r WebApp/requirements.txt
```

### Core dependencies

| Library | Version | Purpose |
|---|---|---|
| `Django` | >=5.2.0 | Web framework |
| `PyPDF2` | >=3.0.0 | Extract text from PDF files |
| `python-docx` | >=1.0.0 | Extract text from DOCX/DOC files |
| `Pillow` | >=10.0.0 | Image processing |
| `opencv-python` | >=4.8.0 | Braille dot detection in images |
| `numpy` | >=1.24.0 | Numerical operations for image processing |

### Optional dependency

| Library | Purpose |
|---|---|
| `python-liblouis` | More accurate Grade 1/2 Braille translation via liblouis |

To use `python-liblouis`, first install the system library, then the Python package:

```bash
# On Debian/Ubuntu
sudo apt-get install liblouis-dev

# On macOS (Homebrew)
brew install liblouis

pip install python-liblouis
```

## Setup & Running

```bash
# 1. Clone the repository
git clone https://github.com/Enok00/PKPD.git
cd PKPD/WebApp

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Apply database migrations
python manage.py migrate

# 5. Start the development server
python manage.py runserver
```

Then open http://127.0.0.1:8000/ in your browser.
