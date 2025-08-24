from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    
     path('', views.index, name='rccm.modification'),
     path('formalite/creation/', views.formalite, name='rccm.formalite'),
     path('formalite/creation-rapide/<pk>', views.formaliteRapide, name='rccm.formalite-rapide'),
     path('formalite/detail-formalite/<slug>', views.detail, name='rccm.formalite.detail'),
     path('form/search-rccm/', views.search_rccm, name='search_rccm'),
     path('form/save-formalite/', views.submit_formalite, name='rccm.submitFormalite'),
     path('form/save-rccm/', views.submit_rccm, name='rccm.submitRccm'),
     path('form/rccms/', views.rccm, name='rccm.list'),
     path('form/rccm-detail/<pk>/', views.rccm_detail, name='rccm.detail'),
     path('upload-pdf/', views.upload_pdf_view, name='rccm.upload_pdf'),
     path('scanner/', views.scan, name='rccm.scan'),
     path('signature/<slug>', views.scanFormalite, name='formalite.scan'),
       
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)