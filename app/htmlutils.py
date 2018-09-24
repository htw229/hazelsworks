from django.urls import reverse

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

