import re

from app.models import Topic, Replacement, Dialect
from debug import Debug
import searchwords
import htmlutils
from __init__ import *

debug = None

def search(formdata) -> dict:
    global debug
    debug = None
    debug = Debug()

    searchstring = formdata['searchword'].lower().strip()

    results = {
        'search': searchstring,
        'error': None,
        'topicsbyname': [],
        'topicsbytext': [],
        'replacements': [],
        'dialectreplacements': [],
        'references': [],
    }

    # ensure not excluded word
    # TODO: create excluded words list (for now using prepositions)
    if searchstring in PREPOSITION_LIST:
        results['error'] = SEARCH_ERROR_EXCLUDEDWORD
        results['debug'] = debug
        return results

    # create list of searchwords
    # searchwordconjugates = searchwords.getirregularconjugates(searchstring)
    # searchwordlist = [searchstring]
    # if searchwordconjugates:
    #     searchwordlist = searchwordconjugates
    # else:
    #     searchwordlist = searchwords.getsuffixwordlist(searchstring)

    searchwordpattern = searchwords.getwordpattern(searchstring)['pattern']
    searchstringnoplural = ''

    if searchstring.endswith('s'):
        searchstringnoplural = searchstring[:len(searchstring)-1]
        debug.add(searchstringnoplural)
        searchwordpattern = r'(?:' + searchwordpattern + '|' + searchwords.getwordpattern(searchstringnoplural)['pattern'] + ')'




    debug.add(searchwordpattern)
    pattern = SEARCH_PATTERN_WRAPPER % searchwordpattern
    debug.add(pattern)

    # TODO: remove curly quotes on save topic

    # check topics
    for topic in Topic.objects.all():
        # debug.add('searching', topic.name)
        if searchstring in topic.name.lower() or (searchstringnoplural and searchstringnoplural in topic.name.lower()):
            results['topicsbyname'].append(topic)
            # debug.add('found topicsbyname')
            continue
        match = re.search(pattern, topic.text, re.IGNORECASE)
        if match:
            # excerptstartpos = match.start() - SEARCH_TOPIC_CHARS_BEFORE_AND_AFTER
            # if excerptstartpos < 0:
            #     excerptstartpos = 0
            #
            # excerptendpos = match.end() + SEARCH_TOPIC_CHARS_BEFORE_AND_AFTER
            # if excerptendpos > (len(topic.text) - 1):
            #     excerptendpos = len(topic.text) - 1

            excerpt = '...' + match.group('excerpt_start') + htmlutils.addspan(match.group('found_string'), cssclass='searchtopicfoundstring') + match.group('excerpt_end') + '...'


            # excerpt = topic.text[excerptstartpos:excerptendpos]

            results['topicsbytext'].append({
                'topic': topic,
                'excerpt': excerpt,
            })
            continue

            # elif s in topic.text.lower():
            #     results['topicsbytext'].append(topic)
            #     # debug.add('found topicsbytext')
            #     continue



    # check searchwords
    for r in Replacement.objects.all():
        texts = [r.searchstrings, r.suggestreplacement, r.considerreplacements, r.clarification]
        text = r'\r\n'.join([t for t in texts if t])
        match = re.search(pattern, text, re.IGNORECASE)

        if searchstring in text:
            debug.add(text)

        if match:
            results['replacements'].append(r)

    # check dialects
    if searchstring != DEFAULT_DIALECT.lower():
        for dialect in Dialect.objects.all():
            if searchstring == dialect.name.lower():
                for r in Replacement.objects.filter(dialect=dialect.name)[:SEARCH_MAX_DIALECT_RESULTS]:
                    results['dialectreplacements'].append(r)



    debug.timer('search finished')
    results['debug'] = debug

    return results