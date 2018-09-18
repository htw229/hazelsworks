from .models import Replacement, Dialect, ReplacementExplanation, ReplacementCategory
from .debug import Debug
from .htmlutils import addspan, getlinkhtml, linebreakstoparagraphs
from __init__ import *

# import appsettings as settings
# import grammar

import re

import collections

debug = ''


findanywherepattern = r"""\b(%s)\b(?=[^>]*?<)"""
findinquotespattern = r"""\b(%s)\b(?=[^"”>]*?[^\s\w>]["”])(?=[^>]*?<)"""


# ReplacementCategory.object.dialogue == (False, True)
searchpatterns = {
    'DIALOGUEONLY':(findinquotespattern, findinquotespattern),
    'ALLTEXT':(findanywherepattern, findanywherepattern),
    'SMART':(findanywherepattern, findinquotespattern),
}


def britpick(formdata):
    global debug
    debug = ''
    debug = Debug()

    searchwords = getsearchwords(formdata)
    debug.add([len(searchwords), 'searchwords'])
    debug.timer('create searchwords')

    for word in searchwords:
        word['pattern'] = getwordpattern(word['str'])
    debug.timer('create word patterns')

    text = formdata['text']

    i = 0
    for searchpattern in searchpatterngenerator(searchwords, formdata):
        # debug.add(['searchpattern', searchpattern], max=10)
        # debug.add(['searchpattern', searchpattern])
        text = maketextreplacements(searchpattern, text)
        i += 1
        if i > 2000:
            break
    debug.timer('get search patterns from generator')
    debug.add(['ITERATIONS', i], max=500)

    text = postprocesstext(text)

    debug.timer('britpick() finished')

    britpickeddata = {
        'text': text,
        'debug': debug,
    }

    return britpickeddata



def getsearchwords(formdata) -> list:
    global debug

    searchwords = []
    patternsbycategory = getcategorypatternwrappers(formdata)

    for r in Replacement.objects\
        .filter(dialect=formdata['dialect'])\
        .filter(active=True)\
        .filter(category__in=formdata['replacement_categories']):

        patternwrapper = patternsbycategory[r.category_id]

        searchwords.extend([{
            'str': s,
            'obj': r,
            'patternwrapper': patternwrapper,
        } for s in r.searchwordlist])

    searchwords = sorted(searchwords, key=lambda w: len(w['str']), reverse=True)

    return searchwords


def getregexlistpattern(items) -> str:
    s = r'(' + r'|'.join(items) + r')'
    return s


