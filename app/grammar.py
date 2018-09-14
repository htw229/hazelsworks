
SUFFIX_LIST = [
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

PREPOSITION_LIST = [
    'to',
    'up',
    'out',
    'of',
    'with',
    'over',
    'it',
    'that',
]

MARKUP_LIST = [

    {'markup': '\[number\]',
     'wordlist': ['\d+', '\d+st', '\d+nd', '\d+th', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight',
                 'nine', 'ten', 'first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth',
                 'tenth', 'eleventh', 'twelfth', 'thirteenth', 'fourteenth', 'fifteenth', 'sixteenth', 'seventeenth',
                 'eighteenth', 'nineteenth', 'twentieth', 'thirtieth', 'fourtieth', 'fiftieth', 'hundredth',
                 'thousandth', 'millionth']},

    {'markup': '\[month\]',
     'wordlist': ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sept', 'oct', 'nov', 'dec', 'january',
                'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november',
                'december']},

    {'markup': '\[word\]',
     'wordlist': [r'([\w\']*?){1,3}']}, # matches 1-3 words (including apostrophe); does not match 0 so can use it to narrow down matches # TODO: doesn't quite work right

    {'markup': '\[\]',
     'wordlist': []},

    {'markup': '\[s\]',
     'wordlist': SUFFIX_LIST}, # use this to denote word that gets suffix (use if the word is not the one right before a preposition or at the end of the phrase
]

#TODO: add british spellings and irregular verbs, unusual endings (ie adding extra consonant)