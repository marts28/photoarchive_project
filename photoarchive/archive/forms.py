from django import forms
from django.contrib.auth import get_user_model

from .models import Document, DocumentPhoto


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'description', 'doc_date']
        widgets = {
            'doc_date': forms.DateInput(attrs={'type': 'date'}),
        }


class PhotoForm(forms.ModelForm):
    class Meta:
        model = DocumentPhoto
        fields = ['image']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'multiple': True}),
        }