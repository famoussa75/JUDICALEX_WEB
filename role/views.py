import html
from django.http import HttpResponse,JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render,redirect,get_object_or_404
from start.models import Juridictions
from magistrats.models import Presidents
from .forms import RoleForm,RoleAffaireForm,EnrollementForm,DecisionsForm
from django.db import IntegrityError, transaction
from django.forms import inlineformset_factory, modelformset_factory
from .models import AffaireRoles, Roles, Enrollement, Decisions, SuivreAffaire
from datetime import datetime, timedelta, date
from django.db.models import Count, Case, When, Value, CharField, Q, F, OuterRef, Subquery
from django.utils.html import mark_safe
import re
from time import sleep
from users.models import Account, Notification

from itertools import groupby
from operator import attrgetter

from django.db.models.functions import Coalesce
from django.db.models import IntegerField


import uuid

# Create your views here.
def index(request):
   
    current_year = date.today().year
    year = int(request.GET.get('year', current_year))

    # Générer une liste d'années de 2010 à l'année courante
    available_years = list(range(2024, current_year + 1))

    today = datetime.today().strftime('%Y-%m-%d')
    roles = Roles.objects.filter(dateEnreg__year=year).order_by('-created_at')
    presidents = Presidents.objects.all().order_by('-created_at')
     # Nombre d'objets par page
    objets_par_page = 10

    paginator = Paginator(roles, objets_par_page)

    # Récupérez le numéro de page à partir de la requête GET
    page_number = request.GET.get('page')
    
    # Obtenez les objets pour la page demandée
    roles = paginator.get_page(page_number)

    total_affaire = {}
    for role in roles:
        total_affaire[role.id] = AffaireRoles.objects.filter(role=role).count()
    total_affaire_items = total_affaire.items()   

    juridictions = Juridictions.objects.all()
    query = []
    context = {
        'selected_year': year,
        'available_years': available_years,
        'roles':roles,
        'presidents':presidents,
        'total_affaire_items':total_affaire_items,
        'juridictions':juridictions,
        'query':query,
        'today':today
    }
    
    return render(request, 'role/index.html',context)

def recherche(request):
    today = datetime.today().strftime('%Y-%m-%d')
    juridictions = Juridictions.objects.all()
    query = request.GET.get('q')  # Récupérer la requête de recherche depuis l'URL
    results = []
    affaireResults = []
    total_affaire_items = []
    roleSearch = []
    affaireSearch = []

    if query:

        roleSearch = Roles.objects.filter(
            Q(dateEnreg__icontains=query) | 
            Q(president__icontains=query) | 
            Q(juge__icontains=query) | 
            Q(juridiction__name__icontains=query) | 
            Q(greffier__icontains=query) 
        ).order_by('-created_at')

        affaireSearch = AffaireRoles.objects.filter(
            Q(numRg__icontains=query) | 
            Q(demandeurs__icontains=query) | 
            Q(defendeurs__icontains=query) | 
            Q(decision__icontains=query) | 
            Q(objet__icontains=query) 
        ).order_by('-created_at').select_related('role')

        # Fusionner les deux résultats
        results = list(affaireSearch) + list(roleSearch)      
       
         # Nombre d'objets par page
        objets_par_page = 8

        paginator = Paginator(results, objets_par_page)

        # Récupérez le numéro de page à partir de la requête GET
        page_number = request.GET.get('page')

        
        # Obtenez les objets pour la page demandée
        results = paginator.get_page(page_number)

        total_affaire = {}
        for role in roleSearch:
            total_affaire[role.id] = AffaireRoles.objects.filter(role=role).count()
        total_affaire_items = total_affaire.items()   

         # Process results to add colorized text
        for role in roleSearch:
            if role:
                role.colored_dateEnreg = colorize_found(query, str(role.dateEnreg.strftime('%d/%m/%Y')))
                role.colored_president = colorize_found(query, role.president)
                role.colored_juge = colorize_found(query, role.juge)
                role.colored_greffier = colorize_found(query, role.greffier)
                role.colored_section = colorize_found(query, role.section)
                # Add colorized text for Juridiction if applicable
                if role.juridiction:
                    role.colored_juridiction = colorize_found(query, role.juridiction.name)
                # Process results to add colorized text


        for affaire in affaireSearch:
            if affaire:
                affaire.colored_demandeurs = colorize_found(query, affaire.demandeurs)
                affaire.colored_defendeurs = colorize_found(query, affaire.defendeurs)
                affaire.colored_numRg = colorize_found(query, affaire.numRg) if affaire.numRg is not None else ''
                affaire.colored_natureInfraction = colorize_found(query, affaire.natureInfraction)
                affaire.colored_objet = colorize_found(query, affaire.objet)

      

    else:
        results = Roles.objects.all().order_by('-created_at')  # Renvoyer tous les éléments si aucune recherche n'est spécifiée

        objets_par_page = 8

        paginator = Paginator(results, objets_par_page)

        # Récupérez le numéro de page à partir de la requête GET
        page_number = request.GET.get('page')
        
        # Obtenez les objets pour la page demandée
        results = paginator.get_page(page_number)

        total_affaire = {}
        for role in results:
            total_affaire[role.id] = AffaireRoles.objects.filter(role=role).count()
        total_affaire_items = total_affaire.items()   

    context = {
        'results':results,
        'roleSearch':roleSearch,
        'affaireSearch':affaireSearch,
        'total_affaire_items':total_affaire_items,
        'juridictions':juridictions,
        'query':query,
        'today':today
    }
    return render(request, 'role/index.html',context)


