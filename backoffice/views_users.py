from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from .forms import AccountCreateForm, AccountUpdateForm
from .permissions import is_admin
from django.contrib.auth import logout


User = get_user_model()

@login_required
@user_passes_test(is_admin)
def user_list(request):
    q = request.GET.get("q", "").strip()
    qs = User.objects.select_related("juridiction").all().order_by("-date_joined")
    if q:
        qs = qs.filter(
            Q(username__icontains=q) |
            Q(email__icontains=q) |
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q)
        )
    paginator = Paginator(qs, 12)
    page = request.GET.get("page")
    page_obj = paginator.get_page(page)

    params = request.GET.copy(); params.pop("page", None)
    querystring = params.urlencode()

    return render(request, "backoffice/ges-users/user_list.html", {
        "page_obj": page_obj,
        "is_paginated": page_obj.has_other_pages(),
        "q": q,
        "querystring": querystring,
    })

@login_required
@user_passes_test(is_admin)
def user_create(request):
    if request.method == "POST":
        form = AccountCreateForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Utilisateur créé avec succès.")
            return redirect("user.list")
    else:
        form = AccountCreateForm()
    return render(request, "backoffice/ges-users/user_form.html", {"form": form, "title": "Créer un utilisateur"})

@login_required
@user_passes_test(is_admin)
def user_update(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        form = AccountUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Utilisateur mis à jour.")
            return redirect("user.list")
    else:
        form = AccountUpdateForm(instance=user)
    return render(request, "backoffice/ges-users/user_form.html", {"form": form, "title": "Modifier l’utilisateur"})

@login_required
@user_passes_test(is_admin)
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        if request.user.pk == user.pk:
            messages.error(request, "Vous ne pouvez pas supprimer votre propre compte.")
        else:
            user.delete()
            messages.success(request, "Utilisateur supprimé.")
            return redirect("user.list")
    return render(request, "backoffice/ges-users/user_confirm_delete.html", {"user_obj": user})

@login_required
def logout_view(request):
    """Déconnecte l'utilisateur puis redirige vers next, LOGOUT_REDIRECT_URL,
    sinon LOGIN_URL, sinon la racine."""
    logout(request)
    messages.success(request, "Vous avez été déconnecté(e).")

    next_url = request.GET.get("next") or request.POST.get("next")
    if next_url:
        return redirect(next_url)

    return redirect('home')
