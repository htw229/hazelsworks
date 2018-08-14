from django import forms
from .models import BritpickDialects
from .britpick import matchoptions, matchoptionsstrings

dialectchoices = [(dialect.name, dialect.name) for dialect in BritpickDialects.objects.all().order_by('name')]

dialoguechoices = [
    (matchoptions['SEARCH_DIALOGUE_IF_SPECIFIED'], matchoptionsstrings['1']),
    (matchoptions['SEARCH_DIALOGUE_ONLY'], matchoptionsstrings['2']),
    (matchoptions['SEARCH_ALL'], matchoptionsstrings['3']),
]

class BritpickForm(forms.Form):
    text = forms.CharField(
        label='Text',
        widget=forms.Textarea,
    )
    dialect = forms.ChoiceField(label='Dialect', choices=dialectchoices)
    dialogue = forms.ChoiceField(label='Text to search', choices=dialoguechoices)

    # def __init__(self, *args, **kwargs):
    #     super(MyForm, self).__init__(*args, **kwargs)
    #     # assign a (computed, I assume) default value to the choice field
    #     self.initial['dialogue'] = matchoptions['SEARCH_DIALOGUE_IF_SPECIFIED']