def colorize_found(query, text):
    colored_text = re.sub(r'(' + re.escape(query) + r')', r'<span style="color:red;">\1</span>', text, flags=re.IGNORECASE)
    return mark_safe(colored_text)

   

def roleDetail(request, pk):
    search_query = request.GET.get('search', '')
    role = Roles.objects.filter(idRole=pk).first()

    if not role:
        return HttpResponse("Rôle non trouvé", status=404)

    # Sous-requête : compter toutes les décisions avec le même numAffaire
    decisions_count_subquery = (
        Decisions.objects.filter(numAffaire=OuterRef('numAffaire'))
        .values('numAffaire')
        .annotate(total=Count('id'))
        .values('total')[:1]
    )

    # Annoter chaque affaire avec nb_decisions global et catégorie
    affaires = AffaireRoles.objects.filter(role=role).annotate(
        nb_decisions=Coalesce(
            Subquery(decisions_count_subquery, output_field=IntegerField()), 
            0
        ),
        categorie=Case(
            When(nb_decisions__lt=2, then=Value('Nouvelles Affaires')),
            When(nb_decisions__gte=2, then=Value('Affaires Encours')),
            output_field=CharField(),
        )
    ).order_by('categorie', 'numOrdre')

    # Recherche
    if search_query:
        affaires = affaires.filter(Q(objet__icontains=search_query))

    # Pagination unique
    paginator = Paginator(affaires, 10)  # 10 affaires par page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Grouper par catégorie pour le template
    sorted_affaires = sorted(page_obj.object_list, key=attrgetter('categorie', 'numOrdre'))
    grouped_affaires = []
    for categorie, items in groupby(sorted_affaires, key=attrgetter('categorie')):
        grouped_affaires.append({
            'grouper': categorie,
            'items': list(items)
        })

    # Infos utilisateur et juridiction
    juridiction = Juridictions.objects.filter(id=role.juridiction_id).first()
    is_chef = request.user.groups.filter(name='Chef').exists()
    affaireSuivis = SuivreAffaire.objects.filter(account=request.user) if request.user.is_authenticated else SuivreAffaire.objects.none()

    context = {
        'role': role,
        'grouped_affaires': grouped_affaires,
        'page_obj': page_obj,
        'is_chef': is_chef,
        'affaireSuivis': affaireSuivis
    }

    # Choix du template selon juridiction et type d'audience
    if juridiction and juridiction.name == 'Tribunal de Commerce de Conakry' and role.typeAudience == 'Fond':
        return render(request, 'role/details/tc-fond-detail.html', context)
    elif juridiction and juridiction.name == 'Tribunal de Commerce de Conakry' and role.typeAudience == 'Refere':
        return render(request, 'role/details/tc-refere-detail.html', context)
    else:
        return HttpResponse("Template non disponible pour cette juridiction/type d'audience")

