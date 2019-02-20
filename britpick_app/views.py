import logging
from . import debug
# import io
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)
# # log_capture_string = io.StringIO()
# logger_handler = logging.StreamHandler(debug.log_capture_string)
# logger_handler.setLevel(logging.DEBUG)
# logger_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
# logger.addHandler(logger_handler)

logger = debug.Logger(__name__)

# f_handler = logging.FileHandler('file.log', 'w+')
#
# f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# f_handler.setFormatter(f_format)
# logger.addHandler(f_handler)

from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
from django.views.generic import ListView, TemplateView, DetailView, FormView

from django.db.models import Count, Q

from .models import Topic, Reference, Britpick, SampleText
from . import forms
from . import britpick



# CLASS


# INDEX (form)
class BritpickView(TemplateView):
    form_class = forms.BritpickForm

    def post(self, request, *args, **kwargs):
        # logger.info('britpickview post')

        context = self.get_context_data()
        form = context['form']
        if form.is_valid():
            # logger = logging.getLogger('britpick_app.britpick')
            logger.critical('form valid critical')
            logger.error('form valid error')
            logger.warning('form valid warning', tags=['testtag'])
            logger.info('form valid info', tags=['infotag', 'anothertag', 'testtag'])
            logger.debug('form valid debug')

            context['options'] = form.cleaned_data
            context['britpicked_paragraphs'] = britpick.britpick(form.cleaned_data)

            # log_contents = debug.log_capture_string.getvalue()
            # debug.log_capture_string.close()

            context['logger'] = debug.loggeroutput()
            # context['logger'] =

        return super().render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class(self.request.POST or None)
        context['sample_texts'] = SampleText.displayed.all()
        return context





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