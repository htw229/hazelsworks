from django import forms
from .models import BritpickDialects

dialectchoices = [(dialect.name, dialect.name) for dialect in BritpickDialects.objects.all().order_by('name')]

class BritpickForm(forms.Form):
    original_text = forms.CharField(label='Text', max_length=10000, widget=forms.Textarea)
    dialect = forms.ChoiceField(label='Dialect', choices=dialectchoices)