def detailAffaire(request, idAffaire):


    type_section = (

        ("Premiere-Section", "Prémière Section"),
        ("Deuxieme-Section", "Deuxième Section"),
        ("Troisieme-Section", "Troisième Section"),
        ("Quatrieme-Section", "Quatrième Section"),
        ("Cinquieme-Section", "Cinquième Section"),
        ("Section-Presidentielle", "Section Présidentielle"),
    )

    type_decisions = (
        ("Renvoi", "Renvoi"),
        ("Mise-en-delibere", "Mise en délibéré"),
        ("Delibere-proroge", "Délibéré prorogé"),
        ("Vide-du-délibéré", "Vidé du délibéré"),
        ("Radie", "Radie"),
        ("Renvoi-sine-die", "Renvoi sine die"),
        ("Affectation", "Affectation"),
    )

    affaire = AffaireRoles.objects.filter(idAffaire=idAffaire).first()
    decisions = Decisions.objects.select_related('affaire').filter(
        affaire__objet=affaire.objet,
        affaire__demandeurs=affaire.demandeurs,
        affaire__defendeurs=affaire.defendeurs,
        affaire__mandatDepot=affaire.mandatDepot,
        affaire__detention=affaire.detention,
        affaire__prevention=affaire.prevention,
        affaire__natureInfraction=affaire.natureInfraction,
        affaire__prevenus=affaire.prevenus,
        affaire__appelants=affaire.appelants,
        affaire__intimes=affaire.intimes,
        affaire__partieCiviles=affaire.partieCiviles,
        affaire__civileResponsables=affaire.civileResponsables
    )
    affaireRole = AffaireRoles.objects.select_related('role__juridiction').get(id=affaire.id)
    affaireEnroller = Enrollement.objects.filter(idAffaire=idAffaire).first()


    is_suivi = SuivreAffaire.objects.filter(affaire=affaire,juridiction=affaireRole.role.juridiction,account=request.user)
    is_greffe = request.user.groups.filter(name='Greffe').exists()
    juridiction = Juridictions.objects.filter(id=request.user.juridiction_id).first()

    

    context = {
        'affaire':affaire,
        'affaireEnroller':affaireEnroller,
        'decisions':decisions,
        'is_greffe':is_greffe,
        'is_suivi':is_suivi,
        'type_section':type_section,
        'type_decisions': type_decisions,
    }

    # Formater l'URL avec l'ID dynamique
    url = f'/role/affaires/details/{idAffaire}'

    # Effectuer la mise à jour
    Notification.objects.filter(
        Q(recipient=request.user) & 
        Q(url=url) & 
        Q(is_read=False)
    ).update(is_read=True)
    return render(request, 'role/detail-affaire.html',context)
  


def download_pdf(request):
    # Récupérer le contenu HTML de la requête POST
    html_content = request.POST.get('html_content', '')

    # Convertir le HTML en PDF avec weasyprint
    pdf_file = html(string=html_content).write_pdf()

    # Créer une réponse avec le PDF
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="contenu.pdf"'

    return response


@csrf_exempt
def suivreAffaire(request):
   if request.method == 'POST':
        try:
            data = json.loads(request.body)
            selected_ids = data.get('selected', [])
            account = request.user  # Assuming there is a one-to-one relationship with the user
            
            for id_affaire in selected_ids:
                is_suivi = SuivreAffaire.objects.filter(affaire_id=id_affaire,account=request.user)
                if not is_suivi :
                    affaire = AffaireRoles.objects.select_related('role__juridiction').get(id=id_affaire)
                    SuivreAffaire.objects.create(
                        affaire=affaire,
                        account=account,
                        juridiction=affaire.role.juridiction
                    )
            messages.success(request, 'Félicitation! Vous suivez désormais ces affaires.')
            return JsonResponse({'status': 'success'}, status=200)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
   return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


@csrf_exempt
def NePasSuivreAffaire(request):
   if request.method == 'POST':
        try:
            data = json.loads(request.body)
            selected_ids = data.get('selected', [])
            #juridiction_id = data.get('juridiction_id')
            account = request.user  # Assuming there is a one-to-one relationship with the user
            
            for id_affaire in selected_ids:
                is_suivi = SuivreAffaire.objects.filter(affaire_id=id_affaire,account=account)
                if is_suivi :
                    is_suivi.delete()
                    
            messages.success(request, 'Vous ne suivez plus ces affaires.')
            return JsonResponse({'status': 'success'}, status=200)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
   return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)
   
