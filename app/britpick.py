from .models import Replacement, Dialect, ReplacementExplanation, ReplacementCategory
from .debug import Debug
from .htmlutils import addspan, getlinkhtml, linebreakstoparagraphs
from __init__ import *

import trie

# import appsettings as settings
# import grammar

import re

import collections

debug = ''


# REPLACE_FIND_ANYWHERE = r"""\b(%s)\b(?=[^>]*?<)"""
# REPLACE_FIND_QUOTES_ONLY = r"""\b(%s)\b(?=[^"”>]*?[^\s\w>]["”])(?=[^>]*?<)"""


# ReplacementCategory.object.dialogue == (False, True)
searchpatterns = {
    'DIALOGUEONLY':(REPLACE_FIND_QUOTES_ONLY, REPLACE_FIND_QUOTES_ONLY),
    'ALLTEXT':(REPLACE_FIND_ANYWHERE, REPLACE_FIND_ANYWHERE),
    'SMART':(REPLACE_FIND_ANYWHERE, REPLACE_FIND_QUOTES_ONLY),
}




def britpick(formdata):
    global debug
    debug = ''
    debug = Debug()

    searchwords = getsearchwords(formdata)
    debug.add([len(searchwords), 'searchwords'])
    debug.timer('create searchwords')

    for word in searchwords:
        word = getwordpattern(word)
        # word['pattern'] = getwordpattern(word['str'])

    debug.timer('create word patterns')
    debug.resetcounter()

    text = formdata['text']

    i = 0
    for searchpattern, ignorecase in searchpatterngenerator(searchwords, formdata):
        # debug.add(['searchpattern', searchpattern], max=10)
        # debug.add(['searchpattern', searchpattern])
        text = maketextreplacements(searchpattern, text, ignorecase)
        i += 1
        if i > 2000:
            break
    debug.timer('text replacements')
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

def getoptionalwordplaceholder(word) -> str:
    s = SEARCH_OPTIONAL_PLACEHOLDER % word
    return s

def removewordboundary(oldpattern) -> str:
    # for word patterns that contain trailing punctuation, remove word boundary
    global debug

    p = oldpattern[:oldpattern.rfind(r"\b")] + oldpattern[oldpattern.rfind(r"\b")+2:]
    # debug.add('removing word boundary', oldpattern, '->', p)
    return p

def getwordpattern(searchword) -> dict:
    global debug

    # for each word:
    #   add british/american variable word endings
    #   add regular suffixes (verb tenses, plurals, adverb -- doubling last consonant, not doubling and doubling l's)

    searchstring = searchword['str']

    pattern = re.compile(SEARCH_STRING_PATTERN, re.IGNORECASE)
    searchpattern = ''

    matches = [m for m in re.finditer(pattern, searchstring)]

    protectedphrase = False
    ignorecase = not any(x.isupper() for x in searchstring) #ignore case if there are no capital letters; otherwise ignorecase will be false; do not need special flag for this and done before processing string (so that protectedphrases get included if needed)

