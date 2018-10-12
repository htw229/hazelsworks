from .models import Replacement, Dialect, ReplacementExplanation, ReplacementCategory
from .debug import Debug
# from .htmlutils import addspan, getlinkhtml, linebreakstoparagraphs
import htmlutils
from __init__ import *


import re
import html

import collections

debug = ''

searchpatterns = {
    'DIALOGUEONLY':(REPLACE_FIND_QUOTES_ONLY, REPLACE_FIND_QUOTES_ONLY),
    'ALLTEXT':(REPLACE_FIND_ANYWHERE, REPLACE_FIND_ANYWHERE),
    'SMART':(REPLACE_FIND_ANYWHERE, REPLACE_FIND_QUOTES_ONLY),
}




def britpick(formdata):
    global debug
    debug = ''
    debug = Debug()

    searchwords = getsearchwords(formdata)
    debug.add('SEARCHWORDS', len(searchwords))
    debug.timer('getsearchwords()')

    text = formatinputtext(formdata['text'])

    debug.sectionbreak()

    i = 0
    for searchpattern, ignorecase in searchpatterngenerator(searchwords, formdata):
        text = maketextreplacements(searchpattern, text, ignorecase)
        i += 1
        if i > 10000: # prevent infinite loop if something goes wrong (generator has while loop)
            break

    debug.add('REGEX ITERATIONS', i)
    debug.timer('maketextreplacements()')


    text = postprocesstext(text)

    # debug.timer('britpick()')

    britpickeddata = {
        'text': text,
        'debug': debug,
    }

    return britpickeddata


def formatinputtext(inputtext) -> str:
    text = htmlutils.replacecurlyquotes(inputtext)

    return text



def getsearchwords(formdata) -> list:
    global debug

    searchwords = []
    patternsbycategory = getcategorypatternwrappers(formdata)

    for r in Replacement.objects\
        .filter(dialect=formdata['dialect'])\
        .filter(active=True)\
        .filter(category__in=formdata['replacement_categories']):

        patternwrapper = patternsbycategory[r.category_id]

        # if r.searchwords:
        #     debug.add(r.searchwords)

        if not r.searchwords:
            debug.add('ERROR: no searchwords in', r)
            continue

        for w in r.searchwords:
            # if 'pregnant' in w['pattern']:
            #     debug.add(w)
            w['patternwrapper'] = patternwrapper
            w['obj'] = r
            searchwords.append(w)

    searchwords = sorted(searchwords, key=lambda w: w['length'], reverse=True)

    return searchwords


def getcategorypatternwrappers(formdata) -> dict:
    """
    takes the submitted formdata dialogue_option
    and returns a dict of patterns either in quotes or not
    for each type of category (ie mandatory, suggested, informal, slang)
    to use later when forming the pattern template for each word
    :param formdata: dict
    :return patternsbycategory: dict
    """
    global debug

    patternsbycategory = collections.defaultdict()
    for obj in ReplacementCategory.objects.all():
        if str(obj.pk) in formdata['replacement_categories']:
            pattern_template = ''
            if formdata['dialogue_option'] == 'ALLTEXT':
                pattern_template = REPLACE_FIND_ANYWHERE
            elif formdata['dialogue_option'] == 'DIALOGUEONLY':
                pattern_template = REPLACE_FIND_QUOTES_ONLY
            elif formdata['dialogue_option'] == 'SMART':
                if obj.dialogue:
                    pattern_template = REPLACE_FIND_QUOTES_ONLY
                else:
                    pattern_template = REPLACE_FIND_ANYWHERE
            patternsbycategory[obj.pk] = pattern_template


    return patternsbycategory



