import html
from django.http import HttpResponse,JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render,redirect,get_object_or_404
from start.models import Juridictions
from .forms import RoleForm,RoleAffaireForm,EnrollementForm,DecisionsForm
from django.db import IntegrityError, transaction
from django.forms import inlineformset_factory, modelformset_factory
from .models import AffaireRoles, Roles, Enrollement, Decisions, SuivreAffaire
from datetime import datetime
from django.db.models import Q
from django.utils.html import mark_safe
import re
from time import sleep


import uuid

# Create your views here.
def index(request):
   

    today = datetime.today().strftime('%Y-%m-%d')
    roles = Roles.objects.all().order_by('-created_at')
     # Nombre d'objets par page
    objets_par_page = 8

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
        'roles':roles,
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
            Q(numRp__icontains=query) | 
            Q(demandeurs__icontains=query) | 
            Q(defendeurs__icontains=query) | 
            Q(mandatDepot__icontains=query) | 
            Q(detention__icontains=query) | 
            Q(prevention__icontains=query) | 
            Q(natureInfraction__icontains=query) | 
            Q(decision__icontains=query) | 
            Q(prevenus__icontains=query) | 
            Q(appelants__icontains=query) | 
            Q(intimes__icontains=query) | 
            Q(partieCiviles__icontains=query) | 
            Q(civileResponsables__icontains=query) | 
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
                affaire.colored_numRp = colorize_found(query, affaire.numRp) if affaire.numRp is not None else ''
                affaire.colored_natureInfraction = colorize_found(query, affaire.natureInfraction)
                affaire.colored_prevenus = colorize_found(query, affaire.prevenus)
                affaire.colored_appelants = colorize_found(query, affaire.appelants)
                affaire.colored_intimes = colorize_found(query, affaire.intimes)
                affaire.colored_partieCiviles = colorize_found(query, affaire.partieCiviles)
                affaire.colored_civileResponsables = colorize_found(query, affaire.civileResponsables)
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

def listRole(request):
    if request.user.groups.filter(name='Greffe').exists():
        roles = Roles.objects.filter(juridiction=request.user.juridiction_id)
    else:
        roles = Roles.objects.all()
    
    return render(request, 'role/gestion-roles.html',{'roles':roles})

def listAffaire(request):
    if request.user.groups.filter(name='Greffe').exists():
       affaires = AffaireRoles.objects.filter(role__juridiction=request.user.juridiction_id)
    else:
       affaires = AffaireRoles.objects.all()
    
    return render(request, 'role/gestion-affaires.html',{'affaires':affaires})

def listEnrollement(request):
    if request.user.groups.filter(name='Greffe').exists():
        enrollements = Enrollement.objects.filter(juridiction=request.user.juridiction_id)
        return render(request, 'role/gestion-enrollements.html',{'enrollements':enrollements})
    else:
        juridictions = Juridictions.objects.all()

        # Nombre d'objets par page
        objets_par_page = 12

        paginator = Paginator(juridictions, objets_par_page)

        # Récupérez le numéro de page à partir de la requête GET
        page_number = request.GET.get('page')
        
        # Obtenez les objets pour la page demandée
        juridictions = paginator.get_page(page_number)

        return render(request, 'role/registres-enrollements.html',{'juridictions':juridictions})

def listEnrollementForAdmin(request, idJuridiction):
    enrollements = Enrollement.objects.filter(juridiction=idJuridiction)
    return render(request, 'role/gestion-enrollements.html',{'enrollements':enrollements})
   

    

