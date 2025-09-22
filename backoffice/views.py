from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.core.paginator import Paginator
from blog.models import Comment, InternalComment, Post
from blog.forms import InternalCommentForm, PostForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from users.models import ContributionRequest
from django.db.models import Q
from django.utils import timezone
from django.http import HttpResponseRedirect
from .models import Ad
from .forms import AdForm


# Create your views here.

def login(request):
     return render(request, 'backoffice/auth/login.html')

def index(request):
     return render(request, 'backoffice/home/home-1.html')

# Vérifie si user est admin ou staff
def is_admin(user):
    return user.is_staff or user.is_superuser


# Liste des articles
@login_required
@user_passes_test(is_admin)
def post_list(request):
    
    # 🔎 Récupérer la recherche
    query = request.GET.get("q", "").strip()

    # ⚡ Base queryset

    posts = Post.objects.select_related("author").all().order_by("-created_at")

    if query:
        posts = posts.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(author__username__icontains=query) |
            Q(author__first_name__icontains=query) |
            Q(author__last_name__icontains=query) |
            Q(author__email__icontains=query)  # si tu veux rechercher par email aussi
            # Si ton modèle auteur custom a un champ "name", ajoute :
            # | Q(author__name__icontains=query)
        )

    # 📄 Pagination (10 par page)
    paginator = Paginator(posts, 10)
    page = request.GET.get("page")
    posts = paginator.get_page(page)

    # Conserver la recherche dans la pagination
    context = {
        "posts": posts,
        "query": query,
    }
    return render(request, "backoffice/ges-news/post_list.html", context)


@login_required
@user_passes_test(is_admin)
def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)


    # Pagination des commentaires
    comment_list = Comment.objects.filter(post=post)
    paginator = Paginator(comment_list, 5)  # 5 commentaires par page
    page_number = request.GET.get("page")
    comments = paginator.get_page(page_number)

    comments_int = InternalComment.objects.all().order_by("-created_at")
    paginator_int = Paginator(comments_int, 5)  # 5 commentaires par page
    page_number_int = request.GET.get("page")
    internal_comments = paginator_int.get_page(page_number_int)

    comments_form = InternalCommentForm()


    return render(request, "backoffice/ges-news/post_detail.html", {
        "post": post,
        "comments": comments,
        "internal_comments": internal_comments,
        "comment_form": comments_form,
    })


# Créer un article
@login_required
@user_passes_test(is_admin)
def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("post_list")
    else:
        form = PostForm()
    return render(request, "backoffice/ges-news/post_form.html", {"form": form})


# Modifier un article
@login_required
@user_passes_test(is_admin)
def post_update(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect("post_detail", slug=post.slug)
    else:
        form = PostForm(instance=post)
    return render(request, "backoffice/ges-news/post_form.html", {"form": form, "post": post})


# Supprimer un article
@login_required
@user_passes_test(is_admin)
def post_delete(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if request.method == "POST":
        post.delete()
        return redirect("post_list")
    return render(request, "backoffice/ges-news/post_confirm_delete.html", {"post": post})


# Liste des demandes
@login_required
@user_passes_test(is_admin)
def liste_demandes(request):
    # ⚡ Recherche simple (optionnelle)
    q = request.GET.get("q", "").strip()
    demandes = ContributionRequest.objects.all().order_by("-created_at")
    if q:
        demandes = demandes.filter(
            nom__icontains=q
        ) | demandes.filter(
            email__icontains=q
        ) | demandes.filter(
            sujet__icontains=q
        )

    # 📄 Pagination (10 par page)
    paginator = Paginator(demandes, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # 🔗 Préserver les filtres dans la pagination
    params = request.GET.copy()
    params.pop("page", None)
    querystring = params.urlencode()

    context = {
        "page_obj": page_obj,
        "is_paginated": page_obj.has_other_pages(),
        "querystring": querystring,
        "q": q,
    }
    return render(request, "backoffice/ges-demandes/liste.html", context)


# Détails d'une demande
@login_required
@user_passes_test(is_admin)
def details_demande(request, demande_id):
    demande = get_object_or_404(ContributionRequest, id=demande_id)
    return render(request, "backoffice/ges-demandes/details.html", {"demande": demande})

# Approuver une demande
@login_required
@user_passes_test(is_admin)
def approuver_demande(request, demande_id):
    demande = get_object_or_404(ContributionRequest, id=demande_id)
    demande.status = "approved"
    demande.save()
    # Ajouter l’utilisateur dans le groupe Contributeur
    from django.contrib.auth.models import Group
    contributeur_group, created = Group.objects.get_or_create(name="Contributeur")
    demande.demandeur.groups.add(contributeur_group)

    messages.success(request, f"La demande de {demande.demandeur.username} a été approuvée.")
    return redirect("liste_demandes")

# Rejeter une demande
@login_required
@user_passes_test(is_admin)
def rejeter_demande(request, demande_id):
    demande = get_object_or_404(ContributionRequest, id=demande_id)
    demande.status = "rejected"
    demande.save()
    messages.warning(request, f"La demande de {demande.demandeur.username} a été rejetée.")
    return redirect("liste_demandes")


# ads/views.py

def ad_list(request):
    ads = Ad.objects.all().order_by("-created_at")
    paginator = Paginator(ads, 6)  # 6 pubs par page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "backoffice/ges-ads/ad_list.html", {"page_obj": page_obj})

def ad_create(request):
    if request.method == "POST":
        form = AdForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("ad_list")
    else:
        form = AdForm()
    return render(request, "backoffice/ges-ads/ad_form.html", {"form": form})

def ad_edit(request, pk):
    ad = get_object_or_404(Ad, pk=pk)
    if request.method == "POST":
        form = AdForm(request.POST, request.FILES, instance=ad)
        if form.is_valid():
            form.save()
            return redirect("ad_list")
    else:
        form = AdForm(instance=ad)
    return render(request, "backoffice/ges-ads/ad_form.html", {"form": form})

def ad_delete(request, pk):
    ad = get_object_or_404(Ad, pk=pk)
    if request.method == "POST":
        ad.delete()
        return redirect("ad_list")
    return render(request, "backoffice/ges-ads/ad_confirm_delete.html", {"ad": ad})

# ---- Gestion des clics ----
def ad_click(request, pk):
    ad = get_object_or_404(Ad, pk=pk)
    ad.clicks += 1
    ad.save(update_fields=["clicks"])
    return HttpResponseRedirect(ad.link)

@login_required
def comment_create(request, slug):
    post = get_object_or_404(Post, slug=slug)

    if request.method == "POST":
        form = InternalCommentForm(request.POST)
        if form.is_valid():
            # Ne pas sauvegarder tout de suite, on ajoute post et user
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
            messages.success(request, "Commentaire créé avec succès !")
        else:
            messages.error(request, "Veuillez corriger les erreurs dans votre commentaire.")

    return redirect("post_detail", slug=post.slug)

# Suppression
@login_required
def comment_delete(request, comment_id, slug):
    post = get_object_or_404(Post, slug=slug)
    comment = get_object_or_404(InternalComment, id=comment_id)
    if request.method == "POST":
        comment.delete()
        messages.success(request, "Commentaire supprimé !")
        return redirect("post_detail", slug=post.slug)
    return render(request, "backoffice/ges-news/comment_confirm_delete.html", {"comment": comment})