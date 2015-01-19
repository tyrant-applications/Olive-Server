from django import forms

class ImageUploadForm(forms.Form):
    """Image upload form."""
    new_picture = forms.ImageField()