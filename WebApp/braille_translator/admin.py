from django.contrib import admin
from .models import Document, BrailleImage


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'document_type', 'uploaded_at', 'is_translated']
    list_filter = ['document_type', 'is_translated', 'uploaded_at']
    search_fields = ['title', 'original_text']
    readonly_fields = ['uploaded_at']
    
    fieldsets = (
        ('Document Information', {
            'fields': ('title', 'document', 'document_type', 'uploaded_at')
        }),
        ('Translation', {
            'fields': ('original_text', 'braille_text', 'is_translated')
        }),
    )


@admin.register(BrailleImage)
class BrailleImageAdmin(admin.ModelAdmin):
    list_display = ['title', 'uploaded_at', 'is_processed']
    list_filter = ['is_processed', 'uploaded_at']
    search_fields = ['title', 'translated_text']
    readonly_fields = ['uploaded_at']
    
    fieldsets = (
        ('Image Information', {
            'fields': ('title', 'image', 'uploaded_at')
        }),
        ('OCR Results', {
            'fields': ('braille_text', 'translated_text', 'is_processed', 'processing_notes')
        }),
    )

