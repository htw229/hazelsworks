from django.contrib import admin
from django import forms
from django.utils.html import mark_safe
from django.db.models import Count

from britpick_app.models import *


class BaseAdmin(admin.ModelAdmin):
    ACTIVE_VERIFIED_LIST = ['active', 'verified', 'hidden', ]

    FOOTER_FIELDSET = (None, {
        'fields': ('date_edited','notes',),
        'classes': ('internal-fieldset',),
    })

    ACTIVE_VERIFIED_FIELDSET = (None, {
        'fields': (('active', 'verified', 'hidden',),),
        'classes': ('checkbox-fieldset', 'optional-fieldset',),
    })

    READONLY_FIELDS = ['date_edited',]

    list_filter = ACTIVE_VERIFIED_LIST
    date_hierarchy = 'date_edited'
    list_display = ['active', '__str__',]
    list_editable = ['active',]
    list_display_links = ['__str__',]

    save_on_top = True
    readonly_fields = READONLY_FIELDS

    smalltextfields = []
    mediumtextfields = ['description', 'explanation', 'notes',]
    optionalinputs = []
    requiredinputs = []

    def formfield_for_dbfield(self, db_field, **kwargs):
        # for displaying text fields as inputs rather than textareas
        formfield = super(BaseAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name in self.smalltextfields:
            formfield.widget = forms.TextInput(attrs={'class':'vTextField small-text-field',})
        if db_field.name in self.mediumtextfields:
            formfield.widget = forms.Textarea(attrs={'class':'vLargeTextField medium-text-field',})

        return formfield

    def britpickcount(self, obj):
        return obj.britpicks.count()
    britpickcount.short_description = 'Britpicks'


class OrderedAdmin(BaseAdmin):
    list_display = ['ordering',*BaseAdmin.list_display,]
    list_editable = ['ordering',*BaseAdmin.list_editable,]

    max_choices = 1

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "ordering":
            kwargs['choices'] = [(x, str(x)) for x in range(1, self.max_choices + 1)]
        return super(OrderedAdmin, self).formfield_for_choice_field(db_field, request, **kwargs)

class DialectAdmin(BaseAdmin):
    list_display = ('__str__', 'default', 'limit_to_dialogue', 'active', 'hidden', 'britpickcount')
    list_editable = ('default', 'limit_to_dialogue', 'active', 'hidden',)
    list_display_links = ('__str__',)

    readonly_fields = ['britpickcount', 'date_edited',]
    fieldsets = [
        (None, {
            'fields': (
                ('name','britpickcount',),
            ),
            'classes': ('header-fieldset',)
        }),
        BaseAdmin.ACTIVE_VERIFIED_FIELDSET,
        (None, {
            'fields': (
                ('default', 'limit_to_dialogue',),
            ),
            'classes': ('checkbox-fieldset',)
        }),
        (None, {
            'fields': (
                'description',
            ),
        }),
        BaseAdmin.FOOTER_FIELDSET,
    ]

    def britpickcount(self, obj):
        return Britpick.objects.filter(dialect=obj.pk).count()
    britpickcount.short_description = 'Britpicks'


admin.site.register(Dialect, DialectAdmin)



class BritpicksFilter(admin.SimpleListFilter):
    title = 'britpicks'
    parameter_name = 'num_britpicks'

    def lookups(self, request, model_admin):
        return (
            ('0', 'none'),
            ('1', 'one'),
            ('2', 'multiple'),
        )

    def queryset(self, request, queryset):
        if self.value() == '0':
            return queryset.annotate(num_britpicks=Count('britpicks')).filter(num_britpicks=0)
        if self.value() == '1':
            return queryset.annotate(num_britpicks=Count('britpicks')).filter(num_britpicks=1)
        if self.value() == '2':
            return queryset.annotate(num_britpicks=Count('britpicks')).filter(num_britpicks__gt=1)









class BritpickCategoryAdmin(OrderedAdmin):
    max_choices = BritpickCategory.objects.all().count()

    fieldsets = [

        (None, {
            'fields': (
                'name',
            ),
            'classes': ('header-fieldset',)
        }),
        BaseAdmin.ACTIVE_VERIFIED_FIELDSET,
        (None, {
            'fields': (
                ('allow_for_word', 'default'),
            ),
            'classes': ('checkbox-fieldset',)
        }),
        (None, {
            'fields': (
                'description',
            ),
        }),
        BaseAdmin.FOOTER_FIELDSET,
    ]

admin.site.register(BritpickCategory, BritpickCategoryAdmin)

class BritpickTypeAdmin(OrderedAdmin):
    max_choices = BritpickType.objects.all().count()

    # list_display = ['ordering','__str__','default_britpick_category',*BaseAdmin.ACTIVE_VERIFIED_LIST, 'date_edited',]

    list_display = [*OrderedAdmin.list_display, 'default_britpick_category',]

    search_fields = ['name', 'explanation',]
    fieldsets = [
        (None, {
            'fields': (
                'name', 'explanation',
            ),
            'classes': ('header-fieldset',)
        }),
        BaseAdmin.ACTIVE_VERIFIED_FIELDSET,
        # (None, {
        #     'fields': (
        #         'explanation',
        #     ),
        # }),
        (None, {
            'fields': (
                'default_britpick_category',
            ),
            'classes': ('optional-fieldset',)
        }),
        BaseAdmin.FOOTER_FIELDSET,
    ]


admin.site.register(BritpickType, BritpickTypeAdmin)

class ReferenceAdmin(BaseAdmin):
    search_fields = ['name', 'url', 'site_name', 'page_name',]
    readonly_fields = [*BaseAdmin.readonly_fields, 'site_name', 'page_name',]

    fieldsets = [
        (None, {
            'fields': (
                'name',
            ),
            'classes': ('header-fieldset',)
        }),
        BaseAdmin.ACTIVE_VERIFIED_FIELDSET,
        (None, {
            'fields': (('main_reference',),),
            'classes': ('checkbox-fieldset',),
        }),
        (None, {
            'fields': (
                'url',
            ),
        }),
        (None, {
            'fields': (
                ('site_name', 'page_name',),
            ),
            'classes': ('optional-fieldset',)
        }),
        BaseAdmin.FOOTER_FIELDSET,
    ]

admin.site.register(Reference, ReferenceAdmin)



class QuoteAdmin(BaseAdmin):
    search_fields = ['quote', 'words__word', 'reference__name', 'reference__url',]

    list_display = [*BaseAdmin.list_display, 'linkedwords', 'reference',]

    # list_display = ['active', '__str__', 'linkedwords', 'reference',]
    # list_display_links = ['__str__']

    autocomplete_fields = ['words','reference',]
    fieldsets = [

        BaseAdmin.ACTIVE_VERIFIED_FIELDSET,
        (None, {
            'fields': ('quote','words',),
        }),
        (None, {
            'fields': (
                'reference', 'reference_url',
            ),
            'classes': ('optional-fieldset',)
        }),
        BaseAdmin.FOOTER_FIELDSET,
    ]

    mediumtextfields = [*BaseAdmin.mediumtextfields, 'quote',]

    def linkedwords(self, obj):
        return ', '.join(w.word for w in Word.objects.filter(quotes=obj.pk))
    linkedwords.short_description = 'words'

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
        BaseAdmin.FOOTER_FIELDSET,
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
    list_filter = [*BaseAdmin.list_filter]

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

# class WordQuoteInline(admin.TabularInline):
#     model = Quote.words.through
#     extra = 0
#     readonly_fields = ['quote',]

class WordExplanationExistsFilter(admin.SimpleListFilter):
    title = 'explanation exists'
    parameter_name = 'explanation_exists'
    #
    def lookups(self, request, model_admin):
        return (
            ('true', 'explanation exists'),
            ('false', 'no explanation')
        )

    def queryset(self, request, queryset):
        if self.value() == 'false':
            return queryset.filter(explanation='')
        if self.value() == 'true':
            return queryset.exclude(explanation='')

class WordBritpickCountFilter(admin.SimpleListFilter):
    title = 'britpicks'
    parameter_name = 'britpick_count'

    def lookups(self, request, model_admin):
        return (
            ('none', '0'),
            ('1', '1'),
            ('multiple', '> 1'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'none':
            return queryset.annotate(num_britpicks=Count('britpicks')).filter(num_britpicks=0)
        if self.value() == '1':
            return queryset.annotate(num_britpicks=Count('britpicks')).filter(num_britpicks=1)
        if self.value() == 'multiple':
            return queryset.annotate(num_britpicks=Count('britpicks')).filter(num_britpicks__gt=1)






class WordAdmin(BaseAdmin):
    search_fields = ['word', 'explanation', 'topics__name',]
    list_display = [*BaseAdmin.list_display, 'dialect', 'category', 'explanation_exists', 'quotes_count', 'topics_count', 'references_count','britpickcount']
    list_filter = [*BaseAdmin.list_filter, 'dialect', 'category', WordExplanationExistsFilter,BritpicksFilter, 'topics',]

    autocomplete_fields = ('topics', 'references',)
    readonly_fields = [
        *BaseAdmin.readonly_fields,
        *['topics_changelinks', 'references_changelinks', 'quotes_changelinks', 'britpicks_changelinks'],
    ]
    # inlines = [WordQuoteInline,]

    fieldsets = [
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
                'explanation',('topics', 'topics_changelinks'),
            ),
        }),
        (None, {
            'fields': (
                ('references', 'references_changelinks'),
                'quotes_changelinks', 'britpicks_changelinks',
            ),
            # 'classes': ('optional-fieldset',)
        }),
        BaseAdmin.FOOTER_FIELDSET,
    ]

    def topics_changelinks(self, obj):
        return getchangelinks(obj.topics.all())
    topics_changelinks.short_description = 'links'

    def references_changelinks(self, obj):
        return getchangelinks(obj.references.all())
    references_changelinks.short_description = 'links'

    def quotes_changelinks(self, obj):
        return getchangelinks(obj.quotes.all(), add_link=True, model_name='quote', attr='quote',)
    quotes_changelinks.short_description = 'quotes'

    def britpicks_changelinks(self, obj):
        return getchangelinks(obj.britpicks.all(), add_link=True, model_name='britpick')
    britpicks_changelinks.short_description = 'britpicks'

    def topics_count(self, obj):
        return obj.topics.all().count()
    topics_count.short_description = 'topics'

    def references_count(self, obj):
        return obj.references.all().count()
    references_count.short_description = 'references'

    def quotes_count(self, obj):
        return obj.quotes.all().count()
    quotes_count.short_description = 'quotes'

    def explanation_exists(self, obj):
        if obj.explanation:
            return mark_safe('<img src="/static/admin/img/icon-yes.svg" alt="True">')
        else:
            return mark_safe('<img src="/static/admin/img/icon-no.svg" alt="False">')
    explanation_exists.short_description = 'explanation'

