from django.db import models
from django.urls import reverse
from django import forms
from multiselectfield import MultiSelectField

from django.utils.text import slugify

import re

import fetchreference

class DisplayedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(active=True).filter(hidden=False)

# britpick_app model
class BaseModel(models.Model):
    active = models.BooleanField(default=True, verbose_name='active')
    hidden = models.BooleanField(default=False, verbose_name='hidden')
    verified = models.BooleanField(default=False, verbose_name='verified')
    date_created = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True, verbose_name='last edited')
    notes = models.TextField(blank=True,)

    objects = models.Manager()
    displayed = DisplayedManager()

    class Meta:
        abstract = True

    # def string(self) -> str:
    #     return str(self)

class OrderedModel(BaseModel):
    ORDERING_MIN = 0
    ORDERING_MAX = 25
    ORDERING_DEFAULT = 0

    ORDERING_CHOICES = [(x, str(x)) for x in range(ORDERING_MIN, ORDERING_MAX)]
    ordering = models.SmallIntegerField(default=ORDERING_DEFAULT, choices=ORDERING_CHOICES)

    class Meta:
        ordering = ['ordering']
        abstract = True






class Dialect(BaseModel):
    name = models.CharField(max_length=100, blank=True,)
    description = models.TextField(blank=True)
    limit_to_dialogue = models.BooleanField(default=False, help_text='search in dialogue only by default; only if true will be allowed to assign directly to word',)
    default = models.BooleanField(default=False)

    class Meta:
        ordering = ['-default', 'hidden', 'name',]

    def __str__(self):
        return self.name
        # if self.default:
        #     return '*' + self.name
        # elif self.hidden:
        #     return '(%s)' % self.name
        # else:
        #     return self.name



class Category(OrderedModel):
    """ mandatory, suggested, common, uncommon, informal, slang """

    name = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    can_assign_to_word = models.BooleanField(default=False)
    dialogue = models.BooleanField(default=False)
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class BritpickType(OrderedModel):
    # formerly 'explanation'
    name = models.CharField(max_length=100, blank=True, help_text='backend')
    explanation = models.TextField(blank=True, help_text='frontend')
    default_category = models.ForeignKey(
        "Category",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        help_text=
            """
            May have specific categories it lends itself to
            (ex same idea/different word -> mandatory)
            This allows automatic assigning of types to Britpicks if they aren't manually specified
            """,
    )
    can_assign_to_word = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Reference(BaseModel):
    name = models.CharField(max_length=100, blank=True)
    url = models.URLField()
    main_reference = models.BooleanField(default=False)
    site_name = models.CharField(max_length=100, blank=True)
    page_name = models.CharField(max_length=100, blank=True)


    class Meta:
        ordering = ['name',]

    def __str__(self):
        if self.name:
            return self.name
        else:
            return str(self.url)[:25]


    def save(self, *args, **kwargs):
        if not self.name and not self.page_name and not self.site_name:
        # if True:
            pagetitle = fetchreference.fetchreferencetitle(self.url)
            print()
            print(pagetitle)

            if 'error' in pagetitle.lower():
                self.page_name = pagetitle

            else:
                splittitle = []

                # page is listed first
                for divider in [' | ', ' · ', ' : ', ' - ', '—', '--',]:
                    if len(splittitle) > 1:
                        break

                    splittitle = pagetitle.split(divider)
                    if len(splittitle) > 2:
                        self.page_name = splittitle.pop(0).strip()
                        splittitle.reverse()
                        self.site_name = ' - '.join(s.strip() for s in splittitle)
                        break
                    elif len(splittitle) > 1:
                        self.page_name = splittitle[0].strip()
                        self.site_name = splittitle[1].strip()
                        break

                # page is listed second
                for divider in [': ']:
                    if len(splittitle) > 1:
                        break

                    splittitle = pagetitle.split(divider, 1)
                    if len(splittitle) > 1:
                        self.page_name = splittitle[1].strip()
                        self.site_name = splittitle[0].strip()
                        break

                    if len(splittitle) < 2:
                        self.page_name = pagetitle

                    if 'reddit' in self.url.lower():
                        self.site_name = 'r/' + self.site_name

        if not self.name:
            if self.page_name == self.site_name:
                self.name = self.page_name
            elif self.page_name and self.site_name:
                self.name = self.site_name + ' - ' + self.page_name
            elif self.page_name:
                self.name = self.page_name
            elif self.site_name:
                self.name = self.site_name


        super().save(*args, **kwargs)







