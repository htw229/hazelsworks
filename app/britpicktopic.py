from django.core.exceptions import ObjectDoesNotExist

import re

from .models import BritpickFindReplace, ReplacementTopic, Citation
from .debug import Debug
from .htmlutils import addspan, linebreakstoparagraphs, getlinkhtml

debug = None

def britpicktopic(topic):
    global debug
    debug = Debug()

    debug.add(['topic found: ', topic])

    # text = topic.text
    text = linebreakstoparagraphs(topic.text)

    citationpattern = r"[\[\{](?P<pk>\d+)[\}\]]"
    text = replacecitations(text, citationpattern)
    text = addspan(text, 'topictext', tagname='div')

    responsedata = {
        'topic': topic,
        'topichtml': text,
        'citations': topic.citations.all(),
        'searchwordobjects': BritpickFindReplace.objects.filter(replacementtopics__pk=topic.pk),
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
            citation = Citation.objects.get(pk=citationpk)

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

