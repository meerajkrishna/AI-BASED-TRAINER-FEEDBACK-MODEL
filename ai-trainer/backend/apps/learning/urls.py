"""Learning module URL configuration."""

from django.urls import path
from . import views

app_name = 'learning'

urlpatterns = [
    path('topics/', views.list_topics, name='topic-list'),
    path('topics/<slug:slug>/', views.topic_detail, name='topic-detail'),
    path('categories/', views.category_list, name='category-list'),
]