# TODO: add negatives? (isn't, weren't, don't, can't, couldn't, shouldn't etc) add contractions? (is -> 's, 's not, s'not)

    for match in matches:
        s = ''
        replacedashes = True

        matchgroups = match.groupdict()

        if matchgroups[SEARCH_PROTECTED_PHRASE]:
            searchpattern = searchstring.replace(matchgroups[SEARCH_PROTECTED_PHRASE], '')
            break

        if matchgroups[SEARCH_MARKUP]:
            s = replacemarkup(matchgroups[SEARCH_MARKUP])

        elif matchgroups[SEARCH_EXCLUDE]:
            s = addexcludedword(matchgroups[SEARCH_EXCLUDE]) #TODO: working opposite of expected --> create custom capture group that if found during later parsing will not consider it found (what happens if is part of conjugation added? such as think<ing> -> reckon)
            replacedashes = False

        elif matchgroups[SEARCH_PUNCTUATION]: # spaces are here
            s = re.escape(match.group())

        # main category
        elif matchgroups[SEARCH_WORD] or matchgroups[SEARCH_WORD_WITH_APOSTROPHE]:
            word = matchgroups[SEARCH_WORD]
            s = ''

            # word = matchgroups[SEARCH_WORD_MAIN] #TODO: MAKE THIS WORK - words with dashes strange behavior - can extract just after dash and add back together but this is unfinished below
            # beginningword = matchgroups[SEARCH_WORD][:len(matchgroups[SEARCH_WORD])-len(word)]

            optional = False

        # TODO: make curly quotes and apostrophes regular?

            if matchgroups[SEARCH_WORD_WITH_APOSTROPHE]:
                s = matchgroups[SEARCH_WORD_WITH_APOSTROPHE]


            elif protectedphrase or matchgroups[SEARCH_PROTECTED_WORD] or len(word) < 3:
                s = word
                # debug.add([word, 'protected word'])

            elif word.lower() in PROTECTED_WORDS:
                if word.lower() in OPTIONAL_WORDS_LIST:
                    s = word
                    optional = True
                else:
                    s = word
            else:

                wordlist = [word]
                wordlist.extend(getirregularconjugates(word))
                wordlist.extend(getsuffixes(word))
                wordlist = list(set(wordlist))

                wordlist = casematchedwordlist(wordlist, word)

                s = r"(%s)" % '|'.join(wordlist)

                # s = getregexlistpattern(wordlist)

                # debug.add('LIST', wordlist, max=30)

                # s = createregexfromlist(wordlist)

                # Actually a lot slower to match for some reason
                # wordtrie = trie.Trie()
                # for w in wordlist:
                #     if not '-' in w:
                #         wordtrie.add(w)
                #
                # s = wordtrie.pattern()
                # s = r"(%s)" % wordtrie.pattern()
                # debug.add('TRIE', s, max=50)


                # debug.add('S', s, max=30)

            if optional:
                s = getoptionalwordplaceholder(s)
                # debug.add('getoptionalwordplaceholder',s)

        # TODO: optional markup not working

        if replacedashes:
            s = s.replace('-', DASH_REPLACEMENT_PATTERN)



        searchpattern += s

            # s = searchstring + "word"

    # optimize by trying first search over again
    searchpattern = '(' + searchstring + '|(%s)' % searchpattern + ')'


    # create OR pattern
    # (if put the regex in earlier, cannot easily manage spaces before/after it)
    searchpattern = re.sub(SEARCH_OPTIONAL_PLACEHOLDER_SEARCH, SEARCH_OPTIONAL_PATTERN % r'\1', searchpattern)

    # remove trailing, leading and multiple spaces
    # (spaces may be escaped, so easier to use regex)
    searchpattern = re.sub(r'( +|(\\ )+)', ' ', searchpattern)
    searchpattern = searchpattern.strip()

    if searchpattern[-1] in r",.!?":
        # debug.add('removing boundary for',word)
        searchword['patternwrapper'] = removewordboundary(searchword['patternwrapper'])
    # elif fullstop:
    #     searchpattern += SEARCH_FULL_STOP_PATTERN


    if 'foot' in searchpattern:
        debug.add('searchpattern:', searchpattern, max = 10)

    searchword['pattern'] = searchpattern
    searchword['ignorecase'] = ignorecase

    return searchword


def compressregexsearchlist(wordlist) -> str:
    # returns regex pattern not a group

    pattern = ''
    # most likely to match first
    # original word, then possessives, then verb tenses

    # whole phrase first?

    # atomic groups -> only processed one time; if code fails after that, does not go back and try to match again (ie \b(?>fir|first)\b, in case of first, will not match
    # (?>first phrase|ins|

    return pattern


def getirregularconjugates(word) -> list:
    global debug

    conjugateslist = []
    for irregularconjugateslist in IRREGULAR_CONJUGATES:
        if word.lower() in irregularconjugateslist:
            conjugateslist.extend(irregularconjugateslist)
            # continue loop, may be a conjugate of multiple different verbs

    # if word[0] == word[0].upper():
    #     conjugateslist = [x[0].upper() + x[1:] for x in conjugateslist]
    # else:
    #     conjugateslist = conjugateslist

    return conjugateslist

def casematchedwordlist(wordlist, originalword) -> list:
    if originalword[0] != originalword[0].upper():
        return wordlist

    capitalizedwordlist = [w[0].upper() + w[1:] for w in wordlist]

    return capitalizedwordlist


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
    return s

# def getalternatespellings(searchstring) -> list:
#     return []
#
# def getverbtenses(searchstring) -> list:
#     return []




# trim end of string by num letters in ending; if matches then add suffixes to it (end up with list of full words)
# return list of words


def getsuffixes(searchstring) -> list:
    word = searchstring.strip()
    wordlist = []

    for suffixformula in SUFFIXES_LIST:
        for ending in suffixformula['ending']:
            for suffix in suffixformula['suffix']:
                if suffixformula['replace']:
                    s = re.sub(ending + r'$', suffix, word)
                else:
                    s = re.sub(ending + r'$', ending + suffix, word)
                wordlist.append(s)

    wordlist = list(set(wordlist)) # remove duplicates

    return wordlist

