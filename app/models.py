from django.db import models
from django.template.defaultfilters import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver

from picklefield.fields import PickledObjectField

import re

import htmlutils
import searchwords
import fetchreference
from __init__ import *



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
    name = models.CharField(max_length=300, blank=True, null=True)

    sitename = models.CharField(max_length=100, blank=True, null=True)
    pagename = models.CharField(max_length=300, blank=True, null=True)

    # adminname = models.CharField(max_length=100, blank=True, null=True)

    url = models.URLField(blank=True, null=True)
    mainreference = models.BooleanField(default=False)
    # minorreference = models.BooleanField(default=False)

    @property
    def link(self) -> str:
        s = '<a href="' + self.url + '"><img class="external-link" src="/static/flag.png">'
        s += self.liststringorurl
        s += '</a>'
        return s

    @property
    def inlinestring(self) -> str:
        s = self.pagename
        if self.sitename:
            s += ' (' + self.sitename + ')'
        return s

    @property
    def liststring(self) -> str:
        if self.pagename == self.sitename:
            s = self.pagename
        elif self.pagename and self.sitename:
            s = self.sitename + ' - ' + self.pagename
        elif self.pagename:
            s = self.pagename
        elif self.sitename:
            s = self.sitename
        else:
            s = 'link'

        return s

    @property
    def liststringorurl(self) -> str:
        if self.pagename and self.sitename:
            s = self.sitename + ' - ' + self.pagename
        elif self.pagename:
            s = self.pagename
        else:
            s = self.url

        return s

    @property
    def adminliststring(self) -> str:
        return self.liststring[:50]


    def __str__(self):

        # s = str(self.id) + ' | ' + self.liststring + ' | ' + self.url
        # if self.adminname:
        #     s = self.adminname
        # else:
        #     s = self.name
        # s += ' [' + str(self.pk) + ']'
        return self.name

    def save(self, *args, **kwargs):
        if not self.pagename and not self.sitename:
        # if True:
            pagetitle = fetchreference.fetchreferencetitle(self.url)
            print()
            print(pagetitle)

            if 'error' in pagetitle.lower():
                self.pagename = pagetitle

            else:
                splittitle = []

                # page is listed first
                for divider in [' | ', ' · ', ' : ', ' - ', '—', '--',]:
                    if len(splittitle) > 1:
                        break

                    splittitle = pagetitle.split(divider)
                    if len(splittitle) > 2:
                        self.pagename = splittitle.pop(0).strip()
                        splittitle.reverse()
                        self.sitename = ' - '.join(s.strip() for s in splittitle)
                        break
                    elif len(splittitle) > 1:
                        self.pagename = splittitle[0].strip()
                        self.sitename = splittitle[1].strip()
                        break

                # page is listed second
                for divider in [': ']:
                    if len(splittitle) > 1:
                        break

                    splittitle = pagetitle.split(divider, 1)
                    if len(splittitle) > 1:
                        self.pagename = splittitle[1].strip()
                        self.sitename = splittitle[0].strip()
                        break

                if len(splittitle) < 2:
                    self.pagename = pagetitle

                if 'reddit' in self.url.lower():
                    self.sitename = 'r/' + self.sitename

                self.name = self.liststring

        if not self.name:
            self.name = self.liststring

        super().save(*args, **kwargs)

    class Meta:
        ordering = ['sitename', 'pagename',]


class Topic(models.Model):
    active = models.BooleanField(default=True)
    maintopic = models.BooleanField(default=True)


    name = models.CharField(max_length=100, unique=True)
    text = models.TextField(blank=True, null=True, help_text='use [1] (where 1 is reference pk) to add reference link; [] will add [link] and {} will add title text only, <1:quoted text> will add quoted text')
    relatedtopics = models.ManyToManyField("self", symmetrical=True, blank=True, help_text='back references are automatically created')
    references = models.ManyToManyField(Reference, blank=True)
    minorreferences = models.ManyToManyField(Reference, blank=True, related_name='minor_references')

    slug = models.CharField(max_length=100)


    @property
    def getslug(self) -> str:
        s = slugify(self.name)
        return s

    @property
    def linkhtml(self) -> str:
        s = htmlutils.getlinkhtml(urlname='topic', urlkwargs={'topicslug':self.slug}, text=self.name)
        return s


    @property
    def hascontent(self) -> bool:
        if len(self.text) > 0:
            return True
        if self.references.count() > 0:
            return True
        return False

    def __str__(self):
        s = self.name
        if self.maintopic:
            s = '*' + s
        if not self.hascontent:
            s += ' (EMPTY)'
        if not self.active:
            s += ' (INACTIVE)'
        return s



    def save(self, *args, **kwargs):
        self.text = htmlutils.replacecurlyquotes(self.text)

        if 'http' in self.text:
            text = self.text
            pattern = r"(?<=[\<\[])(?:(?P<name>.+)\:|)(?P<url>https?\:\/\/[^\s]+)(?=[\:\]])"
            for match in re.finditer(pattern, self.text):
                m = match.groupdict()

                if not m['url']:
                    continue
                try:
                    reference = Reference.objects.get(url=m['url'])
                except ObjectDoesNotExist:
                    reference = Reference(url=m['url'])

                    if m['name']:
                        reference.name = m['name']

                    reference.save()

                text = text.replace(match.group(0), str(reference.pk))

            self.text = text

        self.slug = slugify(self.name)

        super().save(*args, **kwargs)

        # test
        s = ''

    class Meta:
        ordering = ['name']



