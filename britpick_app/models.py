from django.db import models
from django.urls import reverse

# britpick_app model
class BaseModel(models.Model):
    _name = models.CharField(max_length=100, blank=True)
    _display_name = models.CharField(max_length=100, blank=True)
    _description = models.TextField(blank=True)
    _active = models.BooleanField(default=True)
    _verified = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    @property
    def name(self):
        """ for back-end display purposes """
        if self._name:
            return self._name
        elif self._display_name:
            return self._display_name
        else:
            return self.name_model_pk

    @property
    def name_model_pk(self):
        return type(self).__name__ + ' [%s]' % str(self.pk)

    @property
    def name_verbose(self):
        s = self.name_model_pk
        if self._name:
            s += ' ' + self._name
        if self._display_name:
            s += ' ' + '(%s)' % self._display_name
        return s

    @property
    def display_name(self):
        """ for front-end display purposes"""
        if self._display_name:
            return self._display_name
        else:
            return self.name

    @property
    def display_name_verbose(self):
        return self.display_name + ': ' + self.description

    @property
    def description(self):
        return self._description

    @property
    def active(self):
        return self._active

    @property
    def verified(self):
        return self._verified

    def __str__(self):
        return self.name


# class Suggestion(models.Model):
#     # can use for back-end notes and front-end suggestions
#     text = models.TextField()
#     britpick = models.ForeignKey("Britpick", on_delete=models.CASCADE, related_name='suggestions', blank=True)
#     topic = models.ForeignKey("Topic", on_delete=models.CASCADE, related_name='suggestions', blank=True)



class Dialect(BaseModel):
    # name = models.CharField(max_length=100)
    # active = models.BooleanField(default=True)
    default = models.BooleanField(default=False)
    spoken = models.BooleanField(default=False)
    # description = models.TextField(blank=True)

class BritpickType(BaseModel):
    """ mandatory, suggested, uncommon, informal, slang """
    # name = models.CharField(max_length=100, blank=True)
    # active = models.BooleanField(default=True)
    # details = models.TextField(blank=True)

class BritpickCategory(BaseModel):
    # formerly 'explanation'
    # name = models.CharField(max_length=100, blank=True)
    # active = models.BooleanField(default=True)
    default_britpick_type = models.ForeignKey(
        "BritpickType",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='categories',
        help_text=
            """
            Categories may have specific types they lend themselves to
            (ex same idea/different word -> mandatory)
            This allows automatic assigning of types to Britpicks if they aren't manually specified
            """,
    )






class Reference(BaseModel):
    # name = models.CharField(max_length=300, blank=True)
    # active = models.BooleanField(default=True)
    main_reference = models.BooleanField(default=False)

    url = models.URLField()
    site_name = models.CharField(max_length=100, blank=True)
    page_name = models.CharField(max_length=300, blank=True)


class Quote(BaseModel):
    # name = models.CharField(max_length=300, blank=True)
    # active = models.BooleanField(default=True)

    text = models.TextField(blank=True)
    reference = models.ForeignKey("Reference", on_delete=models.CASCADE, related_name='quotes', null=True, blank=True,)


class Topic(BaseModel):
    """
    topic is a way to display a large amount of text, links, etc with large numbers of relationships
    """

    WORD = 'W'
    TOPIC_TYPES = (
        (WORD, 'word'),
    )

    dialect = models.ForeignKey(
        "Dialect",
        models.CASCADE,
        related_name='topics',
        blank=True,
        null=True,
        help_text=
            """
            If dialect is selected, all words/britpicks with this dialect will be automatically linked
            """,
    )

    # add get_absolute_url() for view on site to be enabled on edit page

    # name = models.CharField(max_length=100, unique=True)
    # active = models.BooleanField(default=True)
    # main_topic = models.BooleanField(default=True)
    # show_in_topics_list = models.BooleanField(default=True)
    # word = models.BooleanField(default=False)
    #
    # text = models.TextField(blank=True)
    # # parent_topic
    # related_topics = models.ManyToManyField("self", symmetrical=True, blank=True)
    # references = models.ManyToManyField(Reference, blank=True)
    #
    # # needed or not?
    # # minor_references = models.ManyToManyField(Reference, blank=True, related_name='minor_references')
    #
    # slug = models.CharField(max_length=100, blank=True)

    # def get_absolute_url(self):
        # return reverse('people.views.details', args=[str(self.id)])






