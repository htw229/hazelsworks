from django import forms
from .models import Dialect, ReplacementCategory
from .britpick import matchoptions, matchoptionsstrings
# from .appsettingstest import DEFAULT_DIALECT
import app.appsettings as SETTINGS
import app.strings as STRINGS


# dialoguechoices = [
#     (matchoptions['SEARCH_DIALOGUE_IF_SPECIFIED'], matchoptionsstrings['1']),
#     (matchoptions['SEARCH_DIALOGUE_ONLY'], matchoptionsstrings['2']),
#     (matchoptions['SEARCH_ALL'], matchoptionsstrings['3']),
# ]
#
# searchreplacementchoices = [
#     ('SEARCH_MANDATORY_REPLACEMENTS', 'mandatory'),
#     ('SEARCH_SUGGESTED_REPLACEMENTS', 'suggested'),
#     ('SEARCH_INFORMAL_REPLACEMENTS', 'informal'),
#     ('SEARCH_SLANG_REPLACEMENTS', 'slang/profanity'),
# ]

DIALOGUE_OPTION_CHOICES = [
    ('SMART', STRINGS.BRITPICKFORM_DIALOGUE_SMART),
    ('ALLTEXT', STRINGS.BRITPICKFORM_DIALOGUE_ALL_TEXT),
    ('DIALOGUEONLY', STRINGS.BRITPICKFORM_DIALOGUE_DIALOGUE_ONLY),
]

class BritpickForm(forms.Form):
    text = forms.CharField(
        label=STRINGS.BRITPICKFORM_TEXT_LABEL,
        widget=forms.Textarea,
    )

    # TODO: add search type (all, dialogue only) OR add option for each category to search dialogue or all

    dialect = forms.ChoiceField(
        label=STRINGS.BRITPICKFORM_DIALECT_LABEL,
        choices= [(dialect.pk, dialect.name) for dialect in Dialect.objects.all().order_by('name')],
        widget=forms.RadioSelect
    )

    replacement_categories = forms.MultipleChoiceField(
        label=STRINGS.BRITPICKFORM_REPLACEMENTCATEGORIES_LABEL,
        choices=[(t.pk, t.name) for t in ReplacementCategory.objects.all().order_by('pk')],
        widget=forms.CheckboxSelectMultiple
    )

    dialogue_option = forms.ChoiceField(
        label=STRINGS.BRITPICKFORM_DIALOGUE_LABEL,
        choices=DIALOGUE_OPTION_CHOICES,
        widget = forms.RadioSelect,
    )




    # character_dialogue_name = forms.CharField(
    #     label=STRINGS.BRITPICKFORM_CHARACTERDIALOGUE_LABEL,
    #     max_length=200,
    #     required=False
    # )


    def __init__(self, *args, **kwargs):
        super(BritpickForm, self).__init__(*args, **kwargs)

        # search for default dialect by default
        self.initial['dialect'] = SETTINGS.DEFAULT_DIALECT

        # search for all replacement categories by default
        self.initial['replacement_categories'] = [t.pk for t in ReplacementCategory.objects.all()]

        # search smart by default
        self.initial['dialogue_option'] = DIALOGUE_OPTION_CHOICES[0][0]




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