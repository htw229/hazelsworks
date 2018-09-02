from django.core.exceptions import ObjectDoesNotExist

import re

from .models import BritpickFindReplace, ReplacementTopic, Citation
from .debug import Debug
from .htmlutils import addspan, linebreakstoparagraphs

debug = None

def britpicktopic(topicname):
    global debug
    debug = Debug()

    try:
        topic = ReplacementTopic.objects.get(name__iexact=topicname)
    except ObjectDoesNotExist:
        responsedata = {
            'topic': None,
            'topichtml': 'Topic not found',
            'searchwords': None,
            'debug': debug.html,
        }

        return responsedata

    debug.add(['topic found: ', topic])

    # text = topic.text
    text = linebreakstoparagraphs(topic.text)

    citationpattern = r"\[(?P<pk>\d+)\]"
    text = replacecitations(text, citationpattern)

    text = addspan(text, 'topictext', tagname='div')

    # text = re.sub(citationpattern, Citation.objects.get(pk=int(r'\1')), text)

    searchwords = BritpickFindReplace.objects.filter(replacementtopics__pk=topic.pk)
    citations = topic.citations.all()

    responsedata = {
        'topic': topic,
        'topichtml': text,
        'citations': citations,
        'searchwordobjects': searchwords,
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
            citationlink = citation.link
        except ObjectDoesNotExist:
            citationlink = 'citation missing'

        replacetext = addspan(citationlink, 'citation-inline', '[', ']')
        text = text[:match.start() + addedtextlength] + replacetext + text[match.end() + addedtextlength:]
        addedtextlength += len(replacetext) - len(match.group())

    return text

