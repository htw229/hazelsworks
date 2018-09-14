from .models import Replacement, Dialect, ReplacementExplanation, ReplacementCategory
from .debug import Debug
from .htmlutils import addspan, getlinkhtml, linebreakstoparagraphs

import app.appsettings as settings
import grammar
import markup
import os

import re

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


findanywherepattern = r"""\b(%s)\b(?=[^>]*?<)"""
findinquotespattern = r"""\b(%s)\b(?=[^"”>]*?[^\s\w>]["”])(?=[^>]*?<)"""



class britpicksearch():
    regexpattern = ''
    britpickobj = ''

    def __init__(self, regexpattern, britpickobj):
        self.regexpattern = regexpattern
        self.britpickobj = britpickobj


class ReplacementOptions:
    replacement_categories = None  # ReplacementCategory obj list
    informal_and_slang_in_dialogue_only = False


    def __init__(self, formdata):
        self.replacement_categories = list(ReplacementCategory.objects.filter(pk__in=formdata['replacement_categories']))
        self.informal_and_slang_in_dialogue_only = formdata['informal_and_slang_in_dialogue_only']


def britpick(formdata):
    global debug
    debug = ''
    debug = Debug()

    searches = createsearches(formdata)
    debug.add(['number of searches:', len(searches)])

    outputtext = createoutputtext(formdata['text'], searches)
    # debug.add(outputtext)

    britpickeddata = {
        'text': outputtext,
        'debug': debug,
    }


    debug.timer('britpick() finished')
    return britpickeddata





def getcategorypatterns(formdata):
    categorypatterns = {}
    for obj in ReplacementCategory.objects.all():
        if str(obj.pk) in formdata['replacement_categories']:
            pattern_template = ''
            if formdata['dialogue_option'] == 'ALLTEXT':
                pattern_template = findanywherepattern
            elif formdata['dialogue_option'] == 'DIALOGUEONLY':
                pattern_template = findinquotespattern
            elif formdata['dialogue_option'] == 'SMART':
                if obj.dialogue:
                    pattern_template = findinquotespattern
                else:
                    pattern_template = findanywherepattern
            categorypatterns.update({obj.pk: pattern_template})

    return categorypatterns



def createsearches(formdata) -> list:
    """
    :param formdata:
    :return: list of britpicksearch objects (1 per britpickfindreplace)
    """

    global debug

    categorypatterns = getcategorypatterns(formdata)
    searches = []

    for replaceobject in Replacement.objects\
        .filter(dialect=formdata['dialect'])\
        .filter(active=True)\
        .filter(category__in=categorypatterns.keys()):

        # get all searchwords with markup and suffixes and join in one regex search pattern
        objectpattern = '|'.join(['|'.join(createsearchwordpatterns(s, replaceobject)) for s in replaceobject.searchwordlist])
        regexpattern = categorypatterns[replaceobject.category_id] % objectpattern
        searches.append({'replaceobject': replaceobject, 'pattern': regexpattern})

    # sort by longest searchword (a kludgy way of getting compound words to be found before single words)
    searches.sort(key=lambda search: search['replaceobject'].longestsearchwordlength, reverse=True)

    debug.timer('createsearches() finished')
    return searches



def createoutputtext(inputtext, searches):
    '''

    :param test:
    :param searches:
    :param dialectname:
    :param matchoption:
    :return: html formatted output text
    '''
    global debug

    text = inputtext + '<'

    for search in searches:
        text = replacetext(text, search)


    # remove created {}
    text = text.replace('<', '').replace('>', '')
    # create line breaks
    text = linebreakstoparagraphs(text)

    # debug.timer('createoutputtext() finished')
    return text



