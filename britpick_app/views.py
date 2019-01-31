from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
from django.views.generic import ListView, TemplateView, DetailView, FormView

from django.db.models import Count, Q

from .models import Topic, Reference, Britpick
from . import forms

# CLASS


# INDEX (form)
class BritpickView(TemplateView):
    form_class = forms.BritpickForm

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        form = context['form']
        if form.is_valid():
            context['britpicked'] = self.get_britpicked_text(form.cleaned_data)
            context['formdata'] = form.cleaned_data

        return super().render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['britpicked'] = None
        context['form'] = self.form_class(self.request.POST or None)
        return context

    def get_britpicked_text(self, formdata):
        example_britpick_01 = Britpick.objects.get(id=4)
        example_britpick_02 = Britpick.objects.get(id=7)
        example_britpick_03 = Britpick.objects.get(id=8)
        example_britpick_04 = Britpick.objects.get(id=9)

        paragraphs = [
            {
                'britpicks': [example_britpick_01,example_britpick_02,],
                'inlines': [
                    {
                        'text': '"Hello, I am ',
                        'britpick': None,
                        'classes': [],
                    },
                    {
                        'text': 'Andy',
                        'britpick': example_britpick_01,
                        'classes': ['dialogue',],
                    },
                    {
                        'text': ' and I am Sam',
                        'britpick': example_britpick_02,
                        'classes': ['dialogue', ],
                    },
                    {
                        'text': '," said Sam',
                        'britpick': example_britpick_02,
                        'classes': ['narrative', ],
                    },
                    {
                        'text': '. This is some original text. No britpicks to be found here.',
                        'britpick': None,
                        'classes': [],
                    },
                ]
            },
        ]

        # paragraphs.append(paragraphs[0])

        # paragraphs[1] = paragraphs[0]
        # paragraphs[2] = paragraphs[0]
        # paragraphs[3] = paragraphs[0]


        britpicked = {'paragraphs': [paragraphs[0] for i in range(10)],}

        return britpicked





class TopicView(DetailView):
    model = Topic

    def get_object(self, queryset=None):
        return Topic.objects.get(slug=self.kwargs['topicslug'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = context['topic'].name
        return context

# TOPICS (list)
# class TopicList(ListView):
#     model = Topic
#     queryset = Topic.objects.filter(topic_type=Topic.MAIN_TOPIC)

# TOPIC (obj)

# SUBMIT (form)

# SEARCH (form)

# REFERENCES
class ReferencesView(ListView):
    MAIN_REFERENCES = 'M'
    ALL_REFERENCES = 'A'
    QUOTE_REFERENCES = 'Q'
    TOPIC_REFERENCES = 'T'

    model = Reference
    references_filter = ALL_REFERENCES

    def get_queryset(self):
        if self.kwargs['reference_filter'] == 'all':
            return Reference.displayed.all()
        if self.kwargs['reference_filter'] == 'topic':
            return Reference.displayed.annotate(topic_count=Count('topics')).filter(topic_count__gt=0)
        if self.kwargs['reference_filter'] == 'quote':
            return Reference.displayed.annotate(quote_count=Count('quotes', filter=Q(quotes__direct_quote=0))).filter(quote_count__gt=0)
        else:
            return Reference.displayed.filter(main_reference=True)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if not self.kwargs['reference_filter']:
            context['reference_filter'] = 'main'
        else:
            context['reference_filter'] = self.kwargs['reference_filter']
        return context
# ABOUT (static)