def getwordpattern(searchstring) -> str:
    global debug

    # if PROTECTED_WORD_MARKER in searchstring:
    #     return searchstring



    # when to add escape? if do before markup, will need to change markup to use escape characters (could do this on the fly)

    # chop up words
    # for each word:
    #   if single letter, skip
    #   if in ignore word list, skip
    #   if irregular verb tense, change and continue
    #   add british/american variable word endings
    #   add regular suffixes (verb tenses, plurals, adverb -- doubling last consonant, not doubling and doubling l's)

    # flags for protect word, protect full phrase, protect case
    # handle (keep) punctuation

    # find words with regex
    # decide if protected
    # with each word, go through noun, verb, adj endings
    # add irregular verbs (do this in addition to above, in case it's not used that way)
    # combine all into one subpattern (find a way to optimize this)

    pattern = re.compile(SEARCH_STRING_PATTERN, re.IGNORECASE)
    searchpattern = ''

    matches = [m for m in re.finditer(pattern, searchstring)]

    protectedphrase = False
    ignorecase = True

    if matches[-1].groupdict()['flags']:
        if matches[-1].groupdict()[SEARCH_PROTECTED_PHRASE]:
            protectedphrase = True
        if matches[-1].groupdict()[SEARCH_PRESERVE_CASE]:
            ignorecase = False

    for match in matches:
        s = ''
        replacedashes = True

        matchgroups = match.groupdict()
        if matchgroups[SEARCH_MARKUP]:
            s = replacemarkup(matchgroups[SEARCH_MARKUP])

        elif matchgroups[SEARCH_EXCLUDE]:
            s = addexcludedword(matchgroups[SEARCH_EXCLUDE])
            replacedashes = False

        elif matchgroups[SEARCH_PUNCTUATION]:
            s = re.escape(match.group())

        elif matchgroups[SEARCH_NONMUTABLE]:
            s = re.escape(match.group())

        elif matchgroups[SEARCH_WORD]:
            if protectedphrase or matchgroups[SEARCH_PROTECTED_WORD]:
                s = matchgroups[SEARCH_WORD]
            else:
                # TODO: process word
                s = matchgroups[SEARCH_WORD]

        if replacedashes:
            s = s.replace('-', DASH_REPLACEMENT_PATTERN)

        searchpattern += s

            # s = searchstring + "word"



    # irregular verb tenses
    # for verblist in IRREGULAR_VERBS:
    #     addedtextlength = 0  # increment starting position after every replacement
    #     pattern = re.compile(r'\b' + getregexlistpattern(verblist) + r'\b', re.IGNORECASE)
    #     # debug.add(['pattern', pattern], max=5)
    #     for match in pattern.finditer(s):
    #         replacementtext = getregexlistpattern(verblist)
    #         s = s[:match.start() + addedtextlength] + replacementtext + s[match.end() + addedtextlength:]
    #         addedtextlength += len(replacementtext) - len(match.group())
    #         debug.add(['irregular',s])



    # add markup
    # if '[' in s:
    #     # debug.add(["'[' in", s])
    #     for m in MARKUP_LIST:
    #         if m['markup'] in s:
    #             replacepattern = '(' + '|'.join(m['wordlist']) + ')'
    #             s = s.replace(m['markup'], replacepattern)
                # do not add break here - may have additional matches

    # change "-" to dash, space or no space options
    # wordpattern = s.replace('-', DASH_REPLACEMENT_PATTERN)

    # if 'pregnant' in wordpattern:
        # debug.add(['wordpattern', wordpattern])

    # combine into string


    return searchpattern


def replacemarkup(markupstring):
    s = markupstring
    for m in MARKUP_LIST:
        if m['markup'] in s:
            replacepattern = '(' + '|'.join(m['wordlist']) + ')'
            s = s.replace(m['markup'], replacepattern)

    return s

def addexcludedword(word) -> str:
    # add negative look-behind and look-ahead
    s = r"(?<!%s)" % word
    s += r"(?!%s)" % word
    # TODO: works for t-shirt but not for test
    return s

def getalternatespellings(searchstring) -> list:
    return []

def getverbtenses(searchstring) -> list:
    return []

def getsuffixes(searchstring) -> list:
    return []

#

def searchpatterngenerator(searchwords, formdata) -> str:
    global debug

    # get pattern of next searchword
    # then get patterns of next one, if matches include it
    # until get NUMBER_COMBINED_SEARCHES of words
    # then combine them with wrapper

    while len(searchwords) > 0:
        nextwords = []
        for i, word in enumerate(searchwords):
            if word['patternwrapper'] == searchwords[0]['patternwrapper'] and \
                    word['obj'] not in [w['obj'] for w in nextwords]: # cannot have multiple regex groups with same pk
                nextwords.append(searchwords.pop(i))
            if len(nextwords) == NUMBER_COMBINED_SEARCHES:
                break

        # debug.add(['nextwords', [w['obj'].pk for w in nextwords]])

        wordspatterns = []
        for word in nextwords:
            wordspatterns.append(WORD_PATTERN_GROUP.format(pk=word['obj'].pk, wordpattern=word['pattern']))

        patternwrapper = nextwords[0]['patternwrapper']
        pattern = patternwrapper % '|'.join(wordspatterns)

        yield pattern



    # for searchword in searchwords:
    #     yield searchword




