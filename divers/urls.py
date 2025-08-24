# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('contacts/<str:fonction>', views.liste, name='annuaire'),
    path('liens/', views.liens_utiles_view, name='liens_utiles'),
]