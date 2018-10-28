from django.contrib import admin
from django.forms import Textarea, CheckboxSelectMultiple
from django.db import models
from __init__ import *
# from .britpicktopic import parsetopictext, addtopiccitations
import re

# Register your models here.
from .models import Dialect
admin.site.register(Dialect)

from .models import ReplacementExplanation
admin.site.register(ReplacementExplanation)

from .models import Replacement
admin.site.register(Replacement)

from .models import Topic

class TopicAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':75, 'cols': 75})},
        # models.ManyToManyField: {'widget': CheckboxSelectMultiple(attrs={'size': '10'})},
    }

    def get_form(self, request, obj=None, **kwargs):
        form = super(TopicAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['text'].widget.attrs['style'] = 'height: 600px'
        # form.base_fields['citations'].widget.attrs['style'] = 'height: 600px;'
        # form.base_fields['relatedtopics'].widget.attrs['style'] = 'height: 400px;'
        return form

    def save_related(self, request, form, formsets, change):
        # to modify m2m, needs to be after saving everything or it will clear changes
        super().save_related(request, form, formsets, change)

        try:
            topic = Topic.objects.get(pk=form.instance.id)
            citationpattern = r"(?<=[\<\[])(?P<pk>\d+)(?=[\:\]])"

            for match in re.finditer(citationpattern, topic.text):
                pk = match.groupdict()['pk']
                try:
                    reference = Reference.objects.get(pk=pk)
                    if reference not in topic.citations.all():
                        topic.citations.add(reference)
                except ObjectDoesNotExist:
                    continue

        except ObjectDoesNotExist:
            pass


# TODO: add edit link to references for debug users


admin.site.register(Topic, TopicAdmin)

from .models import Reference
admin.site.register(Reference)

from .models import ReplacementCategory
admin.site.register(ReplacementCategory)