# class Quote(BaseModel):
#     DIRECT_QUOTE = 0
#     EXCERPT = 1
#
#     QUOTE_TYPES = (
#         (DIRECT_QUOTE, 'quote'),
#         (EXCERPT, 'excerpt/explanation'),
#     )
#
#     quote = models.TextField(blank=True,)
#     quote_type = models.SmallIntegerField(choices='', default=DIRECT_QUOTE, )
#
#     reference = models.ForeignKey("Reference", on_delete=models.PROTECT, related_name='quotes', null=True, blank=True,)
#     reference_url = models.URLField(blank=True, null=True, help_text='use to quickly add reference; it will either be assigned existing reference or create new one')
#     words = models.ManyToManyField("Word", related_name='quotes', blank=True,)
#
#     def __str__(self):
#         if len(self.quote) < 50:
#             return '"%s"' % self.quote
#         else:
#             return '"%s"' % (self.quote[:48] + '...')



class Quote(OrderedModel):
    WORD_QUOTE = 0
    EXPLANATION_QUOTE = 1
    SUMMARY = 2

    QUOTE_TYPES = (
        (WORD_QUOTE, 'example'),
        (EXPLANATION_QUOTE, 'explanation (quoted)'),
        (SUMMARY, 'explanation (summarized)'),
    )

    text = models.TextField(blank=True, )

    direct_quote = models.PositiveSmallIntegerField(choices=QUOTE_TYPES, default=WORD_QUOTE, verbose_name='type')

    reference = models.ForeignKey("Reference", on_delete=models.PROTECT, null=True, blank=True, related_name='quotes')
    reference_url = models.URLField(blank=True, null=True, help_text='use to quickly add reference; it will either be assigned existing reference or create new one')

    words = models.ManyToManyField("Word", blank=True, related_name='quotes')
    topic = models.ForeignKey("Topic", on_delete=models.PROTECT, related_name='texts', blank=True, null=True)

    def __str__(self):
        if len(self.text) < 50:
            return '"%s"' % self.text
        else:
            return '"%s"' % (self.text[:48] + '...')

    def save(self, *args, **kwargs):
        if self.reference_url:
            try:
                self.reference = Reference.objects.get(url=self.reference_url)
            except Reference.DoesNotExist:
                r = Reference(url=self.reference_url)
                r.save()
                self.reference = r
            self.reference_url = None

        super().save(*args, **kwargs)

    @property
    def quote_by_word(self) -> dict:
        html = {}

        #TODO: run through suffixes/conjugations here
        for word in self.words.all():
            html[word.pk] = re.sub('(' + word.word + ')', r'<em>\1</em>', self.text, flags=re.IGNORECASE)
            # try:
            #
            #     s = self.text.split(word.word)
            #     html[word.pk] = s[0] + r'<em>' + word.word + r'</em>' + s[1]
            # except IndexError:
            #     html[word.pk] = self.text

        return html


class MainTopicsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(parent_topic__isnull=True)