def searchpatterngenerator(searchwords, formdata) -> list:
    global debug

    # get pattern of next searchword
    # then get patterns of next one, if matches include it
    # until get NUMBER_COMBINED_SEARCHES of words
    # then combine them with wrapper

    iterations = 0
    while len(searchwords) > 0 and iterations < MAX_SEARCHPATTERNGENERATOR_ITERATIONS:
        iterations += 1

        nextwords = [searchwords.pop(0)]
        ignorecase = nextwords[0]['ignorecase']

        for i, word in enumerate(searchwords):
            if len(nextwords) == NUMBER_COMBINED_SEARCHES:
                break

            # if 'is all' in word['pattern']:
            #     debug.add('searchpatterngenerator- is all')
            #     debug.add(word['obj'])

            if word['patternwrapper'] == nextwords[0]['patternwrapper'] \
                and word['ignorecase'] == ignorecase \
                and word['obj'] not in [w['obj'] for w in nextwords]: # cannot have multiple regex groups with same pk
                nextwords.append(searchwords.pop(i))

        # debug.add(['nextwords', [w['obj'].pk for w in nextwords]])

        wordspatterns = []
        for word in nextwords:
            wordspatterns.append(WORD_PATTERN_GROUP.format(pk=word['obj'].pk, wordpattern=word['pattern']))

        patternwrapper = nextwords[0]['patternwrapper']
        pattern = patternwrapper % '|'.join(wordspatterns)

        yield (pattern, ignorecase)



def maketextreplacements(patternstring, inputtext, ignorecase) -> str:
    global debug

    if '688' in patternstring:
        debug.sectionbreak()
        debug.add(patternstring)
        debug.sectionbreak()

    try:
        if ignorecase:
            pattern = re.compile(patternstring, re.IGNORECASE)
        else:
            pattern = re.compile(patternstring)
    except:
        debug.add("regex error")
        debug.add(patternstring)
        return inputtext + '| pattern error:  ' + patternstring + '  |'


    text = inputtext + ' <'
    # debug.add(['text', text])

    addedtextlength = 0  # increment starting position after every replacement

    for match in pattern.finditer(text):
        # debug.add(['match group', match.groupdict()])



        for groupname in match.groupdict().keys():
            if match.groupdict()[groupname]:
                # debug.add(['OBJECT PK FOUND=', groupname])
                pk = groupname[2:] # trim first two characters ('pk456' -> '456')
                replacementtext = r'<' + createreplacementhtml(match.group(), pk) + r'>'

                valid = True
                r = Replacement.objects.get(pk=pk)

                if r.excludepatterns:
                    for excludepattern in r.excludepatterns:
                        # debug.sectionbreak()
                        # debug.add('match.start()', match.start())

                        matchstartpos = match.start() + addedtextlength
                        minstartpos = matchstartpos - EXCLUDE_TEXT_MARGIN
                        startpositions = [0, minstartpos]

                        matchendpos = match.end() + addedtextlength
                        maxendpos = matchendpos + EXCLUDE_TEXT_MARGIN
                        endpositions = [maxendpos]

                        for marker in PHRASE_BOUNDARY_MARKERS:
                            if marker not in excludepattern:
                                p = text.rfind(marker, minstartpos, matchstartpos)
                                if p > -1:
                                    startpositions.append(p)

                                p = text.find(marker, matchendpos, maxendpos)
                                if p > -1:
                                    endpositions.append(p)

                        startpos = sorted(startpositions)[-1]
                        endpos = sorted(endpositions)[0]

                        textchunk = text[startpos:endpos]

                        debug.sectionbreak()
                        debug.add(match.group())
                        debug.add(excludepattern, loop='excludepatterns')
                        debug.add('startpos', startpos, 'endpos', endpos)
                        debug.add(textchunk)
                        debug.sectionbreak()

                        if re.search("[A-Z]", excludepattern):
                            compiledexcludepattern = re.compile(excludepattern)
                        else:
                            compiledexcludepattern = re.compile(excludepattern, re.IGNORECASE)

                        if compiledexcludepattern.search(textchunk):
                            debug.add('invalidated')
                            valid = False
                            break

                if valid:
                    text = text[:match.start() + addedtextlength] + replacementtext + text[match.end() + addedtextlength:]
                    addedtextlength += len(replacementtext) - len(match.group())

    outputtext = text[:-2] # remove added '<' from text


    return outputtext



def createreplacementhtml(inputtext, replacementpk):
    global debug

    s = r"{% include 'inline_replacement.html' with replacement=replacements." + str(replacementpk) + r" inputtext='" + html.escape(inputtext) + r"' %}"

    # debug.add([inputtext, replacementpk, Replacement.objects.get(pk=replacementpk)])
    return s


def postprocesstext(text):
    # remove created {}
    text = text.replace('<', '').replace('>', '')
    # create line breaks
    text = htmlutils.linebreakstoparagraphs(text)

    return text