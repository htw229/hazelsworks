from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
from django.views.generic import ListView, TemplateView

from .models import Topic

# CLASS
class BaseView(TemplateView):
    template_name = 'britpick_app/base.html'

# INDEX (form)

# TOPICS (list)
# class TopicList(ListView):
#     model = Topic
#     queryset = Topic.objects.filter(topic_type=Topic.MAIN_TOPIC)

# TOPIC (obj)

# SUBMIT (form)

# SEARCH (form)

# ABOUT (static)