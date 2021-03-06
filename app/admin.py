from django.contrib import admin
from django.forms import Textarea, CheckboxSelectMultiple
from django.db import models
from __init__ import *
# from .britpicktopic import parsetopictext, addtopicreferences
import re

# Register your models here.
from .models import Dialect
admin.site.register(Dialect)

from .models import ReplacementExplanation
admin.site.register(ReplacementExplanation)

from .models import Replacement


from .models import Topic
from .models import Reference
from .models import ReplacementCategory

# class ReferencesInline(admin.StackedInline):
#     model = Reference
#     filter_horizontal = ('name',)

class ReferenceAdmin(admin.ModelAdmin):
    list_display = ('name', 'sitename', 'pagename', 'mainreference', 'url')
    list_filter = ('mainreference', 'sitename')
    # ordering = ('name',)

    save_on_top = True
    # list_display =
    # filter_horizontal = ('topics',)

class TopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'maintopic', 'active')
    list_filter = ('active',)
    ordering = ('name',)

    save_on_top = True
    # list_display =
    filter_horizontal = ('references', 'relatedtopics', 'minorreferences')

    # inlines = [ReferencesInline]

    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':75, 'cols': 75})},
        # models.ManyToManyField: {'widget': CheckboxSelectMultiple(attrs={'size': '10'})},
    }


    def get_form(self, request, obj=None, **kwargs):
        form = super(TopicAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['text'].widget.attrs['style'] = 'height: 600px'
        # form.base_fields['references'].widget.attrs['style'] = 'height: 600px;'
        # form.base_fields['relatedtopics'].widget.attrs['style'] = 'height: 400px;'
        return form

    def save_related(self, request, form, formsets, change):
        # to modify m2m, needs to be after saving everything or it will clear changes
        super().save_related(request, form, formsets, change)

        try:
            topic = Topic.objects.get(pk=form.instance.id)

            referencepattern = r"(?<=[\<])(?P<pk>\d+)(?:\:)"
            for match in re.finditer(referencepattern, topic.text):
                pk = match.groupdict()['pk']
                try:
                    reference = Reference.objects.get(pk=pk)
                    if reference not in topic.references.all():
                        topic.references.add(reference)
                except ObjectDoesNotExist:
                    continue

            # minor references
            referencepattern = r"(?<=\[)(?P<pk>\d+)(?:\])"
            for match in re.finditer(referencepattern, topic.text):
                pk = match.groupdict()['pk']
                try:
                    reference = Reference.objects.get(pk=pk)
                    if reference not in topic.references.all() and reference not in topic.minorreferences.all():
                        topic.minorreferences.add(reference)
                except ObjectDoesNotExist:
                    continue

        except ObjectDoesNotExist:
            pass




class ReplacementAdmin(admin.ModelAdmin):
    list_display = ('title', 'dialect', 'active')
    list_filter = ('active', 'category', 'verified', 'dialect')
    # ordering = ('name',)

    save_on_top = True
    # list_display =
    filter_horizontal = ('topics', 'references',)














# TODO: add edit link to references for debug users

admin.site.register(Topic, TopicAdmin)
admin.site.register(Reference, ReferenceAdmin)
admin.site.register(ReplacementCategory)
admin.site.register(Replacement, ReplacementAdmin)