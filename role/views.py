import html
from io import BytesIO
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
from django.contrib.auth.decorators import login_required, user_passes_test

import re
from time import sleep
from users.models import Account, Notification

from itertools import groupby
from operator import attrgetter

from django.db.models.functions import Coalesce
from django.db.models import IntegerField

from backoffice.models import Ad
from django.contrib.staticfiles.storage import staticfiles_storage



import re
import unicodedata


import uuid

from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas

from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
)
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import mm
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from copy import deepcopy

from django.conf import settings
import os
from PyPDF2 import PdfReader



def get_static_path(relative_path: str) -> str:
    import os
    from django.conf import settings

    # Cherche dans STATICFILES_DIRS
    for static_dir in getattr(settings, "STATICFILES_DIRS", []):
        if static_dir:
            abs_path = os.path.join(static_dir, relative_path)
            if os.path.exists(abs_path):
                return abs_path

    # Cherche dans STATIC_ROOT
    static_root = getattr(settings, "STATIC_ROOT", None)
    if static_root:
        abs_path = os.path.join(static_root, relative_path)
        if os.path.exists(abs_path):
            return abs_path

    # Cherche dans les apps
    base_dir = getattr(settings, "BASE_DIR", None)
    if base_dir:
        for app in settings.INSTALLED_APPS:
            app_path = os.path.join(base_dir, app, "static", relative_path)
            if os.path.exists(app_path):
                return app_path

    raise FileNotFoundError(f"Static file not found: {relative_path}")




def index(request):
    # --------------------------
    # Filtrage par année
    # --------------------------
    current_year = date.today().year
    year = int(request.GET.get('year', current_year))
    available_years = list(range(2024, current_year + 1))

    # --------------------------
    # Récupération des filtres du formulaire
    # --------------------------
    selected_juridictions_csc = request.GET.getlist('juridictions_csc')  # ["CSC"] ou [ids]
    selected_juridictions_ca = request.GET.getlist('juridictions_ca')    # [ids]
    selected_juridictions_js = request.GET.getlist('juridictions_js')    # [ids]
    selected_juridictions_tpi = request.GET.getlist('juridictions_tpi')  # [ids]
    selected_juridictions_jp = request.GET.getlist('juridictions_jp')    # [ids]

    selected_presidents = request.GET.getlist('presidents[]')              # liste de noms
    filtre_date = request.GET.get('filtreDate')                          # date précise
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # --------------------------
    # Filtrage des rôles
    # --------------------------
    roles = Roles.objects.all().order_by('-dateEnreg')

    # Filtrage par année
    if year:
        roles = roles.filter(dateEnreg__year=year)

    # Filtrage Cour Suprême
    if selected_juridictions_csc:
        ids = [int(j) for j in selected_juridictions_csc if j.isdigit()]
        if 'CSC' in selected_juridictions_csc:
            roles = roles.filter(juridiction__typeTribunal='CSC') | roles.filter(juridiction__id__in=ids)
        elif ids:
            roles = roles.filter(juridiction__id__in=ids)

    # Filtrage Cours d’appel
    if selected_juridictions_ca:
        ids = [int(j) for j in selected_juridictions_ca if j.isdigit()]
        if ids:
            roles = roles.filter(juridiction__id__in=ids)

    # Filtrage Juridictions spécialisées
    if selected_juridictions_js:
        ids = [int(j) for j in selected_juridictions_js if j.isdigit()]
        if ids:
            roles = roles.filter(juridiction__id__in=ids)

    # Filtrage TPI
    if selected_juridictions_tpi:
        ids = [int(j) for j in selected_juridictions_tpi if j.isdigit()]
        if ids:
            roles = roles.filter(juridiction__id__in=ids)

    # Filtrage JP
    if selected_juridictions_jp:
        ids = [int(j) for j in selected_juridictions_jp if j.isdigit()]
        if ids:
            roles = roles.filter(juridiction__id__in=ids)

    # Filtrage par présidents
    if selected_presidents:
        roles = roles.filter(president__in=selected_presidents)

    # Filtrage par date précise
    if filtre_date:
        roles = roles.filter(dateEnreg=filtre_date)

    # Filtrage par période
    if start_date and end_date:
        roles = roles.filter(dateEnreg__range=[start_date, end_date])

    # --------------------------
    # Pagination
    # --------------------------
    paginator = Paginator(roles, 10)  # 10 rôles par page
    page_number = request.GET.get('page')
    roles = paginator.get_page(page_number)

    # --------------------------
    # Total des affaires pour chaque rôle
    # --------------------------
    total_affaire = {role.id: AffaireRoles.objects.filter(role=role).count() for role in roles}

    # --------------------------
    # Données supplémentaires pour le template
    # --------------------------
    presidents = Presidents.objects.all().order_by('-created_at')
    juridictions = Juridictions.objects.all()
    today = datetime.today().strftime('%Y-%m-%d')
    ads_header = Ad.objects.filter(active=True, position='header').order_by('?')
    ads_lateral = Ad.objects.filter(active=True, position='sidebar').order_by('?')

    context = {
        'selected_year': year,
        'available_years': available_years,
        'roles': roles,
        'presidents': presidents,
        'total_affaire_items': total_affaire.items(),
        'juridictions': juridictions,
        'today': today,
        'ads_header': ads_header,
        'ads_lateral': ads_lateral,
        # Retours de sélection
        'selected_juridictions_csc': selected_juridictions_csc,
        'selected_juridictions_ca': selected_juridictions_ca,
        'selected_juridictions_js': selected_juridictions_js,
        'selected_juridictions_tpi': selected_juridictions_tpi,
        'selected_juridictions_jp': selected_juridictions_jp,
        'selected_presidents': selected_presidents,
        'filtre_date': filtre_date,
        'start_date': start_date,
        'end_date': end_date,
    }

    return render(request, 'role/index.html', context)



