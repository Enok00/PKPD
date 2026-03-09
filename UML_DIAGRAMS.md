# UML Diagrams - Braille Translator Application

## 1. Class Diagram

```mermaid
classDiagram
    class Document {
        +int id
        +CharField title
        +FileField document
        +CharField document_type
        +DateTimeField uploaded_at
        +TextField original_text
        +TextField braille_text
        +BooleanField is_translated
        +get_file_extension() str
        +__str__() str
    }

    class BrailleImage {
        +int id
        +CharField title
        +ImageField image
        +DateTimeField uploaded_at
        +TextField braille_text
        +TextField translated_text
        +BooleanField is_processed
        +TextField processing_notes
        +__str__() str
    }

    class DocumentUploadForm {
        +ModelForm
        +fields: title, document
        +clean_document() File
    }

    class BrailleImageUploadForm {
        +ModelForm
        +fields: title, image
        +clean_image() ImageFile
    }

    class Views {
        +home(request) HttpResponse
        +translate_document(request, pk) HttpResponse
        +document_detail(request, pk) HttpResponse
        +delete_document(request, pk) HttpResponse
        +download_braille(request, pk) HttpResponse
        +braille_image_upload(request) HttpResponse
        +translate_braille_image(request, pk) HttpResponse
        +braille_image_detail(request, pk) HttpResponse
        +delete_braille_image(request, pk) HttpResponse
    }

    class Utils {
        +extract_text_from_txt(file_path) str
        +extract_text_from_pdf(file_path) str
        +extract_text_from_docx(file_path) str
        +extract_text_from_file(file_path) tuple
        +text_to_braille(text) str
        +text_to_braille_liblouis(text, grade) str
        +braille_to_text(braille_string) str
        +preprocess_braille_image(image_path) tuple
        +detect_braille_dots(image_path) tuple
        +group_dots_into_cells(dots) list
        +recognize_braille_cell(cell_dots) tuple
        +translate_braille_image(image_path) tuple
    }

    DocumentUploadForm ..> Document : validates
    BrailleImageUploadForm ..> BrailleImage : validates
    Views ..> Document : manages
    Views ..> BrailleImage : manages
    Views ..> DocumentUploadForm : uses
    Views ..> BrailleImageUploadForm : uses
    Views ..> Utils : calls
```

## 2. Use Case Diagram

```mermaid
graph TB
    User((User))
    
    User -->|uploads| UC1[Upload Text Document]
    User -->|uploads| UC2[Upload Braille Image]
    User -->|views| UC3[View Document Details]
    User -->|downloads| UC4[Download Braille Text]
    User -->|deletes| UC5[Delete Document]
    User -->|views| UC6[View Image Results]
    User -->|deletes| UC7[Delete Image]
    
    UC1 -->|triggers| UC8[Extract Text]
    UC1 -->|triggers| UC9[Translate to Braille]
    UC2 -->|triggers| UC10[Process Image OCR]
    UC2 -->|triggers| UC11[Detect Braille Dots]
    UC2 -->|triggers| UC12[Recognize Patterns]
    
    style User fill:#e1f5ff
    style UC1 fill:#ffe1e1
    style UC2 fill:#ffe1e1
    style UC8 fill:#fff4e1
    style UC9 fill:#fff4e1
    style UC10 fill:#fff4e1
    style UC11 fill:#fff4e1
    style UC12 fill:#fff4e1
```

## 3. Sequence Diagram - Document Upload & Translation

```mermaid
sequenceDiagram
    actor User
    participant Browser
    participant View as Django Views
    participant Form as DocumentUploadForm
    participant Model as Document Model
    participant Utils as Utils Module
    
    User->>Browser: Upload document (TXT/PDF/DOCX)
    Browser->>View: POST /
    View->>Form: validate(request.POST, request.FILES)
    Form->>Form: clean_document()
    alt Invalid file
        Form-->>View: ValidationError
        View-->>Browser: Error message
        Browser-->>User: Display error
    else Valid file
        Form->>Model: save(commit=False)
        Model->>Model: get_file_extension()
        Model->>Model: save()
        View->>Browser: redirect to translate_document
        Browser->>View: GET /translate/{pk}/
        View->>Utils: extract_text_from_file(path)
        Utils-->>View: (text, error)
        alt Extraction error
            View-->>Browser: Error message
        else Success
            View->>Model: Update original_text
            View->>Utils: text_to_braille_liblouis(text)
            Utils-->>View: braille_text
            View->>Model: Update braille_text, is_translated=True
            View->>Model: save()
            View->>Browser: Render translate.html
            Browser->>User: Display results
        end
    end
```