def createRole(request):
    if request.user.groups.filter(name='Greffe').exists():
        juridictions = Juridictions.objects.filter(id=request.user.juridiction_id)
    else:
        juridictions = Juridictions.objects.all()

    form = RoleForm(request.POST or None)

    enrollFormset = modelformset_factory(Enrollement, form=EnrollementForm, extra=0, exclude=['id'])
    formset = enrollFormset(request.POST or None, queryset=Enrollement.objects.filter(juridiction_id=request.user.juridiction_id))
    
 
    if request.method == 'POST':
       
         if form.is_valid():
           
            try:
                with transaction.atomic():
                    juridiction_id = request.POST.get('juridiction_id')
                    juridiction = Juridictions.objects.get(pk=juridiction_id)
                    role = form.save(commit=False)
                    role.juridiction = juridiction
                    role.save()
                    if formset.is_valid():
                        for affaire_form2 in formset:
                            idAffairefront = affaire_form2.cleaned_data.get('idAffaire')
                            if idAffairefront is not None:
                                id_affaire = affaire_form2.cleaned_data.get('idAffaire')
                            else:
                                id_affaire = uuid.uuid4() 
                            num_ordre = affaire_form2.cleaned_data.get('numOrdre')
                            num_rg = affaire_form2.cleaned_data.get('numRg')
                            num_rp = affaire_form2.cleaned_data.get('numRp')
                            demandeurs = affaire_form2.cleaned_data.get('demandeurs')
                            defendeurs = affaire_form2.cleaned_data.get('defendeurs')
                            objet = affaire_form2.cleaned_data.get('objet')
                            mandatDepot = affaire_form2.cleaned_data.get('mandatDepot')
                            detention = affaire_form2.cleaned_data.get('detention')
                            prevention = affaire_form2.cleaned_data.get('prevention')
                            natureInfraction = affaire_form2.cleaned_data.get('natureInfraction')
                            decision = affaire_form2.cleaned_data.get('decision')
                            prevenus = affaire_form2.cleaned_data.get('prevenus')
                            appelants = affaire_form2.cleaned_data.get('appelants')
                            intimes = affaire_form2.cleaned_data.get('intimes')
                            partieCiviles = affaire_form2.cleaned_data.get('partieCiviles')
                            civileResponsables = affaire_form2.cleaned_data.get('civileResponsables')

                            affaireEnroller = AffaireRoles(role=role,idAffaire=id_affaire,numOrdre=num_ordre,numRg=num_rg,numRp=num_rp,objet=objet,
                                                       mandatDepot=mandatDepot,detention=detention,prevention=prevention,natureInfraction=natureInfraction,decision=decision,
                                                       prevenus=prevenus,demandeurs=demandeurs,defendeurs=defendeurs,appelants=appelants,intimes=intimes,partieCiviles=partieCiviles,civileResponsables=civileResponsables)
                            affaireEnroller.save()

                           

                        # Reste de votre code après avoir traité les valeurs du formset2
                    else:
                        print(f"Formset is not valid: {formset.errors}")

                                         
                    messages.success(request, 'Rôle enregistré avec succès !')
                    return redirect('role.liste')

            except IntegrityError as e:
                print(f"IntegrityError occurred: {e}")
                return redirect('role.create')

   
    context = {
        'juridictions':juridictions,
        'form':form,
        'formset':formset,
    }        
    return render(request, 'role/new-role.html',context)


