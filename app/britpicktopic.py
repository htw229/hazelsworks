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


    citationpattern = r"[\[\{](?P<pk>\d+)[\}\]]"
    text = replacecitations(text, citationpattern)
    text = replacecitationswithquotes(text)

    text = linebreakstoparagraphs(text)

    responsedata = {
        'topic': topic,
        'topichtml': text,
        'citations': topic.citations.all(),
        'searchwordobjects': Replacement.objects.filter(topics__pk=topic.pk),
        'debug': debug.html,
        'showdebug': True,
    }


    return responsedata


def replacecitations(inputtext, templatepattern):
    global debug

    text = inputtext
    addedtextlength = 0  # increment starting position after every replacement
    pattern = re.compile(templatepattern)

    for match in pattern.finditer(inputtext):
        citationpk = int(match.group('pk'))

        try:
            citation = Reference.objects.get(pk=citationpk)

            # citationlink = citation.link
            if '[' in match.group():
                citationlink = getlinkhtml(citation.url, '[x]', citation.name)
            elif '{' in match.group():
                citationlink = getlinkhtml(citation.url, citation.name)
            else:
                citationlink = '[incorrect markup]'
        except ObjectDoesNotExist:
            citationlink = '[citation missing]'

        replacetext = addspan(citationlink, 'citation-inline')
        text = text[:match.start() + addedtextlength] + replacetext + text[match.end() + addedtextlength:]
        addedtextlength += len(replacetext) - len(match.group())

    return text


def replacecitationswithquotes(inputtext):
    global debug

    text = inputtext
    addedtextlength = 0
    pattern = re.compile(r"<(?P<pk>\d+):(?P<text>(.|\n)*?)>")

    for match in pattern.finditer(inputtext):
        citationpk = int(match.group('pk'))
        citationhtml = "From %s:\r\n" % getcitationlinkhtml(citationpk)

        quotedtext = addspan('\r\n' + match.group('text'), cssclass='quoted', tagname='div')

        replacetext = citationhtml + quotedtext
        text = text[:match.start() + addedtextlength] + replacetext + text[match.end() + addedtextlength:]
        addedtextlength += len(replacetext) - len(match.group())

    return text


def getcitationlinkhtml(citationpk, citationtemplate = '%s'):
    try:
        citation = Reference.objects.get(pk=citationpk)
        citationlink = getlinkhtml(citation.url, citationtemplate % citation.name)

    except ObjectDoesNotExist:
        citationlink = '[citation missing]'

    return citationlink


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


# def addtopiccitations(topic):
#
#     citationpattern = r"(?<=[\<\[])(?P<pk>\d+)(?=[\:\]])"
#
#     for match in re.finditer(citationpattern, topic.text):
#         pk = match.groupdict()['pk']
#         try:
#             reference = Reference.objects.get(pk=pk)
#             if reference not in topic.citations.all():
#                 topic.citations.add(reference)
#         except ObjectDoesNotExist:
#             continue

    # return topic