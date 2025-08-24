from django import forms
from .models import (
    Rccm, Formalite, PersonnePhysique, Foyer_personne_physique, 
    Etablissement, EtablissementSecondaire, PersonnePhysiqueEngager, Gerant, ActiviteAnterieure
)


class ActiviteAnterieureForm(forms.ModelForm):
    class Meta:
        model = ActiviteAnterieure
        fields = [
            'activite_precedente',
            'type_activite',
            'details_autre_activite',
            'periode_fin',
            'rccm_precedent',
            'etablissement_principal',
            'etablissements_secondaires',
            'rccm_principal',
            'adresse',
        ]
        widgets = {
            'activite_precedente': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'type_activite': forms.Select(attrs={'class': 'form-select'}),
            'details_autre_activite': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Détails sur l'autre activité"}),
            'periode_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'rccm_precedent': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Précédent RCCM'}),
            'etablissement_principal': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description de l\'établissement principal'}),
            'etablissements_secondaires': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description des établissements secondaires'}),
            'rccm_principal': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'RCCM principal'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Adresse géographique et postale'}),
        }
        labels = {
            'activite_precedente': "Exercice d'une précédente activité",
            'type_activite': "Nature de l'activité",
            'details_autre_activite': "Détails sur l'autre activité",
            'periode_fin': "Période fin (mois et année)",
            'rccm_precedent': "Précédent RCCM (s'il y a lieu)",
            'etablissement_principal': "Établissement principal",
            'etablissements_secondaires': "Établissements secondaires",
            'rccm_principal': "RCCM principal (s'il y a lieu)",
            'adresse': "Adresse géographique et postale",
        }


# Form for Rccm model
class RccmForm(forms.ModelForm):
    class Meta:
        model = Rccm
        # Define fields to be used in the form
        fields = ['numeroRccm', 'dateEnreg', 'forme_juridique', 'capital_social', 'nom_banque', 'numero_compte', 'duree', 'rccm_file']
        widgets = {
            'numeroRccm': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Numéro RCCM', 'required': True, 'readonly':True, 'id': 'numeroRccm'}),
            'forme_juridique': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Numéro RCCM', 'required': True, 'id': 'numeroRccm'}),
            'capital_social': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Numéro RCCM', 'required': True, 'id': 'numeroRccm'}),
            'nom_banque': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Numéro RCCM', 'required': True, 'id': 'numeroRccm'}),
            'numero_compte': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Numéro RCCM', 'required': True, 'id': 'numeroRccm'}),
            'duree': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Numéro RCCM', 'required': True, 'id': 'numeroRccm'}),
            'rccm_file': forms.ClearableFileInput(attrs={'class': 'form-control', 'id':'rccm_file', 'required': True}),
            'dateEnreg': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'id':'dateEnreg', 'required': True}),
        }