class Topic(BaseModel):
    """
    topic is a way to display a large amount of text, links, etc with large numbers of relationships
    """

    MAIN_TOPIC = 'MT'
    TOPIC = 'T'
    INLINE_TOPIC = 'ST'
    # WORD_TOPIC = 'W'

    TOPIC_TYPES = (
        (MAIN_TOPIC, 'main topic'),
        (TOPIC, 'topic'),
        (INLINE_TOPIC, 'inline topic'),
        # (WORD_TOPIC, 'word'),
    )

    name = models.CharField(max_length=50, blank=True)
    slug = models.SlugField(blank=True, db_index=True)
    topic_type = models.CharField(max_length=20, choices=TOPIC_TYPES, default=TOPIC)

    dialect = models.ForeignKey(
        "Dialect",
        models.PROTECT,
        related_name='topics',
        blank=True,
        null=True,
        help_text=
            """
            If dialect is selected, all words/britpicks with this dialect will be automatically linked
            """,
    )

    # text = models.TextField(blank=True)
    references = models.ManyToManyField("Reference", blank=True, related_name='topics')

    parent_topic = models.ForeignKey("self", on_delete=models.PROTECT, related_name='child_topics', null=True, blank=True,)

    related_topics = models.ManyToManyField("self", symmetrical=True, blank=True,)
    # slugfield w/prepopulated on admin page

    # # needed or not?
    # # minor_references = models.ManyToManyField(Reference, blank=True, related_name='minor_references')

    # add get_absolute_url() for view on site to be enabled on edit page
    # def get_absolute_url(self):
        # return reverse('people.views.details', args=[str(self.id)])

    objects = models.Manager()
    main_topics = MainTopicsManager()

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name) #TODO - create automatic redirect when changing slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def parent_topics(self) -> list:
        """ returns parent topics in order from topic of hierarchy down """
        topics = []
        t = self
        while t.parent_topic:
            t = t.parent_topic
            topics.append(t)

        topics.reverse()

        return topics

    @property
    def descendent_topics(self) -> list:
        topics = []

        for t in Topic.objects.all():
            if self in t.parent_topics:
                topics.append(t)
        return topics

    @property
    def top_parent_or_self(self):
        if self.parent_topic:
            return self.parent_topics[0]
        else:
            return self

    @property
    def top_parent_or_self_as_list(self):
        if self.parent_topic:
            return [self.parent_topics[0]]
        else:
            return [self]
    # def child_topics(self):
    #     return Topic.objects.filter(parent_topic=self)

    @property
    def siblings(self) -> list:
        if self.parent_topic:
            topics = list(self.parent_topic.child_topics.all())
        else:
            topics = list(Topic.main_topics.all())

        return topics

    @property
    def previous_topic(self):
        topics = self.siblings
        i = topics.index(self)
        if i == 0:
            return None
        else:
            return topics[topics.index(self)-1]

    @property
    def next_topic(self):
        topics = self.siblings
        i = topics.index(self)
        if i == len(topics) - 1:
            return None
        else:
            return topics[topics.index(self) + 1]

    # TODO: is the logic correct here?? need to create filter...
    def canbeparentof(self, child_topic) -> bool:
        if self.topic_type == self.INLINE_TOPIC:
            return False
        if child_topic == self:
            return False

        t = self
        while t.parent_topic:
            if t.parent_topic == child_topic:
                return False
            else:
                t = t.parent_topic

        return True




class Britpick(BaseModel):
    """
    ties together things to search for
    with links to replacement words, topics, references, explanation
    and a field for explanation

    for use in-text and in showing relationships in a topic
    """
    dialect = models.ForeignKey(
        "Dialect",
        models.PROTECT,
        related_name='britpicks',
        null=True,
        default=3, #british
    )

    category = models.ForeignKey(
        "Category",
        models.PROTECT,
        related_name='britpicks',
        blank=True,
        null=True,
        help_text='determined by set value > type > word category > word type; within each, the top ordering is used (mandatory -> slang)',
        # default=2, #suggested
    )

    type = models.ForeignKey(
        "BritpickType",
        models.PROTECT,
        related_name='britpicks_onetype',
        blank=True,
        null=True,
        help_text='',
    )

    types = models.ManyToManyField(
        "BritpickType",
        blank=True,
        related_name='britpicks',
    )

    # .search_strings = from SearchString fk
    search_groups = models.ManyToManyField(
        "SearchGroup",
        blank=True,
        related_name='searched_by',
    )

    exclude_search_groups = models.ManyToManyField(
        "SearchGroup",
        blank=True,
        related_name='excluded_by',
        verbose_name='exclude',
    )

    require_search_groups = models.ManyToManyField(
        "SearchGroup",
        blank=True,
        related_name='required_by',
        verbose_name='require',
    )

    words = models.ManyToManyField("Word", blank=True, related_name='britpicks')
    word_groups = models.ManyToManyField("WordGroup", blank=True, related_name='britpicks')

    replacements = models.ManyToManyField("Word", through="BritpickReplacements", blank=True, related_name='breplacements')

    topics = models.ManyToManyField("Topic", blank=True, related_name='britpicks')
    always_show_topic_names = models.BooleanField(
        default=False,
        help_text=
            """
                select if topic name needed to provide context
                (ex 'sports', 'cars', 'clothing')
            """,
    )

    explanation = models.TextField(blank=True, )


    references = models.ManyToManyField("Reference", blank=True, related_name='britpicks')

    def __str__(self):
        s = ', '.join(str(s) for s in self.search_strings.all())
        s += ' -> ' + ', '.join(str(w) for w in self.all_words())
        return s

    def gettypes(self):
        types = [t for t in self.types.all()]
        for w in self.words.all():
            types.extend(t for t in w.types.all())
        return types

    def getcategory(self):
        if self.category:
            return self.category
        if self.types:
            categories = [c.default_category for c in self.types.all() if c.default_category is not None]
            if len(categories) > 0:
                categories.sort(key=lambda x: x.ordering)
                return categories[0]
        if self.words:
            categories = [c.getcategory() for c in self.words.all() if c.getcategory() is not None]
            if len(categories) > 0:
                categories.sort(key=lambda x: x.ordering)
                return categories[0]

        if self.dialect.limit_to_dialogue:
            return Category.objects.get(pk=5)
        else:
            return Category.objects.get(default=True)


    def getcategorysource(self):
        if self.category:
            return 'self'
        if self.types:
            categories = [c.default_category for c in self.types.all() if c.default_category is not None]
            if len(categories) > 0:
                # categories.sort(key=lambda x: x.ordering)
                return 'types'
        if self.words:
            categories = [c.getcategory() for c in self.words.all() if c.getcategory() is not None]
            if len(categories) > 0:
                # categories.sort(key=lambda x: x.ordering)
                return 'words'

        if self.dialect.limit_to_dialogue:
            return 'dialect'
        else:
            return 'database default'

    def all_words(self):
        words = [w for w in self.words.filter(active=True).filter(hidden=False)]
        for group in self.word_groups.filter(active=True).filter(hidden=False):
            words.extend([w for w in group.words.filter(active=True).filter(hidden=False)])
        return words


