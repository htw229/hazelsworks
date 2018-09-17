DEFAULT_DIALECT = 'British'
DEFAULT_REPLACEMENTTYPE = 'suggested'
DEFAULT_NONDEFAULTDIALECT_REPLACEMENTTYPE = 'informal'

# used when inputting searchwords to disallow tenses and suffixes
PROTECTED_WORD_MARKER = '#'

# number of search word patterns to combine for each regex finditer()
NUMBER_COMBINED_SEARCHES = 5

WORD_PATTERN_GROUP = r"(?P<pk{pk}>{wordpattern})"