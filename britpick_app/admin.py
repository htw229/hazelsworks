from django.contrib import admin
from django import forms
from django.utils.html import mark_safe
#
# import nested_admin
#
from britpick_app.models import *


# class BaseForm(forms.ModelForm):
#     class Meta:
#         widgets = {
#             '_description': forms.CharField,
#         }

class BaseAdmin(admin.ModelAdmin):
    list_display = ('name_verbose', '_active', '_hidden', '_verified', 'date_edited',)
    list_editable = ('_active', '_hidden', '_verified',)
    search_fields = ('_name', '_display_name', '_description', '_display_description',)
    date_hierarchy = 'date_edited'

    save_on_top = True
    readonly_fields = ['date_edited',]
    fieldsets = [
        (None, {
            'fields': ('date_edited', ('_active', '_verified', '_hidden',), ('_name', '_display_name',), ('_description', '_display_description',)),
        }),
    ]

    textinputoverrides = ['_description', '_display_description',]
    # hidelabels = []

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super(BaseAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name in self.textinputoverrides:
            formfield.widget = forms.TextInput(attrs={'class':'vTextField',})
        # if db_field.name in self.hidelabels:
        #     formfield.widget.attrs['class'] = 'hidden-label'
        return formfield


    # def get_form(self, request, obj=None, **kwargs):
    #     form = super(BaseAdmin, self).get_form(request, obj, **kwargs)
    #     form.base_fields['_description'].widget.attrs['style'] = 'height: 100px'

    # class Media:
    #     css = {
    #         'all': ('admin/admin.css',),
    #     }




admin.site.register(Dialect)
admin.site.register(BritpickType)

class CategoryAdmin(BaseAdmin):
    pass

admin.site.register(BritpickCategory, CategoryAdmin)

class ReferenceAdmin(BaseAdmin):
    pass

admin.site.register(Reference, ReferenceAdmin)

class QuoteAdmin(BaseAdmin):
    pass

admin.site.register(Quote, QuoteAdmin)

class TopicAdmin(BaseAdmin):
    fieldsets = [f for f in BaseAdmin.fieldsets]
    # fieldsets = basefieldsets.append((None, {
    #         'fields': ('date_edited', ('_active', '_verified', '_hidden',), ('_name', '_display_name',), ('_description', '_display_description',)),
    #     }),)
    pass

admin.site.register(Topic, TopicAdmin)


class BritpickSearchStringInline(admin.TabularInline):
    model = SearchString
    extra = 0
    fields = ('string',)
    insert_before = 'search_groups'


class BritpickAdmin(BaseAdmin):
    # form = BaseForm

    inlines = [BritpickSearchStringInline,]
    autocomplete_fields = ('categories','topics', 'words', 'word_groups', 'references',)
    filter_horizontal = ('search_groups', 'exclude_search_groups', 'require_search_groups',)

    readonly_fields = [f for f in BaseAdmin.readonly_fields]
    readonly_fields.extend(['words_changelinks','search_changelinks','exclude_search_groups_changelinks','require_search_groups_changelinks','word_groups_changelinks','topics_changelinks', 'references_changelinks',])

    textinputoverrides = ['_description', ]
    # hidelabels = ['topics_changelinks',]

    fieldsets = [
        (None, {
            'fields': ('date_edited', ('_name','_description',), ('_active', '_verified', '_hidden',), 'type', 'categories',),
        }),
        (None, {
            'fields': ('search_changelinks',),
        }),
        ('edit search', {
            'classes': ('collapse',),
            'fields': ('search_groups', 'exclude_search_groups', 'require_search_groups',),
        }),

        (None, {
            'fields': (('words', 'words_changelinks', 'word_groups', 'word_groups_changelinks'),),
        }),
        # ('add/remove words', {
        #     'classes': ('collapse',),
        #     'fields': ('words', 'word_groups',),
        # }),
        (None, {
            'fields': (('topics','topics_changelinks','always_show_topic_names',),),
        }),
        # ('add/remove topics', {
        #     'classes': ('collapse',),
        #     'fields': ('topics',),
        # }),
        (None, {
            'fields': (('references','references_changelinks'), '_display_description',),
        }),
    ]

    def words_changelinks(self, obj):
        return getchangelinks(obj.words.all())
    words_changelinks.short_description = 'words'

    def word_groups_changelinks(self, obj):
        return getchangelinks(obj.word_groups.all())
    word_groups_changelinks.short_description = 'word groups'

    def topics_changelinks(self, obj):
        return getchangelinks(obj.topics.all())
    topics_changelinks.short_description = 'links'

    def references_changelinks(self, obj):
        return getchangelinks(obj.references.all())
    references_changelinks.short_description = 'links'


    def search_changelinks(self, obj):
        # s = '<div>%s</div>' % getchangelinks(obj.search_groups.all())
        # s += '<div>exclude if nearby:%s</div>' % getchangelinks(obj.exclude_search_groups.all())
        # s += '<div>require nearby:%s</div>' % getchangelinks(obj.require_search_groups.all())
        s = getchangelinks(obj.search_strings.all())
        s += getchangelinks(obj.search_groups.all())
        s += getchangelinks(obj.exclude_search_groups.all(), label='exclude:')
        s += getchangelinks(obj.require_search_groups.all(), label='require:')

        return mark_safe(s)

    search_changelinks.short_description = 'search'

    # def exclude_search_groups_changelinks(self, obj):
    #     return getchangelinks(obj.exclude_search_groups.all())
    # exclude_search_groups_changelinks.short_description = 'exclude groups'
    #
    # def require_search_groups_changelinks(self, obj):
    #     return getchangelinks(obj.require_search_groups.all())
    # require_search_groups_changelinks.short_description = 'require groups'

admin.site.register(Britpick, BritpickAdmin)

class SearchStringAdmin(BaseAdmin):
    pass

admin.site.register(SearchString, SearchStringAdmin)


class SearchGroupAdmin(BaseAdmin):
    pass

admin.site.register(SearchGroup, SearchGroupAdmin)

admin.site.register(SearchVariables)


class WordAdmin(BaseAdmin):
    pass

admin.site.register(Word, WordAdmin)

class WordGroupAdmin(BaseAdmin):
    pass

admin.site.register(WordGroup, WordGroupAdmin)

def getchangelinks(objs, label = ''):
    links = []
    for o in objs:
        links.append('<div>%s <a href="%s" class="related-widget-wrapper-link add-related">%s</a></div>' % (label,
        reverse("admin:britpick_app_%s_change" % type(o).__name__.lower(), args=(o.id,)), o.name))
    html = ' '.join(links)
    return mark_safe(html)

