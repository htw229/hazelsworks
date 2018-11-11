from django.contrib import admin
from django import forms

from britpick_app.models import *


class BaseAdmin(admin.ModelAdmin):
    exclude = ('date_created', 'date_edited',)
    save_on_top = True




class DialectAdmin(BaseAdmin):
    list_display = ('name', 'default', 'description')

admin.site.register(Dialect, DialectAdmin)

class TopicAdmin(BaseAdmin):
    search_fields = ('name',)

admin.site.register(Topic, TopicAdmin)

class ReferenceAdmin(BaseAdmin):
    search_fields = ('name',)

admin.site.register(Reference, ReferenceAdmin)

class ExplanationAdmin(BaseAdmin):
    search_fields = ('name',)

admin.site.register(Explanation, ExplanationAdmin)

class WordAdmin(BaseAdmin):
    search_fields = ('name',)

admin.site.register(Word, WordAdmin)

class WordGroupAdmin(BaseAdmin):
    search_fields = ('name',)

admin.site.register(WordGroup, WordGroupAdmin)

class SearchGroupAdmin(BaseAdmin):
    search_fields = ('name',)

admin.site.register(SearchGroup, SearchGroupAdmin)

class SearchStringAdmin(BaseAdmin):
    pass

admin.site.register(SearchString, SearchStringAdmin)

class SearchStringInline(admin.TabularInline):
    model = SearchString.britpicks.through
    # model = Britpick.search_strings.through
    # model = Britpick.search_strings
    # model = SearchString.britpicks_searched_by.through
    extra = 0
    # fields = ('search_strings_string',)

class BritpickAdmin(BaseAdmin):

    change_form_template = 'admin/custom/britpick.html'

    list_display = ('name', 'dialect', 'category', 'active', 'verified', 'date_edited', 'date_created',)
    list_editable = ('active', 'verified', 'dialect', 'category',)
    list_filter = ('active', 'verified', 'dialect', 'category', 'explanations',)
    # create a list_filter to get problematic conflicts (instead of duplicates page)
    search_fields = ('name',)
    # add custom search https://docs.djangoproject.com/en/2.0/ref/contrib/admin/#django.contrib.admin.ModelAdmin.get_search_results
    date_hierarchy = 'date_edited'
    empty_value_display = '- unnamed -'


    exclude = ('name',)
    autocomplete_fields = ('topics', 'references', 'explanations', 'search_groups', 'exclude_nearby_groups', 'require_nearby_groups', 'word_groups',)
    inlines = (SearchStringInline,)
    filter_horizontal = ('topics', 'references', 'words',)

    fieldsets = (
        (None, {
            'fields': (('dialect', 'category',), ('active', 'verified',), 'search_groups',),
        }),
        ('Advanced search options', {
            'classes': ('collapse',),
            'fields': ('exclude_nearby_strings', 'exclude_nearby_groups', 'require_nearby_strings', 'require_nearby_groups',),
        }),
        (None, {
            'fields': ('words', 'word_groups', 'details', 'explanations', 'topics', 'references',)
        }),
    )

admin.site.register(Britpick, BritpickAdmin)


admin.site.register(Suggestion)
admin.site.register(Category)

admin.site.register(SearchVariables)

admin.site.register(Example)
admin.site.register(Spelling)