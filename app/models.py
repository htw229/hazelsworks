from django.db import models
from django.template.defaultfilters import slugify

from .htmlutils import getlinkhtml

class BritpickDialects(models.Model):
    name = models.CharField(max_length=100, primary_key=True)

    def __str__(self):
        return self.name

class ReplacementExplanation(models.Model):
    name = models.CharField(max_length=100)
    text = models.TextField(blank=True, null=True)


    def __str__(self):
        return self.name


class Citation(models.Model):
    name = models.CharField(max_length=300)
    adminname = models.CharField(max_length=100, blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    mainreference = models.BooleanField(default=False)

    @property
    def link(self) -> str:
        s = '<a href="' + self.url + '">'
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
    citations = models.ManyToManyField(Citation, blank=True)
    relatedtopics = models.ManyToManyField("self", blank=True, help_text='back references are included when this is displayed in html')


    @property
    def slug(self) -> str:
        s = slugify(self.name)
        return s

    @property
    def linkhtml(self) -> str:
        s = getlinkhtml(urlname='topic', urlkwargs={'topicslug':self.slug}, text=self.name)
        return s

    @property
    def allrelatedtopics(self) -> list:
        # returns all forward and back-referenced relatedtopics
        topics = list(self.relatedtopics.all())
        for t in ReplacementTopic.objects.all():
            if t not in topics:
                if self in t.relatedtopics.all():
                    topics.append(t)
        return topics

    @property
    def minorrelatedtopics(self) -> list:
        topics = self.allrelatedtopics
        minortopics = [t for t in topics if t.maintopic == False]
        return minortopics

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

class BritpickFindReplace(models.Model):
    dialect = models.ForeignKey(BritpickDialects, default="British", on_delete=models.CASCADE)
    active = models.BooleanField(default=True)

    mandatory = models.BooleanField(default=False)
    dialogue = models.BooleanField(default=False, help_text="limit to character's speech")
    slang = models.BooleanField(default=False, help_text="similar to dialogue but may be crude or grammatically incorrect")

    searchwords = models.TextField(blank=True, null=True, help_text="Add multiple words on separate lines; dash in word can be dash, space or no space;")

    directreplacement = models.CharField(blank=True, null=True, max_length=200, help_text="for straightforward required replacements such as apartment -> flat")
    considerreplacement = models.TextField(blank=True, null=True, help_text="for optional replacements such as cool -> brilliant")
    clarifyreplacement = models.TextField(blank=True, null=True, help_text="can be used alone to clarify meaning (such as 1st floor -> ground floor) or along with the above to explain replacement")
    replacementexplanations = models.ManyToManyField(ReplacementExplanation, blank=True)
    replacementtopics = models.ManyToManyField(ReplacementTopic, blank=True)

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
    def considerreplacementlist(self) -> list:
        wordlist = [w for w in self.considerreplacement.split('\r\n') if w.strip() != '']
        return wordlist

    @property
    def replacementwordsstring(self) -> str:
        if self.directreplacement:
            wordlist = [self.directreplacement]
        else:
            wordlist = []
        wordlist.extend(self.considerreplacementlist)
        s = ', '.join(wordlist)
        return s

    @property
    def clarifyreplacementstring(self) -> str:
        # get strings from clarifyreplacement text box
        s = ''

        if self.clarifyreplacement:
            s = s + ' / '.join([w for w in self.clarifyreplacement.split('\r\n') if w.strip() != ''])

        if self.replacementexplanations:
            # get strings from all objects
            explanationstrings = [o.text for o in self.replacementexplanations.all()]
            s = s + ' / '.join(explanationstrings)

        return s

    @property
    def objectstring(self) -> str:
        if self.directreplacement:
            directreplacement = self.directreplacement
        else:
            directreplacement = ''

        if self.clarifyreplacement:
            clarifyreplacementexists = '+explanation'
        else:
            clarifyreplacementexists = ''

        if self.dialogue:
            dialogueonly = "[DIALOGUE]"
        else:
            dialogueonly = ''

        s = ' '.join([
            str(self.pk),
            ': ',
            ', '.join(self.searchwordlist),
            '->',
            directreplacement,
            ', '.join(self.considerreplacementlist),
            clarifyreplacementexists,
            dialogueonly,
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

    def __str__(self):
        return self.objectstring



