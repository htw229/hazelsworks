from django.db import models

class BritpickDialects(models.Model):
    name = models.CharField(max_length=100, primary_key=True)

    def __str__(self):
        return self.name
#
class BritpickFindReplace(models.Model):
    dialect = models.ForeignKey(BritpickDialects, default="British (Generic)", on_delete=models.CASCADE)
    dialogue = models.BooleanField(default=False)

    searchwords = models.TextField(blank=True, null=True, help_text="Add multiple words on separate lines")
    directreplacement = models.CharField(blank=True, null=True, max_length=200, help_text="for straightforward required replacements such as apartment -> flat")
    considerreplacement = models.TextField(blank=True, null=True, help_text="for optional replacements such as cool -> brilliant")
    clarifyreplacement = models.TextField(blank=True, null=True, help_text="can be used alone to clarify meaning (such as 1st floor -> ground floor) or along with the above to explain replacement")
    americanslang = models.BooleanField(default=False, help_text="American slang not generally used in Britain")


    active = models.BooleanField(default=True)

    @property
    def searchwordlist(self) -> list:
        wordlist = [w for w in self.searchwords.split('\r\n') if w.strip() != '']
        return wordlist

    @property
    def considerreplacementlist(self):
        wordlist = [w for w in self.considerreplacement.split('\r\n') if w.strip() != '']
        return wordlist

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

    def __str__(self):
        return self.objectstring




