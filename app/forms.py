from django import forms
from .models import BritpickDialects
from .britpick import matchoptions, matchoptionsstrings
# from .appsettingstest import DEFAULT_DIALECT
import app.appsettings as SETTINGS
import app.strings as STRINGS

dialectchoices = [(dialect.name, dialect.name) for dialect in BritpickDialects.objects.all().order_by('name')]

dialoguechoices = [
    (matchoptions['SEARCH_DIALOGUE_IF_SPECIFIED'], matchoptionsstrings['1']),
    (matchoptions['SEARCH_DIALOGUE_ONLY'], matchoptionsstrings['2']),
    (matchoptions['SEARCH_ALL'], matchoptionsstrings['3']),
]

searchreplacementchoices = [
    ('SEARCH_MANDATORY_REPLACEMENTS', 'mandatory'),
    ('SEARCH_SUGGESTED_REPLACEMENTS', 'suggested'),
    ('SEARCH_INFORMAL_REPLACEMENTS', 'informal'),
    ('SEARCH_SLANG_REPLACEMENTS', 'slang/profanity'),
]

class BritpickForm(forms.Form):
    text = forms.CharField(
        label=STRINGS.BRITPICKFORM_TEXT_LABEL,
        widget=forms.Textarea,
    )

    dialect = forms.ChoiceField(
        label=STRINGS.BRITPICKFORM_DIALECT_LABEL,
        choices=dialectchoices,
        widget=forms.RadioSelect
    )

    replacement_categories = forms.MultipleChoiceField(label=STRINGS.BRITPICKFORM_REPLACEMENTCATEGORIES_LABEL, choices=STRINGS.BRITPICKFORM_REPLACEMENTCATEGORIES_CHOICES, widget=forms.CheckboxSelectMultiple)

    informal_and_slang_in_dialogue_only = forms.BooleanField(label=STRINGS.BRITPICKFORM_SMARTDIALOGUE_LABEL, required=False)

    character_dialogue_name = forms.CharField(label=STRINGS.BRITPICKFORM_CHARACTERDIALOGUE_LABEL, max_length=200, required=False)

    dialogue = forms.ChoiceField(label='Text to search', choices=dialoguechoices)

    def __init__(self, *args, **kwargs):
        super(BritpickForm, self).__init__(*args, **kwargs)

        # search for default dialect by default
        self.initial['dialect'] = SETTINGS.DEFAULT_DIALECT

        # search for all replacement categories by default
        self.initial['replacement_categories'] = [s[0] for s in searchreplacementchoices]





    # exclude dialogue
    # include_dialogue = forms.BooleanField(label='Include informal words')
    # include_slang = forms.BooleanField(label='Include slang words')
    #
    # mandatory_only = forms.BooleanField(label='Mandatory replacements only')

    # exclude slang

    # def __init__(self, *args, **kwargs):
    #     super(MyForm, self).__init__(*args, **kwargs)
    #     # assign a (computed, I assume) default value to the choice field
    #     self.initial['dialogue'] = matchoptions['SEARCH_DIALOGUE_IF_SPECIFIED']


class BritpickfindwordForm(forms.Form):
    searchword = forms.CharField(label='Search')