# -------------------------------
# Fonction utilitaire pour normaliser les chaînes
# -------------------------------
def normalize_str(s):
    """Supprime les accents et met en minuscule"""
    if not s:
        return ""
    return ''.join(
        c for c in unicodedata.normalize('NFD', s)
        if unicodedata.category(c) != 'Mn'
    ).lower()

# -------------------------------
# Surbrillance insensible aux accents et à la casse
# -------------------------------
def colorize_found(query, text):
    if not text or not query:
        return text or ""

    query_norm = normalize_str(query)
    text_norm = normalize_str(text)

    matches = []
    start = 0
    while True:
        idx = text_norm.find(query_norm, start)
        if idx == -1:
            break
        matches.append((idx, idx + len(query_norm)))
        start = idx + len(query_norm)

    if not matches:
        return text

    result = ""
    last_idx = 0
    for start_idx, end_idx in matches:
        result += text[last_idx:start_idx] + f'<span style="color:red;">{text[start_idx:end_idx]}</span>'
        last_idx = end_idx
    result += text[last_idx:]

    return mark_safe(result)

# -------------------------------
# Vue recherche
# -------------------------------
def recherche(request):
    today = datetime.today().strftime('%Y-%m-%d')
    juridictions = Juridictions.objects.all()
    query = request.GET.get('q')  # Récupérer la requête de recherche depuis l'URL
    results = []
    roleSearch = []
    affaireSearch = []
    total_affaire_items = []

    # -------------------------------
    # Recherche
    # -------------------------------
    if query:
        # Roles
        all_roles = Roles.objects.all().order_by('-created_at')
        roleSearch = []
        for role in all_roles:
            # Vérifier chaque champ après normalisation
            role_texts = [
                str(role.dateEnreg.strftime('%d/%m/%Y')) if role.dateEnreg else '',
                role.president or '',
                role.juge or '',
                role.greffier or '',
                role.section or '',
                role.juridiction.name if role.juridiction else ''
            ]
            if any(normalize_str(query) in normalize_str(field) for field in role_texts):
                roleSearch.append(role)

        # AffaireRoles
        all_affaires = AffaireRoles.objects.all().order_by('-created_at').select_related('role')
        affaireSearch = []
        for affaire in all_affaires:
            affaire_texts = [
                affaire.numRg or '',
                affaire.demandeurs or '',
                affaire.defendeurs or '',
                affaire.decision or '',
                affaire.objet or '',
                affaire.natureInfraction or ''
            ]
            if any(normalize_str(query) in normalize_str(field) for field in affaire_texts):
                affaireSearch.append(affaire)

        # Fusionner les résultats
        results = list(affaireSearch) + list(roleSearch)

    else:
        results = Roles.objects.all().order_by('-created_at')
        roleSearch = results

    # -------------------------------
    # Pagination
    # -------------------------------
    objets_par_page = 8
    paginator = Paginator(results, objets_par_page)
    page_number = request.GET.get('page')
    results = paginator.get_page(page_number)

    # -------------------------------
    # Total des affaires par rôle
    # -------------------------------
    total_affaire = {}
    for role in roleSearch:
        total_affaire[role.id] = AffaireRoles.objects.filter(role=role).count()
    total_affaire_items = total_affaire.items()

    # -------------------------------
    # Surbrillance
    # -------------------------------
    if query:
        for role in roleSearch:
            role.colored_dateEnreg = colorize_found(query, role.dateEnreg.strftime('%d/%m/%Y') if role.dateEnreg else '')
            role.colored_president = colorize_found(query, role.president)
            role.colored_juge = colorize_found(query, role.juge)
            role.colored_greffier = colorize_found(query, role.greffier)
            role.colored_section = colorize_found(query, role.section)
            if role.juridiction:
                role.colored_juridiction = colorize_found(query, role.juridiction.name)

        for affaire in affaireSearch:
            affaire.colored_demandeurs = colorize_found(query, affaire.demandeurs)
            affaire.colored_defendeurs = colorize_found(query, affaire.defendeurs)
            affaire.colored_numRg = colorize_found(query, affaire.numRg)
            affaire.colored_natureInfraction = colorize_found(query, affaire.natureInfraction)
            affaire.colored_objet = colorize_found(query, affaire.objet)

    # -------------------------------
    # Contexte
    # -------------------------------
    presidents = Presidents.objects.all().order_by('-created_at')
    current_year = date.today().year
    year = int(request.GET.get('year', current_year))
    available_years = list(range(2024, current_year + 1))
    context = {
        'results': results,
        'roleSearch': roleSearch,
        'affaireSearch': affaireSearch,
        'total_affaire_items': total_affaire_items,
        'juridictions': juridictions,
        'presidents': presidents,
        'available_years': available_years,
        'query': query,
        'today': today
    }
    return render(request, 'role/index.html', context)


   