# Form for Formalite model
class FormaliteForm(forms.ModelForm):
    class Meta:
        model = Formalite
        # Define fields related to Formalite and their attributes
        fields = [
            'typeRccm', 'rccm', 'numeroFormalite', 'denomination', 'siegeSocial','sigle', 'nomCommercial',
            'typeFormalite', 'declarationModificative', 'dateModification','optionActivite','mandataire'
        ]
        widgets = {
            'typeRccm': forms.Select(attrs={'class': 'form-select', 'required': True, 'id': 'typeRccm'}),
            'optionActivite': forms.Select(attrs={'class': 'form-select', 'required': True, 'id': 'optionActivite'}),
            'rccm': forms.Select(attrs={'class': 'form-select', 'id': 'rccm'}),
            'numeroFormalite': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Numéro Formalité',
                'required': True, 
                'id': 'numeroFormalite'
            }),
            'denomination': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Dénomination', 
                'required': True, 
                'id': 'denomination'
            }),
             'mandataire': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ex: Mr Camara Moussa , Gerant', 
                'id': 'mandataire'
            }),
            'siegeSocial': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Siège Social', 
                'required': True, 
                'id': 'siegeSocial'
            }),
            'typeFormalite': forms.Select(attrs={
                'class': 'form-select', 
                'id': 'typeFormalite',
                'required': True, 
            }),
            'declarationModificative': forms.Select(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'required': True, 
                'id': 'declarationModificative'
            }),
            'dateModification': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date', 
                'required': True, 
                'id': 'dateModification'
            }),
            'sigle': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Sigle', 
                'id': 'sigle'
            }),
            'nomCommercial': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Nom commercial', 
                'required': True, 
                'id': 'nomCommercial'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super(FormaliteForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Vider les champs en remplaçant leur valeur initiale
            self.initial['typeFormalite'] = None
            self.initial['declarationModificative'] = ''
            self.initial['optionActivite'] = ''
            self.initial['numeroFormalite'] = ''
            self.initial['dateModification'] = None  # Utiliser None pour un champ DateField   

# Form for PersonnePhysique model
class PersonnePhysiqueForm(forms.ModelForm):
    class Meta:
        model = PersonnePhysique
        # Define fields for managing personal details
        fields = [
            'formalite', 'titreCivil', 'prenom', 'nom', 'dateNaissance', 
            'lieuNaissance', 'nationnalite', 'adressePostale', 'telephone', 'domicile', 
            'ville', 'quartier', 'autrePrecision', 'coordonneesElectro', 'situationMatrimoniale'
            
        ]
        widgets = {
            'formalite': forms.Select(attrs={'class': 'form-control', 'id': 'formalite'}),
            'titreCivil': forms.Select(attrs={'class': 'form-control', 'required': True, 'id': 'titreCivil'}),
            
            # Text input for names and nationalities
            'prenom': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Prénom', 
                'required': True, 
                'id': 'prenom'
            }),
            'nom': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Nom', 
                'required': True, 
                'id': 'nom'
            }),
            'nationnalite': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Nationalité', 
                'required': True, 
                'id': 'nationnalite'
            }),

            # Date input for date of birth
            'dateNaissance': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date', 
                'placeholder': 'YYYY-MM-DD', 
                'required': True, 
                'id': 'dateNaissance'
            }),

            # Text inputs for location and address details
            'lieuNaissance': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Lieu de naissance', 
                'required': True, 
                'id': 'lieuNaissance'
            }),
            'adressePostale': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Adresse complète', 
                'id': 'adressePostale'
            }),
            'ville': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ville', 
                'required': True, 
                'id': 'ville'
            }),
            'quartier': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Quartier', 
                'required': True, 
                'id': 'quartier'
            }),
            'autrePrecision': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Autres précisions', 
                'id': 'autrePrecision'
            }),

            # Phone and contact details
            'telephone': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Numéro de téléphone', 
                'type': 'tel', 
                'required': True, 
                'id': 'telephone'
            }),
            'domicile': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Domicile', 
                'required': True, 
                'id': 'domicile'
            }),
            'coordonneesElectro': forms.EmailInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Email', 
                'id': 'coordonneesElectro'
            }),

            # Dropdown for marital status
            'situationMatrimoniale': forms.Select(attrs={
                'class': 'form-control', 
                'required': True, 
                'id': 'situationMatrimoniale'
            }),
        }

# Form for Foyer_personne_physique model
class FoyerPersonnePhysiqueForm(forms.ModelForm):
    class Meta:
        model = Foyer_personne_physique
        # Fields related to person's marital details
        fields = [
            'personnePhysique', 'conjoint', 'nomComplet', 'dateLieuMariage', 
            'optionMatrimoniale', 'regimeMatrimoniale', 'demandeSeparationBien'
        ]

