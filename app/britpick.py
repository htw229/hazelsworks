from .models import Replacement, Dialect, ReplacementExplanation, ReplacementCategory
from .debug import Debug
from .htmlutils import addspan, getlinkhtml, linebreakstoparagraphs

import app.appsettings as settings
import grammar

import re

debug = ''


findanywherepattern = r"""\b(%s)\b(?=[^>]*?<)"""
findinquotespattern = r"""\b(%s)\b(?=[^"”>]*?[^\s\w>]["”])(?=[^>]*?<)"""



def britpick(formdata):
    global debug
    debug = ''
    debug = Debug()

    searches = createsearches(formdata)
    debug.add(['number of searches:', len(searches)])

    text = createoutputtext(formdata['text'], searches)
    # debug.add(outputtext)

    text = postprocesstext(text)

    # debug.add(text)

    britpickeddata = {
        'text': text,
        'debug': debug,
    }


    debug.timer('britpick() finished')
    return britpickeddata



def createsearches(formdata) -> list:
    """
    :param formdata:
    :return: list of britpicksearch objects (1 per replacement object)
    """
    global debug


    # maxsearches = 25

    patternwrappersbycategory = getcategorypatternwrappers(formdata)
    searches = []

    i = 0
    for replaceobject in Replacement.objects\
        .filter(dialect=formdata['dialect'])\
        .filter(active=True)\
        .filter(category__in=patternwrappersbycategory.keys()):  # category won't be in there if not slected on form

        # get all searchwords with markup and suffixes and join in one regex search pattern

        # create regex pattern substring for each line (word) in searchwords as a list; this adds suffixes and replaces markup
        compiledsearchwords = []

        for s in replaceobject.searchwordlist:
            # combine with OR '|' to create the regex pattern substring for a single word
            compiledsearchword = '|'.join(createsearchwordpatterns(s, replaceobject))
            # then add it to the list
            compiledsearchwords.append(compiledsearchword)

        # join all the searchwordpatterns for an object to create a single regex pattern word string with OR (|) separating them
        objectsubpattern = '|'.join(compiledsearchwords)

        # create full regex pattern string with regex pattern wrapper
        objectpattern = patternwrappersbycategory[replaceobject.category_id] % objectsubpattern
        searches.append({'replaceobject': replaceobject, 'pattern': objectpattern})
        if 'test' in objectsubpattern:
            debug.add([objectpattern])

        i += 1
        # if i > 25:
        #     break

    # sort by longest searchword (a kludgy way of getting compound words to be found before single words)
    searches.sort(key=lambda search: search['replaceobject'].longestsearchwordlength, reverse=True)

    debug.timer('createsearches() finished')
    return searches





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

    patternsbycategory = {}
    for obj in ReplacementCategory.objects.all():
        if str(obj.pk) in formdata['replacement_categories']:
            pattern_template = ''
            if formdata['dialogue_option'] == 'ALLTEXT':
                pattern_template = findanywherepattern
                debug.add([obj, 'ALLTEXT','findanywherepattern'])
            elif formdata['dialogue_option'] == 'DIALOGUEONLY':
                pattern_template = findinquotespattern
                debug.add([obj, 'DIALOGUEONLY', 'findinquotespattern'])
            elif formdata['dialogue_option'] == 'SMART':
                if obj.dialogue:
                    pattern_template = findinquotespattern
                    debug.add([obj, 'SMART', 'findinquotespattern'])
                else:
                    pattern_template = findanywherepattern
                    debug.add([obj, 'SMART', 'findanywherepattern'])
            patternsbycategory.update({obj.pk: pattern_template})

    return patternsbycategory





def addsuffix(word):

    suffixlist = []

    # get the last consonant if word ends in vowel-consonant
    try:
        lastconsonant = re.search(r'[aeiou]([^aeiou])\b', word).group(1)
        vowelsuffixes = []
        nonvowelsuffixes = []
        for suffix in grammar.SUFFIX_LIST:
            if re.search(r'\b[aeiou]', suffix):
                vowelsuffixes.append(suffix)
            else:
                nonvowelsuffixes.append(suffix)
        suffixlist.extend([(lastconsonant + s) for s in vowelsuffixes])
        suffixlist.extend(nonvowelsuffixes)
    except AttributeError:
        suffixlist = grammar.SUFFIX_LIST

    wordwithsuffix = word + r'(|' + '|'.join(suffixlist) + r')'

    return wordwithsuffix


