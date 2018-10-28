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

    def save(self, *args, **kwargs):
        if not self.name or not self.adminname:
            title = self.name

            if not title:
                title = fetchreference.fetchreferencetitle(self.url)

            s = []
            for divider in ['-', '|', '·', ':']:
                s = title.split(' ' + divider + ' ')

                if len(s) > 1:
                    break

            # s = title.split(' - ')
            # if not len(s) > 1:
            #     s = title.split(' | ')
            # if not len(s) > 1:
            #     s = title.split(' · ')
            try:
                pagename = s[0].strip()
                sitename = s[1].strip()

                name = pagename + ' (' + sitename + ')'
                adminname = sitename + ' -  ' + pagename

                self.adminname = sitename + ' - ' + pagename
            except IndexError:
                name = title.strip()
                adminname = title.strip()

            if not self.name:
                self.name = name

            if not self.adminname and self.name != adminname:
                self.adminname = adminname


            # if not self.adminname:
            #     s = self.name.split(' - ')
            #     if not len(s) > 1:
            #         s = self.name.split(' | ')
            #     try:
            #         sitename = s[1]
            #         pagename = s[0]
            #         self.adminname = sitename + ' - ' + pagename
            #     except IndexError:
            #         pass

        super().save(*args, **kwargs)

    class Meta:
        ordering = ['adminname']


class Topic(models.Model):
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
        s = htmlutils.getlinkhtml(urlname='topic', urlkwargs={'topicslug':self.slug}, text=self.name)
        return s


    @property
    def hascontent(self) -> bool:
        if len(self.text) > 0:
            return True
        if self.citations.count() > 0:
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
        super().save(*args, **kwargs)


    class Meta:
        ordering = ['name']


# must be done after save to successfully add m2m relationship
# @receiver(post_save, sender = Topic, dispatch_uid='update_citations_on_save')
# def update_citations_on_save(sender, **kwargs):
#     topic = kwargs['instance']
#     text = topic.text
#
#     if 'http' in topic.text:
#
#         pattern = r"(?<=[\<\[])(?:(?P<name>.+)\:|)(?P<url>https?\:\/\/[^\s]+)(?=[\:\]])"
#         for match in re.finditer(pattern, topic.text):
#             m = match.groupdict()
#
#             if not m['url']:
#                 continue
#             try:
#                 reference = Reference.objects.get(url=m['url'])
#             except ObjectDoesNotExist:
#                 reference = Reference(url=m['url'])
#
#                 if m['name']:
#                     reference.name = m['name']
#
#                 reference.save()
#
#             text = text.replace(match.group(0), str(reference.pk))
#
#         Topic.objects.filter(pk=topic.pk).update(text=text)
            # topic.citations.add(reference)



    # citationpattern = r"[\[\{](?P<pk>\d+)[\}\]]"
    #
    # for match in re.finditer(citationpattern, topic.text):
    #     pk = match.groupdict()['pk']
    #     try:
    #         reference = Reference.objects.get(pk=pk)
    #         if reference not in topic.citations.all():
    #             Topic.objects.get(pk=65).citations.add(reference)
    #             # text += 'adding' + str(reference)
    #             # text += str(topic.citations.all())
    #     except ObjectDoesNotExist:
    #         continue
    #
    # text += 'BEFORE SAVE:' + str(Topic.objects.get(pk=topic.pk).citations.all())
    #
    # # use instead of 'save' to prevent loop
    # Topic.objects.filter(pk=topic.pk).update(text=text)
    #
    # text += 'AFTER SAVE:' + str(Topic.objects.get(pk=topic.pk).citations.all())

    # Topic.objects.filter(pk=topic.pk).update(text=text)


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

    # searchwords = models.TextField(blank=True, null=True)
    # excludepatterns = models.TextField(blank=True, null=True)
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

    @property
    def searchwordstring(self) -> str:
        wordlist = self.searchwordlist
        for i, w in enumerate(wordlist):
            w = htmlutils.searchwordformat(w, markup = htmlutils.Explain_Markup_Verbose)
            wordlist[i] = w
        wordstring = ', '.join(wordlist)
        return wordstring

    @property
    def excludedwordlist(self) -> list:
        try:
            wordlist = [w.strip() for w in self.excludedstrings.split('\r\n') if w.strip() != '']
        except AttributeError:
            wordlist = []
        return wordlist

    @property
    def excludedwordstring(self) -> str:
        wordlist = self.excludedwordlist
        for i, w in enumerate(wordlist):
            w = htmlutils.searchwordformat(w, markup = htmlutils.Explain_Markup_Verbose)
            wordlist[i] = w
        wordstring = ', '.join(wordlist)
        return wordstring

    @property
    def replacementslist(self) -> list:
        wordlist = []
        if self.suggestreplacement:
            wordlist.append(self.suggestreplacement)
        wordlist.extend([w for w in self.considerreplacements.split('\r\n') if w.strip() != ''])
        return wordlist

    @property
    def replacementsstring(self) -> str:
        wordlist = self.replacementslist
        wordstring = ', '.join(wordlist)
        return wordstring

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