## 4. Sequence Diagram - Braille Image OCR

```mermaid
sequenceDiagram
    actor User
    participant Browser
    participant View as Django Views
    participant Form as BrailleImageUploadForm
    participant Model as BrailleImage Model
    participant Utils as Utils Module
    participant CV as OpenCV/Image Processing
    
    User->>Browser: Upload braille image
    Browser->>View: POST /braille-image/
    View->>Form: validate(request.POST, request.FILES)
    Form->>Form: clean_image()
    alt Invalid image
        Form-->>View: ValidationError
        View-->>Browser: Error message
    else Valid image
        Form->>Model: save()
        View->>Browser: redirect to translate_braille_image
        Browser->>View: GET /braille-image/{pk}/translate/
        View->>Utils: translate_braille_image(image_path)
        Utils->>Utils: preprocess_braille_image()
        Utils->>CV: Read image
        CV->>CV: Convert to grayscale
        CV->>CV: Apply bilateral filter
        CV->>CV: Adaptive thresholding
        CV->>CV: Denoise
        CV-->>Utils: Preprocessed image
        Utils->>Utils: detect_braille_dots()
        Utils->>CV: findContours()
        CV-->>Utils: Detected contours
        Utils->>Utils: Filter dots by circularity & size
        Utils->>Utils: group_dots_into_cells()
        Utils->>Utils: Calculate cell dimensions
        Utils->>Utils: Group by spatial proximity
        loop For each cell
            Utils->>Utils: recognize_braille_cell()
            Utils->>Utils: Map dots to 2x3 pattern
            Utils->>Utils: Pattern matching
        end
        Utils-->>View: (braille_text, translated_text, notes)
        View->>Model: Update all fields, is_processed=True
        View->>Model: save()
        View->>Browser: Render image_translate.html
        Browser->>User: Display results & diagnostics
    end
```

## 5. Component Diagram

```mermaid
graph TB
    subgraph "Presentation Layer"
        Templates[HTML Templates<br/>Bootstrap UI]
    end
    
    subgraph "Application Layer"
        Views[Django Views<br/>Request Handlers]
        Forms[Django Forms<br/>Validation]
        URLs[URL Router]
    end
    
    subgraph "Business Logic Layer"
        Utils[Utils Module]
        TextExtract[Text Extraction<br/>TXT/PDF/DOCX]
        BrailleTranslate[Braille Translation<br/>Unicode Mapping]
        ImageOCR[Image OCR<br/>Computer Vision]
    end
    
    subgraph "Data Layer"
        Models[Django Models<br/>ORM]
        DB[(SQLite Database)]
        FileStorage[File Storage<br/>media/]
    end
    
    subgraph "External Libraries"
        PyPDF2[PyPDF2]
        Docx[python-docx]
        OpenCV[opencv-python]
        Pillow[Pillow]
        LibLouis[liblouis<br/>optional]
    end
    
    Templates <--> Views
    Views <--> Forms
    URLs --> Views
    Views <--> Utils
    Views <--> Models
    Forms <--> Models
    
    Utils --> TextExtract
    Utils --> BrailleTranslate
    Utils --> ImageOCR
    
    Models <--> DB
    Models <--> FileStorage
    
    TextExtract --> PyPDF2
    TextExtract --> Docx
    BrailleTranslate -.-> LibLouis
    ImageOCR --> OpenCV
    ImageOCR --> Pillow
    
    style Templates fill:#e3f2fd
    style Views fill:#fff3e0
    style Utils fill:#f3e5f5
    style Models fill:#e8f5e9
    style DB fill:#fce4ec
```

## 6. Activity Diagram - Image Processing Pipeline

