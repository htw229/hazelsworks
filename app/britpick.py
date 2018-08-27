from .models import BritpickFindReplace, BritpickDialects
from .debug import Debug

import re
import regex

debug = ''


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

numberstrings = ['\d+', '\d+st', '\d+nd', '\d+th', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight',
                 'nine', 'ten', 'first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth',
                 'tenth', 'eleventh', 'twelfth', 'thirteenth', 'fourteenth', 'fifteenth', 'sixteenth', 'seventeenth',
                 'eighteenth', 'nineteenth', 'twentieth', 'thirtieth', 'fourtieth', 'fiftieth', 'hundredth',
                 'thousandth', 'millionth']

monthstrings = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sept', 'oct', 'nov', 'dec', 'january',
                'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november',
                'december']

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
    r"\'s",
    'ed',
    'd',
    'ly',
    'ing',
    'ped',
    'ded',
    'ping',
    'ding',
]

# suffixes = [
#     's',
#     'es',
#     r"\'s"
# ]

prepositions = [
    'to',
    'up',
    'out',
    'of',
    'with',
]


findanywherepattern = r"""\b(%s)\b(?=[^}]*?{)"""
findinquotespattern = r"""\b(%s)\b(?=[^"”}]*?[^\s\w}]["”])(?=[^}]*?{)"""



class britpicksearch():
    regexpattern = ''
    britpickobj = ''

    def __init__(self, regexpattern, britpickobj):
        self.regexpattern = regexpattern
        self.britpickobj = britpickobj





def britpick(inputtext, dialectname, matchoption=matchoptions['SEARCH_DIALOGUE_IF_SPECIFIED']):

    # debug
    global debug
    debug = ''
    debug = Debug()

    searches = createsearches(dialectname)
    debug.add(['number of searches:', len(searches)])
    debug.add(['searches[25]', searches[25].regexpattern])

    # TODO: clean up matchoption
    outputtext = createoutputtext(inputtext, searches, dialectname, matchoption)

    debug.timer('britpick() finished')

    return outputtext, debug.html




def createsearches(dialectname) -> list:
    '''

    :param dialectname: string as pk of dialect object
    :return: list of britpicksearch objects (1 per britpickfindreplace)
    '''

    global debug

    searches = []

    britpickobjs = BritpickFindReplace.objects\
        .filter(dialect=dialectname)\
        .filter(active=True)

    for britpickobj in britpickobjs:
        searchpatternlist = []
        for s in britpickobj.searchwordlist:
            searchpatternlist.extend(createsearchwordpatterns(s, britpickobj))
        regexpattern = '|'.join(searchpatternlist)
        searches.append(britpicksearch(regexpattern, britpickobj))

    # sort by longest searchword (a kludgy way of getting compound words to be found before single words)
    searches.sort(key=lambda search: search.britpickobj.longestsearchwordlength, reverse=True)

    debug.timer('createsearches() finished')
    return searches



def createoutputtext(inputtext, searches, dialectname, matchoption):
    '''

    :param inputtext:
    :param searches:
    :param dialectname:
    :param matchoption:
    :return: html formatted output text
    '''
    global debug

    text = inputtext + '{'

    for search in searches:
        if matchoption == matchoptions['SEARCH_DIALOGUE_ONLY']:
            text = replacetext(search, text, findinquotespattern)
        elif matchoption == matchoptions['SEARCH_DIALOGUE_IF_SPECIFIED'] and dialectname != "British (Generic)":
            text = replacetext(search, text, findinquotespattern)
        elif matchoption == matchoptions['SEARCH_DIALOGUE_IF_SPECIFIED'] and search.britpickobj.dialogue == True:
            text = replacetext(search, text, findinquotespattern)
        else:
            # this is majority of replacements for generic dialect
            text = replacetext(search, text, findanywherepattern)


    # create line breaks
    text = text.replace('\r\n', '<br />')
    # remove created {}
    text = text.replace('{', '').replace('}', '')

    debug.timer('createoutputtext() finished')
    return text



