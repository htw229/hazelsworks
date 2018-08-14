from django.http import HttpResponseRedirect
from django.shortcuts import render

from .forms import BritpickForm
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
            britpickedtext = britpick(text, dialect)
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

            duplicatewordlist = [i for i in o.searchwordlist if i in c.searchwordlist]
            if duplicatewordlist:
                o_string = ' '.join([
                    str(o.pk),
                    ': ',
                    ', '.join(o.searchwordlist),
                    '(' + o.dialect.name + ')',
                ])

                c_string = ' '.join([
                    str(c.pk),
                    ': ',
                    ', '.join(c.searchwordlist),
                    '(' + c.dialect.name + ')',
                ])

                duplicateobjects.append({
                    'findreplace01_index': o.pk,
                    'findreplace01_string': o_string,
                    'findreplace02_index': c.pk,
                    'findreplace02_string': c_string,
                })

    responsedata = {
        'findreplaceduplicates': duplicateobjects,
    }

    return render(request, 'britpick_findduplicates.html', responsedata)