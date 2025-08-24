from django.urls import path, include
from . import views

urlpatterns = [
     path('', views.index, name='role.index'),
     path('affaires/details/<idAffaire>', views.detailAffaire, name='affaires.details'),
     path('details/<pk>', views.roleDetail, name='role.detail'),
     path('recherche/', views.recherche, name='role.search'),
     path('download-pdf/', views.download_pdf, name='download_pdf'),


]