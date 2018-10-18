from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
import re
import os

from django.template.loader import get_template
from django.http import HttpResponse
from django.template import RequestContext, Template

from .forms import BritpickForm, BritpickfindwordForm, DIALOGUE_OPTION_CHOICES
from .britpick import britpick
from .britpicktopic import britpicktopic
from .models import Replacement, Topic, Reference, ReplacementCategory
from .debug import Debug
import search
import htmlutils
import searchwords
import testwords

from django.core.exceptions import ObjectDoesNotExist

def robotstxt(request):
    """
    This will serve the robots.txt file located in the static folder.

    :param request:
    :return:
    """
    return render(request, 'robots.txt')


def britpickapp(request):
    forminput = None
    outputtext = ''
    debug = Debug()

    if request.method == 'POST':
        form = BritpickForm(request.POST)
        if form.is_valid():
            britpickeddata = britpick(form.cleaned_data)
            outputtext = britpickeddata['text']
            debug = britpickeddata['debug']

            forminput = {
                'dialect': form.cleaned_data['dialect'],
                'replacement_categories': [t.name for t in ReplacementCategory.objects.all().order_by('pk') if str(t.pk) in form.cleaned_data['replacement_categories']],
                'dialogue_option': [x for x in DIALOGUE_OPTION_CHOICES if x[0]==form.cleaned_data['dialogue_option']][0][1]
            }
        else:
            outputtext = 'Form is not valid'


    elif request.method == 'GET':
        # for testing words
        replacementpk = None
        try:
            replacementpk = int(request.GET.get('id'))
            text = testwords.gettestingtext(replacementpk)
            r = Replacement.objects.get(pk=replacementpk)

            form = BritpickForm(initial={
                'text': text,
                'dialect': r.dialect.name,
            })

        except ObjectDoesNotExist as e:
            form = BritpickForm()
            debug.add(replacementpk,'is not valid', e)

        except TypeError as e:
            form = BritpickForm()
            debug.add('no initial arguments', e)

    else:
        form = BritpickForm()


    replacements = {}
    for r in Replacement.objects.all():
        replacements[r.pk] = r

    responsedata = {
        'pagetitle': 'Britpick',
        'template': 'britpick.html',
        'form': form,
        'forminput': forminput,
        'outputtext': outputtext,
        'replacements': replacements,
        'showdebug': True,
        'debug': debug.html,
        'csspage': 'textreplacepage',
    }

    return render(request, 'britpicktemplate.html', responsedata)


def britpickfindduplicates(request):
    objects = Replacement.objects.all()
    duplicateobjects = []

    for o in objects:
        for c in objects:
            if o.pk == c.pk:
                continue
            if o.dialect != c.dialect:
                continue

            duplicatewordlist = [i for i in o.searchwordlist if i in c.searchwordlist]
            if duplicatewordlist:
                duplicateobjects.append({
                    'findreplace01_index': o.pk,
                    'findreplace01_string': o.objectstring,
                    'findreplace02_index': c.pk,
                    'findreplace02_string': c.objectstring,
                })

    responsedata = {
        'findreplaceduplicates': duplicateobjects,
    }

    return render(request, 'britpick_findduplicates.html', responsedata)


def searchview(request):
    # objects = Replacement.objects.all()
    s = ''
    searchwords = []
    replacementwords = []
    searchresults = {}
    debug = Debug()

    form = BritpickfindwordForm()

    if request.method == 'POST':
        form = BritpickfindwordForm(request.POST)
        if form.is_valid():
            searchresults = search.search(form.cleaned_data)
            debug = searchresults['debug']
        else:
            form = BritpickfindwordForm()

    responsedata = {
        'pagetitle': 'Search',
        'form': form,
        'template': 'search.html',
        'search': s,
        'searchwordobjects': searchwords,
        'replacementwordobjects': replacementwords,
        'results': searchresults,
        'showdebug': True,
        'debug': debug.html,
        'csspage': 'searchpage',
    }

    return render(request, 'britpicktemplate.html', responsedata)

# TODO: add dialect, category to replacement_list.html
# TODO: reformat replacement_list.html
# TODO: integrate replacement_list.html into topics
# TODO: rename replacement snippets to standardized with 'snippet'
# TODO: make search more powerful (looking for not just words but inside topics) and using search parameters from britpick.py to get suffixes etc; also can stop separate input/output
# TODO: create word html (later - since now only using admin)
# TODO: create about page
# TODO: add do not find
# TODO: add any single word markup
# TODO: option don't add suffix
# TODO: option require punctuation (like ? or !)
# TODO: link to topic icon only with mouseover text

def topicview(request, topicslug):

    # responsedata is dict that contains topic (obj), topichtml (html), searchstrings (object list), debug (as html)
    responsedata = {
        'pagetitle': 'Topic not found',
        'topic': None,
        'topichtml': 'Topic not found',
        'searchwords': None,
        'debug': '',
        'showdebug': True,
        'csspage': 'topicpage',
    }

    for topic in Topic.objects.all():
        if topicslug == topic.slug:
            responsedata = britpicktopic(topic)
            responsedata['pagetitle'] = topic.name
            responsedata['template'] = 'britpick_topic.html'
            responsedata['adminlink'] = reverse('admin:app_topic_change', args=(topic.pk,))

            break

    return render(request, 'britpicktemplate.html', responsedata)

def topicslist(request):

    topics = Topic.objects.filter(maintopic=True).order_by('name')

    responsedata = {
        'pagetitle': 'Topics',
        'template': 'topicslist.html',
        'topics': topics,
        'debug': '',
        'showdebug': True,
        'csspage': 'topicslistpage',
    }

    return render(request, 'britpicktemplate.html', responsedata)


def wordview(request, replacementpk):
    responsedata = {
        'pagetitle': 'Word not found',
        'topic': None,
        # 'topichtml': 'Word not found',
        'template': 'word.html',
        'debug': '',
        'showdebug': True,
        'adminlink': '',
        'csspage': 'wordpage',
    }

    try:
        r = Replacement.objects.get(pk=replacementpk)
        responsedata['replacement'] = r
        responsedata['pagetitle'] = r.title
        responsedata['adminlink'] = reverse('admin:app_replacement_change', args=(r.pk,))
    except ObjectDoesNotExist:
        responsedata['replacement'] = None

    return render(request, 'britpicktemplate.html', responsedata)


def referenceslist(request):

    references = Reference.objects.filter(mainreference=True).order_by('name')

    responsedata = {
        'pagetitle': 'References',
        'template': 'britpick_references.html',
        'references': references,
        'debug': '',
        'showdebug': True,
        'csspage': 'referencespage',
    }

    return render(request, 'britpicktemplate.html', responsedata)