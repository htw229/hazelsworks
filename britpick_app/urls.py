from django.urls import path, re_path
from django.views.generic import TemplateView, ListView, DetailView

from . import views
# from . import models
from .models import Topic, Reference

app_name = 'britpick_app'
urlpatterns = [
    path(r'topics/', ListView.as_view(
        template_name='britpick_app/topiclist.html',
        model=Topic,
        queryset = Topic.main_topics.all(),
        extra_context={'title': 'Topics',},
    ), name='topiclist'),

    path(r'topics/<slug:topicslug>/', views.TopicView.as_view(
        template_name='britpick_app/topic.html',
    ), name='topic'),

    path(r'search/', TemplateView.as_view(
        template_name='britpick_app/search.html',
        extra_context={'title': 'Search',},
    ), name='search',),

    # path(r'references/<reference_filter>/', views.ReferencesView.as_view(
    #     template_name='britpick_app/references.html',
    #     extra_context={'title': 'References',},
    # ), name='references',),

    re_path(r'references/(?:(?P<reference_filter>[a-zA-Z]+)/)?$', views.ReferencesView.as_view(
        template_name='britpick_app/references.html',
        extra_context={'title': 'References',},
    ), name='references',),

    # path(r'references/', views.ReferencesView.as_view(
    #     template_name='britpick_app/references.html',
    #     extra_context={'title': 'References', 'reference_filter': 'main',},
    # ), name='references',),

    # path(r'references/', views.ReferencesView.as_view(
    #     template_name='britpick_app/references.html',
    #     references_filter=views.ReferencesView.MAIN_REFERENCES,
    #     extra_context={'title': 'References',},
    # ), name='references',),

    path(r'about/', TemplateView.as_view(
        template_name='britpick_app/about.html',
        extra_context={'title': 'About',},
    ), name='about',),

    path(r'', TemplateView.as_view(
        template_name='britpick_app/britpick.html',
        extra_context={'title': 'Britpick',},
    ), name='britpick',),

    # path('', views.IndexView.as_view(), name='index'),
    # path('<int:pk>/', views.DetailView.as_view(), name='detail'),
]