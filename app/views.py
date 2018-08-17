from django.http import HttpResponseRedirect
from django.shortcuts import render
import re

from .forms import BritpickForm, BritpickfindwordForm
from .britpick import britpick
from .models import BritpickFindReplace

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


    if request.method == 'POST':
        form = BritpickForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            dialect = form.cleaned_data['dialect']
            dialogue = form.cleaned_data['dialogue']
            britpickedtext = britpick(text, dialect, dialogue)
            form.initial.update({'original_text': text})

    responsedata = {
        'form': BritpickForm,
        'text': text,
        'dialect': dialect,
        'britpickedtext': britpickedtext,
    }

    return render(request, 'britpick.html', responsedata)



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
                    searchwords.append({'pk': o.pk, 'string': o.objectstring})
                if o.directreplacement and s in o.directreplacement:
                    replacementwords.append({'pk': o.pk, 'string': o.objectstring})
                if o.considerreplacement and s in o.considerreplacement:
                    replacementwords.append({'pk': o.pk, 'string': o.objectstring})

    responsedata = {
        'form': BritpickfindwordForm,
        'search': s,
        'searchwords': searchwords,
        'replacementwords': replacementwords,
    }

    return render(request, 'britpick_findword.html', responsedata)