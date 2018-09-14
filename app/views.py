from django.http import HttpResponseRedirect
from django.shortcuts import render
import re
import os

from django.template.loader import get_template
from django.http import HttpResponse
from django.template import RequestContext, Template

from .forms import BritpickForm, BritpickfindwordForm, DIALOGUE_OPTION_CHOICES
from .britpick import britpick
from .britpicktopic import britpicktopic
from .models import Replacement, ReplacementTopic, Reference, ReplacementCategory
from .debug import Debug


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
    }

    # template = get_template('britpicktemplate.html')
    # html = template.render(responsedata)

    # template = get_template('britpicktemplate.html')
    # context = RequestContext(request, responsedata)
    # html = template.render(context)
    #
    # return HttpResponse(html)

    return render(request, 'britpicktemplate.html', responsedata)

# TODO: give form's suggest replacements a default

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

    if request.method == 'POST':
        form = BritpickfindwordForm(request.POST)
        if form.is_valid():
            s = form.cleaned_data['searchword']

            for o in Replacement.objects.all():
                if s in o.searchwords:
                    searchwords.append(o)
                if o.replacementwordshtml and s in o.replacementwordshtml:
                    replacementwords.append(o)
                # if o.directreplacement and s in o.directreplacement:
                #     replacementwords.append(o)
                # if o.considerreplacement and s in o.considerreplacement:
                #     replacementwords.append(o)

    responsedata = {
        'form': BritpickfindwordForm,
        'template': 'search.html',
        'search': s,
        'searchwordobjects': searchwords,
        'replacementwordobjects': replacementwords,
    }

    return render(request, 'britpicktemplate.html', responsedata)

# TODO: add dialect, category to replacement_list.html
# TODO: reformat replacement_list.html
# TODO: integrate replacement_list.html into topics
# TODO: rename replacement snippets to standardized with 'snippet'
# TODO: make search more powerful (looking for not just words but inside topics) and using search parameters from britpick.py to get suffixes etc; also can stop separate input/output
# TODO: create word html (later - since now only using admin)
# TODO: create about page

def topicview(request, topicslug):

    # responsedata is dict that contains topic (obj), topichtml (html), searchwords (object list), debug (as html)
    responsedata = {
        'pagetitle': 'Topic not found',
        'topic': None,
        'topichtml': 'Topic not found',
        'searchwords': None,
        'debug': '',
        'showdebug': True,
    }

    for topic in ReplacementTopic.objects.all():
        if topicslug == topic.slug:
            responsedata = britpicktopic(topic)
            responsedata['pagetitle'] = topic.name
            responsedata['template'] = 'britpick_topic.html'

            break



    return render(request, 'britpicktemplate.html', responsedata)

def topicslist(request):

    topics = ReplacementTopic.objects.filter(maintopic=True).order_by('name')

    responsedata = {
        'pagetitle': 'Topics',
        'template': 'topicslist.html',
        'topics': topics,
        'debug': '',
        'showdebug': True,
    }

    return render(request, 'britpicktemplate.html', responsedata)


def referenceslist(request):

    references = Reference.objects.filter(mainreference=True).order_by('name')

    responsedata = {
        'pagetitle': 'References',
        'template': 'britpick_references.html',
        'references': references,
        'debug': '',
        'showdebug': True,
    }

    return render(request, 'britpicktemplate.html', responsedata)