def getwordsuffixpattern(searchword) -> str:
    global debug
    debug.paused = True
    if searchword == "test of":
        debug.unpause()

    #TODO: do all separate words, sorted by length, then at end combine them as possible -- so store only one word at a time in the searchwords

    debug.add(['getwordsuffixpattern()',searchword])

    # no suffix: '#' in l
    if '#' in searchword:
        debug.add('# in searchword, not adding suffixes')
        s = searchword.replace('#', '')
        return s

    # get every word in searchword, with spaces and punctuation as their own groups; keeping "[]" and "-" inside words
    words = re.findall(r'\[?\w*\-?\w*\]?\^?|\s', searchword)
    # words = [x.replace(' ', r'\s') for x in words]
    debug.add(['words', words])
    # find the index of the word to add suffixes to in searchword
    pos = -1
    if len(words) == 1:
        pos = 0
    else: # multiple words
        try:
            # if word pre-defined, choose that one
            pos = words.index([s for s in words if '^' in s][0])
            words[pos] = words[pos].replace(r'^', '') # remove ^ symbol
            debug.add(['^ in', words[pos]])
        except IndexError: # if word is not pre-defined
            # traverse list
            # i = position of word, s = word starting from end
            for i, s in reversed(list(enumerate(words))):
                # if word is space or punctuation, skip it
                if not re.match('\w', s): #skip punctuation and spaces
                    debug.add([i, '"' + s + '"', 'not a word, continuing'])
                    continue
                if '[' in s or ']' in s: #skip markup
                    debug.add ([i, s, 'has markup, continuing'])
                    continue
                elif s in grammar.PREPOSITION_LIST: #skip prepositions
                    debug.add([i, s, 'is a preposition, continuing'])
                    continue
                else:
                    pos = i
                    debug.add(['choosing', i, s])
                    break

    if pos == -1:
        debug.add(('no word to add suffixes to found in ' + searchword + ':' + str(debug)))
        return searchword

    words[pos] = addsuffix(words[pos])
    debug.add(['pos', pos, words[pos]])
    # firstwords = ' '.join(words[:pos-1])
    # firstwords = re.escape(firstwords)
    # lastwords = ' '.join(words[pos+1:])
    # lastwords = re.escape(lastwords)
    # searchwordpattern = firstwords + ' ' + words[pos] + ' ' + lastwords
    searchwordpattern = ' '.join(words).replace('  ', '\s')
    debug.add(['searchwordpattern', searchwordpattern])

    # TODO: when searching, ignore punctuation after inputtext words (such as ! or ? or ,), but make punctuation in searchwords mandatory (allows narrowing down search, such as 'right?' 'really?'; allow adding suffixes to words with punctuation -- if do not want to transform them, put right#? or right?# as searchword in database

    debug.paused = False

    return searchwordpattern







def createsearchwordpatterns(searchword, britpickobj) -> list:
    '''

    :param searchword: string of single (or compound) word
    :param britpickobj:
    :return: list of regex patterns for single searchword with substitutions made and suffixes added
    '''

    global debug

    wordsuffixpattern = getwordsuffixpattern(searchword)
    return [wordsuffixpattern]

    # # TODO: is this actually working, though?
    # # REGEX ESCAPING: retain special characters in search
    # # (such as ?, which can help limit found words);
    # # escape prior to substituting markup (substitutes may contain regex)
    # # (errors occur if done earlier than try/except below)
    #
    # # TODO: count apostrophe and dash as word?
    #
    #
    #
    # # '#' indicates that cannot add suffix to it and cannot have dash or letter after it
    # if '#' in searchword:
    #     wordsuffixpattern = re.escape(searchword.replace('#',''))
    #     wordsuffixpattern += r'[^-a-zA-Z]+?'
    # else:
    #     # create generic regex pattern for with/without suffix
    #     suffixpattern = r'(|' + '|'.join(grammar.SUFFIX_LIST) + r')'
    #
    #     # create patternlist with individual searchwords and suffixes
    #     try:
    #         # will fail if rsplit returns only 1 string (ie if single word)
    #         word, preposition = searchword.rsplit(None, 1)
    #         if preposition in grammar.PREPOSITION_LIST:
    #             # debug.add([word, preposition], max=20)
    #             wordsuffixpattern = re.escape(word) + suffixpattern + ' ' + preposition
    #             # debug.add(searchword)
    #         else:
    #             raise ValueError('not a preposition')
    #     except ValueError:
    #         wordsuffixpattern = re.escape(searchword) + suffixpattern
    #
    # # dash in word can be dash, space or no space (ie ice-cream matches ice cream, icecream and ice-cream)
    # wordsuffixpattern = wordsuffixpattern.replace(r'\-', r"[-\s]*")
    #
    # patternlist = [wordsuffixpattern]

    # markup always has '[', so skip objects that don't have character
    if '[' not in searchword:
        return patternlist

    for m in grammar.MARKUP_LIST:
        for pattern in [p for p in patternlist]:
            if m['markup'] in pattern:
                # remove the string that has markup still in it
                patternlist.remove(pattern)
                # create a list of strings with words substituted for markup
                newpatterns = [pattern.replace(m['markup'], w) for w in m['wordlist']]
                patternlist.extend(newpatterns)

    # debug.timer('createsearchwordpatterns() finished')
    return patternlist



