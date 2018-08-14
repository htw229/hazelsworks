from .models import BritpickFindReplace
import re

suffixes = [
    's',
    'es',
    "'s",
    'ed',
    'ly',
    'ing',
]

def britpick(inputtext = 'here is a whale standing next to the blue lamppost'):
    outputtext = ''

    # iterate through search terms
    # when found, replace with {f1}, f1 = item number in searches
    text = inputtext

    findreplaceobjects = BritpickFindReplace.objects.all()
    searches = []
    markupdict = {}

    # create searches such that ['searchstring', BritpickFindReplace obj]
    for o in findreplaceobjects:
        for s in o.searchwordlist:
            searches.append([s,o])

    originalsearches = [s for s in searches]
    for search in originalsearches:
        for suffix in suffixes:
            searches.append([search[0] + suffix, search[1]])


    for i, search in enumerate(searches):
        markup = 'f' + str(i)
        # text = text.replace(search[0], '{' + markup + '}')

        text = re.sub(r'\b' + search[0] + r'\b',  '{' + markup + '}', text)

        replacetext = addfoundword(search[0]) + ' ' + createreplacetext(search[1])

        markupdict.update({markup: replacetext})

    outputtext = text.format(**markupdict)




    # findreplacelist = [
    #     ('whale', 'elephant'),
    #     ('lamppost', 'sidewalk'),
    #     ('blue', 'green'),
    # ]
    #
    # placeholderdict = {}
    #
    # t = inputtext
    # placeholdertable = {}
    # n = 0
    #
    # for i, replacement in enumerate(findreplacelist):
    #     print(i, replacement)
    #     t = t.replace(replacement[0], '{' + 'r' + str(i) + '}')
    #     print(t)
    #     markup = 'r' + str(i)
    #     placeholderdict.update({markup: addfoundword(replacement[0]) + ' ' + adddirectreplacement(replacement[1])})

    # t = t.format(**placeholderdict)


    # s = 'whale'
    #
    # t = inputtext.replace(s, '{f13}')
    #
    # foundword = addfoundword('whale')
    # replacement = adddirectreplacement('emergency')
    # newstring = foundword + ' ' + replacement
    # markups = { 'f13': newstring}
    #
    # outputtext = t.format(**markups)

    # outputtext = inputtext + adddirectreplacement('whale')

    # outputtext = text

    return outputtext


def createreplacetext(obj):
    s = '['
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
    s += ']'

    return s

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