```mermaid
flowchart TD
    Start([Upload Braille Image]) --> Validate{Validate File}
    Validate -->|Invalid| Error1[Show Error Message]
    Error1 --> End1([End])
    
    Validate -->|Valid| Save[Save to Database]
    Save --> ReadImage[Read Image File]
    ReadImage --> Grayscale[Convert to Grayscale]
    Grayscale --> Resize{Image > 2000px?}
    Resize -->|Yes| ResizeImg[Resize to 2000px max]
    Resize -->|No| Filter
    ResizeImg --> Filter[Apply Bilateral Filter]
    
    Filter --> Threshold[Adaptive Thresholding<br/>3 Methods]
    Threshold --> Compare[Compare Contour Counts]
    Compare --> BestThresh[Select Best Threshold]
    BestThresh --> Denoise[Apply Denoising]
    
    Denoise --> Morphology[Morphological Operations]
    Morphology --> DetectContours[Detect Contours]
    DetectContours --> FilterDots{Filter by<br/>Circularity & Size}
    
    FilterDots -->|No valid dots| NoDots[Return Error:<br/>No dots detected]
    NoDots --> End2([End])
    
    FilterDots -->|Valid dots found| SortDots[Sort Dots by Position]
    SortDots --> CalcSpacing[Calculate Cell Spacing]
    CalcSpacing --> GroupCells[Group into 2x3 Cells]
    
    GroupCells --> LoopStart{For Each Cell}
    LoopStart -->|More cells| MapPattern[Map Dots to Pattern]
    MapPattern --> MatchChar[Pattern Matching]
    MatchChar --> LoopStart
    
    LoopStart -->|Done| BuildResult[Build Result Strings]
    BuildResult --> SaveResult[Save to Database]
    SaveResult --> DisplayResult[Display Results & Notes]
    DisplayResult --> End3([End])
    
    style Start fill:#4caf50,color:#fff
    style End1 fill:#f44336,color:#fff
    style End2 fill:#ff9800,color:#fff
    style End3 fill:#4caf50,color:#fff
    style Error1 fill:#ffcdd2
    style NoDots fill:#ffe0b2
```

## 7. State Diagram - Document Processing States

```mermaid
stateDiagram-v2
    [*] --> Uploaded: User uploads document
    
    Uploaded --> Extracting: Start text extraction
    Extracting --> ExtractionError: Extraction fails
    Extracting --> Translating: Text extracted successfully
    
    ExtractionError --> [*]: User notified
    
    Translating --> TranslationError: Translation fails
    Translating --> Translated: Braille generated
    
    TranslationError --> [*]: User notified
    
    Translated --> Viewing: User views results
    Translated --> Downloading: User downloads
    Translated --> Deleting: User deletes
    
    Viewing --> Downloading: User requests download
    Viewing --> Deleting: User requests delete
    Viewing --> Viewing: User refreshes
    
    Downloading --> Viewing: Return to view
    Deleting --> [*]: Document removed
```

## 8. Deployment Diagram

```mermaid
graph TB
    subgraph "Client Side"
        Browser[Web Browser<br/>HTML/CSS/Bootstrap]
    end
    
    subgraph "Web Server - Development"
        Django[Django Development Server<br/>Port 8000]
        WSGI[WSGI Application]
    end
    
    subgraph "Application Components"
        Views[Views Layer]
        Models[Models Layer]
        Utils[Utils Layer]
    end
    
    subgraph "Data Storage"
        SQLite[(SQLite Database<br/>db.sqlite3)]
        Media[Media Files<br/>documents/ & braille_images/]
    end
    
    subgraph "Python Environment"
        Venv[Virtual Environment<br/>env/]
        Packages[Dependencies<br/>Django, OpenCV, etc.]
    end
    
    Browser <-->|HTTP/HTTPS| Django
    Django --> WSGI
    WSGI --> Views
    Views --> Models
    Views --> Utils
    Models --> SQLite
    Models --> Media
    Django -.-> Venv
    Venv --> Packages
    
    style Browser fill:#e1f5fe
    style Django fill:#fff9c4
    style SQLite fill:#f8bbd0
    style Media fill:#c8e6c9
    style Venv fill:#ede7f6
```

## Diagram Descriptions

### Class Diagram
Shows the main models (`Document`, `BrailleImage`), forms (`DocumentUploadForm`, `BrailleImageUploadForm`), and their relationships with Views and Utils modules.

### Use Case Diagram
Illustrates all user interactions with the system, from uploading documents to viewing results and managing data.

### Sequence Diagrams
- **Document Upload**: Shows the complete flow from file upload through validation, text extraction, and Braille translation
- **Image OCR**: Details the complex image processing pipeline including preprocessing, dot detection, and pattern recognition

### Component Diagram
Displays the layered architecture: Presentation → Application → Business Logic → Data Layer, with external library dependencies.

### Activity Diagram
Visualizes the step-by-step image processing workflow with decision points and error handling.

### State Diagram
Represents the lifecycle of a document from upload through various processing states to final deletion.

### Deployment Diagram
Shows the runtime architecture with Django development server, database, file storage, and virtual environment setup.

---

## Notes
- These diagrams use Mermaid syntax and can be rendered in GitHub, VS Code (with Mermaid extensions), or any Mermaid-compatible viewer
- For production deployment, the deployment diagram would include NGINX/Apache, Gunicorn/uWSGI, and PostgreSQL instead of development components
