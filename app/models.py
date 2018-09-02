from django.db import models

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
    displayname = models.CharField(max_length=100, blank=True, null=True)
    url = models.URLField(blank=True, null=True)

    @property
    def link(self) -> str:
        s = '<a href="' + self.url + '">'
        s += self.name
        s += '</a>'
        return s

    def __str__(self):
        if self.displayname:
            s = self.displayname
        else:
            s = self.name
        s += ' [' + str(self.pk) + ']'
        return s


class ReplacementTopic(models.Model):
    name = models.CharField(max_length=100)
    text = models.TextField(blank=True, null=True, help_text='use [1] (where 1 is citation pk) to add citation link')
    citations = models.ManyToManyField(Citation, blank=True)

    # TODO: inside text field can have citation markup to create direct link for attributing; maybe if link already used in outputtext to only have it once?

    def __str__(self):
        return self.name

class BritpickFindReplace(models.Model):
    dialect = models.ForeignKey(BritpickDialects, default="British", on_delete=models.CASCADE)
    active = models.BooleanField(default=True)

    mandatory = models.BooleanField(default=False)
    dialogue = models.BooleanField(default=False, help_text="limit to character's speech")
    slang = models.BooleanField(default=False, help_text="similar to dialogue but may be crude or grammatically incorrect")

    searchwords = models.TextField(blank=True, null=True, help_text="Add multiple words on separate lines")

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



