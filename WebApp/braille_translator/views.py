from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from .models import Document, BrailleImage
from .utils import (extract_text_from_file, text_to_braille, text_to_braille_liblouis,
                    translate_braille_image as process_braille_image)
from .forms import DocumentUploadForm, BrailleImageUploadForm
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


def braille_image_upload(request):
    """Upload braille image page"""
    images = BrailleImage.objects.all()
    
    if request.method == 'POST':
        form = BrailleImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            braille_image = form.save()
            messages.success(request, f'Image "{braille_image.title}" uploaded successfully!')
            return redirect('translate_braille_image', pk=braille_image.pk)
    else:
        form = BrailleImageUploadForm()
    
    context = {
        'form': form,
        'images': images,
    }
    return render(request, 'braille_translator/image_upload.html', context)


def translate_braille_image(request, pk):
    """Process braille image and extract text"""
    braille_image = get_object_or_404(BrailleImage, pk=pk)
    
    if not braille_image.is_processed:
        # Process the braille image
        image_path = braille_image.image.path
        braille_text, translated_text, notes = process_braille_image(image_path)
        
        # Save results
        braille_image.braille_text = braille_text
        braille_image.translated_text = translated_text
        braille_image.processing_notes = notes
        braille_image.is_processed = True
        braille_image.save()
        
        messages.success(request, 'Braille image processed successfully!')
    
    context = {
        'braille_image': braille_image,
    }
    return render(request, 'braille_translator/image_translate.html', context)


def braille_image_detail(request, pk):
    """View braille image details"""
    braille_image = get_object_or_404(BrailleImage, pk=pk)
    
    context = {
        'braille_image': braille_image,
    }
    return render(request, 'braille_translator/image_translate.html', context)


def delete_braille_image(request, pk):
    """Delete a braille image"""
    braille_image = get_object_or_404(BrailleImage, pk=pk)
    
    if request.method == 'POST':
        # Delete the file from filesystem
        if braille_image.image:
            if os.path.exists(braille_image.image.path):
                os.remove(braille_image.image.path)
        
        braille_image.delete()
        messages.success(request, 'Braille image deleted successfully!')
        return redirect('braille_image_upload')
    
    return render(request, 'braille_translator/delete_confirm.html', {'braille_image': braille_image})