def createEnrollement(request):
    if request.user.groups.filter(name='Greffe').exists():
        juridictions = Juridictions.objects.filter(id=request.user.juridiction_id)
    else:
        juridictions = Juridictions.objects.all()

    context = {}
    form = RoleForm(request.POST or None)
    EnrollementFormset = modelformset_factory(Enrollement, form=EnrollementForm, extra=0)
    formset = EnrollementFormset(request.POST or None, queryset=Enrollement.objects.none())

  
    if request.method == 'POST':
       
        if form.is_valid() and formset.is_valid():
           
            try:
                with transaction.atomic():
                    juridiction_id = request.POST.get('juridiction_id')
                    typeAudience = request.POST.get('typeAudience')
                    section = request.POST.get('section')
                    juridiction = Juridictions.objects.get(pk=juridiction_id)        
                    
                    for affaire_form in formset:
                        affaire = affaire_form.save(commit=False)
                        affaire.juridiction = juridiction
                        affaire.typeAudience = typeAudience
                        affaire.section = section
                         # Vérification si l'affaire existe déjà dans la BD en fonction de certains champs
                        try:
                            affaire_existe = Enrollement.objects.filter(
                                numOrdre=affaire.numOrdre, 
                                juridiction=juridiction,
                                typeAudience=typeAudience,
                                section=section,
                                dateAudience=affaire.dateAudience
                            ).exists()

                            if affaire_existe:
                                # Si l'affaire existe déjà, ne pas l'enregistrer et passer à la suivante
                                # messages.warning(request, f"L'affaire avec le numéro d'ordre {affaire.numOrdre} existe déjà et n'a pas été enregistrée.")
                                continue
                            else:
                                # Si l'affaire n'existe pas, on l'enregistre
                                affaire.save()
                        except Exception as e:
                            messages.error(request, f"Erreur lors de l'enregistrement de l'affaire : {e}")
                            return redirect('role.createEnrollement')
                        
                    messages.success(request, 'Affaire(s) enrollée(s) avec succès !')
                    return redirect('role.enrollement')
            except IntegrityError as e:
                messages.error(request, f"Erreur d'intégrité : {e}")
                return redirect('role.createEnrollement')
            except Exception as e:
                messages.error(request, f"Une erreur est survenue : {e}")
                return redirect('role.createEnrollement')
        else:
            # Si form ou formset ne sont pas valides, afficher les erreurs
            if form.errors:
                messages.error(request, f"Erreurs dans le formulaire principal : {form.errors}")
            if formset.errors:
                messages.error(request, f"Erreurs dans le formset : {formset.errors}")    

   
    context = {
        'juridictions':juridictions,
        'form':form,
        'formset':formset,
    }        
    return render(request, 'role/new-enrollement.html',context)

def roleDetail(request, pk):
    role = Roles.objects.filter(idRole=pk).first()
    detailRole = AffaireRoles.objects.filter(role=role).order_by('numOrdre')
    juridiction = Juridictions.objects.filter(id=role.juridiction_id).first()
    is_greffe = request.user.groups.filter(name='Greffe').exists()
    if request.user.is_authenticated:
        affaireSuivis = SuivreAffaire.objects.filter(account=request.user)
    else:
        affaireSuivis = SuivreAffaire.objects.none()  # ou [] si vous préférez retourner une liste vide

    context = {
        'role':role,
        'detailRole':detailRole,
        'is_greffe':is_greffe,
        'affaireSuivis':affaireSuivis
    }

    if juridiction.typeTribunal=='CA' and role.typeAudience=='Civile':
        return render(request, 'role/details/ca-civile-detail.html',context)
    elif juridiction.typeTribunal=='CA' and role.typeAudience=='Correctionnelle':
        return render(request, 'role/details/ca-correctionnelle-detail.html',context)
    elif juridiction.name=='Tribunal de Commerce' and role.typeAudience=='Fond':
        return render(request, 'role/details/tc-fond-detail.html',context)
    elif juridiction.name=='Tribunal de Commerce' and role.typeAudience=='Refere':
        return render(request, 'role/details/tc-refere-detail.html',context)
    elif juridiction.typeTribunal=='TPI' and role.typeAudience=='Civile':
        return render(request, 'role/details/tpi-civile-detail.html',context)
    elif juridiction.typeTribunal=='TPI' and role.typeAudience=='Correctionnelle':
        return render(request, 'role/details/tpi-correctionnelle-detail.html',context)
    elif juridiction.name=='Tribunal de travail' and role.typeAudience=='Fond':
        return render(request, 'role/details/tt-fond-detail.html',context)
    elif juridiction.name=='Tribunal de travail' and role.typeAudience=='Refere':
        return render(request, 'role/details/tt-refere-detail.html',context)
    elif juridiction.name=='CRIEF':
        return render(request, 'role/details/crief-detail.html',context)
    elif juridiction.name=='Tribunal pour enfant' and role.typeAudience=='Correctionnelle':
        return render(request, 'role/details/te-correctionnelle-detail.html',context)
    elif juridiction.name=='Tribunal militaire' and role.typeAudience=='Correctionnelle':
        return render(request, 'role/details/tm-correctionnelle-detail.html',context)
    else:
        return HttpResponse()

