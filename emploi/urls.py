# urls.py
from django.urls import path
from . import views

urlpatterns = [

    path('docs/', views.liste_docs, name='liste_docs'),
    path('docs/<slug:slug>/', views.voir_modele_doc, name='voir_modele_doc'),
    path('docs/type/<str:type_document>/', views.liste_docs, name='liste_docs_par_type'),

]
