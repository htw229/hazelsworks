from .models import Replacement, Dialect, ReplacementExplanation, ReplacementCategory
from .debug import Debug
from .htmlutils import addspan, getlinkhtml, linebreakstoparagraphs
from __init__ import *

import trie
# import nltk

# import appsettings as settings
# import grammar

import re

import collections

debug = ''

# wordtags = nltk.ConditionalFreqDist((w.lower(), t)
#         for w, t in nltk.corpus.brown.tagged_words(tagset="universal"))


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
    debug.add('SEARCHWORDS', len(searchwords))
    # debug.add(searchwords)
    debug.timer('create searchwords')

    # for word in searchwords:
    #     word = getwordpattern(word)
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
        if i > 2000: # changing to 0 for debug
            break

    debug.add('ITERATIONS', i)
    debug.timer('create text replacements')


    text = postprocesstext(text)

    debug.timer('britpick()')

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

        # if r.searchwords:
        #     debug.add(r.searchwords)

        if not r.searchwords:
            debug.add('ERROR: no searchwords in', r)
            continue

        for w in r.searchwords:
            # if 'pregnant' in w['pattern']:
            #     debug.add(w)
            w['patternwrapper'] = patternwrapper
            w['obj'] = r
            searchwords.append(w)

    searchwords = sorted(searchwords, key=lambda w: w['length'], reverse=True)

    return searchwords


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


    return patternsbycategory


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

    # TODO:  add british/american variable word endings
    # TODO: add negatives? (isn't, weren't, don't, can't, couldn't, shouldn't etc) add contractions? (is -> 's, 's not, s'not)
    # TODO: make curly quotes and apostrophes regular?

    searchstring = searchword['str']

    # IGNORECASE
    # if there are no capital letters in searchstring, then allow ignorecase regex flag
    searchword['ignorecase'] = not any(x.isupper() for x in searchstring)

    # PROTECTED PHRASE
    if PROTECTED_PHRASE_MARKER in searchstring:
        searchword['pattern'] = re.escape(searchstring.replace(PROTECTED_PHRASE_MARKER, '').strip())
        return searchword
    elif PROTECTED_WORD_MARKER in searchstring and not ' ' in searchstring.replace(PROTECTED_WORD_MARKER, '').strip():
        # if there is only one word and there's a protected word marker, treat as protected phrase
        searchword['pattern'] = re.escape(searchstring.replace(PROTECTED_WORD_MARKER, '').strip())
        return searchword



    pattern = re.compile(SEARCH_STRING_PATTERN, re.IGNORECASE)
    matches = [m for m in re.finditer(pattern, searchstring)]
    searchpattern = ''

    for match in matches:
        s = ''
        replacedashes = True

        matchgroups = match.groupdict()



        # elif matchgroups[SEARCH_EXCLUDE]:
        #     s = addexcludedword(matchgroups[SEARCH_EXCLUDE]) #TODO: working opposite of expected --> create custom capture group that if found during later parsing will not consider it found (what happens if is part of conjugation added? such as think<ing> -> reckon)
        #     replacedashes = False

        if matchgroups[SEARCH_PUNCTUATION]: # spaces are here
            s = re.escape(match.group())

        elif matchgroups[SEARCH_MARKUP]:
            s = replacemarkup(matchgroups[SEARCH_MARKUP])

        elif matchgroups[SEARCH_WORD_WITH_APOSTROPHE]:
            s = matchgroups[SEARCH_WORD_WITH_APOSTROPHE]

        elif matchgroups[SEARCH_WORD]:
            word = matchgroups[SEARCH_WORD]
            optional = False

            if matchgroups[SEARCH_PROTECTED_WORD]:
                s = word

            elif word.lower() in PROTECTED_WORDS:
                if word.lower() in OPTIONAL_WORDS_LIST:
                    s = word
                    optional = True
                else:
                    s = word

            elif len(word) < MIN_WORD_LENGTH_FOR_SUFFIX:
                s = word

            else:
                wordlist = [word]
                irregularconjugates = getirregularconjugates(word)
                if irregularconjugates:
                    wordlist.extend(irregularconjugates)
                    wordlist = casematchedwordlist(wordlist, word)
                    wordlist = list(set(wordlist))
                else:
                    wordlist.append(getsuffixpattern(word))
                # wordlist.extend(getsuffixes(word))

                s = r"(?:%s)" % '|'.join(wordlist)
                # BROKEN
                # if wordlist:
                #     s = r"(?>" + word + r"\b|(?:" + '|'.join(wordlist) + '))'
                # else:
                #     s = word

            if optional:
                s = getoptionalwordplaceholder(s)


        if replacedashes:
            if r'\-' in s:
                s = s.replace(r'\-', DASH_REPLACEMENT_PATTERN)
            elif '-' in s:
                s = s.replace('-', DASH_REPLACEMENT_PATTERN)


        searchpattern += s


    # optimize by trying first search as atomic group

    # broken
    # if searchstring != searchpattern:
    #     searchpattern = r'(?>' + searchstring + r'\b|' + searchpattern + ')'


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


    if '-' in searchpattern:
        debug.add('final searchpattern:', searchpattern, max = 10)

    searchword['pattern'] = searchpattern

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

def getsuffixpattern(searchstring) -> str:
    global debug

    word = searchstring.strip()
    wordlist = []
    s = ''

    tag = ''


    # global wordtags
    # debug.add('wordtags', wordtags[word], max=20)


    for suffixformula in SUFFIXES_LIST:
        for ending in suffixformula['ending']:
            for suffix in suffixformula['suffix']:
                if suffixformula['replace']:
                    s = re.sub(ending + r'$', suffix, word)
                else:
                    s = re.sub(ending + r'$', ending + suffix, word)
                wordlist.append(s)

    wordlist = list(set(wordlist)) # remove duplicates
    wordtrie = trie.Trie()
    for w in wordlist:
        wordtrie.add(w)
    pattern = wordtrie.pattern()

    # if '-' in pattern:
    #     debug.add('suffix pattern', pattern)

    return pattern


# def getregextrie(wordlist) -> str:
#     p = ''
#     wordlist = list(set(wordlist))
#     wordlist = sorted(wordlist)
#
#     s = ''
#     worddict = {}
#     for i, word in enumerate(wordlist):
#         worddict[word[0]] = word
#         wordlist[i] = word[1:]
#
#     for character in worddict.keys():
#         for word in worddict[character]:
#             worddict[character][word[0]] = word
#             worddict[character]
#
#     return p



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

            if 'is all' in word['pattern']:
                debug.add('searchpatterngenerator- is all')
                debug.add(word['obj'])

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




    # for searchword in searchstrings:
    #     yield searchword




def maketextreplacements(patternstring, inputtext, ignorecase) -> str:
    global debug


    if 'is all' in patternstring:
        debug.add(['is all', patternstring])

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



def createreplacementhtml(inputtext, replacementpk):
    global debug

    html = r'{% include "inline_replacement.html" with replacement=replacements.' + str(replacementpk) + r' inputtext="' + inputtext + r'" %}'

    # debug.add([inputtext, replacementpk, Replacement.objects.get(pk=replacementpk)])
    return html


def postprocesstext(text):
    # remove created {}
    text = text.replace('<', '').replace('>', '')
    # create line breaks
    text = linebreakstoparagraphs(text)

    return text