def maketextreplacements(patternstring, inputtext) -> str:
    global debug

    # if 'pregnant' in patternstring:
    #     debug.add(['patternstring:', patternstring])

    try:
        pattern = re.compile(patternstring, re.IGNORECASE) #TODO: allow case for instances of ER
    except:
        debug.add("regex error")
        debug.add(patternstring)
        return inputtext + 'ERROR'

    text = inputtext + ' <'
    # debug.add(['text', text])

    addedtextlength = 0  # increment starting position after every replacement

    for match in pattern.finditer(text):
        # debug.add(['match group', match.groupdict()])
        for groupname in match.groupdict().keys():
            if match.groupdict()[groupname]:
                # debug.add(['OBJECT PK FOUND=', groupname])
                pk = groupname[2:] # trim first two characters ('pk456' -> '456')
                replacementtext = r'<' + createreplacementhtml(match.group(), pk) + r'>'

        # replacementtext = 'found'
                text = text[:match.start() + addedtextlength] + replacementtext + text[match.end() + addedtextlength:]
                addedtextlength += len(replacementtext) - len(match.group())

    outputtext = text[:-2] # remove added '<' from text


    return outputtext











#------------------------------------------------------------------------
#------------------------------------------------------------------------
#------------------------------------------------------------------------



def createsearches(formdata) -> list:
    """
    :param formdata:
    :return: list of britpicksearch objects (1 per replacement object)
    """
    global debug


    # maxsearches = 25

    patternwrappersbycategory = getcategorypatternwrappers(formdata)
    searches = []

    i = 0
    for replaceobject in Replacement.objects\
        .filter(dialect=formdata['dialect'])\
        .filter(active=True)\
        .filter(category__in=patternwrappersbycategory.keys()):  # category won't be in there if not slected on form

        # get all searchwords with markup and suffixes and join in one regex search pattern

        # create regex pattern substring for each line (word) in searchwords as a list; this adds suffixes and replaces markup
        compiledsearchwords = []

        for s in replaceobject.searchwordlist:
            # combine with OR '|' to create the regex pattern substring for a single word
            compiledsearchword = '|'.join(createsearchwordpatterns(s, replaceobject))
            # then add it to the list
            compiledsearchwords.append(compiledsearchword)

        # join all the searchwordpatterns for an object to create a single regex pattern word string with OR (|) separating them
        objectsubpattern = '|'.join(compiledsearchwords)

        # create full regex pattern string with regex pattern wrapper
        objectpattern = patternwrappersbycategory[replaceobject.category_id] % objectsubpattern
        searches.append({'replaceobject': replaceobject, 'pattern': objectpattern})
        # if 'test' in objectsubpattern:
        #     debug.add([objectpattern])

        i += 1
        # if i > 25:
        #     break

    # sort by longest searchword (a kludgy way of getting compound words to be found before single words)
    searches.sort(key=lambda search: search['replaceobject'].longestsearchwordlength, reverse=True)

    debug.timer('createsearches() finished')
    return searches





def getcategorypatternwrappers(formdata) -> dict:
    """
    takes the submitted formdata dialogue_option
    and returns a dict of patterns either in quotes or not
    for each type of category (ie mandatory, suggested, informal, slang)
    to use later when forming the pattern template for each word
    :param formdata: dict
    :return patternsbycategory: dict
    """
    global debug

    patternsbycategory = collections.defaultdict()
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
            patternsbycategory[obj.pk] = pattern_template

    # patternsbycategory = collections.defaultdict()
    # for obj in ReplacementCategory.objects.all():
    #     if str(obj.pk) in formdata['replacement_categories']:
    #         pattern_template = ''
    #         if formdata['dialogue_option'] == 'ALLTEXT':
    #             pattern_template = findanywherepattern
    #             debug.add([obj, 'ALLTEXT','findanywherepattern'])
    #         elif formdata['dialogue_option'] == 'DIALOGUEONLY':
    #             pattern_template = findinquotespattern
    #             debug.add([obj, 'DIALOGUEONLY', 'findinquotespattern'])
    #         elif formdata['dialogue_option'] == 'SMART':
    #             if obj.dialogue:
    #                 pattern_template = findinquotespattern
    #                 debug.add([obj, 'SMART', 'findinquotespattern'])
    #             else:
    #                 pattern_template = findanywherepattern
    #                 debug.add([obj, 'SMART', 'findanywherepattern'])
    #         patternsbycategory.update({obj.pk: pattern_template})

    return patternsbycategory