# TODO: get possessives (separate function, run both irregular and regular words through it)




# def createregexfromlist(originalwordlist):
#     global debug
#     patternstrings = []
#
#     wordlist = list(set([w for w in sorted(originalwordlist)])) # sort and remove duplicates
#
#     iteration = 0
#     maxiterations = 30
#
#     while len(wordlist) > 0 and iteration < maxiterations:
#         iteration += 1
#         word = wordlist.pop(0)
#         matchingwordendings = []
#
#
#         for i, w in [(i, w) for (i, w) in enumerate(wordlist) if word in w]:
#             matchingwordendings.append(wordlist.pop(i)[:len(word)-1])
#
#         patternstrings.append(word + '(|' + '|'.join(matchingwordendings) + ')')
#
#     debug.add(patternstrings, max=50)
#     pattern = r"(%s)" % '|'.join(patternstrings)
#
#     return pattern


# sort so that

# abcd
# abcdef












def searchpatterngenerator(searchwords, formdata) -> list:
    global debug

    # get pattern of next searchword
    # then get patterns of next one, if matches include it
    # until get NUMBER_COMBINED_SEARCHES of words
    # then combine them with wrapper

    iterations = 0
    while len(searchwords) > 0 and iterations < MAX_SEARCHPATTERNGENERATOR_ITERATIONS:
        iterations += 1

        nextwords = [searchwords.pop(0)]
        ignorecase = nextwords[0]['ignorecase']

        for i, word in enumerate(searchwords):
            if len(nextwords) == NUMBER_COMBINED_SEARCHES:
                break
            if word['patternwrapper'] == nextwords[0]['patternwrapper'] \
                and word['ignorecase'] == ignorecase \
                and word['obj'] not in [w['obj'] for w in nextwords]: # cannot have multiple regex groups with same pk
                nextwords.append(searchwords.pop(i))

        # debug.add(['nextwords', [w['obj'].pk for w in nextwords]])

        wordspatterns = []
        for word in nextwords:
            wordspatterns.append(WORD_PATTERN_GROUP.format(pk=word['obj'].pk, wordpattern=word['pattern']))

        patternwrapper = nextwords[0]['patternwrapper']
        pattern = patternwrapper % '|'.join(wordspatterns)

        yield (pattern, ignorecase)




    # for searchword in searchwords:
    #     yield searchword




def maketextreplacements(patternstring, inputtext, ignorecase) -> str:
    global debug


    if 'foot' in patternstring:
        debug.add(['foot:', patternstring])

    try:
        if ignorecase:
            pattern = re.compile(patternstring, re.IGNORECASE)
        else:
            pattern = re.compile(patternstring)
    except:
        debug.add("regex error")
        debug.add(patternstring)
        return inputtext + '| pattern error:  ' + patternstring + '  |'


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
                pattern_template = REPLACE_FIND_ANYWHERE
            elif formdata['dialogue_option'] == 'DIALOGUEONLY':
                pattern_template = REPLACE_FIND_QUOTES_ONLY
            elif formdata['dialogue_option'] == 'SMART':
                if obj.dialogue:
                    pattern_template = REPLACE_FIND_QUOTES_ONLY
                else:
                    pattern_template = REPLACE_FIND_ANYWHERE
            patternsbycategory[obj.pk] = pattern_template

    # patternsbycategory = collections.defaultdict()
    # for obj in ReplacementCategory.objects.all():
    #     if str(obj.pk) in formdata['replacement_categories']:
    #         pattern_template = ''
    #         if formdata['dialogue_option'] == 'ALLTEXT':
    #             pattern_template = REPLACE_FIND_ANYWHERE
    #             debug.add([obj, 'ALLTEXT','REPLACE_FIND_ANYWHERE'])
    #         elif formdata['dialogue_option'] == 'DIALOGUEONLY':
    #             pattern_template = REPLACE_FIND_QUOTES_ONLY
    #             debug.add([obj, 'DIALOGUEONLY', 'REPLACE_FIND_QUOTES_ONLY'])
    #         elif formdata['dialogue_option'] == 'SMART':
    #             if obj.dialogue:
    #                 pattern_template = REPLACE_FIND_QUOTES_ONLY
    #                 debug.add([obj, 'SMART', 'REPLACE_FIND_QUOTES_ONLY'])
    #             else:
    #                 pattern_template = REPLACE_FIND_ANYWHERE
    #                 debug.add([obj, 'SMART', 'REPLACE_FIND_ANYWHERE'])
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

    # debug.add(['getwordsuffixpattern()',searchword])

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

    # debug.add([inputtext, replacementpk, Replacement.objects.get(pk=replacementpk)])
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