def createoutputtext(inputtext, searches):
    '''

    :param test:
    :param searches:
    :param dialectname:
    :param matchoption:
    :return: html formatted output text
    '''
    global debug

    text = inputtext + '<'

    for search in searches:
        text = replacetext(text, search)


    debug.timer('createoutputtext() finished')
    return text


def replacetext(inputtext, search):
    global debug

    text = inputtext
    addedtextlength = 0     # increment starting position after every replacement
    pattern = re.compile(search['pattern'].replace(' ', ''), re.IGNORECASE)

    if 'test' in search['pattern']:
        debug.add(['replacetext()', search['pattern']])
        debug.add(['inputtext', inputtext])

    for match in pattern.finditer(inputtext):
        # replacementtext = createreplacetext(r'{' + match.group() + ' ', search['replaceobject']) + r'}'
        replacementtext = r'<' + createreplacementhtml(match.group(), search['replaceobject'].pk) + r'>'
        text = text[:match.start() + addedtextlength] + replacementtext + text[match.end() + addedtextlength:]
        addedtextlength += len(replacementtext) - len(match.group())

    return text





# ------------------------------------
# CREATE AND FORMAT REPLACEMENT TEXTS
# ------------------------------------

def createreplacementhtml(inputtext, replacementpk):
    global debug
    # templatepath = os.path.dirname(os.path.dirname(__file__)) + r'/templates/inline_replacement_python.html'
    # replacementhtml = open(templatepath, 'r').read()
    #
    # replacementdata = {
    #     'inputtext': inputtext,
    #     'suggestreplacement': replacement.suggestreplacement,
    #     'considerreplacements': ', '.join(replacement.considerreplacementlist),
    #     'clarification': replacement.clarifyreplacementstring,
    #     'category': replacement.category.name,
    #     'explanation': str(replacement.explanations),
    #     'topic': str(replacement.topics),
    # }
    #
    # html = replacementhtml.format(**replacementdata)


    html = r'{% include "inline_replacement.html" with replacement=replacements.' + str(replacementpk) + r' inputtext="' + inputtext + r'" %}'

    debug.add([inputtext, replacementpk, Replacement.objects.get(pk=replacementpk)])
    return html

def createreplacetext(textstring, britpickobj):
    '''
    :param textstring: string from the input text
    :param britpickobj: britpickfindreplace object
    :return: span with css formatting
    '''

    global debug
    # debug.timer('createreplacetext() start')

    # format original string
    textstring = addspan(textstring, 'found word')

    # create replacement text that will be in []
    stringlist = []

    if britpickobj.suggestreplacement:
        if britpickobj.category.name == 'mandatory':
            stringlist.append(addspan(britpickobj.suggestreplacement, 'mandatory'))
        else:
            stringlist.append(addspan(britpickobj.suggestreplacement, 'suggestreplacement'))
    if britpickobj.category.name == 'suggested':
        c = ', '.join(w for w in britpickobj.considerreplacementlist)
        stringlist.append(addspan(c, 'considerreplacements'))

    # add explanations
    if britpickobj.clarifyexplanationspan:
        if len(stringlist) == 0:
            # if no other text, then don't add parenthesis
            stringlist.append(addspan(britpickobj.clarifyexplanationspan, 'clarification'))
        else:
            stringlist.append(addspan(britpickobj.clarifyexplanationspan, 'clarification', '(', ')'))

    # add topic
    for topic in britpickobj.topics.all():
        stringlist.append(addspan(topic.linkhtml, 'topiclink'))

    # if it's mandatory and there's no replacement/explanation, then add generic explanation
    if britpickobj.category.name == 'mandatory' and len(stringlist) == 0:
        stringlist.append(addspan(ReplacementExplanation.objects.get(name='not used').text, 'clarification'))

    s = ' '.join(stringlist)
    s = addspan(s, 'replacement', '[', ']')

    # combine texts
    text = addspan(textstring, 'foundword') + ' ' + s

    # debug.timer('createreplacetext()')
    return text



def postprocesstext(text):
    # remove created {}
    text = text.replace('<', '').replace('>', '')
    # create line breaks
    text = linebreakstoparagraphs(text)

    return text