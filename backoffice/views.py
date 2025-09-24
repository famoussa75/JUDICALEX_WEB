from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.core.paginator import Paginator
from blog.models import Comment, InternalComment, Post
from blog.forms import InternalCommentForm, PostForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from users.models import Account, ContributionRequest, Notification
from django.db.models import Q
from django.utils import timezone
from django.http import HttpResponseRedirect
from .models import Ad
from .forms import AdForm
from django.http import JsonResponse
from .utils import create_notification


# Create your views here.

def login(request):
     return render(request, 'backoffice/auth/login.html')



# Vérifie si user est admin ou staff
def is_admin(user):
    return user.is_staff or user.is_superuser


# Liste des articles
@login_required
def post_list(request):
    
    # 🔎 Récupérer la recherche
    query = request.GET.get("q", "").strip()

    # ⚡ Base queryset

    if request.user.groups.filter(name="Pigiste").exists():
        # Sinon → uniquement ses posts
        posts = Post.objects.select_related("author").filter(author=request.user).order_by("-created_at")
       
    else:
         # Si admin → tous les posts
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
def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)


    # Pagination des commentaires
    comment_list = Comment.objects.filter(post=post)
    paginator = Paginator(comment_list, 5)  # 5 commentaires par page
    page_number = request.GET.get("page")
    comments = paginator.get_page(page_number)

    comments_int = InternalComment.objects.filter(post=post).order_by("-created_at")
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
def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)   # On récupère l'objet sans enregistrer
            post.author = request.user       # Auteur = utilisateur connecté
            post.status = "draft"            # Exemple : statut par défaut "draft"
            post.save()

            # Notifier tous les utilisateurs sauf celui qui a soumis
            recipients = Account.objects.exclude(id=request.user.id).exclude(groups__name__in=["Visiteur", "Contributeur"])
            for recipient in recipients:
                create_notification(
                    recipient=recipient,
                    sender=request.user,
                    type="info",
                    message=f"Nouvel article soumis : {post.title}",
                    objet_cible=post.id,
                    url=reverse("post_detail", args=[post.slug])
                )
            return redirect("post_list")
    else:
        form = PostForm()
    return render(request, "backoffice/ges-news/post_form.html", {"form": form})


# Modifier un article
@login_required
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
def post_delete(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if request.method == "POST":
        post.delete()
        return redirect("post_list")
    return render(request, "backoffice/ges-news/post_confirm_delete.html", {"post": post})


@login_required
@user_passes_test(is_admin)
def post_publish(request, slug):
    post = get_object_or_404(Post, slug=slug)

    # Vérification de l'autorisation : auteur ou admin
    if post.author != request.user and not request.user.is_staff:
        messages.error(request, "Vous n’avez pas la permission de publier cet article.")
        return redirect("post_detail", slug=post.slug)

    # Mettre à jour le statut
    post.status = "published"
    post.save()

     # Notifier l’auteur
    create_notification(
        recipient=post.author,
        sender=request.user,
        type="success",
        message=f"Votre article '{post.title}' a été approuvé et publié",
        objet_cible=post.id,
        url=reverse("post_detail", args=[post.slug])
    )

    messages.success(request, "L’article a été publié avec succès ✅")
    return redirect("post_detail", slug=post.slug)

@login_required
def post_unpublish(request, slug):
    post = get_object_or_404(Post, slug=slug)

    # Seuls les administrateurs peuvent dépublier
    if not request.user.groups.filter(name="Administrateur").exists():
        messages.error(request, "Vous n’avez pas la permission de retirer cet article de la publication.")
        return redirect("post_detail", slug=post.slug)

    post.status = "draft"
    post.save()

     # Notifier l’auteur
    create_notification(
        recipient=post.author,
        sender=request.user,
        type="warning",
        message=f"Votre article '{post.title}' a été retiré de la publication",
        objet_cible=post.id,
        url=reverse("post_detail", args=[post.slug])
    )

    messages.success(request, "L’article a été retiré de la publication.")
    return redirect("post_detail", slug=post.slug)


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

     # Notifier Demandeur
    create_notification(
        recipient=demande.demandeur,
        sender=request.user,
        type="success",
        message=f"Votre demande a été approuvée. Bienvenue dans l'équipe des contributeurs !",
        url='profile/'
    )
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
     # Notifier Demandeur (refus poli)
    create_notification(
        recipient=demande.demandeur,
        sender=request.user,
        type="warning",
        message="Votre demande de contribution n’a pas été retenue pour le moment. Nous vous remercions pour votre intérêt et vous encourageons à réessayer ultérieurement.",
        url='profile/'
    )

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

def ad_impression(request):
    ad_id = request.GET.get('ad_id')
    ad = get_object_or_404(Ad, id=ad_id)
    ad.impressions += 1
    ad.save()
    return JsonResponse({'status': 'ok', 'impressions': ad.impressions})

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

            # Notifier tous les utilisateurs sauf celui qui a soumis
            recipients = Account.objects.exclude(id=request.user.id).exclude(groups__name__in=["Visiteur", "Contributeur"])
            for recipient in recipients:
                create_notification(
                    recipient=recipient,
                    sender=request.user,
                    type="info",
                    message=f"Nouvelle observation dans l'article : {post.title}",
                    objet_cible=post.id,
                    url=reverse("post_detail", args=[post.slug])
                )
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


@login_required
def read_notification(request, pk):
    notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notif.is_read = True
    notif.save()
    # Redirige vers l'URL de la notification si elle existe, sinon vers l'accueil
    return redirect(notif.url or 'home')

@login_required
def notifications_list(request):
    # Récupère toutes les notifications de l'utilisateur connecté
    notifications_qs = request.user.notifications.all()
    paginator = Paginator(notifications_qs, 10)  # 10 notifications par page
    page_number = request.GET.get('page')
    notifications = paginator.get_page(page_number)

    return render(request, 'backoffice/ges-users/notifications_list.html', {
        'notifications': notifications
    })

@login_required
def mark_all_notifications_read(request):
    # Marque toutes les notifications comme lues
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return redirect('notifications_list')

@login_required
def notifications_delete_all(request):
    """Supprime toutes les notifications de l'utilisateur connecté."""
    user_notifications = request.user.notifications.all()
    
    if user_notifications.exists():
        count = user_notifications.count()
        user_notifications.delete()
        messages.success(request, f"Toutes vos {count} notifications ont été supprimées.")
    else:
        messages.info(request, "Vous n'avez aucune notification à supprimer.")
    
    return redirect('notifications_list')  # Redirige vers la liste des notifications