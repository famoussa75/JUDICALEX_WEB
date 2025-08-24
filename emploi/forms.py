from django import forms

TITRE_CHOICES = [
    ('Madame', 'Madame'),
    ('Monsieur', 'Monsieur'),
]

class PersonnalisationConvocationForm(forms.Form):
    nom_employe = forms.CharField(label="Nom de l'employé", required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    fonction_employe = forms.CharField(label="Fonction de l'employé", required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    titre_employe = forms.ChoiceField(
        label="Titre de l'employé",
        choices=TITRE_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    titre_employeur = forms.ChoiceField(
        label="Titre de l'employeur",
        choices=TITRE_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    date_document = forms.DateField(label="Date du document", required=True, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    
    date_debut_conge = forms.DateField(label="Début du congé", required=True, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    date_fin_conge = forms.DateField(label="Fin du congé", required=True, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    raison_conge = forms.CharField(label="Raison du congé", required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))

    
    date_entretien = forms.DateField(label="Date de l'entretien", required=True, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    heure_entretien = forms.TimeField(label="Heure de l'entretien", required=True, widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}))
    lieu_entretien = forms.CharField(label="Lieu de l'entretien", required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))

    nom_signataire = forms.CharField(label="Nom du signataire", required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    fonction_signataire = forms.CharField(label="Fonction du signataire", required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))


