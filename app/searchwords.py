from __init__ import *
import re
import trie

sortedspellinglist = [sorted(p, key=lambda x: len(x), reverse=True) for p in BRITISH_SPELLINGS]
spellingvariantlist = [w[0] for w in BRITISH_SPELLINGS] + [w[1] for w in sortedspellinglist]


#TODO: don't, can't, shouldn't etc being caught by apostrophe word

def getwordpattern(searchstring, usetrie = None) -> dict:

    searchword = {}




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
            phraseending = r'[.,?!]'
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
                'needs_processing': True,
                'string': matchgroups['plural_protected_word'],
                'plural_possessive_only': True,
                # 'string': re.escape(matchgroups['plural_protected_word']) + r"(?:|s|es)"
            })

        elif matchgroups['noun_protected_word']:
            # creates [possessive or article] + [optional words] + [word](s)
            constructors.append({
                'needs_processing': False,
                'string': '(?:' + '|'.join(MARKUP['noun_preceding']) + ')',
            })
            # allow one optional word (adjectives) -- too many doesn't limit sufficiency, having any does allow for over-finding such as 'she really loves'
            constructors.append({
                'needs_processing': False,
                'string': OPTIONAL_WORD_PLACEHOLDER % r"([\w\'\-]+ ?)",
            })
            constructors.append({
                'needs_processing': True,
                'string': matchgroups['noun_protected_word'],
                'plural_possessive_only': True,
                # 'string': re.escape(matchgroups['plural_protected_word']) + r"(?:|s|es)"
            })
            
        elif matchgroups['word']:
            constructors.append({
                'needs_processing': True,
                'string': matchgroups['word'],
            })

    for i, c in reversed(list(enumerate(constructors))):
        if re.search(r'[.,?!]', phraseending):
            break
        elif re.search(r'[a-z]', c['string'], re.IGNORECASE):
            constructors[i]['possessive_exempt'] = True
            # constructors[i]['string'] = 'lastword'
            break

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
            if s.lower() in OPTIONAL_WORDS_LIST: # not making 'a' and 'the' optional
                # constructors[i]['string'] = OPTIONAL_WORD_PLACEHOLDER % s
                constructors[i]['string'] = s
            elif s.lower() in PROTECTED_WORDS:
                constructors[i]['string'] = s
            elif len(s) < MIN_WORD_LENGTH_FOR_SUFFIX:
                constructors[i]['string'] = s
            elif getconjugates(s, PROTECTED_CONJUGATES):
                wordlist = getconjugates(s, PROTECTED_CONJUGATES)
                constructors[i]['string'] = patternfromlist(wordlist, s)
            else:
                wordlist = [s]

                # get PLURALS
                wordlist.extend(getsuffixwordlist(s, PLURALS))

                # get POSSESSIVES of original word and plural words
                # only if they're not last word or phrase ends on punctuation
                # (otherwise \b will stop at apostrophe anyways)
                if ('possessive_exempt' not in c.keys()) or (not c['possessive_exempt']):
                    wordlist.extend(getsuffixwordlist(wordlist, POSSESSIVES))

                # get CONJUGATES
                if ('plural_possessive_only' in c.keys()) and c['plural_possessive_only']:
                    pass
                elif getconjugates(s, IRREGULAR_CONJUGATES):
                    wordlist.extend(getconjugates(s, IRREGULAR_CONJUGATES))
                else:
                    wordlist.extend(getsuffixwordlist(s, REGULAR_CONJUGATES)) # do not make conjugates plural or possessive, or conjugate plural or possessive words

                # get BRITISH SPELLING VARIANTS
                spellingvariants = []
                for w in wordlist:
                    for spellingpair in sortedspellinglist:
                        if w.startswith(spellingpair[0]):
                            spellingvariants.append(w.replace(spellingpair[0], spellingpair[1]))
                        elif w.startswith(spellingpair[1]):
                            spellingvariants.append(w.replace(spellingpair[1], spellingpair[0]))

                wordlist.extend(spellingvariants)
                wordpattern = patternfromlist(wordlist, s, usetrie=usetrie)

                # replace DASHES with nothing/dash/space options
                # does not replace dashes in protected words or phrases
                if r'\-' in wordpattern:
                    wordpattern = wordpattern.replace(r'\-', DASH_REPLACEMENT_PATTERN)
                elif '-' in s:
                    wordpattern = wordpattern.replace('-', DASH_REPLACEMENT_PATTERN)

                constructors[i]['string'] = wordpattern

    pattern = ''.join([c['string'] for c in constructors])

    # create OPTIONAL pattern
    # (if put the regex in earlier, cannot easily manage spaces before/after it)
    pattern = re.sub(OPTIONAL_WORD_PLACEHOLDER_PATTERN, OPTIONAL_WORD_PATTERN % r'\1', pattern)

    # remove trailing, leading and multiple spaces
    # (spaces may be escaped, so easier to use regex)
    pattern = re.sub(r'( +|(\\ )+)', ' ', pattern)
    pattern = pattern.strip()

    searchword['pattern'] = pattern

    # IGNORECASE
    # if there are no capital letters in searchstring, then allow ignorecase regex flag
    # (do this with pattern instead of searchstring since may have case-sensitive markup)
    if pattern != pattern.lower():
        searchword['ignorecase'] = False
    else:
        searchword['ignorecase'] = True

    # LENGTH
    # allows sorting for prioritizing longer/multiple word searches
    searchword['length'] = len(searchstring)

    return searchword

