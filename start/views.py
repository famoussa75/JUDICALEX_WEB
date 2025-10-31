from django.shortcuts import render
from blog.models import Post
from role.models import AffaireRoles, Decisions, Roles
from .models import MessageDefilant
from users.models import Account
from backoffice.models import Ad
from datetime import datetime, timedelta, date
from django.utils import timezone  # ✅ Django timezone
from datetime import timedelta
from django.db.models.functions import TruncDate
from django.db.models import Count
from django.db.models import F, Count, Value, CharField
from itertools import chain
from django.utils.timezone import now



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
    old_post_news = Post.objects.filter(type='news', status='published').order_by('-created_at')[6:12]
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
    user = request.user

    # 📊 Statistiques principales
    total_news = Post.objects.filter(author=user).count()

    # 🕓 News récentes de ce pigiste
    recent_news = Post.objects.filter(author=user).order_by('-created_at')[:5]

    # 📈 Statistiques hebdomadaires pour ses posts
    last_week = timezone.now() - timedelta(days=7)
    daily_news = (
        Post.objects.filter(author=user, created_at__gte=last_week)
        .extra(select={'day': "date(created_at)"})
        .values('day')
        .annotate(total=Count('id'))
        .order_by('day')
    )

    # Format pour ApexCharts
    dates = [n['day'].strftime('%Y-%m-%d') for n in daily_news]
    totals = [n['total'] for n in daily_news]

    # 📝 Activités récentes du pigiste
    posts_activities = Post.objects.filter(author=user).annotate(
        action_type=Value('Post', output_field=CharField()),
        action=Value('publié', output_field=CharField())
    ).values('id', 'title', 'created_at', 'action_type', 'action')

    recent_activities = sorted(posts_activities, key=lambda x: x['created_at'], reverse=True)[:10]

    context = {
        'total_news': total_news,
        'recent_news': recent_news,
        'chart_dates': dates,
        'chart_values': totals,
        'recent_activities': recent_activities,
    }
    return render(request, 'backoffice/home/index-pigiste.html', context)

def collaborateurDashboard(request):
    user = request.user

    # 📊 Statistiques principales
    total_news = Post.objects.count()

    # 🕓 News récentes
    recent_news = Post.objects.select_related('author').order_by('-created_at')[:5]

    # 📈 Statistiques hebdomadaires pour ApexCharts
    last_week = timezone.now() - timedelta(days=7)
    daily_news = (
        Post.objects.filter(created_at__gte=last_week)
        .extra(select={'day': "date(created_at)"})
        .values('day')
        .annotate(total=Count('id'))
        .order_by('day')
    )

    dates = [n['day'].strftime('%Y-%m-%d') for n in daily_news]
    totals = [n['total'] for n in daily_news]

    # 🔔 Activités récentes du collaborateur (posts seulement)
    posts_activities = Post.objects.filter(author=user).annotate(
        action_type=Value('Post', output_field=CharField()),
        action=Value('publié', output_field=CharField())
    ).values('id','title','created_at','action_type','action')

    recent_activities = sorted(
        posts_activities,
        key=lambda x: x['created_at'], reverse=True
    )[:10]

    context = {
        'total_news': total_news,
        'recent_news': recent_news,
        'chart_dates': dates,
        'chart_values': totals,
        'recent_activities': recent_activities,
    }
    return render(request, 'backoffice/home/index-collaborateur.html', context)

def superAdminDashboard(request):
    """Dashboard principal pour l’administrateur"""
    
    # 📊 Statistiques principales
    total_news = Post.objects.count()
    total_pub = Ad.objects.count()
    total_employes = Account.objects.count()

    # 📰 News récentes
    recent_news = (
        Post.objects.select_related("author")
        .order_by("-created_at")[:5]
    )

    # 📈 Statistiques sur les 7 derniers jours
    last_week = timezone.now() - timedelta(days=7)
    daily_stats = (
        Post.objects.filter(created_at__gte=last_week)
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(total=Count("id"))
        .order_by("day")
    )

    # 🗓️ Données formatées pour ApexCharts
    chart_dates = [item["day"].strftime("%Y-%m-%d") for item in daily_stats]
    chart_values = [item["total"] for item in daily_stats]

    # Activités récentes : combiner différents modèles
    posts_activities = Post.objects.select_related('author').annotate(
        action_type=Value('Post', output_field=CharField()),
        action=Value('publié', output_field=CharField())
    ).values('id','title','author__username','created_at','action_type','action')

    ads_activities = Ad.objects.annotate(
        action_type=Value('Ad', output_field=CharField()),
        action=Value('publié', output_field=CharField())
    ).values('id', 'title', 'created_at', 'action_type', 'action')

    # Annoter les users et renommer 'date_joined' en 'created_at' pour uniformiser
    users_activities = Account.objects.annotate(
        action_type=Value('Utilisateur', output_field=CharField()),
        action=Value('créé', output_field=CharField()),
        created_at=F('date_joined')  # Ajout pour uniformiser le tri
    ).values('id', 'username', 'created_at', 'action_type', 'action')

    # Combiner et trier par date
    recent_activities = sorted(
        chain(posts_activities, ads_activities, users_activities),
        key=lambda x: x['created_at'], reverse=True
    )[:10]  # les 10 activités les plus récentes


    # 📦 Contexte transmis au template
    context = {
        "total_news": total_news,
        "total_pub": total_pub,
        "total_employes": total_employes,
        "recent_news": recent_news,
        "chart_dates": chart_dates,
        "chart_values": chart_values,
        "recent_activities": recent_activities,
        # tu peux ajouter d'autres stats ici plus tard (par ex: trafic, activité récente, etc.)
    }

    return render(request, "backoffice/home/index-admin.html", context)

