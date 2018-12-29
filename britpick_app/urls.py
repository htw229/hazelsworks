from django.urls import path
from django.views.generic import TemplateView, ListView

from . import views
# from . import models
from .models import Topic

app_name = 'britpick_app'
urlpatterns = [
    path(r'', ListView.as_view(template_name='britpick_app/topiclist.html', model=Topic, queryset = Topic.main_topics.all())),
    path(r'topics/', views.BaseView.as_view()),
    # path('', views.IndexView.as_view(), name='index'),
    # path('<int:pk>/', views.DetailView.as_view(), name='detail'),
]