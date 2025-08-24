from django import forms

from django import forms

class DemandeCompteForm(forms.Form):
    nom_banque = forms.CharField(
        label="Nom de la banque",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    ville = forms.CharField(
        label="Ville",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    date = forms.DateField(
        label="Date",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    nom_entreprise = forms.CharField(
        label="Nom de l’entreprise",
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    forme_juridique = forms.CharField(
        label="Forme juridique",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    numero_rccm = forms.CharField(
        label="Numéro RCCM",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    numero_nif = forms.CharField(
        label="Numéro NIF",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    activite = forms.CharField(
        label="Activité de l’entreprise",
        widget=forms.Textarea(attrs={'rows': 2, 'class': 'form-control'})
    )
    
    nom_signataire = forms.CharField(
        label="Votre nom",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    telephone = forms.CharField(
        label="Téléphone",
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label="Adresse email",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

