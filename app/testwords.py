from __init__ import *
import searchwords
import re
import random
from app.models import Replacement
from django.core.exceptions import ObjectDoesNotExist

testtext = """

this is a @.
"this is a @ in quotes."

this is a plural @s.
this is a @ in the middle of a phrase.
is this a @?

we are @ing here.
we will be @.

"""


"""
random choice from markup, random word not in markup
random word for ___ and (_)
conjugation - irregular and regular
protected words and phrases

excluded words


hardcoded:
- with and without end punctuation
- with and without words markers ___
"""

# transforms={
#     'w': None,
#     'changecase': lambda w: w.capitalize() if w == w.lower() else w.lower(),
#     '':,
#
#
# }


def gettestingtext(replacementpk) -> str:
    text = str(replacementpk) + ': \r\n'
    teststrings = []

    try:
        r = Replacement.objects.get(pk=replacementpk)
    except ObjectDoesNotExist as e:
        return str(e)

    wordslist = r.searchwordlist + r.excludedwordlist
    for w in wordslist:
        teststrings.extend(getsearchwordvariants(w))

    text += '\r\n'.join(teststrings)

    return text




def getsearchwordvariants(searchstring) -> list:
    constructors = []

    ignorecase = not any(x.isupper() for x in searchstring)

    pattern = re.compile(SEARCH_STRING_PATTERN, re.IGNORECASE)
    matches = [m for m in re.finditer(pattern, searchstring)]

    for match in matches:
        matchgroups = match.groupdict()

        # get word
        word = matchgroups['protected_word'] if matchgroups['protected_word'] else None
        word = matchgroups['plural_protected_word'] if matchgroups['plural_protected_word'] and not word else word
        word = matchgroups['noun_protected_word'] if matchgroups['noun_protected_word'] and not word else word
        word = matchgroups['word'] if matchgroups['word'] and not word else word

        if matchgroups['optional_words_marker'] or matchgroups['words_marker']:
            constructors.append([ # get random words 0-3
                '',
                'one',
                'one two',
                'one two three',
            ])

        elif matchgroups['markup']:
            try:
                constructors.append(
                    [random.choice(MARKUP[matchgroups['markup']]) for _ in range(3)]
                )
            except KeyError as e:
                constructors.append(['MARKUP ERROR: ' + str(e)])
        elif matchgroups['punctuation']:
            constructors.append([matchgroups['punctuation']])
        elif word:
            # required to test
            wordvariants = [word]
            wordvariants.extend(searchwords.getsuffixwordlist(word, PLURALS))
            wordvariants.extend(searchwords.getsuffixwordlist(wordvariants, POSSESSIVES))
            wordvariants.extend(searchwords.getspellingvariants([word]))

            # choose randomly to test
            possiblevariants = []
            possiblevariants.extend(searchwords.getconjugates(word, IRREGULAR_CONJUGATES))
            possiblevariants.extend(searchwords.getsuffixwordlist(word, REGULAR_CONJUGATES))

            # combine
            wordvariants.extend(random.choice(possiblevariants) for _ in range(5))

            wordvariants = list(set(list(wordvariants)))

            if not ignorecase:
                # do something
                pass
            if '-' in word:
                # do something
                pass

            constructors.append(wordvariants)

    teststrings = ['']
    for constructor in constructors:
        newstrings = []
        for i, s in enumerate(teststrings):
            for variant in constructor:
                newstrings.append(s + variant)
        teststrings = [w for w in newstrings]

    return teststrings