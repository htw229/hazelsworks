from django.db import models
from django.urls import reverse

# custom model
class BaseModel(models.Model):
    name = models.CharField(max_length=100, blank=True)
    active = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Suggestion(models.Model):
    # can use for back-end notes and front-end suggestions
    text = models.TextField()
    britpick = models.ForeignKey("Britpick", on_delete=models.CASCADE, related_name='suggestions', blank=True)
    topic = models.ForeignKey("Topic", on_delete=models.CASCADE, related_name='suggestions', blank=True)


# Create your models here.
class Dialect(BaseModel):
    # name = models.CharField(max_length=100)
    # active = models.BooleanField(default=True)
    default = models.BooleanField(default=False)
    description = models.TextField(blank=True)



class Category(BaseModel):
    """ mandatory, suggested, uncommon, informal, slang """
    dialogue = models.BooleanField(default=False)
    description = models.TextField(blank=True)


class Explanation(BaseModel):
    # name = models.CharField(max_length=100)
    # active = models.BooleanField(default=True)
    display_text = models.TextField(blank=True)

    # def __str__(self):
    #     return self.name


class Reference(BaseModel):
    # name = models.CharField(max_length=300, blank=True)
    # active = models.BooleanField(default=True)
    main_reference = models.BooleanField(default=False)

    url = models.URLField()
    site_name = models.CharField(max_length=100, blank=True)
    page_name = models.CharField(max_length=300, blank=True)


class Topic(BaseModel):
    """
    topic is a way to display a large amount of text, links, etc with large numbers of relationships
    """

    WORD = 'W'
    TOPIC_TYPES = (
        (WORD, 'word'),
    )

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
    category = models.ForeignKey("Category", models.CASCADE, related_name='britpicks', blank=True, null=True)
    # For category, if none chosen, generate on the fly from replacement if needed for filtering

    searches = models.ManyToManyField("Search", blank=True)


    # Word m2m
    # Explanation m2m
    # Topic m2m
    # Reference m2m

    # details text


class Search(BaseModel):
    """
    tie together search constructors
    (slightly more complex through field)
    """

    # SEARCH FOR
    search_string = models.ForeignKey("SearchString", on_delete=models.CASCADE, blank=True, null=True, related_name='searched_by')
    search_group = models.ForeignKey("SearchGroup", on_delete=models.CASCADE, blank=True, null=True, related_name='searched_by')

    # CONTEXT
    exclude_nearby_strings = models.ManyToManyField("SearchString", blank=True, related_name='excluded_by')
    exclude_nearby_groups = models.ManyToManyField("SearchGroup", blank=True, related_name='excluded_by')
    require_nearby_strings = models.ManyToManyField("SearchString", blank=True, related_name='required_by')
    require_nearby_groups = models.ManyToManyField("SearchGroup", blank=True, related_name='required_by')



class SearchString(BaseModel):

    # could potentially have single search with multiple britpicks - "grade" - included in long list of words that link to education topic; also included in britpick to change to 'level' or 'mark'; also in britpicks with different dialects
    # having link to single record allows better detection of duplicates/conflicts
    # word like "piss off" - searchstring "piss off" linked to word- piss off, topic- piss,

    # name = models.CharField(max_length=100) # optional
    string = models.CharField(max_length=300)
    # options created from separate searchwords functions/regex wrapper to create pattern; ie preserve all words, preserve case, beginning of sentence, end of phrase, question, noun
    # inline - preserve word (#), markup, noun, dash

    # search patterns (verbose)
    # search patterns (trie)
    pattern = models.CharField(max_length=300)


class SearchGroup(BaseModel):
    """
    can use with things like idiot that could have multiple results based on dialect
    also use with things contexts to include/exclude (driving context, swimming context)
    """
    # name = models.CharField(max_length=100)
    # m2m SearchString

class SearchVariables(BaseModel):
    # database-side representation of markup
    # can contain regex
    pass

class Word(BaseModel):
    pass
    # word = models.CharField(max_length=100)
    # category (fk) optional
    # example quotes - quote + reference

    # make unique? or if not unique make word topic to differentiate (if not unique, then may have quote examples that don't work well)
    # or make unique back-end word such as ("grade (noun)" and "grade (verb)") with displaying both as "grade"

    # word topic (fk)
    # topics (m2m)

class WordGroup(BaseModel):
    pass
    # name = models.CharField(max_length=100)
    # Word m2m

class Example(BaseModel):
    text = models.TextField(blank=True)
    # Reference fk
    # Word m2m


class Spelling(models.Model):
    find_string = models.CharField(max_length=100)
    replace_string = models.CharField(max_length=100)













