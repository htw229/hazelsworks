import logging
from . import debug
import io
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)
# # log_capture_string = io.StringIO()
# logger_handler = logging.StreamHandler(debug.log_capture_string)
# logger_handler.setLevel(logging.DEBUG)
# logger_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
# logger.addHandler(logger_handler)

logger = debug.Logger(__name__)

import re

from .models import Britpick

SECTION_BREAK_MARKER = '{{ SECTION_BREAK }}'
BRITPICK_MARKER = '### {original_text} | {britpick_pk} ###'
BRITPICK_MARKER_DELIMITER = r'(### .+? ###)'
BRITPICK_MARKER_PATTERN = r'### (?P<original_text>.+?) \| (?P<britpick_pk>\d+?) ###'

PARAGRAPH = 'PARAGRAPH'
SECTION_BREAK = 'SECTION_BREAK'

# get text
# get search strings by dialect (have to do by dialect because if do all at once, same searched will override and won't get results)
# perform regex searches on whole text
#   (place markers within text for britpicks, so don't search already britpicked ones)
# divide text into paragraphs and spans
#   (determine if britpick in main text or dialogue and add marker for that)
#   (in future, determine speaker?)

# create paragraphs - which britpicks in paragraph and spans within paragraph with text and with britpicks
# return list of paragraphs (with spans within them) to view

def britpick(formdata):
    text = standardizetext(formdata['text'])
    text = getbritpicks(text)
    paragraphs = getparagraphs(text)

    logger.error('BRITPICK ERROR')
    logger.debug('britpick debug')

    return paragraphs


def standardizetext(text):
    substitutions = [
        ('“', '"'),
        ('”', '"'),
        ('’', "'"),
        ('*',''),
        ('[',''),
        (']',''),
    ]
    for sub in substitutions:
        text = text.replace(sub[0], sub[1])

    # get rid of html tags
    text = re.sub(r'<.*?>', '', text)

    # replace blank space (spaces or tabs) at beginning of paragraphs with nothing
    text = re.sub(r'(?<=\n)[ \t]*', '', text)

    # replace multiple gaps between paragraphs with section break
    text = re.sub(r'(\r\n){3,}', r'\n%s\n' % SECTION_BREAK_MARKER, text)

    # replace any number of carriage returns/newlines with a single newline \n
    text = re.sub(r'((\r\n)|(\r)|(\n))+', r'\n', text)

    # TODO: if using single quote dialogue replace with double quotes

    return text


def getbritpicks(text):
    searches = [('call', '5'), ('Derek', '2'), ('trouble', '8'),]
    for search in searches:
        text = re.sub(r'(%s)' % search[0], BRITPICK_MARKER.format(original_text=r'\1', britpick_pk=search[1]), text)

    return text


def getparagraphs(text):
    paragraphs = []
    paragraph_texts = text.split('\n')

    for paragraph_text in paragraph_texts:
        p = {}
        p['britpicks'] = []
        if paragraph_text == SECTION_BREAK_MARKER:
            p['type'] = SECTION_BREAK
        else:
            p['type'] = PARAGRAPH
            span_texts = re.split(BRITPICK_MARKER_DELIMITER, paragraph_text)
            p['spans'] = []
            for span_text in span_texts:
                britpickmatch = re.match(BRITPICK_MARKER_PATTERN, span_text)
                if britpickmatch:
                    original_text = britpickmatch.groupdict()['original_text']
                    britpick_pk = int(britpickmatch.groupdict()['britpick_pk'])
                    britpick = Britpick.objects.get(pk=britpick_pk)
                    p['britpicks'].append(britpick)
                    p['spans'].append(
                        {
                            'text': original_text,
                            'britpick': britpick,
                        }
                    )
                elif span_text:
                    p['spans'].append(
                        {
                            'text': span_text,
                        }
                    )

        p['britpicks'] = set(p['britpicks'])
        paragraphs.append(p)


    return paragraphs