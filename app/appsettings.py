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

REPLACE_FIND_ANYWHERE = r"""\b(%s)(?=[^>]*?<)"""
REPLACE_FIND_QUOTES_ONLY = r"""\b(%s)(?=[^\>"]*?(\<[^"]*?\>)*?[^\>"]*?[\,\.\!\?]")"""

EXCLUDE_TEXT_MARGIN = 25
PHRASE_BOUNDARY_MARKERS = [r'.', '\r\n', r'"', r'<', r'>', r',']


#SEARCHWORDS
TRIE_SEARCHWORD_PATTERN = False

OPTIONAL_WORD_PLACEHOLDER = r"<OPTIONAL>%s</OPTIONAL>"
OPTIONAL_WORD_PLACEHOLDER_PATTERN = r"[ \\]*\<OPTIONAL\>(.*)\<\/OPTIONAL\>[ \\]*"
OPTIONAL_WORD_PATTERN = "(?: %s | )"

SEARCH_FULL_STOP_PATTERN = r"[\.\,\!\?]"

# TODO: do we still need pural protected word if we have noun protected word?
SEARCH_STRING_PATTERN = r"^(?P<protected_phrase>\#)|(?P<question>\?)$|(?P<end_punctuation>[\.\,\!])$|(?P<optional_words_marker>\(\_\))|(?P<words_marker>\_\_\_)|\[(?P<markup>\w+)\]|(?P<punctuation>[^\w\$\|\-\<\>\(\)\[\]\#]+)|(?P<protected_word>[\w\-]+\'[\w\-]+|[\w\-]+(?=\#))|(?P<plural_protected_word>[\w\-]+)\(s\)|(?P<noun_protected_word>[\w\-]+)\(n\)|(?P<word>[\w\-]+)"


DASH_REPLACEMENT_PATTERN = r"(?:|\-|\s)"


# SEARCH
MAKE_LOWERCASE = False

SEARCH_PATTERN_WRAPPER = r"(?P<excerpt_start>(?:(?:\w{0,15})\b[ \"\'\,]{1,2}){0,10})\b(?P<found_string>%s)\b(?P<excerpt_end>(?:(?:\w{0,15})\b[ \"\'\,]{0,3}){0,10})"
SEARCH_PATTERN_WRAPPER_REVERSE = r"\b%s\b"
SEARCH_MAX_DIALECT_RESULTS = 100