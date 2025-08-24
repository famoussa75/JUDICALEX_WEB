# urls.py
from django.urls import path
from . import views

urlpatterns = [

    path('entreprise/', views.creation, name='creation_entreprise'),
    path('modele-courrier/', views.liste_docs, name='courrier_entreprise'),
    path('docs/<slug:slug>/', views.voir_modele_doc, name='voir_modele_courrier'),

]
