from django import forms
from .models import File

class FileUploadForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ['upload']


class RenameFileForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ['name']