def detailAffaire(request, idAffaire):
    affaire = AffaireRoles.objects.filter(idAffaire=idAffaire).first()
    decisions = Decisions.objects.filter(affaire=affaire)
    affaireRole = AffaireRoles.objects.select_related('role__juridiction').get(id=affaire.id)
    is_suivi = SuivreAffaire.objects.filter(affaire=affaire,juridiction=affaireRole.role.juridiction,account=request.user)
    is_greffe = request.user.groups.filter(name='Greffe').exists()

    if request.method == 'POST':
        form = DecisionsForm(request.POST)
        if form.is_valid():
            decision = form.save(commit=False)
            decision.affaire = affaire
            form.save()
            messages.success(request, 'Décision ajoutée avec succès !')
            return redirect(request.META.get('HTTP_REFERER', '/'))  
    else:
        form = DecisionsForm()

    context = {
        'affaire':affaire,
        'decisions':decisions,
        'is_greffe':is_greffe,
        'is_suivi':is_suivi,
        'form': form
    }
    return render(request, 'role/detail-affaire.html',context)
  

def fetchForm(request, selectedJuridiction,selectedType,dateRole,selectedSection):
    juridiction = Juridictions.objects.filter(id=selectedJuridiction).first()
    affaireEnrollers = Enrollement.objects.filter(juridiction=juridiction,typeAudience=selectedType,dateAudience=dateRole,section=selectedSection)
    verifRole = Roles.objects.filter(juridiction=juridiction,typeAudience=selectedType,dateEnreg=dateRole,section=selectedSection)
    message = ''

    default_data = []
    if verifRole.exists():
       message = 'Le role pour cette date a déjà été enregistré !'
       return render(request, 'role/roleForms/message_role_exist.html',{'message':message})
    else:
        for a in affaireEnrollers:
            default_data.append({
            'numOrdre': a.numOrdre,
            'idAffaire': a.idAffaire,
            'numRg': a.numRg,
            'demandeurs': a.demandeurs,
            'defendeurs': a.defendeurs,
            'appelants': a.appelants,
            'intimes': a.intimes,
            'partieCiviles': a.partieCiviles,
            'civileResponsables': a.civileResponsables,
            'numRp': a.numRp,
            'mandatDepot': a.mandatDepot,
            'detention': a.detention,
            'prevention': a.prevention,
            'natureInfraction': a.natureInfraction,
            'prevenus': a.prevenus,
            'objet': a.objet,
            'dateEnrollement': a.dateEnrollement,
            'dateAudience': a.dateAudience
            })              
                
        enrollementFormset = modelformset_factory(Enrollement, form=EnrollementForm, extra=affaireEnrollers.count())
        formset = enrollementFormset(request.POST or None,queryset=Enrollement.objects.none(), initial=default_data)
    
    form = RoleForm(request.POST or None)
    print(default_data)
    context = {
        'formset':formset,
        'form':form,
        'message':message,
        'default_data':default_data,
        'affaireEnrollers':affaireEnrollers,
        'selectedJuridiction':selectedJuridiction,
        'selectedType':selectedType,
        'dateRole':dateRole,
        'selectedSection':selectedSection,
    }
    if juridiction.name=='Tribunal de Commerce' and selectedType=='Fond':
        return render(request, 'role/roleForms/tc-fond.html',context)
    elif juridiction.name=='Tribunal de Commerce' and selectedType=='Refere':
        return render(request, 'role/roleForms/tc-refere.html',context)
    elif juridiction.name=='Tribunal de travail' and selectedType=='Fond':
        return render(request, 'role/roleForms/tt-fond.html',context)
    elif juridiction.name=='Tribunal de travail' and selectedType=='Refere':
        return render(request, 'role/roleForms/tt-refere.html',context)
    elif juridiction.typeTribunal=='TPI' and selectedType=='Civile':
        return render(request, 'role/roleForms/tpi-civile.html',context)
    elif juridiction.typeTribunal=='TPI' and selectedType=='Correctionnelle':
        return render(request, 'role/roleForms/tpi-correctionnelle.html',context)
    elif juridiction.typeTribunal=='CA' and selectedType=='Civile':
        return render(request, 'role/roleForms/ca-civile.html',context)
    elif juridiction.typeTribunal=='CA' and selectedType=='Correctionnelle':
        return render(request, 'role/roleForms/ca-correctionnelle.html',context)
    elif juridiction.name=='CRIEF' and selectedType=='Standard':
        return render(request, 'role/roleForms/crief.html',context)
    elif juridiction.name=='Tribunal pour enfant' and selectedType=='Correctionnelle':
        return render(request, 'role/roleForms/te-correctionnelle.html',context)
    elif juridiction.name=='Tribunal militaire' and selectedType=='Correctionnelle':
        return render(request, 'role/roleForms/tm-correctionnelle.html',context)
    else:
        return HttpResponse()