class SearchString(BaseModel):
    CONJUGATE_PHRASE = 0
    PLURAL_PHRASE = 1
    PRESERVE_PHRASE = 2

    MODIFIER_CHOICES = [
        (CONJUGATE_PHRASE, 'conjugate'),
        (PLURAL_PHRASE, 'plural to end only'),
        (PRESERVE_PHRASE, "don't conjugate"),
    ]

    # foreign key - so that any duplicates have to be made with groups
    britpick = models.ForeignKey("Britpick", on_delete=models.PROTECT, related_name='search_strings', blank=True, null=True, )

    # modifiers = MultiSelectField(choices=MODIFIER_CHOICES, blank=True, null=True,)

    processing = models.SmallIntegerField(choices=MODIFIER_CHOICES, default=CONJUGATE_PHRASE)

    # plural_only = models.BooleanField(default=False)
    # preserve_string = models.BooleanField(default=False)
    begin_sentence = models.BooleanField(default=False)
    end_sentence = models.BooleanField(default=False)
    case_sensitive = models.BooleanField(default=False)

    string = models.CharField(max_length=300)
    pattern = models.TextField(blank=True,)
    # options created from separate searchwords functions/regex wrapper to create pattern; ie preserve all words, preserve case, beginning of sentence, end of phrase, question, noun
    # inline - preserve word (#), markup, noun, dash

    @property
    def ignorecase(self):
        return not self.case_sensitive

    def __str__(self):
        if not '(' in self.string:
            return self.string

        strings = [self.string]

        for string in strings:
            option_match = re.search(r"\(.*?\)", string)
            if option_match:
                options = [m for m in re.finditer(r'(?<=[\(\|])([^\(\|]*)(?=[\)\|])', option_match.group(0))]
                for m in options:
                    strings.append(string[:option_match.start()] + m.group(0) + string[option_match.end():])

        return ', '.join(s for s in strings if '(' not in s)

    def save(self, *args, **kwargs):
        self.createpattern()

        super().save(*args, **kwargs)

    def createpattern(self):
        self.pattern = self.string
        if self.processing == self.PLURAL_PHRASE:
            self.process_plural_only()
        elif self.processing == self.CONJUGATE_PHRASE:
            self.pattern = self.string

        if self.begin_sentence:
            self.process_begin_sentence()
        if self.end_sentence:
            self.process_end_sentence()

        return self.pattern

    def process_plural_only(self):
        self.pattern += r'(|s|es)'
        self.preserve_string = True

    def process_begin_sentence(self):
        self.case_sensitive = True
        s = self.pattern[0].upper() + self.pattern[1:].lower()
        s = r'(\n|\. |\? |\! |")' + s
        self.pattern = s

    def process_end_sentence(self):
        self.pattern += r'(\.|\?|\,|\!)'

