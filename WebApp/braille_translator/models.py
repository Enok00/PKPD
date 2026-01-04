from django.db import models
from django.utils import timezone


class Document(models.Model):
    """Model to store uploaded documents for Braille translation"""
    
    DOCUMENT_TYPES = [
        ('txt', 'Text File'),
        ('pdf', 'PDF Document'),
        ('docx', 'Word Document'),
    ]
    
    title = models.CharField(max_length=255)
    document = models.FileField(upload_to='documents/')
    document_type = models.CharField(max_length=10, choices=DOCUMENT_TYPES)
    uploaded_at = models.DateTimeField(default=timezone.now)
    
    # Original text content
    original_text = models.TextField(blank=True)
    
    # Braille translation
    braille_text = models.TextField(blank=True)
    
    # Translation status
    is_translated = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.title} - {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"
    
    def get_file_extension(self):
        """Get the file extension"""
        return self.document.name.split('.')[-1].lower()


class BrailleImage(models.Model):
    """Model to store uploaded braille images for OCR translation"""
    
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='braille_images/')
    uploaded_at = models.DateTimeField(default=timezone.now)
    
    # Extracted braille text (as braille unicode characters)
    braille_text = models.TextField(blank=True)
    
    # Translated regular text
    translated_text = models.TextField(blank=True)
    
    # Translation status
    is_processed = models.BooleanField(default=False)
    
    # Processing notes/errors
    processing_notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.title} - {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"

