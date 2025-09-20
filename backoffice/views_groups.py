from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from .forms import GroupForm
from .permissions import is_admin

@login_required
@user_passes_test(is_admin)
def group_list(request):
    q = request.GET.get("q", "").strip()
    qs = Group.objects.all().order_by("name")
    if q:
        qs = qs.filter(Q(name__icontains=q))
    paginator = Paginator(qs, 20)
    page = request.GET.get("page")
    page_obj = paginator.get_page(page)
    params = request.GET.copy(); params.pop("page", None)
    querystring = params.urlencode()

    return render(request, "groups/group_list.html", {
        "page_obj": page_obj,
        "is_paginated": page_obj.has_other_pages(),
        "q": q,
        "querystring": querystring,
    })

@login_required
@user_passes_test(is_admin)
def group_create(request):
    if request.method == "POST":
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Groupe créé.")
            return redirect("groups:list")
    else:
        form = GroupForm()
    return render(request, "groups/group_form.html", {"form": form, "title": "Créer un groupe"})

@login_required
@user_passes_test(is_admin)
def group_update(request, pk):
    group = get_object_or_404(Group, pk=pk)
    if request.method == "POST":
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            messages.success(request, "Groupe mis à jour.")
            return redirect("groups:list")
    else:
        form = GroupForm(instance=group)
    return render(request, "groups/group_form.html", {"form": form, "title": "Modifier le groupe"})

@login_required
@user_passes_test(is_admin)
def group_delete(request, pk):
    group = get_object_or_404(Group, pk=pk)
    if request.method == "POST":
        group.delete()
        messages.success(request, "Groupe supprimé.")
        return redirect("groups:list")
    return render(request, "groups/group_confirm_delete.html", {"group": group})
