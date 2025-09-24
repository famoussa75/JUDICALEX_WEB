from django.shortcuts import render
from blog.models import Post
from role.models import AffaireRoles, Decisions, Roles
from .models import MessageDefilant
from users.models import Account
from backoffice.models import Ad
from datetime import datetime, timedelta, date
from django.db.models.functions import TruncDate
from django.db.models import Count



# Create your views here.
def index(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(name='Administrateur').exists():
            return superAdminDashboard(request)
        elif request.user.groups.filter(name='Pigiste').exists():
            return pigisteDashboard(request)
        elif request.user.groups.filter(name='Collaborateur').exists():
            return collaborateurDashboard(request)
        else:
            return visiteurDashboard(request)
        
    else:
       return visiteurDashboard(request)

def visiteurDashboard(request):

    last_post_news = Post.objects.filter(type='news', status='published').order_by('-created_at')[:6]
    last_post_contrib = Post.objects.filter(type='contribution', status='published').order_by('-created_at')[:6]
    old_post_news = Post.objects.filter(type='news', status='published').order_by('created_at')[:6]
    ads_header = Ad.objects.filter(active=True, position='header').order_by('?')
    ads_lateral = Ad.objects.filter(active=True, position='sidebar').order_by('?')
    context = {
        'last_post_news': last_post_news,
        'old_post_news': old_post_news,
        'last_post_contrib': last_post_contrib,
        'ads_header': ads_header,
        'ads_lateral': ads_lateral,
    }
    return render(request, 'start/home/index-visiteur.html', context)

def pigisteDashboard(request):
    return render(request, 'backoffice/home/index-pigiste.html')

def collaborateurDashboard(request):
    return render(request, 'backoffice/home/index-collaborateur.html')

def superAdminDashboard(request):
    return render(request, 'backoffice/home/index-admin.html')

