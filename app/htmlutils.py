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
    paragraphs = [w for w in inputtext.split('\r\n') if w.strip() != '']
    text = r'<p>' + r'</p><p>'.join(paragraphs)
    return text