from django import forms
from .models import HCDocument

class HCDocumentForm(forms.ModelForm):
    class Meta:
        model = HCDocument
        fields = ["tab", "archivo", "nombre_visible"]
