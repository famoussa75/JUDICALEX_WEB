from django.shortcuts import get_object_or_404, render
from django.template import Template, Context
from .models import ModeleDoc
from .forms import PersonnalisationConvocationForm

def voir_modele_doc(request, slug):
    doc = get_object_or_404(ModeleDoc, slug=slug)

    # Choix du formulaire selon le type de document
    if doc.type_document == 'convocation':
        FormClass = PersonnalisationConvocationForm
    else:
        FormClass = PersonnalisationConvocationForm  # Form par défaut, à adapter selon ton projet

    form = FormClass(request.GET or None)

    # Par défaut, afficher le contenu avec des champs vides (placeholder)
    contexte_brut = {name: "__________" for name in form.fields.keys()}
    template = Template(doc.contenu)
    contenu = template.render(Context(contexte_brut))

    # Si le formulaire est valide, remplir les champs
    if form.is_valid():
        contenu = template.render(Context(form.cleaned_data))

    return render(request, 'emploi/voir_modele.html', {
        'doc': doc,
        'form': form,
        'contenu': contenu,
    })


def liste_docs(request, type_document=None):
    docs = ModeleDoc.objects.all()
    if type_document:
        docs = docs.filter(type_document=type_document)
    return render(request, 'emploi/liste.html', {'docs': docs})

