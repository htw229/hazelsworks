from django import forms
from .models import Dialect, ReplacementCategory
# from .britpick import matchoptions, matchoptionsstrings
# from .appsettingstest import DEFAULT_DIALECT
import app.appsettings as SETTINGS
import app.strings as STRINGS



DIALOGUE_OPTION_CHOICES = [
    ('SMART', STRINGS.BRITPICKFORM_DIALOGUE_SMART),
    ('ALLTEXT', STRINGS.BRITPICKFORM_DIALOGUE_ALL_TEXT),
    ('DIALOGUEONLY', STRINGS.BRITPICKFORM_DIALOGUE_DIALOGUE_ONLY),
]

# class BritpickForm(forms.Form):
#     text = forms.CharField(
#         label='',
#         widget=forms.Textarea,
#         max_length=100000,
#     )
#
#     dialect = forms.ChoiceField(
#         label=STRINGS.BRITPICKFORM_DIALECT_LABEL,
#         choices= [(dialect.pk, dialect.name) for dialect in Dialect.objects.all().order_by('name')],
#         # widget=forms.RadioSelect
#     )
#
#     replacement_categories = forms.MultipleChoiceField(
#         label=STRINGS.BRITPICKFORM_REPLACEMENTCATEGORIES_LABEL,
#         choices=[(t.pk, t.name) for t in ReplacementCategory.objects.all().order_by('pk')],
#         widget=forms.CheckboxSelectMultiple
#     )
#
#     dialogue_option = forms.ChoiceField(
#         label=STRINGS.BRITPICKFORM_DIALOGUE_LABEL,
#         choices=DIALOGUE_OPTION_CHOICES,
#         # widget = forms.RadioSelect,
#     )
#
#
#     def __init__(self, *args, **kwargs):
#         super(BritpickForm, self).__init__(*args, **kwargs)
#
#         # search for default dialect by default
#         self.initial['dialect'] = SETTINGS.DEFAULT_DIALECT
#
#         # search for all replacement categories by default
#         self.initial['replacement_categories'] = [t.pk for t in ReplacementCategory.objects.all()]
#
#         # search smart by default
#         self.initial['dialogue_option'] = DIALOGUE_OPTION_CHOICES[0][0]




class BritpickfindwordForm(forms.Form):
    searchword = forms.CharField(label='Search')