"""britpick URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf.urls import include, url
from django.urls import path
from django.contrib import admin
from app import views

urlpatterns = [
    url(r'^admin/', admin.site.urls, name='admin'),
    url(r'^britpick/findduplicates/', views.duplicates_view, name='britpick_findduplicates.html'),
    url(r'^database/', views.database_view, name='database'),

    url(r'^robots.txt', views.robotstxt),

    path(r'suggestion/<objclass>/<int:objpk>/', views.suggestion_view, name='objsuggestion'),
    url(r'^suggestion/', views.suggestion_view, name='suggestion'),

    url(r'^about/', views.about_view, name='about'),
    url(r'^references', views.references_view, name='references'),

    path(r'words/<int:replacementpk>/', views.word_view, name='word'),
    url(r'^search/', views.search_view, name='search'),

    path(r'topics/<slug:topicslug>/', views.topic_view, name='topic'),
    path(r'topics/<slug:topicslug>', views.topic_view,), # without this, above will redirect to topicslist if no slash
    url(r'^topics/', views.topicslist_view, name='topicslist'),

    url(r'^$', views.britpick_view, name='britpick'),

]