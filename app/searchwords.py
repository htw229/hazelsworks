from __init__ import *
import re
import trie

def getwordpattern(searchstring) -> dict:

    searchword = {}

    # IGNORECASE
    # if there are no capital letters in searchstring, then allow ignorecase regex flag
    searchword['ignorecase'] = not any(x.isupper() for x in searchstring)

    # LENGTH
    # allows sorting for prioritizing longer/multiple word searches
    searchword['length'] = len(searchstring)


    pattern = re.compile(SEARCH_STRING_PATTERN, re.IGNORECASE)
    matches = [m for m in re.finditer(pattern, searchstring)]

    constructors = []
    protectedphrase = False
    phraseending = r'\b'

    # create pattern constructors
    # (adds end, which is either word marker or punctuation, but does not add beginning word marker)
    for match in matches:
        matchgroups = match.groupdict()
        if matchgroups['protected_phrase']:
            protectedphrase = True
        elif matchgroups['question']:
            phraseending = r'\?'
        elif matchgroups['end_punctuation']:
            phraseending = r'[\.\,\?\!]'
        elif matchgroups['optional_words_marker']:
            constructors.append({
                'needs_processing': False,
                'string': OPTIONAL_WORD_PLACEHOLDER % r"([\w\'\-]+ ?){1,3}",
            })
        elif matchgroups['words_marker']:
            constructors.append({
                'needs_processing': False,
                'string': r"([\w\'\-]+ ?){1,3}",
            })
        elif matchgroups['markup']:
            try:
                constructors.append({
                    'needs_processing': False,
                    'string': '(?:' + '|'.join(MARKUP[matchgroups['markup']]) + ')',
                })
            except KeyError:
                print('markup key error: ' + searchstring)
        elif matchgroups['punctuation']:
            constructors.append({
                'needs_processing': False,
                'string': re.escape(matchgroups['punctuation']),
            })
        elif matchgroups['protected_word']:
            constructors.append({
                'needs_processing': False,
                'string': re.escape(matchgroups['protected_word'])
            })
        elif matchgroups['plural_protected_word']:
            constructors.append({
                'needs_processing': False,
                'string': re.escape(matchgroups['plural_protected_word']) + r"(?:|s|es)"
            })
        elif matchgroups['word']:
            constructors.append({
                'needs_processing': True,
                'string': matchgroups['word'],
            })
    constructors.append({
        'needs_processing': False,
        'string': phraseending,
    })

    for i, c in enumerate(constructors):
        if not c['needs_processing']:
            continue
        elif protectedphrase:
            constructors[i]['string'] = re.escape(constructors[i]['string'])
        else:
            s = c['string']
            if s.lower() in OPTIONAL_WORDS_LIST:
                constructors[i]['string'] = OPTIONAL_WORD_PLACEHOLDER % s
            elif s.lower() in PROTECTED_WORDS:
                constructors[i]['string'] = re.escape(s)
            elif len(s) < MIN_WORD_LENGTH_FOR_SUFFIX:
                constructors[i]['string'] = re.escape(s)
            else:
                wordlist = [s]
                irregularconjugates = getirregularconjugates(s)
                if irregularconjugates:
                    wordlist.extend(irregularconjugates)
                else:
                    regularconjugates = getsuffixwordlist(s)
                    wordlist.extend(regularconjugates)
                wordlist = casematchedwordlist(wordlist, s)
                wordlist = list(set(wordlist))

                wordtrie = trie.Trie()
                for w in wordlist:
                    wordtrie.add(w)
                wordpattern = wordtrie.pattern()

                if r'\-' in wordpattern:
                    wordpattern = wordpattern.replace(r'\-', DASH_REPLACEMENT_PATTERN)
                elif '-' in s:
                    wordpattern = wordpattern.replace('-', DASH_REPLACEMENT_PATTERN)

                constructors[i]['string'] = wordpattern

    pattern = ''.join([c['string'] for c in constructors])

    # create optional pattern
    # (if put the regex in earlier, cannot easily manage spaces before/after it)
    pattern = re.sub(OPTIONAL_WORD_PLACEHOLDER_PATTERN, OPTIONAL_WORD_PATTERN % r'\1', pattern)

    # remove trailing, leading and multiple spaces
    # (spaces may be escaped, so easier to use regex)
    pattern = re.sub(r'( +|(\\ )+)', ' ', pattern)
    pattern = pattern.strip()

    searchword['pattern'] = pattern

    return searchword


# def replacemarkup(markupstring):
#     s = markupstring
#
#     # create while loop so that can repeat until no markup is in there
#     for m in MARKUP_LIST:
#         if m['markup'] in s:
#             replacepattern = '(' + '|'.join(m['wordlist']) + ')'
#             s = s.replace(m['markup'], replacepattern)
#
#     return s


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

# def getoptionalwordplaceholder(word) -> str:
#     s = SEARCH_OPTIONAL_PLACEHOLDER % word
#     return s

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