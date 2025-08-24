from django.shortcuts import render
from blog.models import Post
from role.models import AffaireRoles, Decisions, Roles
from .models import MessageDefilant
from users.models import Account
from datetime import datetime, timedelta, date
from django.db.models.functions import TruncDate
from django.db.models import Count



# Create your views here.
def index(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(name='Visiteur').exists():
            return visiteurDashboard(request)
        else:
            return backoffice(request)
        

    # Si l'utilisateur n'est pas authentifié ou n'appartient à aucun des groupes spécifiés
    last_post = Post.objects.all().order_by('-created_at')
    return render(request, 'start/home/index-visiteur.html', {'last_post': last_post})



def backoffice(request):

    current_year = date.today().year
    year = int(request.GET.get('year', current_year))

    # Générer une liste d'années de 2010 à l'année courante
    available_years = list(range(2024, current_year + 1))


    today = datetime.today().date()
    start = datetime.combine(today, datetime.min.time())
    end = datetime.combine(today, datetime.max.time())

    today_roles_fond = Roles.objects.filter(juridiction=request.user.juridiction, dateEnreg=today, typeAudience='Fond')
    today_roles_refere = Roles.objects.filter(juridiction=request.user.juridiction, dateEnreg=today, typeAudience='Refere')
    today_affaires = AffaireRoles.objects.filter(role__juridiction=request.user.juridiction, role__dateEnreg=today)

    tribunal_users = Account.objects.filter(juridiction=request.user.juridiction).count()
    visiteurs_users = Account.objects.filter(
            juridiction=request.user.juridiction,
            groups__name="Visiteur"
        ).count()

    T_roles = Roles.objects.filter(juridiction=request.user.juridiction,  dateEnreg__year=year).count()
    T_roles_today = Roles.objects.filter(juridiction=request.user.juridiction, dateEnreg=today).count()

    T_roles_fond = Roles.objects.filter(juridiction=request.user.juridiction, typeAudience='Fond',  dateEnreg__year=year).count()
    fond_pourcentage = round(T_roles_fond / T_roles * 100) if T_roles != 0 else 0

    T_roles_refere = Roles.objects.filter(juridiction=request.user.juridiction, typeAudience='Refere',  dateEnreg__year=year).count()
    refere_pourcentage = round(T_roles_refere / T_roles * 100) if T_roles != 0 else 0


    T_affaires = AffaireRoles.objects.filter(role__juridiction=request.user.juridiction,  role__dateEnreg__year=year).count()
    T_affaires_today = AffaireRoles.objects.filter(role__juridiction=request.user.juridiction, role__dateEnreg=today).count()

    T_decisions = Decisions.objects.filter(juridiction=request.user.juridiction, dateDecision__year=year).count()
    T_decisions_today = Decisions.objects.filter(juridiction=request.user.juridiction, dateDecision=today).count()

    T_affaires_sp = AffaireRoles.objects.filter(role__juridiction=request.user.juridiction, role__section='Section Présidentielle',  role__dateEnreg__year=year).count()
    president_sp = AffaireRoles.objects.filter(role__juridiction=request.user.juridiction, role__section='Section Présidentielle').last()

    T_affaires_s1 = AffaireRoles.objects.filter(role__juridiction=request.user.juridiction, role__section='Premiere-Section',  role__dateEnreg__year=year).count()
    president_s1 = AffaireRoles.objects.filter(role__juridiction=request.user.juridiction, role__section='Premiere-Section').last()

    T_affaires_s2 = AffaireRoles.objects.filter(role__juridiction=request.user.juridiction, role__section='Deuxieme-Section',  role__dateEnreg__year=year).count()
    president_s2 = AffaireRoles.objects.filter(role__juridiction=request.user.juridiction, role__section='Deuxieme-Section').last()

    T_affaires_s3 = AffaireRoles.objects.filter(role__juridiction=request.user.juridiction, role__section='Troisieme-Section',  role__dateEnreg__year=year).count()
    president_s3 = AffaireRoles.objects.filter(role__juridiction=request.user.juridiction, role__section='Troisieme-Section').last()

    T_affaires_s4 = AffaireRoles.objects.filter(role__juridiction=request.user.juridiction, role__section='Quatrieme-Section',  role__dateEnreg__year=year).count()
    president_s4 = AffaireRoles.objects.filter(role__juridiction=request.user.juridiction, role__section='Quatrieme-Section').last()

    T_affaires_s5 = AffaireRoles.objects.filter(role__juridiction=request.user.juridiction, role__section='Cinquieme-Section',  role__dateEnreg__year=year).count()
    president_s5 = AffaireRoles.objects.filter(role__juridiction=request.user.juridiction, role__section='Cinquieme-Section').last()

    # Graphes 1
    today = date.today()
    start_date = today - timedelta(days=4)

    # Tous les jours de l'intervalle (pour inclure les jours sans enregistrement)
    days = [start_date + timedelta(days=i) for i in range(5)]

    # Stats depuis la base
    raw_stats = (
        AffaireRoles.objects
        .filter(
            role__juridiction=request.user.juridiction,
            role__dateEnreg__range=(start_date, today)
        )
        .annotate(day=TruncDate('role__dateEnreg'))
        .values('day')
        .annotate(total=Count('id'))
    )


    # Dictionnaire jour => total
    stats_dict = {item['day']: item['total'] for item in raw_stats}

    # Données formatées pour le graphique
    labels = [d.strftime('%Y-%m-%d') for d in days]  # ou '%Y-%m-%d' selon ton format préféré
    data = [stats_dict.get(d, 0) for d in days]  # 0 si pas d'enregistrement ce jour-là


     # Graphes 2
    stats_decisions = (
        Decisions.objects
        .filter(
            juridiction=request.user.juridiction,
            dateDecision__year=year
        )
        .values('typeDecision')
        .annotate(total=Count('id'))
        .order_by('typeDecision')  # optionnel
    )

    # Conversion en deux listes
    decision_labels = [item['typeDecision'] for item in stats_decisions]
    decision_counts = [item['total'] for item in stats_decisions]


    messages = MessageDefilant.objects.filter(actif=True).order_by('-date_creation')


    context = {
        'today':today,
        'selected_year': year,
        'available_years': available_years,
        'today_roles_fond':today_roles_fond,
        'today_roles_refere':today_roles_refere,
        'today_affaires':today_affaires,
        'T_roles':T_roles,
        'T_roles_today':T_roles_today,
        'T_affaires':T_affaires,
        'T_affaires_today':T_affaires_today,
        'T_decisions':T_decisions,
        'T_decisions_today':T_decisions_today,
        'T_roles_fond':T_roles_fond,
        'T_roles_refere':T_roles_refere,
        'fond_pourcentage':fond_pourcentage,
        'refere_pourcentage':refere_pourcentage,
        'T_affaires_sp':T_affaires_sp,
        'president_sp':president_sp,
        'T_affaires_s1':T_affaires_s1,
        'president_s1':president_s1,
        'T_affaires_s2':T_affaires_s2,
        'president_s2':president_s2,
        'T_affaires_s3':T_affaires_s3,
        'president_s3':president_s3,
        'T_affaires_s4':T_affaires_s4,
        'president_s4':president_s4,
        'T_affaires_s5':T_affaires_s5,
        'president_s5':president_s5,
        'chart_labels': labels,
        'chart_data': data,
        'decision_labels': decision_labels,
        'decision_counts': decision_counts,
        'tribunal_users': tribunal_users,
        'visiteurs_users': visiteurs_users,
        'messages': messages,
        
    }

    return render(request, 'start/home/index-backoffice.html', context)

def visiteurDashboard(request):

    last_post = Post.objects.all().order_by('-created_at')
    return render(request, 'start/home/index-visiteur.html',{'last_post': last_post})

