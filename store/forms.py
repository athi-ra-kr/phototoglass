from django import forms
from .models import Lead

class QuoteForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ["name", "company", "email", "segment", "quantity", "message"]

class ContactForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ["name", "email", "message"]