admin.site.register(Word, WordAdmin)

class WordGroupAdmin(BaseAdmin):
    search_fields = ['name',]

admin.site.register(WordGroup, WordGroupAdmin)

def getchangelinks(objs, label = '', add_link=False, model_name = None, attr = None):
    links = []
    for o in objs:
        if attr:
            s = getattr(o,attr)
        else:
            s = str(o)
        links.append('<div>%s <a href="%s" class="related-widget-wrapper-link add-related change-icon">%s</a></div>' % (label,
        reverse("admin:britpick_app_%s_change" % type(o).__name__.lower(), args=(o.id,)), s))

    if add_link:
        try:
            links.append('<div>%s <a href="%s" class="related-widget-wrapper-link add-related">%s</a></div>' % (
                label,
                reverse("admin:britpick_app_%s_add" %
                        type(objs[0]).__name__.lower(),
                        args=()),
                '<img src="/static/admin/img/icon-addlink.svg" alt="Add">'))
        except IndexError:
            links.append('<div>%s <a href="%s" class="related-widget-wrapper-link add-related">%s</a></div>' % (
                label,
                reverse("admin:britpick_app_%s_add" %
                        model_name,
                        args=()),
                '<img src="/static/admin/img/icon-addlink.svg" alt="Add">'))
    html = ' '.join(links)


    return mark_safe(html)

