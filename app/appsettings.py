DEFAULT_DIALECT = 'British'
DEFAULT_REPLACEMENTTYPE = 'suggested'
DEFAULT_NONDEFAULTDIALECT_REPLACEMENTTYPE = 'informal'

MAX_SEARCHPATTERNGENERATOR_ITERATIONS = 2000

# used when inputting searchstrings to disallow tenses and suffixes
PROTECTED_WORD_MARKER = '#'
PROTECTED_PHRASE_MARKER = "###"

MIN_WORD_LENGTH_FOR_SUFFIX = 3

# number of search word patterns to combine for each regex finditer()
NUMBER_COMBINED_SEARCHES =5
# 10000 -> 34s
# 1 -> 4s
# 5 -> 3.2s
# 10 -> 3.9s
# 8 -> 3.7s
# 3 -> 3.3s
# remove word as separate search -> 3.1s (5 iterations)

WORD_PATTERN_GROUP = r"(?P<pk{pk}>{wordpattern})"

REPLACE_FIND_ANYWHERE = r"""\b(%s)\b(?=[^>]*?<)"""
REPLACE_FIND_QUOTES_ONLY = r"""\b(%s)\b(?=[^"”>]*?[^\s\w>]["”])(?=[^>]*?<)"""





SEARCH_OPTIONAL_PLACEHOLDER = r"<OPTIONAL>%s</OPTIONAL>"
SEARCH_OPTIONAL_PLACEHOLDER_SEARCH = r"[ \\]*\<OPTIONAL\>(.*)\<\/OPTIONAL\>[ \\]*"
SEARCH_OPTIONAL_PATTERN = "(?: %s | )"

SEARCH_FULL_STOP_PATTERN = r"[\.\,\!\?]"

# SEARCH_STRING_PATTERN = r"(?P<protectedphrase>[\#]{3}$)|\<(?P<exclude>(\w+|-))\>|\[(?P<markup>\w+)\]|(?P<punctuation>[^\w\$\|\-\<\>\(\)\[\]\#])|(?P<apostropheword>[\w\-]+\'[\w\-]+)|((?P<word>[\w\-]+)(?P<protectedword>(\#)+?)?)|(\s)+"
# note protected phrase ### must have preceding space

SEARCH_STRING_PATTERN = r"^(?P<protectedphrase>\#)|(?P<question>\?)$|(?P<endphrase>[\.\,\!])$|(?P<optional_words>\(\_\))|(?P<words>\_\_\_)|\[(?P<markup>\w+)\]|(?P<punctuation>[^\w\$\|\-\<\>\(\)\[\]\#]+?)|(?P<apostropheword>[\w\-]+\'[\w\-]+)|(?:(?P<word>[\w\-]+)(?P<protectedword>(\#)+?)?)"



SEARCH_MARKUP = 'markup'
SEARCH_PUNCTUATION = 'punctuation'
SEARCH_WORD = 'word'
# SEARCH_WORD_MAIN = 'mainword'
SEARCH_WORD_WITH_APOSTROPHE = 'apostropheword'
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

DASH_REPLACEMENT_PATTERN = r"(?:|\-|\s)"




# SEARCH
SEARCH_PATTERN_WRAPPER = r"(?P<excerpt_start>(?:(?:\w{0,15})\b[ \"\'\,]{1,2}){0,10})\b(?P<found_string>%s)\b(?P<excerpt_end>(?:(?:\w{0,15})\b[ \"\'\,]{0,3}){0,10})"
SEARCH_PATTERN_WRAPPER_REVERSE = r"\b%s\b"
SEARCH_MAX_DIALECT_RESULTS = 100