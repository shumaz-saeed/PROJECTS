from django import forms
from .models import Document

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'file', 'department', 'access_level']
        widgets = {
            'file': forms.FileInput(), # Ensures a file input widget is used
        }
