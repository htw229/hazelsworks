from django.core.exceptions import ObjectDoesNotExist

from bs4 import BeautifulSoup

import re

from app.models import Replacement, Topic, Reference
from app.debug import Debug
from app.htmlutils import addspan, linebreakstoparagraphs, getlinkhtml



debug = None



def topictexthtml(topic):
    global debug
    debug = Debug()

    text = topic.text

    text = formathtml2(text)

    # text = replacereferences(text)
    # text = replacereferenceswithquotes(text)
    # # text = linebreakstoparagraphs(text)
    #
    # text = formathtml(text)


    # topic link [t3]


    return text

def formathtml2(inputtext) -> str:
    global debug

    soup = BeautifulSoup()
    debug.sectionbreak('debug')

    # get sections
    sectionpattern = re.compile(
        r'(?P<excerpt>\<(?P<referencepk>\d+)\:(?P<excerptcontent>[^\>]*)\>)|\n(?P<header>[A-Z][^a-z\n]+)\n|\-{0,3} *(?P<example>"(?P<examplequote>.*?)"(?P<exampletrailer>.*?))\n|(?:(?P<l3>\-\-\-)|(?P<l2>\-\-)|(?P<l1>\-)) *(?P<listitem>.+)|(?P<p>.+)'
    )

    for match in sectionpattern.finditer(inputtext):
        # debug.add(match.string)
        groups = match.groupdict()

        if groups['excerpt']:
            # debug.add('EXCERPT', groups['referencepk'], groups['excerptcontent'])

            p = soup.new_tag('p')
            p.append(getreferencelink(groups['referencepk'], soup))
            soup.append(p)

            excerptdiv = soup.new_tag('div')
            excerptdiv['class'] = 'quoted'

            for paragraph in re.finditer('.+', groups['excerptcontent']):
                p = soup.new_tag('p')
                p.string = paragraph.group(0)
                excerptdiv.append(p)

            # excerptdiv.string = groups['excerptcontent']
            soup.append(excerptdiv)

        elif groups['header']:
            # debug.add('HEADER', groups['header'])
            p = soup.new_tag('p')
            p['class'] = 'contentheader'
            p.string = groups['header']
            soup.append(p)

        elif groups['example']:
            # debug.add('EXAMPLE', groups['examplequote'])

            # p = soup.new_tag('p')
            # p['class'] = 'l2'
            quote = soup.new_tag('span')
            quote['class'] = 'quote'
            quote.string = '"' + groups['examplequote'].strip() + '"'
            # p.append(quote)
            # p.append(groups['exampletrailer'])
            p = createparagraph([quote, groups['exampletrailer']], soup, paragraphclass='l2')

            debug.add('EXAMPLE')
            debug.add('p.strings', [s for s in p.strings])

            soup.append(p)

        elif groups['listitem']:
            # debug.add('LISTITEM', groups['listitem'])
            p = soup.new_tag('p')
            if groups['l1']:
                p['class'] = 'l1'
            elif groups['l2']:
                p['class'] = 'l2'
            elif groups['l3']:
                p['class'] = 'l3'

            p.string = groups['listitem']
            soup.append(p)

        elif groups['p']:
            # debug.add('P', groups['p'])
            p = soup.new_tag('p')
            p.string = groups['p']
            soup.append(p)



    for p in soup.find_all('p'):


        try:
            if "[" in p.string:
                p.string = 'FOUND REFERENCE'
        except TypeError:
            strings = [s for s in p.strings]
            if "[" in strings[-1]:
                strings[-1] = 'FOUND REFERENCE'
            # pass


    # divide excerpt into paragraphs

    # parse tags within each paragraph

    # inside sections, get paragraphs

    # div - nothing, list, excerpt
    # <> - start and end excerpt div
    # - - paragraph with class tag for levels (instead of doing ul/li do css list)



    s = soup.prettify()
    s = s + debug.html

    return s


def createparagraph(contents, soup, paragraphclass=None):
    if type(contents) != list:
        contents = [contents]

    p = soup.new_tag('p')
    if paragraphclass:
        p['class'] = paragraphclass

    for c in contents:
        if type(c) == str:
            p.append('STRING' + c)
        else:
            p.append(c)

    return p


def gettexttags(inputtext, soup) -> list:
    contentslist = []


    return contentslist

def getreferencelink(pk, soup):
    a = soup.new_tag('a')

    try:
        reference = Reference.objects.get(pk=int(pk))
        a['href'] = reference.url
        a.string = '[x]'
    except ObjectDoesNotExist:
        a.string = '[reference not found]'

    return a



def getlines(inputtext) -> list:
    return inputtext.split('\r\n')


