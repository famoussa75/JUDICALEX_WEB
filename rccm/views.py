import datetime
import locale
import PyPDF2
from django.shortcuts import redirect, render, get_object_or_404
from django.db import transaction
from django.http import JsonResponse
import pdfplumber
from django.views.decorators.csrf import csrf_exempt
import json

from rccm.forms import ActiviteAnterieureForm, PDFUploadForm,EtablissementForm, EtablissementSecondaireForm, FormaliteForm, GerantForm, PDFUploadSignature, PersonnePhysiqueEngagerForm, PersonnePhysiqueForm, RccmForm, FoyerPersonnePhysiqueForm
from .models import PersonnePhysiqueEngager, Rccm,Formalite,PersonnePhysique,Foyer_personne_physique,Etablissement,EtablissementSecondaire,Gerant

import re

import pytesseract
from PIL import Image
from django.core.files.storage import default_storage
from django.conf import settings

from pdf2image import convert_from_path
import os
from django.utils.text import slugify





# Dashboard
def index(request):

    formalites = Formalite.objects.all().order_by('-id')
    context = {'formalites':formalites}  
    return render(request, 'rccm/modification/index.html', context)

def detail(request, slug):

    formalite = Formalite.objects.filter(slug=slug).first()
    etablissement = Etablissement.objects.filter(formalite=formalite).first()
    personne_physique = PersonnePhysique.objects.filter(formalite=formalite).first()
    context = {'formalite':formalite, 'etablissement':etablissement, 'personne_physique':personne_physique }  

    return render(request, 'rccm/modification/personne_physique/activite/detail/single-formalite.html', context)


def search_rccm(request):
    if  request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "GET":
        query = request.GET.get('query', '').strip()
        results = []

        if query:  # Vérifiez que le champ de recherche n'est pas vide
            results = Rccm.objects.filter(numeroRccm__icontains=query).values('numeroRccm','id')

        return JsonResponse({'results': list(results)}, safe=False)

    return JsonResponse({'error': 'Invalid request'}, status=400)

def rccm(request):

    rccms = Rccm.objects.all().order_by('-id')
    context = {'rccms':rccms}  
    return render(request, 'rccm/creation/list-rccm.html', context)

def rccm_detail(request, pk):

    rccm = Rccm.objects.filter(id=pk).first()
    formalites = Formalite.objects.filter(rccm=pk)
    context = {
                'formalites':formalites,
                'rccm':rccm
              }  
    return render(request, 'rccm/creation/detail-rccm.html', context)


def formalite(request):
    
    rccmForm = RccmForm()
    formaliteForm = FormaliteForm()
    personnePhysiqueForm = PersonnePhysiqueForm()
    foyerPersonnePhysiqueForm = FoyerPersonnePhysiqueForm()
    etablissementForm = EtablissementForm()
    etablissementSecondaireForm = EtablissementSecondaireForm()
    personnePhysiqueEngagerForm = PersonnePhysiqueEngagerForm()
    gerantForm = GerantForm()

    context = {
        'rccmForm':rccmForm,
        'formaliteForm':formaliteForm,
        'personnePhysiqueForm':personnePhysiqueForm,
        'foyerPersonnePhysiqueForm':foyerPersonnePhysiqueForm,
        'etablissementForm': etablissementForm,
        'etablissementSecondaireForm': etablissementSecondaireForm,
        'personnePhysiqueEngagerForm': personnePhysiqueEngagerForm,
        'gerantForm': gerantForm,
    }
    return render (request, 'rccm/modification/create.html', context)

