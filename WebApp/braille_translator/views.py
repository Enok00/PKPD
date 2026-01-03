from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from .models import Document
from .utils import extract_text_from_file, text_to_braille, text_to_braille_liblouis
from .forms import DocumentUploadForm
import os


def home(request):
    """Home page with upload form and list of documents"""
    documents = Document.objects.all()
    
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            
            # Determine document type from file extension
            file_extension = document.get_file_extension()
            document.document_type = file_extension
            document.save()
            
            messages.success(request, f'Document "{document.title}" uploaded successfully!')
            return redirect('translate_document', pk=document.pk)
    else:
        form = DocumentUploadForm()
    
    context = {
        'form': form,
        'documents': documents,
    }
    return render(request, 'braille_translator/home.html', context)


def translate_document(request, pk):
    """Extract text and translate document to Braille"""
    document = get_object_or_404(Document, pk=pk)
    
    if not document.is_translated:
        # Extract text from document
        file_path = document.document.path
        text, error = extract_text_from_file(file_path)
        
        if error:
            messages.error(request, f'Error processing document: {error}')
            return redirect('home')
        
        # Save extracted text
        document.original_text = text
        
        # Translate to Braille
        # Try using liblouis first (Grade 2), fallback to basic translation
        document.braille_text = text_to_braille_liblouis(text, grade=1)
        
        document.is_translated = True
        document.save()
        
        messages.success(request, 'Document translated to Braille successfully!')
    
    context = {
        'document': document,
    }
    return render(request, 'braille_translator/translate.html', context)


def document_detail(request, pk):
    """View document details and Braille translation"""
    document = get_object_or_404(Document, pk=pk)
    
    context = {
        'document': document,
    }
    return render(request, 'braille_translator/detail.html', context)


def delete_document(request, pk):
    """Delete a document"""
    document = get_object_or_404(Document, pk=pk)
    
    if request.method == 'POST':
        # Delete the file from filesystem
        if document.document:
            if os.path.exists(document.document.path):
                os.remove(document.document.path)
        
        document.delete()
        messages.success(request, 'Document deleted successfully!')
        return redirect('home')
    
    return render(request, 'braille_translator/delete_confirm.html', {'document': document})


def download_braille(request, pk):
    """Download Braille translation as text file"""
    document = get_object_or_404(Document, pk=pk)
    
    if not document.is_translated:
        messages.error(request, 'This document has not been translated yet.')
        return redirect('document_detail', pk=pk)
    
    # Create response with Braille text
    response = HttpResponse(document.braille_text, content_type='text/plain; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{document.title}_braille.txt"'
    
    return response