def fetchFormEnrollement(request, selectedJuridiction,selectedType,selectedSection):
    juridiction = Juridictions.objects.filter(id=selectedJuridiction).first()
    enrollementFormset = modelformset_factory(Enrollement, form=EnrollementForm, extra=1)
    formset = enrollementFormset(request.POST or None, queryset=Enrollement.objects.none())
    form = EnrollementForm(request.POST or None)

    context = {
        'formset':formset,
        'form':form,
    }
    if juridiction.name=='Tribunal de Commerce' and selectedType=='Fond':
        return render(request, 'role/enrollementForms/tc-fond.html',context)
    elif juridiction.name=='Tribunal de Commerce' and selectedType=='Refere':
        return render(request, 'role/enrollementForms/tc-refere.html',context)
    elif juridiction.name=='Tribunal de travail' and selectedType=='Fond':
        return render(request, 'role/enrollementForms/tt-fond.html',context)
    elif juridiction.name=='Tribunal de travail' and selectedType=='Refere':
        return render(request, 'role/enrollementForms/tt-refere.html',context)
    elif juridiction.typeTribunal=='TPI' and selectedType=='Civile':
        return render(request, 'role/enrollementForms/tpi-civile.html',context)
    elif juridiction.typeTribunal=='TPI' and selectedType=='Correctionnelle':
        return render(request, 'role/enrollementForms/tpi-correctionnelle.html',context)
    elif juridiction.typeTribunal=='CA' and selectedType=='Civile':
        return render(request, 'role/enrollementForms/ca-civile.html',context)
    elif juridiction.typeTribunal=='CA' and selectedType=='Correctionnelle':
        return render(request, 'role/enrollementForms/ca-correctionnelle.html',context)
    elif juridiction.name=='CRIEF' and selectedType=='Standard':
        return render(request, 'role/enrollementForms/crief.html',context)
    elif juridiction.name=='Tribunal pour enfant' and selectedType=='Correctionnelle':
        return render(request, 'role/enrollementForms/te-correctionnelle.html',context)
    elif juridiction.name=='Tribunal militaire' and selectedType=='Correctionnelle':
        return render(request, 'role/enrollementForms/tm-correctionnelle.html',context)
    else:
        return HttpResponse()

def download_pdf(request):
    # Récupérer le contenu HTML de la requête POST
    html_content = request.POST.get('html_content', '')

    # Convertir le HTML en PDF avec weasyprint
    pdf_file = html(string=html_content).write_pdf()

    # Créer une réponse avec le PDF
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="contenu.pdf"'

    return response


