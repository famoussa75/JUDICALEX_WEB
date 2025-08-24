from django.shortcuts import render
from .models import ContactPro, Lien


# Create your views here.
def liste(request, fonction):
    contacts = ContactPro.objects.filter(fonction=fonction)
    return render(request, 'divers/annuaire.html', {'contacts': contacts, 'fonction':fonction})



def liens_utiles_view(request):
    liens = Lien.objects.all()
    return render(request, 'divers/liens_utiles.html', {'liens': liens})