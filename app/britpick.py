from .models import BritpickFindReplace, BritpickDialects
import re
import regex
from timeit import default_timer

# matchoption
matchoptions = {
    'SEARCH_ALL': '1',
    'SEARCH_DIALOGUE_ONLY': '2',
    'SEARCH_DIALOGUE_IF_SPECIFIED': '3',
}

matchoptionsstrings = {
    '1': 'Smart search',
    '2': 'Search dialogue only',
    '3': 'Search all text',
}

numberstrings = ['\d+', '\d+st', '\d+nd', '\d+th', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth', 'tenth', 'eleventh', 'twelfth', 'thirteenth', 'fourteenth', 'fifteenth', 'sixteenth', 'seventeenth', 'eighteenth', 'nineteenth', 'twentieth', 'thirtieth', 'fourtieth', 'fiftieth', 'hundredth', 'thousandth', 'millionth']

monthstrings = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sept', 'oct', 'nov', 'dec', 'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']

markups = [
    {'markup': '\[number\]', 'wordlist': numberstrings},
    {'markup': '\[month\]', 'wordlist': monthstrings},
]

# SEARCH_ALL = 1 # searches all text
# SEARCH_DIALOGUE_ONLY = 2 # only searches dialogue
# SEARCH_DIALOGUE_IF_SPECIFIED = 3 # searches dialogue if non-general dialect or if object specified as dialogue only

suffixes = [
    's',
    'es',
    "'s",
    'ed',
    'd',
    'ly',
    'ing',
]

def createsubstitutedstrings(originalsearchword, obj) -> list:


    # retain special characters in search (such as ?, which can help limit found words)
    # requires escaping them for regex
    # escape prior to substituting (substitutes may contain regex such as numbers)
    searchword = re.escape(originalsearchword)
    stringslist = [searchword]

    if not obj.markup:
        return stringslist

    for m in markups:
        # if m['markup'] not in searchword:
        #     # most won't have markup, so have a quick exit for them
        #     # note that this prevents markup from containing other markup
        #     # (if that's needed, could create loop with escape when there's no markup left)
        #     continue

        # reiterating the generated list allows for more than one markup in a searchword
        for s in [t for t in stringslist]:
            # s is the searchword that (potentially) contains markup
            if m['markup'] in s:
                # remove the string that has markup still in it
                stringslist.remove(s)
                # create a list of strings with words substituted for markup
                newstrings = [s.replace(m['markup'], w) for w in m['wordlist']]
                stringslist.extend(newstrings)



    return stringslist

def createsearches(dialectname) -> list:
    # this is fast! total runtime 0.06s
    findreplaceobjects = BritpickFindReplace.objects.filter(dialect=dialectname).filter(active=True)
    searches = []

    # create searches such that ['searchstring', BritpickFindReplace obj]
    for o in findreplaceobjects:
        stringslist = []
        for s in o.searchwordlist:
            stringslist.extend(createsubstitutedstrings(s, o))
            # searches.extend([[w, o] for w in createsubstitutedstrings(s, o)])
        searches.append(['|'.join(stringslist), o])

    # sort all but length, descending; so that multiple word searches will be found before single ones
    # searches.sort(key=lambda search: len(search[0]), reverse=True)

    # add suffixes to searchwords; do this after all original words added so that they take lower priority
    # originalsearches = [s for s in searches]
    # for search in originalsearches:
    #     for suffix in suffixes:
    #         searches.append([search[0] + suffix, search[1]])



    return searches

def replaceanytext(search: list, s: str, text: str) -> str:
    # can't be inside prior match that's been found
    # must be before { or # (# marks end of text)

    # 2 capture groups (word and suffix)
    textpattern = r"""(?<=\b)%s(?=\b[^}]*?{)"""
    # textreplacepattern = r'{\1\2 ' + createreplacetext('TEST', search[1]) + r'}'

    text = re.sub(textpattern % s, createreplacetext(r'{\1\2 ', search[1]) + r'}', text, flags=re.IGNORECASE)

    return text

def replaceinquotes(search: list, s: str, text: str) -> str:
    # group 1 = captured word, group 2 = suffix
    dialogpattern = r"""\b(%s)\b(?=[^"”}]*?[^\s\w}]["”])(?=[^}]*?{)"""

    # dialogreplacepattern = r'\1{\2\3 ' + createreplacetext(search[1]) + r'}\4'
    text = re.sub(dialogpattern % s, r'{' + createreplacetext(r'\2\3', search[1]) + r'}', text, flags=re.IGNORECASE)
    return text


def britpick(text, dialectname, matchoption = matchoptions['SEARCH_DIALOGUE_IF_SPECIFIED']):

    debug = ''

    starttime = default_timer()
    searches = createsearches(dialectname)
    debug += 'createsearches: ' + str(default_timer() - starttime)
    debug += '   len(searches)=' + str(len(searches)) + ' | '

    # substitute every instance of 'searchstring' with '{f1}'

    # create markup dict items so that {'{f1}': 'original word [replacement text]',}
    markupdict = {}
    replacelist = []


    combinedsearches = []

    #combined search = ['hello | hi | hello there ']


    # for i, search in enumerate (searches):
    #     markup = 'f' + str(i)
    #
    #     # remove regex from dispalyed searchstring
    #     # can't regenerate original text but can make it more readable
    #     displayedsearchword = search[0].replace('\d+', '[number]').replace(r'\ ', ' ')
    #     replacetext = addfoundword(displayedsearchword) + ' ' + createreplacetext(search[1])
    #     markupdict.update({markup: replacetext})
        # replacelist.append(replacetext)

    text = text + '{'

    suffixpattern = r'(|' + '|'.join(suffixes) + r')'

    for i, search in enumerate(searches):
        # ie {f1}, {f2}
        markup = 'f' + str(i)

        s = '(' + search[0] + ')' + suffixpattern

        # replacepattern = "REPLACED"

        if matchoption == matchoptions['SEARCH_DIALOGUE_ONLY']:
            # \1 and \3 refer to groups, since we are only substituting group 2 (see patten above), keep groups 1 and 3 the same as in original text
            text = replaceinquotes(search, s, text)
        elif matchoption == matchoptions['SEARCH_DIALOGUE_IF_SPECIFIED'] and dialectname != "British (Generic)":
            text = replaceinquotes(search, s, text)
        elif matchoption == matchoptions['SEARCH_DIALOGUE_IF_SPECIFIED'] and search[1].dialogue == True:
            text = replaceinquotes(search, s, text)
        else:
            # search all text
            text = replaceanytext(search, s, text)

        # # remove regex from dispalyed searchstring
        # # can't regenerate original text but can make it more readable
        # displayedsearchword = search[0].replace('\d+', '[number]').replace(r'\ ', ' ')
        #
        # replacetext = addfoundword(displayedsearchword) + ' ' + createreplacetext(search[1])
        # markupdict.update({markup: replacetext})

    # replace every instance of {f1} with 'original word [replacement text]'
    # outputtext = text.format(**markupdict)

    outputtext = text

    # create line breaks
    outputtext = outputtext.replace('\r\n', '<br />')

    debug += 'total runtime: ' + str(default_timer() - starttime)

    return outputtext, debug


def createreplacetext(originalstring, obj):
    # format original string
    originalstring = addspan(originalstring, 'found word')

    # create replacement text that will be in []
    stringlist = []



    if obj.directreplacement:
        if obj.mandatory:
            stringlist.append(addspan(obj.directreplacement, 'mandatory'))
        else:
            stringlist.append(addspan(obj.directreplacement, 'directreplacement'))
    if obj.considerreplacement:
        c = ', '.join(w for w in obj.considerreplacementlist)
        stringlist.append(addspan(c, 'considerreplacement'))
    if obj.clarifyreplacement:
        if len(stringlist) == 0:
            # if no other text, then don't add parenthesis
            stringlist.append(addspan(obj.clarifyreplacementstring, 'clarifyreplacement'))
        else:
            stringlist.append(addspan(obj.clarifyreplacementstring, 'clarifyreplacement', '(', ')'))
    if obj.mandatory and len(stringlist) == 0:
        # if it's mandatory and there's no replacement/explanation, then add generic explanation
        stringlist.append(addspan('may not be used in britain', 'clarifyreplacement'))

    s = ' '.join(stringlist)
    s = addspan(s, 'replacement', '[', ']')

    # combine
    text = addspan(originalstring, 'foundword') + ' ' + s

    return text

def addfoundword(text):
    s = addspan(text, 'foundword')
    return s

# def adddirectreplacement(text):
#     s = addspan(text, 'directreplacement')
#     return s

def addspan(text, cssclass, wrapperstart = '', wrapperend = ''):
    if not text:
        return ''
    s = "<span class='"
    s += cssclass
    s += "'>"
    s += wrapperstart + text + wrapperend
    s += '</span>'
    return s


