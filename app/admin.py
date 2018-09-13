from django.contrib import admin
from django.forms import Textarea, CheckboxSelectMultiple
from django.db import models

# Register your models here.
from .models import BritpickDialects
admin.site.register(BritpickDialects)

from .models import ReplacementExplanation
admin.site.register(ReplacementExplanation)

from .models import BritpickFindReplace
admin.site.register(BritpickFindReplace)

from .models import ReplacementTopic

class TopicAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':35, 'cols': 75})},
        models.ManyToManyField: {'widget': CheckboxSelectMultiple(attrs={'size': '10'})},
    }

    # def get_form(self, request, obj=None, **kwargs):
    #     form = super(TopicAdmin, self).get_form(request, obj, **kwargs)
    #     form.base_fields['citations'].widget.attrs['style'] = 'height: 600px;'
    #     form.base_fields['relatedtopics'].widget.attrs['style'] = 'height: 400px;'
    #     return form

admin.site.register(ReplacementTopic, TopicAdmin)

from .models import Citation
admin.site.register(Citation)

from .models import ReplacementType
admin.site.register(ReplacementType)