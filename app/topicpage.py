from django.core.exceptions import ObjectDoesNotExist

import re

from app.models import Replacement, Topic, Reference
from app.debug import Debug
from app.htmlutils import addspan, linebreakstoparagraphs, getlinkhtml

debug = None

# def britpicktopic(topic):
#     global debug
#     debug = Debug()
#
#     debug.add(['topic found: ', topic])
#
#     responsedata = {
#         'topic': topic,
#         'topichtml': topictexthtml(topic.text),
#         'references': topic.references.all(),
#         'searchwordobjects': Replacement.objects.filter(topics__pk=topic.pk),
#         'debug': debug.html,
#         'showdebug': True,
#     }
#
#     return responsedata


def topictexthtml(topic):
    global debug
    debug = Debug()

    text = topic.text

    text = replacereferences(text)
    text = replacereferenceswithquotes(text)
    # text = linebreakstoparagraphs(text)

    text = formathtml(text)


    # topic link [t3]


    return text


def formathtml(inputtext) -> str:
    text = inputtext
    text = linebreakstoparagraphs(text)


    # quotes - "quote" [33]
    # prior to making list for simplicity of regex matching -

    # replace quotes (example quotes in {})
    quotepattern = r"\{(.+)\}"
    quotetemplate = r'"<span class="quote">\1</span>"'
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