def updateRole(request):

    if request.method == 'POST':
        if request.POST.get('idAffaire'):        
            idAffaire = request.POST.get('idAffaire')
            # Table affaire role
            obj = AffaireRoles.objects.filter(idAffaire=idAffaire).first()

            if request.POST.get('demandeurs'): 
                obj.demandeurs = request.POST.get('demandeurs')
            if request.POST.get('defendeurs'): 
                obj.defendeurs = request.POST.get('defendeurs')
            if request.POST.get('objet'): 
                obj.objet = request.POST.get('objet')
            if request.POST.get('mandatDepot'): 
                obj.mandatDepot = request.POST.get('mandatDepot')
            if request.POST.get('detention'): 
                obj.detention = request.POST.get('detention')
            if request.POST.get('natureInfraction'): 
                obj.natureInfraction = request.POST.get('natureInfraction')
            if request.POST.get('decision'): 
                obj.decision = request.POST.get('decision')
            if request.POST.get('prevenus'): 
                obj.prevenus = request.POST.get('prevenus')
            if request.POST.get('appelants'): 
                obj.appelants = request.POST.get('appelants')
            if request.POST.get('intimes'): 
                obj.intimes = request.POST.get('intimes')
            if request.POST.get('partieCiviles'): 
                obj.partieCiviles = request.POST.get('partieCiviles')
            if request.POST.get('civileResponsables'): 
                obj.civileResponsables = request.POST.get('civileResponsables')

            obj.save()

            # Table enrollement
            obj2 = Enrollement.objects.filter(idAffaire=idAffaire).first()

            if obj2 is not None:
                if request.POST.get('demandeurs'): 
                    obj2.demandeurs = request.POST.get('demandeurs')
                if request.POST.get('defendeurs'): 
                    obj2.defendeurs = request.POST.get('defendeurs')
                if request.POST.get('objet'): 
                    obj2.objet = request.POST.get('objet')
                if request.POST.get('mandatDepot'): 
                    obj2.mandatDepot = request.POST.get('mandatDepot')
                if request.POST.get('detention'): 
                    obj2.detention = request.POST.get('detention')
                if request.POST.get('natureInfraction'): 
                    obj2.natureInfraction = request.POST.get('natureInfraction')
                if request.POST.get('decision'): 
                    obj2.decision = request.POST.get('decision')
                if request.POST.get('prevenus'): 
                    obj2.prevenus = request.POST.get('prevenus')
                if request.POST.get('appelants'): 
                    obj2.appelants = request.POST.get('appelants')
                if request.POST.get('intimes'): 
                    obj2.intimes = request.POST.get('intimes')
                if request.POST.get('partieCiviles'): 
                    obj2.partieCiviles = request.POST.get('partieCiviles')
                if request.POST.get('civileResponsables'): 
                    obj2.civileResponsables = request.POST.get('civileResponsables')

                obj2.save()
            
        else:
            idRole = request.POST.get('idRole')
            obj = Roles.objects.filter(id=idRole).first()

            if request.POST.get('dateEnreg'): 
                obj.dateEnreg = request.POST.get('dateEnreg')
            if request.POST.get('president'): 
                obj.president = request.POST.get('president')
            if request.POST.get('juge'): 
                obj.juge = request.POST.get('juge')
            if request.POST.get('greffier'):
                obj.greffier = request.POST.get('greffier')
            if request.POST.get('assesseur'):
                obj.assesseur = request.POST.get('assesseur')
            if request.POST.get('assesseur1'):
                obj.assesseur1 = request.POST.get('assesseur1')
            if request.POST.get('assesseur2'):
                obj.assesseur2 = request.POST.get('assesseur2')
            if request.POST.get('conseillers'):
                obj.conseillers = request.POST.get('conseillers')
            if request.POST.get('ministerePublic'):
                obj.ministerePublic = request.POST.get('ministerePublic')
            if request.POST.get('typeAudience'):
                obj.typeAudience = request.POST.get('typeAudience')
            if request.POST.get('dateEnreg'):
                obj.dateEnreg = request.POST.get('dateEnreg')
            if request.POST.get('procureurMilitaire'):
                obj.procureurMilitaire = request.POST.get('procureurMilitaire')
            if request.POST.get('subtituts'):
                obj.subtituts = request.POST.get('subtituts')
            

            obj.save()
            
    return redirect(request.META.get('HTTP_REFERER', '/'))

def deleteRole(request):
    role = get_object_or_404(Roles, id=request.POST.get('idRole'))
    role.delete()
    messages.success(request, 'Rôle supprimé avec succès !')
    return redirect('role.liste')

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
   