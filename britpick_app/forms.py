from django import forms
from django.utils.translation import ugettext as _
import re

from .models import Dialect, SampleText

class BritpickForm(forms.Form):
    text = forms.CharField(
        label='',
        widget=forms.Textarea,
        max_length=100000,
    )

    sample_text = forms.ChoiceField(
        #TODO: only display if superuser
        choices=[(None, '-----'), *[(t.text, t.name) for t in SampleText.displayed.all()]],
        label=_('sample text'),
    )

    dialect = forms.ModelChoiceField(
        queryset=Dialect.displayed.all(),
        label=_('dialect'),
        initial=Dialect.displayed.get(default=True),
    )

    # def get_britpicked_text(self):
    #     return self.fields['text'].value()

    # def clean_text(self):
    #     text = self.cleaned_data.get('text')
    #     substitutions = [('“', '"'), ('”', '"'), ('’',"'"),]
    #     for sub in substitutions:
    #         text = text.replace(sub[0], sub[1])
    #
    #     text = re.sub(r'<.*?>', '', text)
    #
    #     #TODO: if using single quote dialogue replace with double quotes
    #
    #     return text + ' CLEANED'