def formaliteRapide(request, pk):
    # Récupération de l'objet RCCM correspondant au `pk`
    rccm_instance = get_object_or_404(Rccm, pk=pk)
    
    # Préremplissage des formulaires avec l'instance `rccm_instance`
    rccmForm = RccmForm(instance=rccm_instance)
    
    # Préremplir les autres formulaires liés au RCCM
    formalite_instance = Formalite.objects.filter(rccm=rccm_instance).last()
    formaliteForm = FormaliteForm(instance=formalite_instance)

    personne_physique_instance = PersonnePhysique.objects.filter(formalite=formalite_instance).first()
    personnePhysiqueForm = PersonnePhysiqueForm(instance=personne_physique_instance)

    foyer_personne_physique_instance = Foyer_personne_physique.objects.filter(formalite=formalite_instance).first()
    foyerPersonnePhysiqueForm = FoyerPersonnePhysiqueForm(instance=foyer_personne_physique_instance)

    etablissement_instance = Etablissement.objects.filter(formalite=formalite_instance).first()
    etablissementForm = EtablissementForm(instance=etablissement_instance)

    etablissement_secondaire_instance = EtablissementSecondaire.objects.filter(formalite=formalite_instance).first()
    etablissementSecondaireForm = EtablissementSecondaireForm(instance=etablissement_secondaire_instance)

    personne_physique_engager_instance = PersonnePhysiqueEngager.objects.filter(formalite=formalite_instance).first()
    personnePhysiqueEngagerForm = PersonnePhysiqueEngagerForm(instance=personne_physique_engager_instance)

    gerant_instance = Gerant.objects.filter(formalite=formalite_instance).first()
    gerantForm = GerantForm(instance=gerant_instance)

    # Préparation du contexte avec les formulaires préremplis
    context = {
        'rccmForm': rccmForm,
        'formaliteForm': formaliteForm,
        'personnePhysiqueForm': personnePhysiqueForm,
        'foyerPersonnePhysiqueForm': foyerPersonnePhysiqueForm,
        'etablissementForm': etablissementForm,
        'etablissementSecondaireForm': etablissementSecondaireForm,
        'personnePhysiqueEngagerForm': personnePhysiqueEngagerForm,
        'gerantForm': gerantForm,
    }

    return render(request, 'rccm/modification/create.html', context)


def submit_formalite(request):

    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':  # Vérifie uniquement que la requête est une POST
        # Initialisation des formulaires avec les données soumises
        formalite_form = FormaliteForm(request.POST)
        rccm_form = RccmForm(request.POST)
        personne_physique_form = PersonnePhysiqueForm(request.POST)
        etablissement_form = EtablissementForm(request.POST)
        personne_engager_form = PersonnePhysiqueEngagerForm(request.POST)

        # Vérification des formulaires
        if (
            formalite_form.is_valid()
            and rccm_form.is_valid()
            and personne_physique_form.is_valid()
            and etablissement_form.is_valid()
            and personne_engager_form.is_valid()
        ):
            # Enregistrer les données dans la base
            numero_rccm = rccm_form.cleaned_data.get('numeroRccm')
            rccm = Rccm.objects.filter(numeroRccm=numero_rccm).first()

            # Sauvegarder la formalité
            formalite = formalite_form.save(commit=False)
            formalite.rccm = rccm
            formalite.created_by = request.user
            if not formalite_form.cleaned_data.get('typeFormalite'):
                formalite.typeFormalite = 'Création'
            formalite.save()

            # Sauvegarder les autres modèles liés
            for form, model in [
                (personne_physique_form, PersonnePhysique),
                (etablissement_form, Etablissement),
                (personne_engager_form, PersonnePhysiqueEngager)
            ]:
                instance = form.save(commit=False)
                instance.formalite = formalite
                instance.save()

            # Retourner une réponse JSON en cas de succès
            return JsonResponse({"success": True}, status=200)

        else:
            # Collecter les erreurs de validation
            errors = {
                "formalite_form": formalite_form.errors,
                "rccm_form": rccm_form.errors,
                "personne_physique_form": personne_physique_form.errors,
                "etablissement_form": etablissement_form.errors,
                "personne_engager_form": personne_engager_form.errors,
            }
            return JsonResponse({"success": False, "errors": errors}, safe=False, status=400)

    context = last_formalite()
    context = last_formalite()

    return render(request, 'rccm/modification/create-succes.html', context)

def last_formalite():
     # Gestion de la récupération des dernières données si la requête n'est pas une POST
    latest_formalite = Formalite.objects.order_by('-id').first()
    etablissement = Etablissement.objects.filter(formalite=latest_formalite).order_by('-created_at').first()
    personne_physique = PersonnePhysique.objects.filter(formalite=latest_formalite).order_by('-created_at').first()
    personne_engager = PersonnePhysiqueEngager.objects.filter(formalite=latest_formalite).order_by('-created_at').first()

    context = {
        'formalite': latest_formalite,
        'etablissement': etablissement,
        'personne_physique': personne_physique,
        'personne_engager': personne_engager,
    }

    return context


