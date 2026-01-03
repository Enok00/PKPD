from django import forms
from .models import Document


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
            
            # Check file size (limit to 10MB)
            if document.size > 10 * 1024 * 1024:
                raise forms.ValidationError('File size must be under 10MB')
        
        return document
