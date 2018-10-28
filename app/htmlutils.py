from django.urls import reverse
import re

def addspan(string, cssclass, wrapperstart='', wrapperend='', tagname='span'):
    '''
    :param string: plain text or html to be formatted
    :param cssclass: css class to reference in <span>
    :param wrapperstart: optional open/closing marks (such as parentheses)
    :param wrapperend: optional open/closing marks (such as parentheses)
    :return: <span> with css
    '''
    if not string:
        return ''

    s = "<" + tagname + " class='"

    s += cssclass
    s += "'>"
    s += wrapperstart + string + wrapperend

    s += "</" + tagname + ">"

    return s

def linebreakstoparagraphs(inputtext):

    paragraphs = [w for w in inputtext.split('\r\n')]

    # if double carriage returns, create blank paragraph
    blanklines = 0
    for i, p in enumerate(paragraphs):
        if not p and blanklines > 2:
            paragraphs[i] = '&nbsp;'
            blanklines = 0
        elif not p:
            blanklines += 1
        else:
            blanklines = 0
    paragraphs = [p for p in paragraphs if p]

    html = r'<p>' + r'</p><p>'.join(paragraphs) + r'</p>'
    return html

def getlinkhtml(url = '', text = 'link', mouseovertext ='', newbrowsertab = False, urlname = None, urlkwargs = None):
    """

    :param urldata: string of address verbatim
    :param text:
    :param mouseovertext:
    :param newbrowsertab: open in new browser tab (target='_blank')
    :return:
    """

    # if urlname is provided, use reverse lookup to get the url
    if urlname:
        url = reverse(urlname, kwargs=urlkwargs)


    s = r'<a href="' + url + r'"'
    s += r' title="' + str(mouseovertext) + '"'

    if newbrowsertab:
        s += r' target="_blank"'

    s += r'>'
    s += str(text)
    s += r'</a>'

    return s


def replacecurlyquotes(text) -> str:
    text = text. \
        replace('“', '"'). \
        replace('”', '"'). \
        replace("’", "'").\
        replace("’", "'")

    return text

def titlecase(inputtitle) -> str:
    words = re.split(r'(\W+)', inputtitle)
    lowercasewords = ['a', 'an', 'the']
    for i, w in enumerate(words):
        if w == w.lower(): #only change if nothing is capitalized
            if i == 0 or i == len(words) - 1:
                words[i] = w.capitalize()
            elif w not in lowercasewords and len(w) > 4:
                words[i] = w.capitalize()

    title = ' '.join(words)

    return title

Keep_Markup = 0
Delete_Markup = 1
Explain_Markup = 2
Explain_Markup_Verbose = 3

# TODO: for dialect searches, add search results from generic?

def searchwordformat(inputstring, title=False, markup=Explain_Markup, replacedashes=False) -> str:
    s = inputstring

    markup_explanations = [
        (r'\[(\w*)\]', r'(any \1)'),
        (r'\.', r''),
        (r'\(n\)', r' (noun)'),
        (r'#', r''),
        (r'___', r''),
        (r'\(_\)', r''),
        (r'\(s\)', r'(s)')
    ]

    markup_explanations_optional = [
        (r'^#(.*)', r'\1**'),
        (r'#', '*'),
        (r'\.$', r' (end of phrase)'),
        (r'\?', ' (question)'),
        (r'___', '(any words)'),
        (r'\(_\)', '(optional words)'),
    ]

    if replacedashes:
        s = s.replace('-', '')

    if markup == Explain_Markup:
        for m in markup_explanations:
            s = re.sub(m[0], m[1], s)
        for m in markup_explanations_optional:
            s = re.sub(m[0], '', s)
    elif markup == Explain_Markup_Verbose:
        for m in (markup_explanations_optional + markup_explanations):
            s = re.sub(m[0], m[1], s)
    elif markup == Delete_Markup:
        for m in (markup_explanations + markup_explanations_optional):
            s = re.sub(m[0], '', s)

    if title:
        s = titlecase(s)

    return s

#
# def replacematch(match, replacement, text):
#     text = text[:match.start() + addedtextlength] + replacementtext + text[match.end() + addedtextlength:]
#     addedtextlength += len(replacementtext) - len(match.group())
#
#     return text


def convertmarkup():
    markups = [
        {
            'opentag': '*',
            'closetag': '*',
            'wrapper': 'div',
            'class': 'emphasis',
        },
    ]

    # TODO: create markup for emphasis * and all caps into headers and lists and automatic example text



