def submit_rccm(request):
    if request.method == 'POST':
        # Initialisation des formulaires avec les données soumises
        formalite_form = FormaliteForm(request.POST)
        rccm_form = RccmForm(request.POST, request.FILES)
        personne_physique_form = PersonnePhysiqueForm(request.POST)
        etablissement_form = EtablissementForm(request.POST)
        personne_engager_form = PersonnePhysiqueEngagerForm(request.POST)

        # Vérification des formulaires
        if all(
            form.is_valid()
            for form in [
                formalite_form,
                rccm_form,
                personne_physique_form,
                etablissement_form,
                personne_engager_form,
            ]
        ):
            # Gestion du RCCM
            numero_rccm = rccm_form.cleaned_data.get("numeroRccm")
            rccm = Rccm.objects.filter(numeroRccm=numero_rccm).first()

            if rccm:
                # L'objet existe déjà, renvoyer une réponse claire
                return render(request, "rccm/creation/create-error.html")

          # Charger le fichier depuis la session
            temp_file_path = request.session.get('temp_file_path')
            
            if temp_file_path:
                with open(temp_file_path, 'rb') as file:
                    # Faites quelque chose avec le fichier, par exemple, l'attacher à l'objet RCCM
                    rccm = rccm_form.save(commit=False)
                    rccm.created_by = request.user
                    rccm.rccm_file.save(request.session['uploaded_pdf'], file)  # Supposant un champ FileField
                    
                rccm.save()
                
                # Nettoyer la session après utilisation
                del request.session['uploaded_pdf']
                del request.session['temp_file_path']

            # Création de la formalité
            formalite = formalite_form.save(commit=False)
            formalite.rccm = rccm
            formalite.dateModification = rccm.dateEnreg
            formalite.created_by = request.user
            if not formalite.typeFormalite:
                formalite.typeFormalite = "Création"
            formalite.save()

            # Association des autres modèles
            personne_physique = personne_physique_form.save(commit=False)
            personne_physique.formalite = formalite
            personne_physique.save()

            etablissement = etablissement_form.save(commit=False)
            etablissement.formalite = formalite
            etablissement.save()

            personne_engager = personne_engager_form.save(commit=False)
            personne_engager.formalite = formalite
            personne_engager.save()

            return render(request, "rccm/creation/create-succes.html")

        else:
            # Collecter les erreurs de validation
            errors = {
                "formalite_form": formalite_form.errors,
                "rccm_form": rccm_form.errors,
                "personne_physique_form": personne_physique_form.errors,
                "etablissement_form": etablissement_form.errors,
                "personne_engager_form": personne_engager_form.errors,
            }
            return JsonResponse({"Erreur": False, "errors": errors}, safe=False, status=400)

    # Dernière formalité en mode GET
    latest_formalite = Formalite.objects.order_by("-id").first()
    context = {
        "formalite": latest_formalite,
        "etablissement": Etablissement.objects.filter(formalite=latest_formalite).order_by("-id").first(),
        "personne_physique": PersonnePhysique.objects.filter(formalite=latest_formalite).order_by("-id").first(),
        "personne_engager": PersonnePhysiqueEngager.objects.filter(formalite=latest_formalite).order_by("-id").first(),
    }
    #return render(request, "rccm/modification/create-succes.html", context)
    return redirect('rccm.list')



