from .models import BritpickFindReplace, BritpickDialects
import re

suffixes = [
    's',
    'es',
    "'s",
    'ed',
    'ly',
    'ing',
]

def britpick(text, dialectname):
    # dialect = BritpickDialects.objects.get(pk = dialectname)

    findreplaceobjects = BritpickFindReplace.objects.filter(dialect = dialectname)
    searches = []
    markupdict = {}

    # create searches such that ['searchstring', BritpickFindReplace obj]
    for o in findreplaceobjects:
        for s in o.searchwordlist:
            searches.append([s,o])

    # add suffixes to searchwords; do this after all original words added so that they take lower priority
    originalsearches = [s for s in searches]
    for search in originalsearches:
        for suffix in suffixes:
            searches.append([search[0] + suffix, search[1]])

    # substitute every instance of 'searchstring' with '{f1}'
    # create markup dict items so that {'{f1}': 'original word [replacement text]',}
    for i, search in enumerate(searches):
        markup = 'f' + str(i)
        text = re.sub(r'\b' + search[0] + r'\b',  '{' + markup + '}', text)
        replacetext = addfoundword(search[0]) + ' ' + createreplacetext(search[1])

        markupdict.update({markup: replacetext})

    # replace every instance of {f1} with 'original word [replacement text]'
    outputtext = text.format(**markupdict)

    # create line breaks
    outputtext = outputtext.replace('\r\n', '<br />')

    return outputtext


def createreplacetext(obj):
    s = ''
    if obj.directreplacement:
        s += addspan(obj.directreplacement, 'directreplacement')
    if obj.considerreplacement:
        s += 'consider: '
        for w in obj.considerreplacementlist:
            s += addspan(w, 'considerreplacement')
    if obj.clarifyreplacement:
        s += addspan(obj.clarifyreplacement, 'clarifyreplacement')
    if obj.americanslang:
        s += addspan('phrase may not be used in britain', 'americanslang')

    return addspan(s, 'replacement', '[', ']')

def addfoundword(text):
    s = addspan(text, 'foundword')
    return s

def adddirectreplacement(text):
    s = addspan(text, 'directreplacement')
    return s

def addspan(text, cssclass, wrapperstart = '', wrapperend = ''):
    if not text:
        return ''
    s = "<span class='"
    s += cssclass
    s += "'>"
    s += wrapperstart + text + wrapperend
    s += '</span>'
    return s