def getspellingvariants(wordlist) -> list:
    spellingvariants = []
    for w in wordlist:
        for spellingpair in sortedspellinglist:
            if w.startswith(spellingpair[0]):
                spellingvariants.append(w.replace(spellingpair[0], spellingpair[1]))
            elif w.startswith(spellingpair[1]):
                spellingvariants.append(w.replace(spellingpair[1], spellingpair[0]))

    return spellingvariants

def patternfromlist(wordlist, word = '', usetrie = None) -> str:
    if word:
        wordlist = casematchedwordlist(wordlist, word)

    wordlist.append(word) # just in case
    wordlist = list(set(wordlist))

    if usetrie is None:
        usetrie = TRIE_SEARCHWORD_PATTERN

    if usetrie:
        wordtrie = trie.Trie()
        for w in wordlist:
            wordtrie.add(w)
        wordpattern = wordtrie.pattern()
    else:
        wordpattern = r"(?:%s)" % '|'.join(wordlist)

    return wordpattern



def getconjugates(word, conjugateslist) -> list:

    wordlist = []
    for conjugate in conjugateslist:
        if word.lower() in conjugate:
            wordlist.extend(conjugate)
            # continue loop, may be a conjugate of multiple different verbs

    return wordlist


def casematchedwordlist(wordlist, originalword) -> list:
    if originalword[0] != originalword[0].upper():
        return wordlist

    capitalizedwordlist = [w[0].upper() + w[1:] for w in wordlist]

    return capitalizedwordlist



def getsuffixwordlist(search, suffixlist, include_original=False) -> list:
    searchwordlist = []
    suffixwordlist = []

    if type(search) is list:
        searchwordlist = [w for w in search]
    elif type(search) is str:
        searchwordlist = [search]

    for searchstring in searchwordlist:
        word = searchstring.strip().lower()

        if include_original:
            wordlist = [word]
        else:
            wordlist = []

        if re.search(r"(%s)$" % '|'.join(EXCLUDED_ENDINGS), word):
            break

        for suffixformula in suffixlist:
            for ending in suffixformula['ending']:
                for suffix in suffixformula['suffix']:
                    if re.search(ending + r'$', word):

                        # exclude if contains the negated ending
                        valid = True
                        try:
                            for negativeending in suffixformula['negativeending']:
                                if re.search(negativeending + r'$', word):
                                    valid = False
                        except KeyError:
                            pass

                        # do not allow words to end in twice of substituted suffixes (or the related ones in list)
                        suffixes = [s for s in suffixformula['suffix'] if '1' not in s]
                        if suffixes:
                            suffixespattern = r"(%s)$" % '|'.join(suffixes)
                            # wordlist.append('SUFFIXPATTERN: ' + str(suffixespattern))
                            if re.search(suffixespattern, word):
                                valid = False

                        if valid:
                            if suffixformula['replace']:
                                s = re.sub(ending + r'$', suffix, word)
                                # s = ('[ending]' + ending + ' [suffix]' + suffix + ' word:' + word + ' s:' + s)
                            else:
                                s = word + suffix
                            wordlist.append(s)
        suffixwordlist.extend(wordlist)

    suffixwordlist = list(set(suffixwordlist)) # remove duplicates

    for i, w in enumerate(suffixwordlist):
        if w in searchwordlist:
            continue
        for ending in DISALLOWED_ENDINGS:
            if re.search(ending + r'$', w):
                suffixwordlist.pop(i)

    return suffixwordlist