@login_required
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
    
def export_roleDetail_pdf(request):

    try:
        path = get_static_path("_base/assets_role/statics/armoirie.png")
        print("✅ Trouvé :", path)
    except FileNotFoundError as e:
        print("❌", e)
    # =======================
    # Récupérer les filtres
    # =======================
    query = request.GET.get('q', '').strip()
    role_id = request.GET.get('role_id', '').strip()

    affaire = AffaireRoles.objects.filter(role_id=role_id)
    role = Roles.objects.filter(id=role_id).first()

    if query:
        affaire = affaire.filter(
            Q(objet__icontains=query) |
            Q(demandeurs__icontains=query) |
            Q(defendeurs__icontains=query)
        )

    # =======================
    # Réponse HTTP PDF
    # =======================
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="role_{role.dateEnreg or "tous"}.pdf"'

    # =======================
    # Callbacks pour en-tête et pied de page
    # =======================
    def add_footer(canvas, doc, total_pages):
        page_width, page_height = canvas._pagesize
        footer_text = f"Téléchargé à partir de judicalex-gn.org - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        page_num = f"P.{doc.page} sur {total_pages}"
        canvas.drawString(10 * mm, 5 * mm, page_num)
        canvas.drawCentredString(page_width / 2, 5 * mm, footer_text)
        canvas.restoreState()

    def add_header(canvas, doc):
        page_width, page_height = canvas._pagesize
        canvas.saveState()
        canvas.setFont('Helvetica-Bold', 10)
        header_text = f"TCC - RÔLE D'AUDIENCE DE {role.get_typeAudience_display().upper()} DU {role.dateEnreg.strftime('%d/%m/%Y') if role.dateEnreg else 'TOUS'}"
        canvas.drawCentredString(page_width / 2, page_height - 20, header_text)
        canvas.restoreState()

    # =======================
    # Styles
    # =======================
    styles = getSampleStyleSheet()
    style_normal = styles["Normal"]
    style_normal.fontSize = 9
    style_normal.leading = 11
    style_normal.alignment = TA_CENTER

    style_title = ParagraphStyle("title", parent=styles["Heading2"], alignment=TA_CENTER, textColor=colors.HexColor("#000000"))
    style_title2 = ParagraphStyle(name="TitleCenter", alignment=1, fontSize=12, leading=16, underline=True, spaceAfter=6)
    style_normal2 = ParagraphStyle(name="NormalCenter", alignment=1, fontSize=12, leading=16)

    # =======================
    # En-tête du PDF
    # =======================
    try:
        armoirie = Image(staticfiles_storage.path("start/_base/assets_role/armoirie.png"), width=50, height=50)
        branding = Image(staticfiles_storage.path("start/_base/assets_role/branding.png"), width=80, height=50)
        simandou = Image(staticfiles_storage.path("start/_base/assets_role/simandou.png"), width=70, height=40)
        judicalex = Image(staticfiles_storage.path("start/_base/assets_role/ejustice_logo_white.png"), width=120, height=30)
    except Exception as e:
        print("❌ Image non trouvée :", e)
        armoirie = branding = simandou = judicalex = Paragraph("[Image manquante]", style_normal)

    col_gauche = Table(
        [[armoirie],
         [Paragraph("<b>République de Guinée</b>", style_normal)],
         [Paragraph("Travail - Justice - Solidarité", style_normal)],
         [Paragraph("Ministère de la Justice et des Droits de l'Homme", style_normal)],
         [branding]],
         style=TableStyle([
            ("ALIGN", (0,0), (-1,-1), "CENTER"),
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("BOTTOMPADDING", (0,0), (-1,-1), 4),
            ("TOPPADDING", (0,0), (-1,-1), 4),
        ])
    )

    titre_final = f"""
    <para>
    <b>RÔLE D'AUDIENCE DE {role.get_typeAudience_display().upper()} DU {role.dateEnreg.strftime('%d/%m/%Y') if role.dateEnreg else 'TOUS'}</b><br/>
    <b>COMPOSITION DU TRIBUNAL</b><br/>
    <b>PRÉSIDENT(E) :</b> {role.president or ''}<br/>
    {f'<b>JUGE(S) CONSULAIRE(S) :</b> {role.juge}<br/>' if role.juge else ''}
    <b>GREFFIER(E) :</b> {role.greffier or ''}
    </para>
    """

    filtre_text = f"FILTRE – Recherche : {query}" if query else ""

    centre_elements = [
        Paragraph("<b>COUR D'APPEL DE CONAKRY</b>", style_title),
        Paragraph("Tribunal de Commerce de Conakry", style_title),
        Paragraph("* &nbsp;&nbsp; * &nbsp;&nbsp; *", style_title),
        Paragraph(titre_final, style_title2)
    ]
    if filtre_text:
        centre_elements.append(Paragraph(filtre_text, style_normal2))

    col_centre = Table([[e] for e in centre_elements],
       style=TableStyle([
            ("ALIGN", (0,0), (-1,-1), "CENTER"),
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("BOTTOMPADDING", (0,0), (-1,-1), 6),
            ("TOPPADDING", (0,0), (-1,-1), 6),
        ])
    )

    role_url = f"https://judicalex-gn.org/role/{role.id}"
    qr_code = qr.QrCodeWidget(role_url)
    qr_drawing = Drawing(55, 55)
    qr_drawing.scale(0.8, 0.8)
    qr_drawing.add(qr_code)
    

    # Style pour le texte en italique
    style_italic = ParagraphStyle(
        name="Italic",
        fontName="Helvetica-Oblique",
        fontSize=8,
        alignment=1,  # centre le texte
        textColor=colors.black,
        spaceBefore=-8,  # réduit l’espace au-dessus du texte

    )


    col_droite = Table(
        [
            [judicalex],
            [Paragraph("<b>Conception & Réalisation</b><br/>Judicalex SARL<br/>contact@judicalex-gn.org<br/>Tel: 613 87 08 92 / 612 73 55 77<br/><br/>", style_normal)],
            [qr_drawing],
            [Paragraph("<i>Télécharger / consulter en ligne</i>", style_italic)],  # ✅ texte sous le QR code

        ],
       style=TableStyle([
            ("ALIGN", (0,0), (-1,-1), "CENTER"),
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("TOPPADDING", (0,0), (-1,-1), 4),
            ("BOTTOMPADDING", (0,0), (-1,-1), 4),
              # 🔽 Réduction spécifique sous le QR code (3e ligne, index 2)
            ("BOTTOMPADDING", (0, 2), (0, 2), -6),
        ]),
    )

    header_table = Table([[col_gauche, col_centre, col_droite]], colWidths=[155, 440, 155], rowHeights=170)

    # =======================
    # Contenu principal
    # =======================
    data = [[
        Paragraph("<b>No</b>", style_normal),
        Paragraph("<b>NUA</b>", style_normal),
        Paragraph("<b>RG</b>", style_normal),
        Paragraph("<b>Demandeurs</b>", style_normal),
        Paragraph("<b>Défendeurs</b>", style_normal),
        Paragraph("<b>Objet</b>", style_normal),
    ]]

    for i, r in enumerate(affaire, start=1):
        data.append([
            Paragraph(str(i), style_normal),
            Paragraph(r.numAffaire or "", style_normal),
            Paragraph(r.numRg or "", style_normal),
            Paragraph(r.demandeurs or "", style_normal),
            Paragraph(r.defendeurs or "", style_normal),
            Paragraph(r.objet or "", style_normal),
        ])

    table = Table(data, repeatRows=1, colWidths=[35, 120, 40, 190, 190, 170])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#4CAF50')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.3, colors.grey),
    ]))

    # =======================
    # Éléments du PDF
    # =======================
    elements = [header_table, Spacer(1, 12), table]

    # =======================
    # 1️⃣ Duplication (évite corruption)
    # =======================
    elements_temp = deepcopy(elements)
    elements_final = deepcopy(elements)

    # =======================
    # 2️⃣ Première passe — compter les pages
    # =======================
    buffer_temp = BytesIO()
    doc_temp = SimpleDocTemplate(
        buffer_temp,
        pagesize=landscape(A4),
        rightMargin=10, leftMargin=10, topMargin=20, bottomMargin=20
    )
    doc_temp.build(elements_temp)
    buffer_temp.seek(0)
    total_pages = len(PdfReader(buffer_temp).pages)

    # =======================
    # 3️⃣ Deuxième passe — PDF final
    # =======================
    def footer_final(canvas, doc): add_footer(canvas, doc, total_pages)
    def later_final(canvas, doc): add_header(canvas, doc); add_footer(canvas, doc, total_pages)

    doc_final = SimpleDocTemplate(
        response,
        pagesize=landscape(A4),
        rightMargin=10, leftMargin=10, topMargin=20, bottomMargin=20
    )
    doc_final.build(elements_final, onFirstPage=footer_final, onLaterPages=later_final)

    return response



@login_required
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
   
