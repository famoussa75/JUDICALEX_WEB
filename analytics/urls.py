from django.urls import path
from . import views

urlpatterns = [
    path('data/', views.stats_data, name='stats_data'),
]