def upload_pdf_view(request):


    if request.method == 'POST':

        form_file = PDFUploadForm(request.POST, request.FILES)
        if form_file.is_valid():
            uploaded_file = request.FILES['pdf_file']
            type_rccm = form_file.cleaned_data.get('type_rccm')
            pdf_reader = PyPDF2.PdfReader(uploaded_file)

            request.session['uploaded_pdf'] = uploaded_file.name  # Stocke uniquement le nom du fichier en session
    
            # Enregistrez temporairement le fichier
            temp_file_path = f'/tmp/{uploaded_file.name}'
            with open(temp_file_path, 'wb+') as temp_file:
                for chunk in uploaded_file.chunks():
                    temp_file.write(chunk)
            
            request.session['temp_file_path'] = temp_file_path  # Enregistre le chemin temporaire

            if request.method == "POST" and request.FILES.get("pdf_file"):
                    image_file = request.FILES["pdf_file"]
                    image_path = default_storage.save("uploads/" + image_file.name, image_file)
                    file_path = os.path.join(settings.MEDIA_ROOT, image_path)

                    extracted_text = ""

                    # Vérifier si le fichier est un PDF
                    if image_file.name.endswith(".pdf"):
                        images = convert_from_path(file_path)  # Convertir le PDF en images
                        text_list = [pytesseract.image_to_string(img, lang="eng+fra") for img in images]
                        extracted_text = "\n\n".join(text_list)  # Fusionner le texte de toutes les pages
                    else:
                        image = Image.open(file_path)  # Ouvrir l’image normale
                        extracted_text = pytesseract.image_to_string(image, lang="eng+fra")

                   
            # Définir la locale pour les noms de mois en français
            locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')  # Assurez-vous que cette locale est installée sur votre système

            extracted_text = form_file.cleaned_data.get('result_ocr')
            
            # Exemple d'extraction des données avec expressions régulières (ajustez selon vos besoins)
            num_rccm = re.search(r"N°ENTREPRISE/RCCM/(.*)", extracted_text, re.IGNORECASE)
            num_formalite = re.search(r"N°FORMALITE/RCCM/(.*)", extracted_text, re.IGNORECASE)

            nom_commercial = re.search(r"NOM\s+COMMERCIAL\s+\(s'il y a lieu\)\s+:(.+)", extracted_text, re.IGNORECASE)
            sigle = re.search(r"SIGLE\s+OU\s+ENSEIGNE\s+\(s'il y a lieu\)\s+:(.+)", extracted_text, re.IGNORECASE)
            siegeSocial = re.search(r"\(géographique\s+et\s+postale\)\s+:(.*)", extracted_text, re.IGNORECASE)
            activites_match = re.search(r"ACTMTE\(S\)\s+EXERCEE\(S\)\(préciser\)\s+:(.*(?:\n.*)?)", extracted_text, re.IGNORECASE)
            activites_text = activites_match.group(1).strip() if activites_match else ''
            activites = "\n".join(activites_text.split("\n")[:2])
            date_rccm_str = re.search(r"DATE\s*:\s*(\d{1,2}\s+[A-ZÉÈÀÊÎÔÛÂ]+)\s+(\d{4})", extracted_text, re.IGNORECASE)
            if date_rccm_str:
                day_month = date_rccm_str.group(1)  # "2 NOVEMBRE"
                year = date_rccm_str.group(2)       # "2023"
                date_str = f"{day_month} {year}"  # "2 NOVEMBRE 2023"

                date_rccm = datetime.datetime.strptime(date_str, "%d %B %Y").date()
            else:
                date_rccm = ''

            nom = re.search(r"Mlle(.*?)PRENOM\(s\)", extracted_text, re.IGNORECASE)
            prenom = re.search(r"PRENOM\(s\)\s+:(.*)", extracted_text, re.IGNORECASE)
            tel = re.search(r"TEL:(.*)", extracted_text, re.IGNORECASE)
            domicile = re.search(r"DOMICILE\s+PERSONNEL\s+:(.*)", extracted_text, re.IGNORECASE)
            ville = re.search(r"VILLE\s+:(.*?)QUARTIER", extracted_text, re.IGNORECASE)
            quartier = re.search(r"QUARTIER\s+:(.*)", extracted_text, re.IGNORECASE)
            autre_precision = re.search(r"AUTRES\s+PRECISIONS\s+:(.*)", extracted_text, re.IGNORECASE)
            email = re.search(r"COORDONNEES\s+ELECTRONIQUES\s+\(s'il ya lieu\):(.*)", extracted_text, re.IGNORECASE)
            date_naissance_str = re.search(r"DATE\s+ET\s+LIEU\s+DE\s+NAISSANCE\s+:\s*(\d{2}-\d{2}-\d{4})", extracted_text, re.IGNORECASE)
            if date_naissance_str:
                # Récupérer la date capturée
                date_str = date_naissance_str.group(1) if date_naissance_str else ''  # Exemple : "09-07-1981"
                
                # Convertir la date au format datetime.date
                date_naissance = datetime.datetime.strptime(date_str, "%d-%m-%Y").date()
            else:
                date_naissance = ''

            lieu_naissance = re.search(r"à(.*?)NATIONALITE", extracted_text, re.IGNORECASE)
            nationnalite = re.search(r"NATIONALITE\s+:(.+)", extracted_text, re.IGNORECASE)


            RccmForm_data = {
                'numeroRccm': num_rccm.group(1).replace(" ", "") if num_rccm else None,
                'dateEnreg': date_rccm,
            }

            FormaliteForm_data = {
                'numeroFormalite': num_formalite.group(1).replace(" ", "") if num_formalite else None,
                'nomCommercial': nom_commercial.group(1).strip() if nom_commercial else '',
                'denomination': nom_commercial.group(1).strip() if nom_commercial else '',
                'sigle': sigle.group(1).strip() if sigle else '',
                'siegeSocial': siegeSocial.group(1).strip() if siegeSocial else '',
                'typeRccm':type_rccm
            }

            EtablissementForm_data = {
                'activites': activites
            }

            PersonnePhysique_data = {
                'nom': nom.group(1).strip() if nom else '',
                'prenom': prenom.group(1).strip() if prenom else '',
                'lieuNaissance': lieu_naissance.group(1).strip() if lieu_naissance else '',
                'nationnalite': nationnalite.group(1).strip() if nationnalite else '',
                'telephone': tel.group(1).strip() if tel else '',
                'domicile': domicile.group(1).strip() if domicile else '',
                'ville': ville.group(1).strip() if ville else '',
                'quartier': quartier.group(1).strip() if quartier else '',
                'dateNaissance': date_naissance,
                'autrePrecision': autre_precision.group(1).strip() if autre_precision else '',
                'coordonneesElectro': email.group(1).strip() if email else '',
            }


            # Pré-remplir le formulaire avec les données extraites
            pre_filled_RccmForm = RccmForm(initial=RccmForm_data)
            pre_filled_FormaliteForm = FormaliteForm(initial=FormaliteForm_data)
            pre_filled_EtablissementForm = EtablissementForm(initial=EtablissementForm_data)
            pre_filled_PersonnePhysique = PersonnePhysiqueForm(initial=PersonnePhysique_data)
            activiteAnterieureForm = ActiviteAnterieureForm()

            clignoter = True

            context = {
                'form_file': form_file,
                'type_rccm':type_rccm,
                'rccmForm': pre_filled_RccmForm,
                'formaliteForm': pre_filled_FormaliteForm,
                'etablissementForm': pre_filled_EtablissementForm,
                'personnePhysiqueForm': pre_filled_PersonnePhysique,
                'activiteAnterieureForm': activiteAnterieureForm,
                'clignoter': clignoter,
            }

            return render(request, 'rccm/creation/create-rccm.html', context)

    form_rccm = RccmForm()
    formaliteForm = FormaliteForm()
    personnePhysiqueForm = PersonnePhysiqueForm()
    foyerPersonnePhysiqueForm = FoyerPersonnePhysiqueForm()
    etablissementForm = EtablissementForm()
    etablissementSecondaireForm = EtablissementSecondaireForm()
    personnePhysiqueEngagerForm = PersonnePhysiqueEngagerForm()
    gerantForm = GerantForm()
    activiteAnterieureForm = ActiviteAnterieureForm()
    form_file = PDFUploadForm()

    context = {
        'rccmForm':form_rccm,
        'form_file':form_file,
        'formaliteForm':formaliteForm,
        'personnePhysiqueForm':personnePhysiqueForm,
        'foyerPersonnePhysiqueForm':foyerPersonnePhysiqueForm,
        'etablissementForm': etablissementForm,
        'etablissementSecondaireForm': etablissementSecondaireForm,
        'personnePhysiqueEngagerForm': personnePhysiqueEngagerForm,
        'gerantForm': gerantForm,
        'activiteAnterieureForm': activiteAnterieureForm,
    }
       
    return render(request, 'rccm/creation/create-rccm.html', context)


def scan(request):

    form_file = PDFUploadForm()
    context = {
    'form_file':form_file,
    }

    return render(request, 'rccm/creation/scan.html', context)


def scanFormalite(request, slug):
    # Récupérer l'objet Formalite correspondant au slug
    formalite_signer = PDFUploadSignature()
    formalite = get_object_or_404(Formalite, slug=slug)

    if request.method == "POST":
        uploaded_file = request.FILES.get('formaliteSignee')

        if uploaded_file:
            # Générer un nom de fichier unique
            file_name = f"{slugify(slug)}_{uploaded_file.name}"
            file_path = f"formalites_signees/{file_name}"

            # Sauvegarder le fichier
            saved_path = default_storage.save(file_path, uploaded_file)

            # Mettre à jour le champ formaliteSignee dans la table Formalite
            formalite.formaliteSignee = saved_path
            formalite.save()

            return redirect('rccm.formalite.detail', slug=slug)

    context = {
        'formalite_signer': formalite_signer,
        'formalite_slug': slug,
    }

    return render(request, 'rccm/modification/scanSigner.html', context)
