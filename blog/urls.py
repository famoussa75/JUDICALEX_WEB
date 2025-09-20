from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_list, name='blog.post_list'),
    path('post/<slug>/', views.post_detail, name='blog.post_detail'),
]