#TODO: inline replacement, explanation before clarification; add link if only has topic

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
    verified = models.BooleanField(default=True)

    category = models.ForeignKey(ReplacementCategory, default=ReplacementCategory.objects.get(name=DEFAULT_REPLACEMENTTYPE).pk, on_delete=models.CASCADE)

    searchstrings = models.TextField(blank=True, null=True,
                                     help_text="Add multiple words on separate lines; dash in word can be dash, space or no space;")

    excludedstrings = models.TextField(blank=True, null=True,
                                     help_text="Add phrases to exclude (example - searchstring 'shirt', excludedstring 't-shirt')")

    suggestreplacement = models.CharField(blank=True, null=True, max_length=200, help_text="for the strongest suggestion")
    considerreplacements = models.TextField(blank=True, null=True, help_text="for less strong suggestions")
    clarification = models.TextField(blank=True, null=True, help_text="can be used alone to clarify meaning (such as 1st floor -> ground floor) or along with the above to explain replacement")
    explanations = models.ManyToManyField(ReplacementExplanation, blank=True)
    topics = models.ManyToManyField(Topic, blank=True)

    references = models.ManyToManyField(Reference, blank=True)

    searchwords = PickledObjectField(null=True)
    excludepatterns = PickledObjectField(null=True)

    # TODO: change admin form to have checkboxes (like for topic)

    @property
    def title(self) -> str:
        s = self.searchwordlist[0]
        s = htmlutils.searchwordformat(s, title=True, markup=htmlutils.Delete_Markup, replacedashes=True)
        if self.replacementslist:
            s += ' 🡆 '
            s += htmlutils.titlecase(self.replacementslist[0])

        return s

    @property
    def searchwordlist(self) -> list:
        wordlist = [w.strip() for w in self.searchstrings.split('\r\n') if w.strip() != '']
        return wordlist

# TODO: exclude compound words (-); see 598, ill catches ill-mannered

    # @property
    # def searchwordstring(self) -> str:
    #     wordlist = self.searchwordlist
    #     for i, w in enumerate(wordlist):
    #         w = htmlutils.searchwordformat(w, markup = htmlutils.Explain_Markup_Verbose)
    #         wordlist[i] = w
    #     wordstring = ', '.join(wordlist)
    #     return wordstring

    @property
    def excludedwordlist(self) -> list:
        try:
            wordlist = [w.strip() for w in self.excludedstrings.split('\r\n') if w.strip() != '']
        except AttributeError:
            wordlist = []
        return wordlist

    # @property
    # def excludedwordstring(self) -> str:
    #     wordlist = self.excludedwordlist
    #     for i, w in enumerate(wordlist):
    #         w = htmlutils.searchwordformat(w, markup = htmlutils.Explain_Markup_Verbose)
    #         wordlist[i] = w
    #     wordstring = ', '.join(wordlist)
    #     return wordstring

    @property
    def replacementslist(self) -> list:
        wordlist = []
        if self.suggestreplacement:
            wordlist.append(self.suggestreplacement)
        wordlist.extend([w for w in self.considerreplacements.split('\r\n') if w.strip() != ''])
        return wordlist

    # @property
    # def replacementsstring(self) -> str:
    #     wordlist = self.replacementslist
    #     wordstring = ', '.join(wordlist)
    #     return wordstring

    @property
    def considerreplacementlist(self) -> list:
        wordlist = [w for w in self.considerreplacements.split('\r\n') if w.strip() != '']
        return wordlist

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


    @property
    def clarifyexplanationhtml(self) -> str or bool:
        # get strings from clarification and explanations
        # s = ''

        w = []
        w.extend([o.text for o in self.explanations.all()])
        w.extend([w for w in self.clarification.split('\r\n') if w.strip() != ''])


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

    def createpatterns(self):
        self.searchwords = [] # reset field first
        for searchwordstring in self.searchwordlist:
            searchword = searchwords.getwordpattern(searchwordstring)
            self.searchwords.append(searchword)

        self.excludepatterns = []
        if self.excludedstrings:
            for excludewordstring in [w for w in self.excludedstrings.split('\r\n') if w.strip() != '']:
                excludepattern = searchwords.getwordpattern(excludewordstring)['pattern']
                self.excludepatterns.append(excludepattern)

    def save(self, *args, **kwargs):
        # if it's the non-default dialect, unless the words are manually marked as something different
        # assign them to 'informal'
        if self.dialect.name != DEFAULT_DIALECT and self.category.name == DEFAULT_REPLACEMENTTYPE:
            self.category = ReplacementCategory.objects.get(name=DEFAULT_NONDEFAULTDIALECT_REPLACEMENTTYPE)

        self.createpatterns()

        super().save(*args, **kwargs)



    def __str__(self):
        return self.objectstring