def createsearchwordpatterns(searchword, britpickobj) -> list:
    '''

    :param searchword: string of single (or compound) word
    :param britpickobj:
    :return: list of regex patterns for single searchword with substitutions made and suffixes added
    '''

    global debug

    # REGEX ESCAPING: retain special characters in search
    # (such as ?, which can help limit found words);
    # escape prior to substituting markup (substitutes may contain regex)
    # (errors occur if done earlier than try/except below)

    # create generic regex pattern for with/without suffix
    suffixpattern = r'(|' + '|'.join(grammar.SUFFIX_LIST) + r')'

    # create patternlist with individual searchwords and suffixes
    try:
        # will fail if rsplit returns only 1 string (ie if single word)
        word, preposition = searchword.rsplit(None, 1)
        if preposition in grammar.PREPOSITION_LIST:
            # debug.add([word, preposition], max=20)
            wordsuffixpattern = re.escape(word) + suffixpattern + ' ' + preposition
            # debug.add(searchword)
        else:
            raise ValueError('not a preposition')
    except ValueError:
        wordsuffixpattern = re.escape(searchword) + suffixpattern

    # dash in word can be dash, space or no space (ie ice-cream matches ice cream, icecream and ice-cream)
    wordsuffixpattern = wordsuffixpattern.replace(r'\-', r"[-\s]*")

    patternlist = [wordsuffixpattern]

    # markup always has '[', so skip objects that don't have character
    if '[' not in searchword:
        return patternlist

    for m in markup.MARKUP_LIST:
        for pattern in [p for p in patternlist]:
            if m['markup'] in pattern:
                # remove the string that has markup still in it
                patternlist.remove(pattern)
                # create a list of strings with words substituted for markup
                newpatterns = [pattern.replace(m['markup'], w) for w in m['wordlist']]
                patternlist.extend(newpatterns)

    # debug.timer('createsearchwordpatterns() finished')
    return patternlist


def replacetext(inputtext, search):
    global debug

    text = inputtext
    addedtextlength = 0     # increment starting position after every replacement
    pattern = re.compile(search['pattern'], re.IGNORECASE)

    for match in pattern.finditer(inputtext):
        # replacementtext = createreplacetext(r'{' + match.group() + ' ', search['replaceobject']) + r'}'
        replacementtext = r'<' + createreplacementhtml(match.group(), search['replaceobject'].pk) + r'>'
        text = text[:match.start() + addedtextlength] + replacementtext + text[match.end() + addedtextlength:]
        addedtextlength += len(replacementtext) - len(match.group())

    return text



# ------------------------------------
# CREATE AND FORMAT REPLACEMENT TEXTS
# ------------------------------------

def createreplacementhtml(inputtext, replacementpk):
    global debug
    # templatepath = os.path.dirname(os.path.dirname(__file__)) + r'/templates/inline_replacement_python.html'
    # replacementhtml = open(templatepath, 'r').read()
    #
    # replacementdata = {
    #     'inputtext': inputtext,
    #     'suggestreplacement': replacement.suggestreplacement,
    #     'considerreplacements': ', '.join(replacement.considerreplacementlist),
    #     'clarification': replacement.clarifyreplacementstring,
    #     'category': replacement.category.name,
    #     'explanation': str(replacement.explanations),
    #     'topic': str(replacement.topics),
    # }
    #
    # html = replacementhtml.format(**replacementdata)


    html = r'{% include "inline_replacement.html" with replacement=replacements.' + str(replacementpk) + r' inputtext="' + inputtext + r'" %}'

    debug.add([inputtext, replacementpk, Replacement.objects.get(pk=replacementpk)])
    return html

def createreplacetext(textstring, britpickobj):
    '''
    :param textstring: string from the input text
    :param britpickobj: britpickfindreplace object
    :return: span with css formatting
    '''

    global debug
    # debug.timer('createreplacetext() start')

    # format original string
    textstring = addspan(textstring, 'found word')

    # create replacement text that will be in []
    stringlist = []

    if britpickobj.suggestreplacement:
        if britpickobj.category.name == 'mandatory':
            stringlist.append(addspan(britpickobj.suggestreplacement, 'mandatory'))
        else:
            stringlist.append(addspan(britpickobj.suggestreplacement, 'suggestreplacement'))
    if britpickobj.category.name == 'suggested':
        c = ', '.join(w for w in britpickobj.considerreplacementlist)
        stringlist.append(addspan(c, 'considerreplacements'))

    # add explanations
    if britpickobj.clarifyexplanationspan:
        if len(stringlist) == 0:
            # if no other text, then don't add parenthesis
            stringlist.append(addspan(britpickobj.clarifyexplanationspan, 'clarification'))
        else:
            stringlist.append(addspan(britpickobj.clarifyexplanationspan, 'clarification', '(', ')'))

    # add topic
    for topic in britpickobj.topics.all():
        stringlist.append(addspan(topic.linkhtml, 'topiclink'))

    # if it's mandatory and there's no replacement/explanation, then add generic explanation
    if britpickobj.category.name == 'mandatory' and len(stringlist) == 0:
        stringlist.append(addspan(ReplacementExplanation.objects.get(name='not used').text, 'clarification'))

    s = ' '.join(stringlist)
    s = addspan(s, 'replacement', '[', ']')

    # combine texts
    text = addspan(textstring, 'foundword') + ' ' + s

    # debug.timer('createreplacetext()')
    return text
