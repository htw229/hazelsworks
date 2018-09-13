from django.http import HttpResponseRedirect
from django.shortcuts import render
import re

from .forms import BritpickForm, BritpickfindwordForm
from .britpick import britpick
from .britpicktopic import britpicktopic
from .models import BritpickFindReplace, ReplacementTopic, Citation
from .debug import Debug


def robotstxt(request):
    """
    This will serve the robots.txt file located in the static folder.

    :param request:
    :return:
    """
    return render(request, 'robots.txt')


def britpickapp(request):
    dialect = ''
    text = ''
    britpickedtext = ''
    debug = ''

    if request.method == 'POST':
        form = BritpickForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            dialect = form.cleaned_data['dialect']
            dialogue = form.cleaned_data['dialogue']
            britpickedtext, debug = britpick(text, dialect, dialogue)
            form.initial.update({'original_text': text})

    responsedata = {
        'pagetitle': 'Britpick',
        'template': 'britpick.html',
        'form': BritpickForm,
        'text': text,
        'dialect': dialect,
        'britpickedtext': britpickedtext,
        'showdebug': True,
        'debug': debug,
    }

    return render(request, 'britpicktemplate.html', responsedata)



def britpickfindduplicates(request):
    objects = BritpickFindReplace.objects.all()
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


def britpickfindword(request):
    # objects = BritpickFindReplace.objects.all()
    s = ''
    searchwords = []
    replacementwords = []

    if request.method == 'POST':
        form = BritpickfindwordForm(request.POST)
        if form.is_valid():
            s = form.cleaned_data['searchword']

            for o in BritpickFindReplace.objects.all():
                if s in o.searchwords:
                    searchwords.append(o)
                if o.directreplacement and s in o.directreplacement:
                    replacementwords.append(o)
                if o.considerreplacement and s in o.considerreplacement:
                    replacementwords.append(o)

    responsedata = {
        'form': BritpickfindwordForm,
        'search': s,
        'searchwordobjects': searchwords,
        'replacementwordobjects': replacementwords,
    }

    return render(request, 'britpick_findword.html', responsedata)


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

    references = Citation.objects.filter(mainreference=True).order_by('name')

    responsedata = {
        'pagetitle': 'References',
        'template': 'britpick_references.html',
        'references': references,
        'debug': '',
        'showdebug': True,
    }

    return render(request, 'britpicktemplate.html', responsedata)