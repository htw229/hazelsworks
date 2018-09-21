DEFAULT_DIALECT = 'British'
DEFAULT_REPLACEMENTTYPE = 'suggested'
DEFAULT_NONDEFAULTDIALECT_REPLACEMENTTYPE = 'informal'

MAX_SEARCHPATTERNGENERATOR_ITERATIONS = 2000

# used when inputting searchwords to disallow tenses and suffixes
PROTECTED_WORD_MARKER = '#'

# number of search word patterns to combine for each regex finditer()
NUMBER_COMBINED_SEARCHES = 1 # TODO: find optimal number

WORD_PATTERN_GROUP = r"(?P<pk{pk}>{wordpattern})"

REPLACE_FIND_ANYWHERE = r"""\b(%s)\b(?=[^>]*?<)"""
REPLACE_FIND_QUOTES_ONLY = r"""\b(%s)\b(?=[^"”>]*?[^\s\w>]["”])(?=[^>]*?<)"""





SEARCH_OPTIONAL_PLACEHOLDER = r"<OPTIONAL>%s</OPTIONAL>"
SEARCH_OPTIONAL_PLACEHOLDER_SEARCH = r"[ \\]*\<OPTIONAL\>(.*)\<\/OPTIONAL\>[ \\]*"
SEARCH_OPTIONAL_PATTERN = "( %s | )"

SEARCH_FULL_STOP_PATTERN = r"[\.\,\!\?]"


# SEARCH_STRING_PATTERN = r"(?P<nonmutable>\w\W|\w+'s|(?P<punctuation>[^\w\s\$\|])|\s)+|((?P<word>(\w+-?)+)(?P<protected>(\$)+)?)|(\s)+|\|(?P<flags>((?P<protectedphrase>\$)|(?P<preservecase>~))+)"
# - nonmutable (includes punctuation, spaces, words of single letter, words that end in possessive)
# - word, (opt) protected
# - flags, protectedphrase or preservecase


# SEARCH_STRING_PATTERN_UNFORMATTED = r"(?P<markup>\[\w+\])|(?P<punctuation>[^\w\s\$\|-])|(?P<nonmutable>\w\W|\w+'s|\s)|((?P<word>(\w+-?)+)(?P<protectedword>(\$)+)?)|(\s)+|\|(?P<flags>((?P<protectedphrase>\$)|(?P<preservecase>~))+)"

# SEARCH_STRING_PATTERN_UNFORMATTED = r"(?P<markup>\[\w+\])|(?P<punctuation>[^\w\s\$\|-])|(?P<nonmutable>\w[^\w-]|\w+'s|\s)|((?P<word>(\w+-?)+)(?P<protectedword>(\$)+)?)|(\s)+|\|(?P<flags>((?P<protectedphrase>\$)|(?P<preservecase>~))+)"

# SEARCH_STRING_PATTERN_UNFORMATTED = r"\<(?P<exclude>(\w+-))\>|(?P<optional>\(\w+\))|\[(?P<markup>\w+)\]|(?P<punctuation>[^\w\s\$\|\-\<\>\(\)\[\]])|(?P<nonmutable>\w[^\w-]|\w+'s|\s)|((?P<word>(\w+-?)+)(?P<protectedword>(\$)+)?)|(\s)+|\|(?P<flags>((?P<protectedphrase>\$)|(?P<preservecase>~))+)"

# SEARCH_STRING_PATTERN_UNFORMATTED = r"\<(?P<exclude>(\w+-))\>|(?P<optional>\(\w+\))|\[(?P<markup>\w+)\]|(?P<punctuation>[^\w\s\$\|\-\<\>\(\)\[\]])|((?P<word>(\w+-?)+)(?P<protectedword>(\$)+)?)|(\s)+|\|(?P<flags>((?P<protectedphrase>\$)|(?P<preservecase>~))+)"

# SEARCH_STRING_PATTERN_UNFORMATTED = r"""\<(?P<exclude>(\w+-))\>|\((?P<optional>\w+)\]|\[(?P<markup>\w+)\]|(?P<punctuation>[^\w\$\|\-\<\>\(\)\[\]])|((?P<word>(\w+-?)+)(?P<protectedword>(\$)+)?)|(\s)+|\|(?P<flags>((?P<protectedphrase>\$)|(?P<preservecase>~))+)"""

SEARCH_STRING_PATTERN = r"(?P<protectedphrase>[\#]{3}$)|\<(?P<exclude>(\w+|-))\>|\[(?P<markup>\w+)\]|(?P<punctuation>[^\w\$\|\-\<\>\(\)\[\]\#])|((?P<word>(?P<mainword>\w+-?)+)(?P<protectedword>(\#)?)?)|(\s)+"

SEARCH_MARKUP = 'markup'
SEARCH_PUNCTUATION = 'punctuation'
SEARCH_WORD = 'word'
SEARCH_WORD_MAIN = 'mainword'
SEARCH_PROTECTED_WORD = 'protectedword'
SEARCH_PROTECTED_PHRASE = 'protectedphrase'
SEARCH_EXCLUDE = 'exclude'



# NOTE: don't think this is doing anything? since not marking words as dict in string (would be hard to test regex)
# SEARCH_STRING_PATTERN = SEARCH_STRING_PATTERN_UNFORMATTED.format(
#     # nonmutable=SEARCH_NONMUTABLE,
#     punctuation=SEARCH_PUNCTUATION,
#     word=SEARCH_WORD,
#     protectedword=SEARCH_PROTECTED_WORD,
#     flags=SEARCH_FLAGS,
#     protectedphrase=SEARCH_PROTECTED_PHRASE,
#     preservecase=SEARCH_PRESERVE_CASE,
#     exclude=SEARCH_EXCLUDE,
#     optional=SEARCH_OPTIONAL,
#     markup=SEARCH_MARKUP,
# )

DASH_REPLACEMENT_PATTERN = r"(|-|\s)"