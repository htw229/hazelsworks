from django import forms
from django.utils.translation import ugettext as _

from .models import Dialect

class BritpickForm(forms.Form):
    text = forms.CharField(
        label='',
        widget=forms.Textarea,
        max_length=100000,
    )

    dialect = forms.ModelChoiceField(
        queryset=Dialect.displayed.all(),
        label=_('dialect'),
        initial=Dialect.displayed.get(default=True),
    )

    # def get_britpicked_text(self):
    #     return self.fields['text'].value()