def addsuffix(word):

    suffixlist = []

    # get the last consonant if word ends in vowel-consonant
    try:
        lastconsonant = re.search(r'[aeiou]([^aeiou])\b', word).group(1)
        vowelsuffixes = []
        nonvowelsuffixes = []
        for suffix in grammar.SUFFIX_LIST:
            if re.search(r'\b[aeiou]', suffix):
                vowelsuffixes.append(suffix)
            else:
                nonvowelsuffixes.append(suffix)
        suffixlist.extend([(lastconsonant + s) for s in vowelsuffixes])
        suffixlist.extend(nonvowelsuffixes)
    except AttributeError:
        suffixlist = grammar.SUFFIX_LIST

    wordwithsuffix = word + r'(|' + '|'.join(suffixlist) + r')'

    return wordwithsuffix


def getwordsuffixpattern(searchword) -> str:
    global debug
    debug.paused = True
    if searchword == "test of":
        debug.unpause()

    #TODO: do all separate words, sorted by length, then at end combine them as possible -- so store only one word at a time in the searchwords

    debug.add(['getwordsuffixpattern()',searchword])

    # no suffix: '#' in l
    if '#' in searchword:
        debug.add('# in searchword, not adding suffixes')
        s = searchword.replace('#', '')
        return s

    # get every word in searchword, with spaces and punctuation as their own groups; keeping "[]" and "-" inside words
    words = re.findall(r'\[?\w*\-?\w*\]?\^?|\s', searchword)
    # words = [x.replace(' ', r'\s') for x in words]
    debug.add(['words', words])
    # find the index of the word to add suffixes to in searchword
    pos = -1
    if len(words) == 1:
        pos = 0
    else: # multiple words
        try:
            # if word pre-defined, choose that one
            pos = words.index([s for s in words if '^' in s][0])
            words[pos] = words[pos].replace(r'^', '') # remove ^ symbol
            debug.add(['^ in', words[pos]])
        except IndexError: # if word is not pre-defined
            # traverse list
            # i = position of word, s = word starting from end
            for i, s in reversed(list(enumerate(words))):
                # if word is space or punctuation, skip it
                if not re.match('\w', s): #skip punctuation and spaces
                    debug.add([i, '"' + s + '"', 'not a word, continuing'])
                    continue
                if '[' in s or ']' in s: #skip markup
                    debug.add ([i, s, 'has markup, continuing'])
                    continue
                elif s in grammar.PREPOSITION_LIST: #skip prepositions
                    debug.add([i, s, 'is a preposition, continuing'])
                    continue
                else:
                    pos = i
                    debug.add(['choosing', i, s])
                    break

    if pos == -1:
        debug.add(('no word to add suffixes to found in ' + searchword + ':' + str(debug)))
        return searchword

    words[pos] = addsuffix(words[pos])
    debug.add(['pos', pos, words[pos]])
    # firstwords = ' '.join(words[:pos-1])
    # firstwords = re.escape(firstwords)
    # lastwords = ' '.join(words[pos+1:])
    # lastwords = re.escape(lastwords)
    # searchwordpattern = firstwords + ' ' + words[pos] + ' ' + lastwords
    searchwordpattern = ' '.join(words).replace('  ', '\s')
    debug.add(['searchwordpattern', searchwordpattern])

    # TODO: when searching, ignore punctuation after inputtext words (such as ! or ? or ,), but make punctuation in searchwords mandatory (allows narrowing down search, such as 'right?' 'really?'; allow adding suffixes to words with punctuation -- if do not want to transform them, put right#? or right?# as searchword in database

    debug.paused = False

    return searchwordpattern







