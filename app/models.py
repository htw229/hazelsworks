from django.db import models
from django.template.defaultfilters import slugify

from .htmlutils import getlinkhtml
import htmlutils
from appsettings import *
# import appsettings as appsettingstest

class Dialect(models.Model):
    name = models.CharField(max_length=100, primary_key=True)

    def __str__(self):
        return self.name

class ReplacementExplanation(models.Model):
    name = models.CharField(max_length=100)
    text = models.TextField(blank=True, null=True)


    def __str__(self):
        return self.name


class Reference(models.Model):
    name = models.CharField(max_length=300)
    adminname = models.CharField(max_length=100, blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    mainreference = models.BooleanField(default=False)

    @property
    def link(self) -> str:
        s = '<a href="' + self.url + '"><img class="external-link" src="/static/flag.png">'
        s += self.name
        s += '</a>'
        return s

    def __str__(self):
        if self.adminname:
            s = self.adminname
        else:
            s = self.name
        s += ' [' + str(self.pk) + ']'
        return s

    class Meta:
        ordering = ['adminname']


class ReplacementTopic(models.Model):
    active = models.BooleanField(default=True)
    maintopic = models.BooleanField(default=True)

    name = models.CharField(max_length=100)
    text = models.TextField(blank=True, null=True, help_text='use [1] (where 1 is citation pk) to add citation link; [] will add [link] and {} will add title text only, <1:quoted text> will add quoted text')
    citations = models.ManyToManyField(Reference, blank=True)
    relatedtopics = models.ManyToManyField("self", symmetrical=True, blank=True, help_text='back references are automatically created')


    @property
    def slug(self) -> str:
        s = slugify(self.name)
        return s

    @property
    def linkhtml(self) -> str:
        s = getlinkhtml(urlname='topic', urlkwargs={'topicslug':self.slug}, text=self.name)
        return s

    # @property
    # def link(self) ->
    #
    #     return s

    @property
    def hascontent(self) -> bool:
        if len(self.text) > 0:
            return True
        if self.citations.count() > 0:
            return True
        return False

    # TODO: maybe if link already used in outputtext to only have it once?

    def __str__(self):
        s = self.name
        if self.maintopic:
            s = '*' + s
        if not self.hascontent:
            s += ' (EMPTY)'
        if not self.active:
            s += ' (INACTIVE)'
        return s

    class Meta:
        ordering = ['name']


class ReplacementCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    dialogue = models.BooleanField(default=False)

    def __str__(self):
        s = self.name
        return s

    class Meta:
        ordering = ['pk']

class Replacement(models.Model):
    dialect = models.ForeignKey(Dialect, default=DEFAULT_DIALECT, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)

    category = models.ForeignKey(ReplacementCategory, default=ReplacementCategory.objects.get(name=DEFAULT_REPLACEMENTTYPE).pk, on_delete=models.CASCADE)

    searchwords = models.TextField(blank=True, null=True, help_text="Add multiple words on separate lines; dash in word can be dash, space or no space;")

    suggestreplacement = models.CharField(blank=True, null=True, max_length=200, help_text="for the strongest suggestion")
    considerreplacements = models.TextField(blank=True, null=True, help_text="for less strong suggestions")
    clarification = models.TextField(blank=True, null=True, help_text="can be used alone to clarify meaning (such as 1st floor -> ground floor) or along with the above to explain replacement")
    explanations = models.ManyToManyField(ReplacementExplanation, blank=True)
    topics = models.ManyToManyField(ReplacementTopic, blank=True)

    # TODO: change admin form to have checkboxes (like for topic)
    # TODO: change search link BritpickFindReplace to Replacement so link to admin works

    @property
    def searchwordlist(self) -> list:
        wordlist = [w for w in self.searchwords.split('\r\n') if w.strip() != '']
        return wordlist

    @property
    def searchwordstring(self) -> str:
        s = ', '.join(self.searchwordlist)
        return s

    @property
    def longestsearchwordlength(self) -> int:
        return len(max(self.searchwordlist, key=lambda l: len(l)))

    @property
    def multiplereplacements(self) -> bool:
        if (self.suggestreplacement == '') or (len(self.considerreplacementlist) == 0):
            return False
        else:
            return True



    @property
    def replacementwordshtml(self) -> str or bool:
        w = []
        if self.suggestreplacement:
            w.append(r'<span class="word">' + self.suggestreplacement.strip() + r'</span>')
        if self.considerreplacementlist:
            w.extend([r'<span class="word">' + s + r'</span>' for s in self.considerreplacementlist])

        if len(w) == 0:
            return False

        s = ', '.join(w)
        s = htmlutils.addspan(s, 'wordwrapper')

        # if self.category.name != 'mandatory' and self.category.name != 'suggested':
        if self.category.name == 'slang':
            # s = r'<span class="considerstring">consider</span>: ' + s
            categorystring = self.category.name + ': '
            s = htmlutils.addspan(categorystring, 'categorystring') + s

        return s


#TODO: not treating dialogue correctly

    @property
    def clarifyexplanationhtml(self) -> str or bool:
        # get strings from clarification and explanations
        # s = ''

        w = [w for w in self.clarification.split('\r\n') if w.strip() != '']
        w.extend([o.text for o in self.explanations.all()])

        if len(w) == 0:
            return False

        s = '; '.join(w)
        s = htmlutils.addspan(s, 'explanation')

        return s

    @property
    def replacementhtml(self) -> str or bool:

        words = self.replacementwordshtml
        explanation = self.clarifyexplanationhtml

        if words and explanation:
            s = words + r' | ' + explanation
        elif words:
            s = words
        elif explanation:
            s = explanation
        else:
            return None

        s = htmlutils.addspan(s, 'replacement')

        # if s:
        #     s = '<span class="category-' + self.category.name + '">' + s + '</span>'

        return s






    @property
    def considerreplacementlist(self) -> list:
        wordlist = [w for w in self.considerreplacements.split('\r\n') if w.strip() != '']
        return wordlist

    @property
    def replacementwordsstring(self) -> str:
        if self.suggestreplacement:
            wordlist = [self.suggestreplacement]
        else:
            wordlist = []
        wordlist.extend(self.considerreplacementlist)
        s = ', '.join(wordlist)
        return s



    @property
    def objectstring(self) -> str:
        if self.suggestreplacement:
            directreplacement = self.suggestreplacement
        else:
            directreplacement = ''

        if self.clarification:
            clarifyreplacementexists = '+explanation'
        else:
            clarifyreplacementexists = ''


        s = ' '.join([
            str(self.pk),
            ': ',
            ', '.join(self.searchwordlist),
            '->',
            directreplacement,
            ', '.join(self.considerreplacementlist),
            clarifyreplacementexists,
            '(' + self.dialect.name + ')',
        ])
        return s

    @property
    def shortstring(self) -> str:
        wordlist = self.searchwordlist
        s = wordlist[0]
        if len(wordlist) == 1:
            return s
        else:
            return s + ' (+ ' + str(len(wordlist) - 1) + ')'


    def save(self, *args, **kwargs):
        # if it's the non-default dialect, unless the words are manually marked as something different
        # assign them to 'informal'
        if self.dialect.name != DEFAULT_DIALECT and self.category.name == DEFAULT_REPLACEMENTTYPE:
            self.category = ReplacementCategory.objects.get(name=DEFAULT_NONDEFAULTDIALECT_REPLACEMENTTYPE)

        super().save(*args, **kwargs)



    def __str__(self):
        return self.objectstring



