from __init__ import *
import re
import trie

def getwordpattern(searchstring) -> dict:

    # TODO:  add british/american variable word endings
    # TODO: add negatives? (isn't, weren't, don't, can't, couldn't, shouldn't etc) add contractions? (is -> 's, 's not, s'not)
    # TODO: make curly quotes and apostrophes regular?

    searchword = {}

    # IGNORECASE
    # if there are no capital letters in searchstring, then allow ignorecase regex flag
    searchword['ignorecase'] = not any(x.isupper() for x in searchstring)

    searchword['length'] = len(searchstring)

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

                s = r"(?:%s)" % '|'.join(wordlist)

            if optional:
                s = getoptionalwordplaceholder(s)


        if replacedashes:
            if r'\-' in s:
                s = s.replace(r'\-', DASH_REPLACEMENT_PATTERN)
            elif '-' in s:
                s = s.replace('-', DASH_REPLACEMENT_PATTERN)


        searchpattern += s


    # create OR pattern
    # (if put the regex in earlier, cannot easily manage spaces before/after it)
    searchpattern = re.sub(SEARCH_OPTIONAL_PLACEHOLDER_SEARCH, SEARCH_OPTIONAL_PATTERN % r'\1', searchpattern)


    # remove trailing, leading and multiple spaces
    # (spaces may be escaped, so easier to use regex)
    searchpattern = re.sub(r'( +|(\\ )+)', ' ', searchpattern)
    searchpattern = searchpattern.strip()

    # if searchpattern[-1] in r",.!?": # TODO: will need to be more specific if multiple punctuation possible
    #     # debug.add('removing boundary for',word)
    #     searchword['patternwrapper'] = removewordboundary(searchword['patternwrapper'])
    # # elif fullstop:
    # #     searchpattern += SEARCH_FULL_STOP_PATTERN

    #TODO: add punctuation markup [end]=\!\.\?
    #TODO: add possessive markup [possessive]=his, hers, my, your, our, [word]'s

    searchword['pattern'] = searchpattern

    return searchword


def replacemarkup(markupstring):
    s = markupstring

    # create while loop so that can repeat until no markup is in there
    for m in MARKUP_LIST:
        if m['markup'] in s:
            replacepattern = '(' + '|'.join(m['wordlist']) + ')'
            s = s.replace(m['markup'], replacepattern)

    return s


def getirregularconjugates(word) -> list:

    conjugateslist = []
    for irregularconjugateslist in IRREGULAR_CONJUGATES:
        if word.lower() in irregularconjugateslist:
            conjugateslist.extend(irregularconjugateslist)
            # continue loop, may be a conjugate of multiple different verbs

    return conjugateslist


def casematchedwordlist(wordlist, originalword) -> list:
    if originalword[0] != originalword[0].upper():
        return wordlist

    capitalizedwordlist = [w[0].upper() + w[1:] for w in wordlist]

    return capitalizedwordlist


def removewordboundary(oldpattern) -> str:
    # for word patterns that contain trailing punctuation, remove word boundary
    p = oldpattern[:oldpattern.rfind(r"\b")] + oldpattern[oldpattern.rfind(r"\b")+2:]
    return p

def getoptionalwordplaceholder(word) -> str:
    s = SEARCH_OPTIONAL_PLACEHOLDER % word
    return s

def getsuffixpattern(searchstring) -> str:

    # word = searchstring.strip()
    # wordlist = []
    #
    # for suffixformula in SUFFIXES_LIST:
    #     for ending in suffixformula['ending']:
    #         for suffix in suffixformula['suffix']:
    #             if suffixformula['replace']:
    #                 s = re.sub(ending + r'$', suffix, word)
    #             else:
    #                 s = re.sub(ending + r'$', ending + suffix, word)
    #             wordlist.append(s)
    #
    # wordlist = list(set(wordlist)) # remove duplicates

    wordlist = getsuffixwordlist(searchstring)

    wordtrie = trie.Trie()
    for w in wordlist:
        wordtrie.add(w)
    pattern = wordtrie.pattern()

    return pattern

def getsuffixwordlist(searchstring) -> list:
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