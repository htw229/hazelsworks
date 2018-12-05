from django.contrib import admin
from django import forms
from django.utils.html import mark_safe

from britpick_app.models import *


class BaseAdmin(admin.ModelAdmin):
    ACTIVE_VERIFIED_LIST = ['active', 'verified', 'hidden', ]

    DATE_EDITED_FIELDSET = (None, {
        'fields': (('date_edited', 'notes'),),
        'classes': ('internal-fieldset',),
    })

    ACTIVE_VERIFIED_FIELDSET = (None, {
        'fields': (('active', 'verified', 'hidden',),),
        'classes': (),
    })

    # NOTES_FIELDSET = (None, {
    #     'fields': ('notes',),
    #     'classes': ('internal-fieldset',),
    # })

    READONLY_FIELDS = ['date_edited',]

    list_filter = ACTIVE_VERIFIED_LIST
    date_hierarchy = 'date_edited'
    list_display = ('__str__',*ACTIVE_VERIFIED_LIST, 'date_edited',)
    list_editable = ('active', 'verified', 'hidden',)

    save_on_top = True
    readonly_fields = READONLY_FIELDS

    textinputoverrides = []
    optionalinputs = []
    requiredinputs = []

    def formfield_for_dbfield(self, db_field, **kwargs):
        # for displaying text fields as inputs rather than textareas
        formfield = super(BaseAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name in self.textinputoverrides:
            formfield.widget = forms.TextInput(attrs={'class':'vTextField',})

        return formfield

class DialectAdmin(BaseAdmin):
    fieldsets = [
        BaseAdmin.DATE_EDITED_FIELDSET,
        BaseAdmin.ACTIVE_VERIFIED_FIELDSET,
        (None, {
            'fields': (
                'name',
            ),
            'classes': ('header-fieldset',)
        }),
        (None, {
            'fields': ('description','default', 'limit_to_dialogue',),
        }),
        # BaseAdmin.NOTES_FIELDSET,
    ]


admin.site.register(Dialect, DialectAdmin)

class BritpickCategoryAdmin(BaseAdmin):
    fieldsets = [
        BaseAdmin.DATE_EDITED_FIELDSET,
        (None, {
            'fields': (
                'name',
            ),
            'classes': ('header-fieldset',)
        }),
        BaseAdmin.ACTIVE_VERIFIED_FIELDSET,
        (None, {
            'fields': (
                'description','allow_for_word', 'default',
            ),
        }),
    ]

admin.site.register(BritpickCategory, BritpickCategoryAdmin)

class BritpickTypeAdmin(BaseAdmin):
    search_fields = ['type', 'explanation',]

admin.site.register(BritpickType, BritpickTypeAdmin)

class ReferenceAdmin(BaseAdmin):
    search_fields = ['name', 'url', 'site_name', 'page_name',]

admin.site.register(Reference, ReferenceAdmin)

class QuoteAdmin(BaseAdmin):
    autocomplete_fields = ['words',]

    fieldsets = [
        BaseAdmin.DATE_EDITED_FIELDSET,
        BaseAdmin.ACTIVE_VERIFIED_FIELDSET,
        (None, {
            'fields': ('quote', 'reference', 'words',),
        }),
    ]

admin.site.register(Quote, QuoteAdmin)

class TopicAdmin(BaseAdmin):
    search_fields = ['name',]

admin.site.register(Topic, TopicAdmin)


class BritpickSearchStringInline(admin.TabularInline):
    model = SearchString
    extra = 0
    fields = ('string',)
    insert_before = 'search_groups'

class BritpickAdmin(BaseAdmin):

    inlines = [BritpickSearchStringInline,]
    autocomplete_fields = ('types','topics', 'words', 'word_groups', 'references', 'search_groups', 'exclude_search_groups','require_search_groups',)
    # filter_horizontal = ('search_groups', 'exclude_search_groups', 'require_search_groups',)

    readonly_fields = [
        *BaseAdmin.readonly_fields,
        *['words_changelinks','search_changelinks','word_groups_changelinks','topics_changelinks', 'references_changelinks',],
    ]

    # readonly_fields = [f for f in BaseAdmin.readonly_fields]
    # readonly_fields.extend(['words_changelinks','search_changelinks','exclude_search_groups_changelinks','require_search_groups_changelinks','word_groups_changelinks','topics_changelinks', 'references_changelinks',])

    fieldsets = [
        BaseAdmin.DATE_EDITED_FIELDSET,
        BaseAdmin.ACTIVE_VERIFIED_FIELDSET,
        (None, {
            'fields': ('dialect', 'category', 'types',),
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
        (None, {
            'fields': (('topics','topics_changelinks','always_show_topic_names',),),
        }),
        (None, {
            'fields': (('references','references_changelinks'),),
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
        s = getchangelinks(obj.search_strings.all())
        s += getchangelinks(obj.search_groups.all())
        s += getchangelinks(obj.exclude_search_groups.all(), label='exclude:')
        s += getchangelinks(obj.require_search_groups.all(), label='require:')

        return mark_safe(s)

    search_changelinks.short_description = 'search'

admin.site.register(Britpick, BritpickAdmin)

class SearchStringAdmin(BaseAdmin):
    pass

admin.site.register(SearchString, SearchStringAdmin)


class SearchGroupAdmin(BaseAdmin):
    search_fields = ['name',]

admin.site.register(SearchGroup, SearchGroupAdmin)

admin.site.register(SearchVariables)


# class WordQuoteInline(admin.TabularInline):
#     model = Quote
#     extra = 0
#     fields = ('text', 'reference',)
#     autocomplete_fields = ('reference',)
#     # insert_before = ''

class WordAdmin(BaseAdmin):
    # inlines = [WordQuoteInline,]
    search_fields = ['word',]
    autocomplete_fields = ('topics', 'references',)
    readonly_fields = [
        *BaseAdmin.readonly_fields,
        *['topics_changelinks', 'references_changelinks', 'quotes_changelinks',],
    ]

    fieldsets = [
        BaseAdmin.DATE_EDITED_FIELDSET,
        (None, {
            'fields': (
                'word',
            ),
            'classes': ('header-fieldset',)
        }),
        BaseAdmin.ACTIVE_VERIFIED_FIELDSET,
        (None, {
            'fields': (
                'dialect',
                'category',
            ),
            'classes': ('optional-fieldset', 'indented-fieldset',)
        }),
        (None, {
            'fields': (
                ('topics', 'topics_changelinks'),
            ),
        }),
        (None, {
            'fields': (
                ('references', 'references_changelinks'),
                'quotes_changelinks',
            ),
            # 'classes': ('optional-fieldset',)
        }),
    ]

    def topics_changelinks(self, obj):
        return getchangelinks(obj.topics.all())
    topics_changelinks.short_description = 'links'

    def references_changelinks(self, obj):
        return getchangelinks(obj.references.all())
    references_changelinks.short_description = 'links'

    def quotes_changelinks(self, obj):
        # TODO: quotes_changelinks
        return getchangelinks(Quote.objects.filter(words=obj))
    quotes_changelinks.short_description = 'quotes'


admin.site.register(Word, WordAdmin)

class WordGroupAdmin(BaseAdmin):
    search_fields = ['name',]

admin.site.register(WordGroup, WordGroupAdmin)

def getchangelinks(objs, label = ''):
    links = []
    for o in objs:
        links.append('<div>%s <a href="%s" class="related-widget-wrapper-link add-related">%s</a></div>' % (label,
        reverse("admin:britpick_app_%s_change" % type(o).__name__.lower(), args=(o.id,)), o.name))
    html = ' '.join(links)
    return mark_safe(html)