# Form for Etablissement model
class EtablissementForm(forms.ModelForm):
    class Meta:
        model = Etablissement
        # Fields for handling establishment details
        fields = [
            'formalite', 'sigle', 'nomCommercial', 'rccm', 'activites', 'activitesAjouter', 
            'activitesSupprimer', 'activitesActualiser', 'adresseEtablissement', 'ancienneAdresse', 
            'nouvelleAdresse'
        ]

        widgets = {
            # Text inputs for sigle and nomCommercial
            'sigle': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Entrez le sigle de l\'établissement',
                'id': 'sigle'
            }),
            'nomCommercial': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Entrez le nom commercial',
                'id': 'nomCommercialNew'
            }),

            # Text input for RCCM (unique business identifier)
            'rccm': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Entrez le RCCM',
                'id': 'rccm'
            }),

            # Textarea for activities
            'activites': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Décrivez les activités principales',
                'required': True,
                'id': 'activites'
            }),
            'activitesAjouter': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ajoutez des activités',
                'id': 'activitesAjouter'
            }),
            'activitesSupprimer': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Supprimez des activités',
                'id': 'activitesSupprimer'
            }),
            'activitesActualiser': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Mettez à jour les activités',
                'id': 'activitesActualiser'
            }),

            # Textarea for addresses
            'adresseEtablissement': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Entrez l\'adresse complète de l\'établissement',
                'rows': 2,
                'id': 'adresseEtablissement'
            }),
            'ancienneAdresse': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Entrez l\'ancienne adresse',
                'rows': 2,
                'id': 'ancienneAdresse'
            }),
            'nouvelleAdresse': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Entrez la nouvelle adresse',
                'rows': 2,
                'id': 'nouvelleAdresse'
            }),
        }

    def __init__(self, *args, **kwargs):
        super(EtablissementForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Vider les champs en remplaçant leur valeur initiale
            self.initial['activitesAjouter'] = ''
            self.initial['sigle'] = ''
            self.initial['nomCommercial'] = ''
            self.initial['activitesSupprimer'] = ''
            self.initial['activitesActualiser'] = ''  # Utiliser None pour un champ DateField

# Form for EtablissementSecondaire model
class EtablissementSecondaireForm(forms.ModelForm):
    class Meta:
        model = EtablissementSecondaire
        # Additional fields for secondary establishments
        fields = [
            'formalite', 'sigle', 'nomCommercial', 'rccm', 'activites', 'activitesAjouter', 
            'activitesSupprimer', 'activitesActualiser', 'autresActivites', 'adresseEtablissement', 
            'ancienneAdresse', 'nouvelleAdresse'
        ]

# Form for PersonnePhysiqueEngager model
class PersonnePhysiqueEngagerForm(forms.ModelForm):
    class Meta:
        model = PersonnePhysiqueEngager
        # Fields for managing person's engagement information
        fields = [
            'formalite', 'prenom', 'nom', 'dateNaissance', 'lieuNaissance', 
            'nationnalite', 'domicile', 'modeDomicilier', 'objetModification', 'dateModification2', 
        ]
        widgets = {
            # Text input for prenom and nom
            'prenom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Entrez le prénom',
                'id': 'prenom2'
            }),
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Entrez le nom',
                'id': 'nom2'
            }),

            # Date picker for dateNaissance
            'dateNaissance': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'id': 'dateNaissance2'
            }),

            # Text input for lieuNaissance
            'lieuNaissance': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Entrez le lieu de naissance',
                'id': 'lieuNaissance2'
            }),

            # Dropdown for nationnalite
            'nationnalite': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Sélectionnez la nationalité',
                'id': 'nationnalite2'
            }),

            # Text input for domicile
            'domicile': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Entrez le domicile',
                'id': 'domicile2'
            }),

            # Dropdown or radio buttons for modeDomicilier
            'modeDomicilier': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Sélectionnez le mode de domiciliation',
                'id': 'modeDomicilier'
            }),

            # Textarea for objetModification
            'objetModification': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Décrivez l\'objet de la modification',
                'id': 'objetModification'
            }),

            # Date picker for dateModification
            'dateModification2': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'id': 'dateModification2'
            }),
        }


# Form for Gerant model
class GerantForm(forms.ModelForm):
    class Meta:
        model = Gerant
        # Fields for managing manager information
        fields = [
            'formalite', 'titreCivil', 'prenom', 'nom', 'typeDemande'
        ]

class PDFUploadForm(forms.Form):
    type_rccm = forms.ChoiceField(
        choices=[('', '--------------'), ('PERSONNE PHYSIQUE', 'Personne physique'), ('PERSONNE MORALE', 'Personne morale')],  # Remplacez par les choix appropriés, par exemple : [('option1', 'Option 1'), ('option2', 'Option 2')]
        widget=forms.Select(attrs={'class': 'form-select mb-4', 'id': 'typeRccm'}),
        required=True
    )

    pdf_file = forms.FileField(
        label="Importez ici le document scanné ",
        required=True,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control mb-4', 'id':'upload_input', 'accept': 'application/pdf'})
    )

    result_ocr = forms.CharField(
        label="Texte extrait",
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'id': 'ocrResult',
            'rows': 6,
            'cols': 40,
            'readonly': True,  # Rend le champ non modifiable
            'style': 'background-color: #e9ecef; cursor: not-allowed;'  # Grise le champ et change le curseur
        })
    )


class PDFUploadSignature(forms.Form):
   
    formaliteSignee = forms.FileField(
        label="Importez ici le document scanné ",
        required=True,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control mb-4', 'id':'upload_signature', 'accept': 'application/pdf'})
    )



