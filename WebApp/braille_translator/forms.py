from django import forms
from .models import Document, BrailleImage


class DocumentUploadForm(forms.ModelForm):
    """Form for uploading documents"""
    
    class Meta:
        model = Document
        fields = ['title', 'document']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter document title'
            }),
            'document': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.txt,.pdf,.docx'
            })
        }
    
    def clean_document(self):
        """Validate uploaded document"""
        document = self.cleaned_data.get('document')
        
        if document:
            # Check file extension
            file_extension = document.name.split('.')[-1].lower()
            allowed_extensions = ['txt', 'pdf', 'docx']
            
            if file_extension not in allowed_extensions:
                raise forms.ValidationError(
                    f'Unsupported file type. Please upload: {", ".join(allowed_extensions)}'
                )  
        return document


class BrailleImageUploadForm(forms.ModelForm):
    """Form for uploading braille images"""
    
    class Meta:
        model = BrailleImage
        fields = ['title', 'image']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter image title'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
    
    def clean_image(self):
        """Validate uploaded image"""
        image = self.cleaned_data.get('image')
        
        if image:
            # Check file extension
            file_extension = image.name.split('.')[-1].lower()
            allowed_extensions = ['jpg', 'jpeg', 'png', 'bmp', 'tiff', 'tif']
            
            if file_extension not in allowed_extensions:
                raise forms.ValidationError(
                    f'Unsupported image type. Please upload: {", ".join(allowed_extensions)}'
                )
        return image