def createsearchwordpatterns(searchword, britpickobj) -> list:
    '''

    :param searchword: string of single (or compound) word
    :param britpickobj:
    :return: list of regex patterns for single searchword with substitutions made and suffixes added
    '''

    global debug

    if britpickobj.regex:
        # do nothing to it
        return [searchword]

    # create generic regex pattern for with/without suffix
    suffixpattern = r'(|' + '|'.join(suffixes) + r')'


    # REGEX ESCAPING: retain special characters in search (such as ?, which can help limit found words); escape prior to substituting markup (substitutes may contain regex)

    # TODO
    # add suffixes to 2nd to last word if ends with preposition
    # get last word in string
    # stringprepositionlist = searchword.rsplit(None, 1)
    #
    # if len(stringprepositionlist) > 1 and stringprepositionlist[1] in prepositions:
    #     s = '(' + re.escape(stringprepositionlist[0]) + suffixpattern + ' ' + re.escape(stringprepositionlist[1]) + ')'
    #     # debug += 'preposition: ' + s + '<br>'
    # else:
    #     s = '(' + re.escape(searchword) + suffixpattern + ')'
    #     # debug += 'no preposition: ' + s + '<br>'

    try:
        # will fail if rsplit returns only 1 string (ie if single word)
        word, preposition = searchword.rsplit(None, 1)
        if preposition in prepositions:
            debug.add([word, preposition], max=20)
            wordsuffixpattern = re.escape(word) + suffixpattern + ' ' + preposition
        else:
            raise ValueError('not a preposition')
    except ValueError:
        wordsuffixpattern = re.escape(searchword) + suffixpattern

    # searchwordsplit = searchword.rsplit(None, 1)
    # lastword = searchwordsplit[-1]
    # if len(searchwordsplit) > 1 and lastword in prepositions:
    #     debug.add(['preposition', searchword], max=20)
    #     wordsuffixpattern = re.escape(searchwordsplit) + suffixpattern + lastword)
    #

    # wordsuffixpattern = re.escape(searchword) + suffixpattern
    patternlist = [wordsuffixpattern]

    # add markup
    if not britpickobj.markup:
        return patternlist

    for m in markups:
        for pattern in [p for p in patternlist]:
            if m['markup'] in pattern:
                # remove the string that has markup still in it
                patternlist.remove(pattern)
                # create a list of strings with words substituted for markup
                newpatterns = [pattern.replace(m['markup'], w) for w in m['wordlist']]
                patternlist.extend(newpatterns)

    # debug.timer('createsearchwordpatterns() finished')
    return patternlist


def replacetext(search, inputtext, templatepattern):
    global debug

    pattern = templatepattern % search.regexpattern
    # debug.add(['pattern:', pattern], max=100)

    # DEBUG SINGLE WORD
    # if 'reverse' in pattern:
    #     debug.add(pattern)

    # \1 detects entire match (lookahead is not included)
    text = re.sub(pattern, createreplacetext(r'{\1 ', search.britpickobj) + r'}', inputtext, flags=re.IGNORECASE)

    return text



# ------------------------------------
# CREATE AND FORMAT REPLACEMENT TEXTS
# ------------------------------------

def createreplacetext(textstring, britpickobj):
    '''
    :param textstring: string from the input text
    :param britpickobj: britpickfindreplace object
    :return: span with css formatting
    '''

    # format original string
    textstring = addspan(textstring, 'found word')

    # create replacement text that will be in []
    stringlist = []

    if britpickobj.directreplacement:
        if britpickobj.mandatory:
            stringlist.append(addspan(britpickobj.directreplacement, 'mandatory'))
        else:
            stringlist.append(addspan(britpickobj.directreplacement, 'directreplacement'))
    if britpickobj.considerreplacement:
        c = ', '.join(w for w in britpickobj.considerreplacementlist)
        stringlist.append(addspan(c, 'considerreplacement'))
    if britpickobj.clarifyreplacement:
        if len(stringlist) == 0:
            # if no other text, then don't add parenthesis
            stringlist.append(addspan(britpickobj.clarifyreplacementstring, 'clarifyreplacement'))
        else:
            stringlist.append(addspan(britpickobj.clarifyreplacementstring, 'clarifyreplacement', '(', ')'))
    if britpickobj.mandatory and len(stringlist) == 0:
        # if it's mandatory and there's no replacement/explanation, then add generic explanation
        stringlist.append(addspan('may not be used in britain', 'clarifyreplacement'))

    s = ' '.join(stringlist)
    s = addspan(s, 'replacement', '[', ']')

    # combine texts
    text = addspan(textstring, 'foundword') + ' ' + s

    return text


def addspan(string, cssclass, wrapperstart='', wrapperend=''):
    '''
    :param string: text to be formatted
    :param cssclass: css class to reference in <span>
    :param wrapperstart: optional open/closing marks (such as parentheses)
    :param wrapperend: optional open/closing marks (such as parentheses)
    :return: <span> with css
    '''
    if not string:
        return ''
    s = "<span class='"
    s += cssclass
    s += "'>"
    s += wrapperstart + string + wrapperend
    s += '</span>'
    return s