class SearchGroup(BaseModel):
    """
    can use with things like idiot that could have multiple results based on dialect
    also use with things contexts to include/exclude (driving context, swimming context)
    """
    name = models.CharField(max_length=100, blank=True)
    search_strings = models.ManyToManyField("SearchString", blank=True, related_name='search_groups',)

    def __str__(self):
        return self.name

class SearchVariables(BaseModel):
    # database-side representation of markup
    # can contain regex
    pass



class BritpickReplacements(models.Model):
    ORDERING_CHOICES = [(x, str(x)) for x in range(0, 26)]
    REPLACEMENT_CHOICES = [(True, 'replacement'), (False, 'disambiguation')]

    britpick = models.ForeignKey("Britpick", on_delete=models.SET_NULL, null=True, blank=True, related_name='bwreplacements')
    word = models.ForeignKey("Word", on_delete=models.SET_NULL, related_name='wbreplacements', null=True, blank=True,)

    replacement = models.BooleanField(default=True, choices=REPLACEMENT_CHOICES)

    ordering = models.IntegerField(default=0, choices=ORDERING_CHOICES)

    class Meta:
        ordering = ['-replacement', 'ordering']

    def __str__(self):
        return str(self.britpick) + ':' + str(self.word)






class Word(BaseModel):

    word = models.CharField(
        max_length=255,
        help_text=
            """
                for multiple related words, separate by commas, most important word first (ie "underground, London Underground")\r\n
                not unique (ex 'grade')\r\n
                use description for differentiation (ex 'Grade (noun)')\r\n
                (replaces .name)
            """,
    )

    explanation = models.TextField(blank=True,)

    # AND/OR GET DIALECT DYNAMICALLY THROUGH BRITPICK - make property???
    dialect = models.ForeignKey(
        "Dialect",
        models.PROTECT,
        related_name='words',
        blank=True,
        null=True,
    )
    category = models.ForeignKey(
        "Category",
        models.PROTECT,
        related_name='words',
        blank=True,
        null=True,
        help_text=
            """
                For selecting 'slang' or 'informal'.
                If britpick does not have type, then selection here will determine britpick type. Can also be used to only display certain results (ie skip slang/informal results that aren't in dialogue or if not wanted).
            """,
    )

    types = models.ManyToManyField(
        "BritpickType",
        blank=True,
        related_name='words',
        help_text='usually in britpick, not here',
    )

    type = models.ForeignKey("BritpickType", on_delete=models.PROTECT, related_name='wtype', limit_choices_to={'can_assign_to_word': True}, blank=True, null=True,)


    topics = models.ManyToManyField(
        "Topic",
        related_name='words',
        blank=True,
        help_text=
            """
                If it's the word that's the main point (ie insults; 'slag') then select topic here.
                But if it's the britpick that's the main point (ie kitchen; counter -> worktop) then topic should be linked in britpick.
            """,
    )
    references = models.ManyToManyField("Reference", blank=True, related_name='words')

    @property
    def explanation_present(self):
        return bool(self.explanation)

    def __str__(self):
        return self.word
        return self.word

    def getcategory(self):
        if self.category:
            return self.category
        if self.types:
            categories = [c.default_category for c in self.types.all() if c.default_category is not None]
            if len(categories) > 0:
                categories.sort(key=lambda x: x.ordering)
                return categories[0]
        return None

    def getcategorysource(self):
        if self.category:
            return 'self'
        if self.types:
            categories = [c.default_category for c in self.types.all() if c.default_category is not None]
            if len(categories) > 0:
                # categories.sort(key=lambda x: x.ordering)
                return 'types'
        return None

class Definition(BaseModel):
    dialect = models.ForeignKey(
        "Dialect",
        models.PROTECT,
        related_name='definitions',
        blank=False,
        null=False,
    )

    definition = models.TextField(blank=False, )

    word = models.ForeignKey("Word", on_delete=models.PROTECT, related_name='definitions', blank=False, null=False,)


class WordGroup(BaseModel):
    name = models.CharField(max_length=100, blank=True)
    words = models.ManyToManyField("Word", blank=True, related_name='groups',)

    def __str__(self):
        return self.name





class SampleText(BaseModel):
    name = models.CharField(max_length=100, blank=True)
    text = models.TextField(blank=True)

    def __str__(self):
        return self.name