def formathtml(inputtext) -> str:
    text = inputtext
    text = linebreakstoparagraphs(text)


    # quotes - "quote" [33]
    # prior to making list for simplicity of regex matching -

    # replace quotes (example quotes in {})
    quotepattern = r"\{(.+?)\}"
    quotetemplate = r'<span class="quote">\1</span>'
    text = re.sub(quotepattern, quotetemplate, text)

    # list
    listitemformats = [
        # (r"\<p\>\-\-\-([^\-].+?)\<\/p\>", r'<li class="level-three">%s</li>'),
        (r"\<p\>\-\-([^\-].+?)\<\/p\>", r'<li class="level-two">%s</li>'),
        (r"\<p\>\-([^\-].+?)\<\/p\>", r'<li class="level-one">%s</li>'),
    ]
    for listitemformat in listitemformats:
        text = re.sub(listitemformat[0], listitemformat[1] % r"\1".strip(), text)

    listpattern = r"(?<!\<\/li\>) *(?P<list>(?:\<li[^\>]*?\>.*?\<\/li\> *))(?=\<p|\<h|\Z)"
    listtemplate = r"<ul>\g<list></ul>"
    text = re.sub(listpattern, listtemplate, text)

    # headers ALL CAPS LINE
    # do this after paragraphs, it replaces <p></p> with <h4></h4>
    headerpattern = r"\<p\>([A-Z][^a-z]*?)\<\/p\>"
    headertemplate = r"<h4>%s</h4>"
    text = re.sub(headerpattern, headertemplate % r'\1', text)

    # emphasis *word* or new line (paragraph or list item) followed by -
    emphasisformats = [
        (r"\*(?P<emphasistext>[^\n\*\<\>]+?)\*",r"<span class='emphasis'>\g<emphasistext></span>"),
        (r"(?P<opentag>\<(?:li|p)[^\>]*?\>) *(?P<emphasistext>\w[^\-\n\<\>]+)(?=\- )", r"\g<opentag><span class='emphasis'>\g<emphasistext></span>"),
    ]
    # emphasistemplate = r"<span class='emphasis'>%s</span>"

    for emphasisformat in emphasisformats:
        text = re.sub(emphasisformat[0], emphasisformat[1], text)

    text = text.replace("<p>...</p>", "<p class='nobackground'>&nbsp;</p>")
    text = text.replace("<div class='quoted'></p>", "</p><div class='quoted'>")

    # for emphasispattern in emphasispatterns:
    #     text = re.sub(emphasispattern, emphasistemplate % r"\g<emphasistext>", text)

    # quotes "quote" [33]
    # spanreference = r"\<span class\='reference-inline'\>"
    # quotepattern = r' "(?P<quote>[^"]+?)"\W'
    # quotetemplate = r' "<span class="quote">\g<quote></span>" '
    # text = re.sub(quotepattern, quotetemplate, text)
    # text = re.sub(r'".*"', "quote", text)

    return text


def replacereferences(inputtext):
    global debug

    templatepattern = r"\[(?P<pk>\d+)\]"

    text = inputtext
    addedtextlength = 0  # increment starting position after every replacement
    pattern = re.compile(templatepattern)

    for match in pattern.finditer(inputtext):
        referencepk = int(match.group('pk'))

        try:
            reference = Reference.objects.get(pk=referencepk)

            # referencelink = reference.link
            if '[' in match.group():
                referencelink = getlinkhtml(reference.url, '[x]', reference.liststring)
            # elif '{' in match.group():
            #     referencelink = getlinkhtml(reference.url, reference.name)
            else:
                referencelink = '[incorrect markup]'
        except ObjectDoesNotExist:
            referencelink = '[reference missing]'

        replacetext = addspan(referencelink, 'reference-inline')
        text = text[:match.start() + addedtextlength] + replacetext + text[match.end() + addedtextlength:]
        addedtextlength += len(replacetext) - len(match.group())

    return text


def replacereferenceswithquotes(inputtext):
    global debug

    text = inputtext
    addedtextlength = 0
    pattern = re.compile(r"<(?P<pk>\d+):(?P<text>(.|\n)*?)>")

    for match in pattern.finditer(inputtext):
        referencepk = int(match.group('pk'))
        referencehtml = "From %s:\r\n" % getreferencelinkhtml(referencepk)

        quotedtext = addspan('\r\n' + match.group('text'), cssclass='quoted', tagname='div')

        replacetext = referencehtml + quotedtext
        text = text[:match.start() + addedtextlength] + replacetext + text[match.end() + addedtextlength:]
        addedtextlength += len(replacetext) - len(match.group())

    return text


def getreferencelinkhtml(referencepk, referencetemplate = '%s'):
    try:
        reference = Reference.objects.get(pk=referencepk)
        referencelink = getlinkhtml(reference.url, referencetemplate % reference.liststring, reference.liststring)

    except ObjectDoesNotExist:
        referencelink = '[reference missing]'

    return referencelink


# def parsetopictext(topic):
#
#     text = topic.text
#
#     if 'http' in topic.text:
#
#         pattern = r"(?<=[\<\[])(?:(?P<name>.+)\:|)(?P<url>https?\:\/\/[^\s]+)(?=[\:\]])"
#         for match in re.finditer(pattern, topic.text):
#             m = match.groupdict()
#
#             if not m['url']:
#                 continue
#             try:
#                 reference = Reference.objects.get(url=m['url'])
#             except ObjectDoesNotExist:
#                 reference = Reference(url=m['url'])
#
#                 if m['name']:
#                     reference.name = m['name']
#
#                 reference.save()
#
#             text = text.replace(match.group(0), str(reference.pk))



