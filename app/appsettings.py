DEFAULT_DIALECT = 'British'
DEFAULT_REPLACEMENTTYPE = 'suggested'
DEFAULT_NONDEFAULTDIALECT_REPLACEMENTTYPE = 'informal'

# used when inputting searchwords to disallow tenses and suffixes
PROTECTED_WORD_MARKER = '#'

# number of search word patterns to combine for each regex finditer()
NUMBER_COMBINED_SEARCHES = 1 # TODO: find optimal number

WORD_PATTERN_GROUP = r"(?P<pk{pk}>{wordpattern})"



SEARCH_MARKUP = 'markup'
SEARCH_NONMUTABLE = 'nonmutable'
SEARCH_PUNCTUATION = 'punctuation'
SEARCH_WORD = 'word'
SEARCH_PROTECTED_WORD = 'protectedword'
SEARCH_FLAGS = 'flags'
SEARCH_PROTECTED_PHRASE = 'protectedphrase'
SEARCH_PRESERVE_CASE = 'preservecase'
SEARCH_EXCLUDE = 'exclude'
SEARCH_OPTIONAL = 'optional'


# SEARCH_STRING_PATTERN = r"(?P<nonmutable>\w\W|\w+'s|(?P<punctuation>[^\w\s\$\|])|\s)+|((?P<word>(\w+-?)+)(?P<protected>(\$)+)?)|(\s)+|\|(?P<flags>((?P<protectedphrase>\$)|(?P<preservecase>~))+)"
# - nonmutable (includes punctuation, spaces, words of single letter, words that end in possessive)
# - word, (opt) protected
# - flags, protectedphrase or preservecase


# SEARCH_STRING_PATTERN_UNFORMATTED = r"(?P<markup>\[\w+\])|(?P<punctuation>[^\w\s\$\|-])|(?P<nonmutable>\w\W|\w+'s|\s)|((?P<word>(\w+-?)+)(?P<protectedword>(\$)+)?)|(\s)+|\|(?P<flags>((?P<protectedphrase>\$)|(?P<preservecase>~))+)"

# SEARCH_STRING_PATTERN_UNFORMATTED = r"(?P<markup>\[\w+\])|(?P<punctuation>[^\w\s\$\|-])|(?P<nonmutable>\w[^\w-]|\w+'s|\s)|((?P<word>(\w+-?)+)(?P<protectedword>(\$)+)?)|(\s)+|\|(?P<flags>((?P<protectedphrase>\$)|(?P<preservecase>~))+)"

SEARCH_STRING_PATTERN_UNFORMATTED = r"\<(?P<exclude>(\w+-))\>|(?P<optional>\(\w+\))|\[(?P<markup>\w+)\]|(?P<punctuation>[^\w\s\$\|\-\<\>\(\)\[\]])|(?P<nonmutable>\w[^\w-]|\w+'s|\s)|((?P<word>(\w+-?)+)(?P<protectedword>(\$)+)?)|(\s)+|\|(?P<flags>((?P<protectedphrase>\$)|(?P<preservecase>~))+)"

SEARCH_STRING_PATTERN = SEARCH_STRING_PATTERN_UNFORMATTED.format(
    nonmutable=SEARCH_NONMUTABLE,
    punctuation=SEARCH_PUNCTUATION,
    word=SEARCH_WORD,
    protectedword=SEARCH_PROTECTED_WORD,
    flags=SEARCH_FLAGS,
    protectedphrase=SEARCH_PROTECTED_PHRASE,
    preservecase=SEARCH_PRESERVE_CASE,
    exclude=SEARCH_EXCLUDE,
    optional=SEARCH_OPTIONAL,
    markup=SEARCH_MARKUP,
)

DASH_REPLACEMENT_PATTERN = r"(|-|\s)"