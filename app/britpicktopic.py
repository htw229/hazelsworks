from django.core.exceptions import ObjectDoesNotExist

import re

from .models import Replacement, Topic, Reference
from .debug import Debug
from .htmlutils import addspan, linebreakstoparagraphs, getlinkhtml

debug = None

def britpicktopic(topic):
    global debug
    debug = Debug()

    debug.add(['topic found: ', topic])

    text = topic.text


    referencepattern = r"[\[\{](?P<pk>\d+)[\}\]]"
    text = replacereferences(text, referencepattern)
    text = replacereferenceswithquotes(text)

    text = linebreakstoparagraphs(text)

    responsedata = {
        'topic': topic,
        'topichtml': text,
        'references': topic.references.all(),
        'searchwordobjects': Replacement.objects.filter(topics__pk=topic.pk),
        'debug': debug.html,
        'showdebug': True,
    }


    return responsedata


def replacereferences(inputtext, templatepattern):
    global debug

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
            elif '{' in match.group():
                referencelink = getlinkhtml(reference.url, reference.name)
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


def parsetopictext(topic):

    text = topic.text

    if 'http' in topic.text:

        pattern = r"(?<=[\<\[])(?:(?P<name>.+)\:|)(?P<url>https?\:\/\/[^\s]+)(?=[\:\]])"
        for match in re.finditer(pattern, topic.text):
            m = match.groupdict()

            if not m['url']:
                continue
            try:
                reference = Reference.objects.get(url=m['url'])
            except ObjectDoesNotExist:
                reference = Reference(url=m['url'])

                if m['name']:
                    reference.name = m['name']

                reference.save()

            text = text.replace(match.group(0), str(reference.pk))


# def addtopicreferences(topic):
#
#     referencepattern = r"(?<=[\<\[])(?P<pk>\d+)(?=[\:\]])"
#
#     for match in re.finditer(referencepattern, topic.text):
#         pk = match.groupdict()['pk']
#         try:
#             reference = Reference.objects.get(pk=pk)
#             if reference not in topic.references.all():
#                 topic.references.add(reference)
#         except ObjectDoesNotExist:
#             continue

    # return topic