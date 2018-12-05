from django.db import models
from django.urls import reverse

# britpick_app model
class BaseModel(models.Model):
    active = models.BooleanField(default=True, verbose_name='active')
    hidden = models.BooleanField(default=False, verbose_name='hidden')
    verified = models.BooleanField(default=False, verbose_name='verified')
    date_created = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True, verbose_name='last edited')
    notes = models.CharField(max_length=255, blank=True,)

    class Meta:
        abstract = True



# class Suggestion(models.Model):
#     # can use for back-end notes and front-end suggestions
#     text = models.TextField()
#     britpick = models.ForeignKey("Britpick", on_delete=models.CASCADE, related_name='suggestions', blank=True)
#     topic = models.ForeignKey("Topic", on_delete=models.CASCADE, related_name='suggestions', blank=True)



class Dialect(BaseModel):
    name = models.CharField(max_length=100, blank=True,)
    description = models.CharField(max_length=255, blank=True,)
    limit_to_dialogue = models.BooleanField(default=False, help_text='search in dialogue only by default',)
    default = models.BooleanField(default=False)


    def __str__(self):
        return self.name

class BritpickCategory(BaseModel):
    """ mandatory, suggested, common, uncommon, informal, slang """
    name = models.CharField(max_length=100, blank=True)
    description = models.CharField(max_length=255, blank=True)
    allow_for_word = models.BooleanField(default=False)
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class BritpickType(BaseModel):
    # formerly 'explanation'
    name = models.CharField(max_length=100, blank=True, help_text='backend')
    explanation = models.CharField(max_length=255, blank=True, help_text='frontend')
    # default_britpick_category = models.ForeignKey(
    #     "models.BritpickCategory",
    #     on_delete=models.PROTECT,
    #     blank=True,
    #     null=True,
    #     help_text=
    #         """
    #         May have specific categories it lends itself to
    #         (ex same idea/different word -> mandatory)
    #         This allows automatic assigning of types to Britpicks if they aren't manually specified
    #         """,
    # )

    def __str__(self):
        return self.name


class Reference(BaseModel):
    name = models.CharField(max_length=100, blank=True)
    url = models.URLField()
    main_reference = models.BooleanField(default=False)
    site_name = models.CharField(max_length=100, blank=True)
    page_name = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name

class Quote(BaseModel):
    quote = models.TextField(blank=True,)
    reference = models.ForeignKey("Reference", on_delete=models.PROTECT, related_name='quotes', null=True, blank=True,)
    words = models.ManyToManyField("Word", related_name='quotes', blank=True,)

    def __str__(self):
        s = '"' + self.quote[:25] + '..."'
        if self.words:
            s += ' [%s]' % ','.join(w.word for w in self.words.all())
        return s

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
        "BritpickCategory",
        models.PROTECT,
        related_name='britpicks',
        blank=True,
        null=True,
        default=2, #suggested
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
    )

    require_search_groups = models.ManyToManyField(
        "SearchGroup",
        blank=True,
        related_name='required_by',
    )

    words = models.ManyToManyField("Word", blank=True, related_name='britpicks')
    word_groups = models.ManyToManyField("WordGroup", blank=True, related_name='britpicks')

    topics = models.ManyToManyField("Topic", blank=True, related_name='britpicks')
    always_show_topic_names = models.BooleanField(
        default=False,
        help_text=
            """
                select if topic name needed to provide context
                (ex 'sports', 'cars', 'clothing')
            """,
    )


    references = models.ManyToManyField("Reference", blank=True, related_name='britpicks')







class SearchString(BaseModel):

    # foreign key - so that any duplicates have to be made with groups
    searched_by = models.ForeignKey("Britpick", on_delete=models.PROTECT, related_name='search_strings', blank=True, null=True)

    string = models.CharField(max_length=300)
    # options created from separate searchwords functions/regex wrapper to create pattern; ie preserve all words, preserve case, beginning of sentence, end of phrase, question, noun
    # inline - preserve word (#), markup, noun, dash


    # search patterns (verbose)
    # search patterns (trie)
    # _pattern = models.TextField(blank=True)
    #
    # @property
    # def name(self):
    #     s = self.string
    #     if self._name:
    #         s += ' (%s)' % self._name
    #     return s
    #
    # @property
    # def pattern(self):
    #     return self._pattern
    #
    # @pattern.setter
    # def pattern(self, value):
    #     self._pattern = value





class SearchGroup(BaseModel):
    """
    can use with things like idiot that could have multiple results based on dialect
    also use with things contexts to include/exclude (driving context, swimming context)
    """
    name = models.CharField(max_length=100, blank=True)
    search_strings = models.ManyToManyField("SearchString", blank=True, related_name='search_groups',)


class SearchVariables(BaseModel):
    # database-side representation of markup
    # can contain regex
    pass

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

    description = models.CharField(max_length=255, blank=True)

    # AND/OR GET DIALECT DYNAMICALLY THROUGH BRITPICK - make property???
    dialect = models.ForeignKey(
        "Dialect",
        models.PROTECT,
        related_name='words',
        blank=True,
        null=True,
    )
    category = models.ForeignKey(
        "BritpickCategory",
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



class WordGroup(BaseModel):
    words = models.ManyToManyField("Word", blank=True, related_name='groups',)