class Britpick(BaseModel):
    """
    ties together things to search for
    with links to replacement words, topics, references, explanation
    and a field for explanation

    for use in-text and in showing relationships in a topic
    """

    verified = models.BooleanField(default=True)

    dialect = models.ForeignKey("Dialect", models.CASCADE, related_name='britpicks', default=Dialect.objects.get(default=True).pk)
    type = models.ForeignKey("BritpickType", models.CASCADE, related_name='britpicks', blank=True, null=True)
    categories = models.ManyToManyField("BritpickCategory", blank=True, related_name='britpicks')

    # search_strings -> from SearchString fk
    search_groups = models.ManyToManyField("SearchGroup", blank=True, related_name='britpicks')

    words = models.ManyToManyField("Word", blank=True, related_name='britpicks')
    word_groups = models.ManyToManyField("WordGroup", blank=True, related_name='britpicks')

    topics = models.ManyToManyField("Topic", blank=True, related_name='britpicks')
    always_show_topic_names = models.BooleanField(
        default=False,
        help_text=
            """
                if you want topics to provide context
                ex 'sports', 'cars', 'clothing'
            """,
    )


    references = models.ManyToManyField("Reference", blank=True, related_name='britpicks')

    details = models.TextField(blank=True)



class SearchString(BaseModel):
    OPTIONS = (('1', 'one'),)

    britpick = models.ForeignKey("Britpick", on_delete=models.CASCADE, related_name='search_strings',)

    string = models.CharField(max_length=300)
    # options created from separate searchwords functions/regex wrapper to create pattern; ie preserve all words, preserve case, beginning of sentence, end of phrase, question, noun
    # inline - preserve word (#), markup, noun, dash


    # search patterns (verbose)
    # search patterns (trie)
    pattern = models.CharField(max_length=300, blank=True)

    def __str__(self):
        if self.name:
            return self.name
        else:
            return self.string

class SearchGroup(BaseModel):
    """
    can use with things like idiot that could have multiple results based on dialect
    also use with things contexts to include/exclude (driving context, swimming context)
    """

    search_strings = models.ManyToManyField("SearchString", blank=True, related_name='search_groups',)


class SearchVariables(BaseModel):
    # database-side representation of markup
    # can contain regex
    pass

class Word(BaseModel):
    """
    name = unique ('Grade (noun)')
    word = not unique ('grade')
    """
    word = models.CharField(max_length=200)
    dialect = models.ForeignKey(
        "Dialect",
        models.CASCADE,
        related_name='words',
        blank=True,
        null=True,
    )
    britpick_type = models.ForeignKey(
        "BritpickType",
        models.CASCADE,
        related_name='words',
        blank=True,
        null=True,
        help_text=
            """
            For selecting 'slang' or 'informal'.
            If britpick does not have type, then selection here will determine britpick type. Can also be used to only display certain results (ie skip slang/informal results that aren't in dialogue or if not wanted).
            """,
    )

    quotes = models.ManyToManyField("Quote", blank=True, related_name='words',)
    word_topic = models.ForeignKey("Topic", on_delete=models.CASCADE, related_name='words', blank=True, null=True,)
    related_topics = models.ManyToManyField(
        "Topic",
        related_name='related_words',
        blank=True,
        help_text=
            """
                If it's the word that's the main point (ie insults; 'slag') then select topic here.
                But if it's the britpick that's the main point (ie kitchen; counter -> worktop) then topic should be linked in britpick.
            """,
    )



class WordGroup(BaseModel):
    words = models.ManyToManyField("Word", blank=True, related_name='groups',)




# class Spelling(models.Model):
#     find_string = models.CharField(max_length=100)
#     replace_string = models.CharField(max_length=100)













