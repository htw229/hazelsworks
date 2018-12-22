from django.db import models
from django.urls import reverse
from django import forms
from multiselectfield import MultiSelectField




# britpick_app model
class BaseModel(models.Model):
    active = models.BooleanField(default=True, verbose_name='active')
    hidden = models.BooleanField(default=False, verbose_name='hidden')
    verified = models.BooleanField(default=False, verbose_name='verified')
    date_created = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True, verbose_name='last edited')
    notes = models.TextField(blank=True,)

    class Meta:
        abstract = True


class OrderedModel(BaseModel):
    ORDERING_CHOICES = [(x, str(x)) for x in range(1,100)]
    ordering = models.IntegerField(default=99, choices=ORDERING_CHOICES)

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

    def __str__(self):
        if self.name:
            return self.name
        else:
            return str(self.url)[:25]

class Quote(BaseModel):
    quote = models.TextField(blank=True,)
    reference = models.ForeignKey("Reference", on_delete=models.PROTECT, related_name='quotes', null=True, blank=True,)
    reference_url = models.URLField(blank=True, null=True, help_text='use to quickly add reference; it will either be assigned existing reference or create new one')
    words = models.ManyToManyField("Word", related_name='quotes', blank=True,)

    def __str__(self):
        if len(self.quote) < 50:
            return '"%s"' % self.quote
        else:
            return '"%s"' % (self.quote[:48] + '...')

class Topic(BaseModel):
    """
    topic is a way to display a large amount of text, links, etc with large numbers of relationships
    """

    WORD = 'W'
    MAIN_TOPIC = 'MT'
    TOPIC = 'T'
    TOPIC_TYPES = (
        (TOPIC, 'topic'),
        (MAIN_TOPIC, 'main topic'),
        (WORD, 'word'),
    )

    name = models.CharField(max_length=50, blank=True)
    slug = models.SlugField(null=True, blank=True,)
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

    text = models.TextField(blank=True)
    references = models.ManyToManyField("Reference", blank=True, related_name='topics')
    related_topics = models.ManyToManyField("self", symmetrical=True, blank=True)
    # slugfield w/prepopulated on admin page

    # # needed or not?
    # # minor_references = models.ManyToManyField(Reference, blank=True, related_name='minor_references')

    # add get_absolute_url() for view on site to be enabled on edit page
    # def get_absolute_url(self):
        # return reverse('people.views.details', args=[str(self.id)])

    def __str__(self):
        return self.name




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
        return ', '.join(s.string for s in self.search_strings.all())

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
        return self.string

    def createpattern(self):
        self.pattern = self.string
        if self.processing == self.PLURAL_PHRASE:
            self.process_plural_only()
        elif self.processing == self.CONJUGATE_PHRASE:
            pass

        if self.begin_sentence:
            self.process_begin_sentence()
        if self.end_sentence:
            self.process_end_sentence()

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

    britpick = models.ForeignKey("Britpick", on_delete=models.PROTECT, related_name='bwreplacements')
    word = models.ForeignKey("Word", on_delete=models.PROTECT, related_name='wbreplacements')

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
                not unique (ex 'grade')
                use description for differentiation (ex 'Grade (noun)')
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
