def createsearchwordpatterns(searchword, britpickobj) -> list:
    '''

    :param searchword: string of single (or compound) word
    :param britpickobj:
    :return: list of regex patterns for single searchword with substitutions made and suffixes added
    '''

    global debug

    wordsuffixpattern = getwordsuffixpattern(searchword)
    return [wordsuffixpattern]

    # # TODO: is this actually working, though?
    # # REGEX ESCAPING: retain special characters in search
    # # (such as ?, which can help limit found words);
    # # escape prior to substituting markup (substitutes may contain regex)
    # # (errors occur if done earlier than try/except below)
    #
    # # TODO: count apostrophe and dash as word?
    #
    #
    #
    # # '#' indicates that cannot add suffix to it and cannot have dash or letter after it
    # if '#' in searchword:
    #     wordsuffixpattern = re.escape(searchword.replace('#',''))
    #     wordsuffixpattern += r'[^-a-zA-Z]+?'
    # else:
    #     # create generic regex pattern for with/without suffix
    #     suffixpattern = r'(|' + '|'.join(grammar.SUFFIX_LIST) + r')'
    #
    #     # create patternlist with individual searchwords and suffixes
    #     try:
    #         # will fail if rsplit returns only 1 string (ie if single word)
    #         word, preposition = searchword.rsplit(None, 1)
    #         if preposition in grammar.PREPOSITION_LIST:
    #             # debug.add([word, preposition], max=20)
    #             wordsuffixpattern = re.escape(word) + suffixpattern + ' ' + preposition
    #             # debug.add(searchword)
    #         else:
    #             raise ValueError('not a preposition')
    #     except ValueError:
    #         wordsuffixpattern = re.escape(searchword) + suffixpattern
    #
    # # dash in word can be dash, space or no space (ie ice-cream matches ice cream, icecream and ice-cream)
    # wordsuffixpattern = wordsuffixpattern.replace(r'\-', r"[-\s]*")
    #
    # patternlist = [wordsuffixpattern]

    # markup always has '[', so skip objects that don't have character
    if '[' not in searchword:
        return patternlist

    for m in grammar.MARKUP_LIST:
        for pattern in [p for p in patternlist]:
            if m['markup'] in pattern:
                # remove the string that has markup still in it
                patternlist.remove(pattern)
                # create a list of strings with words substituted for markup
                newpatterns = [pattern.replace(m['markup'], w) for w in m['wordlist']]
                patternlist.extend(newpatterns)

    # debug.timer('createsearchwordpatterns() finished')
    return patternlist



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


    debug.timer('createoutputtext() finished')
    return text


def replacetext(inputtext, search):
    global debug

    text = inputtext
    addedtextlength = 0     # increment starting position after every replacement
    pattern = re.compile(search['pattern'].replace(' ', ''), re.IGNORECASE)

    if 'test' in search['pattern']:
        debug.add(['replacetext()', search['pattern']])
        debug.add(['inputtext', inputtext])

    for match in pattern.finditer(inputtext):
        replacementtext = r'<' + createreplacementhtml(match.group(), search['replaceobject'].pk) + r'>'
        text = text[:match.start() + addedtextlength] + replacementtext + text[match.end() + addedtextlength:]
        addedtextlength += len(replacementtext) - len(match.group())

    return text





# ------------------------------------
# CREATE AND FORMAT REPLACEMENT TEXTS
# ------------------------------------

def createreplacementhtml(inputtext, replacementpk):
    global debug

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



def postprocesstext(text):
    # remove created {}
    text = text.replace('<', '').replace('>', '')
    # create line breaks
    text = linebreakstoparagraphs(text)

    return text