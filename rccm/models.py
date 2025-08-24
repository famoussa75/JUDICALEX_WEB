import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from users.models import Account


# Rccm.
class Rccm(models.Model):

    numeroRccm = models.TextField(null=True, blank=True,verbose_name=_('Numéro Rccm'))
    dateEnreg =  models.DateField(null=True, blank=True,verbose_name=_('Date d\'enregistrement'))
    forme_juridique = models.CharField(max_length=50, null=True, blank=True, verbose_name="Forme Juridique", default="SARL")
    capital_social = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Capital Social")
    nom_banque = models.CharField(max_length=255, null=True, blank=True, verbose_name="Nom de la Banque")
    numero_compte = models.CharField(max_length=50, null=True, blank=True, verbose_name="Numéro de Compte")
    duree = models.IntegerField(null=True, blank=True, verbose_name="Durée (en années)")
    rccm_file = models.FileField(upload_to='rccm_files/', null=True, blank=True, verbose_name="Fichier associé")
    slug = models.UUIDField(default=uuid.uuid4, editable=False)
    created_by = models.ForeignKey(Account,blank=True, null=True, on_delete=models.CASCADE, verbose_name=_('Rccm Creer par'))
    created_at = models.DateTimeField(null=True, blank=True,auto_now=True, verbose_name=_('Date de creation Rccm')) 

# Formalités.
class Formalite(models.Model):

    TYPE_FORMALITE = (
        ("Modification", "Modification"),
        ("Radiation", "Radiation"),
        ("Dissolution", "Dissolution"),
    )

    TYPE_RCCM = (
        ("PERSONNE PHYSIQUE", "Personne physique"),
        ("PERSONNE MORALE", "Personne morale"),
    )

    DECLARATION = (
        ("A L'ACTIVITE", "L'activite"),
        ("A LA DENOMINATION", "La dénomination"),
        ("AU SIEGE SOCIAL", "Au siège Social"),
    )

    OPTION_ACTIVITE = (
        ("Rajout", "Rajout"),
        ("Suppression", "Suppression"),
        ("Suppression_et_Rajout", "Suppression et Rajout"),
        ("Changement", "Changement"),
    )

    typeRccm = models.TextField(null=True, blank=True,choices=TYPE_RCCM,verbose_name=_('Type Rccm'))
    rccm = models.ForeignKey(Rccm,blank=True, null=True, on_delete=models.CASCADE, verbose_name=_('Rccm'))
    numeroFormalite = models.TextField(null=True, blank=True,verbose_name=_('Numéro Formalite'))
    denomination = models.TextField(null=True, blank=True,verbose_name=_('Denomination'))
    sigle = models.TextField(null=True, blank=True,verbose_name=_('Sigle'))
    nomCommercial = models.TextField(null=True, blank=True,verbose_name=_('Nom commercial'))
    mandataire = models.TextField(null=True, blank=True,verbose_name=_('Mandataire'))
    siegeSocial = models.TextField(null=True, blank=True,verbose_name=_('Siege Social'))
    typeFormalite = models.TextField(null=True, blank=True,choices=TYPE_FORMALITE,verbose_name=_('Type Formalité'))
    optionActivite = models.TextField(null=True, blank=True,choices=OPTION_ACTIVITE,verbose_name=_('Option activite'))
    declarationModificative = models.TextField(null=True, blank=True,choices=DECLARATION,verbose_name=_('Déclaration modificative'))
    dateModification =  models.DateField(null=True, blank=True,verbose_name=_('Date Modification'))
    slug = models.UUIDField(default=uuid.uuid4, editable=False)
    created_by = models.ForeignKey(Account,blank=True, null=True, on_delete=models.CASCADE, verbose_name=_('Formalité Creer par'))
    created_at = models.DateTimeField(null=True, blank=True,auto_now=True, verbose_name=_('Date de creation formalité'))
    formaliteSignee = models.FileField(upload_to='formalite_signees/', null=True, blank=True, verbose_name=_('Formalité signée'))


# Renseignements relatifs a la personne physique.
class PersonnePhysique(models.Model):

    TITRE_CIVIL = (
        ("M", "Monsieur"),
        ("Mme", "Madame"),
        ("Mlle", "Mademoiselle"),
    )

    SITUATION_MATRIMONIALE = (
        ("Celibataire", "Célibataire"),
        ("Marie(e)", "Marié(e)"),
        ("Veuf(e)", "Veuf(e)"),
        ("Divorce(e)", "Divorcé(e)"),
    )


    formalite = models.ForeignKey(Formalite,blank=True, null=True, on_delete=models.CASCADE, verbose_name=_('Formalité'))
    titreCivil = models.TextField(null=True, blank=True,choices=TITRE_CIVIL,verbose_name=_('Titre civil'))
    prenom = models.TextField(null=True, blank=True,verbose_name=_('Prenom'))
    nom = models.TextField(null=True, blank=True,verbose_name=_('Nom'))
    dateNaissance =  models.DateField(null=True, blank=True,verbose_name=_('Date naissance'))
    lieuNaissance = models.TextField(null=True, blank=True,verbose_name=_('Lieu naisssance'))
    nationnalite = models.TextField(null=True, blank=True,verbose_name=_('Nationnalité'))
    adressePostale = models.TextField(null=True, blank=True,verbose_name=_('Adresse postale'))
    telephone = models.TextField(null=True, blank=True,verbose_name=_('Telephone'))
    domicile = models.TextField(null=True, blank=True,verbose_name=_('Domicile personnel'))
    ville = models.TextField(null=True, blank=True,verbose_name=_('Ville'))
    quartier = models.TextField(null=True, blank=True,verbose_name=_('Quartier'))
    autrePrecision = models.TextField(null=True, blank=True,verbose_name=_('Autres precisions'))
    coordonneesElectro = models.TextField(null=True, blank=True,verbose_name=_('Coordonnées electroniques'))
    situationMatrimoniale = models.TextField(null=True, blank=True,choices=SITUATION_MATRIMONIALE,verbose_name=_('Situation matrimonial'))
    slug = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(null=True, blank=True,auto_now=True, verbose_name=_('Date de creation personne physique')) 

# Tableau de la situation matrimoniale de la personne
class Foyer_personne_physique(models.Model):

    formalite = models.ForeignKey(Formalite,blank=True, null=True, on_delete=models.CASCADE, verbose_name=_('Formalité'))
    personnePhysique = models.ForeignKey(PersonnePhysique,blank=True, null=True, on_delete=models.CASCADE, verbose_name=_('personne physique'))
    conjoint = models.TextField(null=True, blank=True,verbose_name=_('Conjoint'))
    nomComplet = models.TextField(null=True, blank=True,verbose_name=_('Nom et prenom'))
    dateLieuMariage = models.TextField(null=True, blank=True,verbose_name=_('Date et lieu de mariage'))
    optionMatrimoniale = models.TextField(null=True, blank=True,verbose_name=_('Option matrimoniale'))
    regimeMatrimoniale = models.TextField(null=True, blank=True,verbose_name=_('Regime matrimoniale'))
    demandeSeparationBien = models.TextField(null=True, blank=True,verbose_name=_('Demande en séparation de biens'))


# Modifications relatives a l'etablissement
class Etablissement(models.Model):

    formalite = models.ForeignKey(Formalite,blank=True, null=True, on_delete=models.CASCADE, verbose_name=_('Formalité'))
    sigle = models.TextField(null=True, blank=True,verbose_name=_('Sigle'))
    nomCommercial = models.TextField(null=True, blank=True,verbose_name=_('Nom commercial'))
    rccm = models.TextField(null=True, blank=True,verbose_name=_('N'))
    activites = models.TextField(null=True, blank=True,verbose_name=_('Activités'))
    activitesAjouter = models.TextField(null=True, blank=True,verbose_name=_('Activités Ajoutées'))
    activitesSupprimer = models.TextField(null=True, blank=True,verbose_name=_('Activités Supprimées'))
    activitesActualiser = models.TextField(null=True, blank=True,verbose_name=_('Activités Actualisées'))
    adresseEtablissement = models.TextField(null=True, blank=True,verbose_name=_('Adresse etablissement'))
    ancienneAdresse = models.TextField(null=True, blank=True,verbose_name=_('Ancienne adresse'))
    nouvelleAdresse = models.TextField(null=True, blank=True,verbose_name=_('Nouvelle adresse'))
    slug = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(null=True, blank=True,auto_now=True, verbose_name=_('Date de creation etablissement')) 


# Modifications relatives a l'etablissement secondaire
class EtablissementSecondaire(models.Model):

    formalite = models.ForeignKey(Formalite,blank=True, null=True, on_delete=models.CASCADE, verbose_name=_('Formalité'))
    sigle = models.TextField(null=True, blank=True,verbose_name=_('Sigle'))
    nomCommercial = models.TextField(null=True, blank=True,verbose_name=_('Nom commercial'))
    rccm = models.TextField(null=True, blank=True,verbose_name=_('N'))
    activites = models.TextField(null=True, blank=True,verbose_name=_('Activités'))
    activitesAjouter = models.TextField(null=True, blank=True,verbose_name=_('Activités Ajoutées'))
    activitesSupprimer = models.TextField(null=True, blank=True,verbose_name=_('Activités Supprimées'))
    activitesActualiser = models.TextField(null=True, blank=True,verbose_name=_('Activités Actualisées'))
    autresActivites = models.TextField(null=True, blank=True,verbose_name=_('Autres Activités'))
    adresseEtablissement = models.TextField(null=True, blank=True,verbose_name=_('Adresse etablissement'))
    ancienneAdresse = models.TextField(null=True, blank=True,verbose_name=_('Ancienne adresse'))
    nouvelleAdresse = models.TextField(null=True, blank=True,verbose_name=_('Nouvelle adresse'))
    slug = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(null=True, blank=True,auto_now=True, verbose_name=_('Date de creation etablissement secondaire')) 


# Modifications relatives aux personnes pouvant engager la personne physique
class PersonnePhysiqueEngager(models.Model):

    MODE_DOMICILIER = (
        ("Partante", "Partante"),
        ("Nouvelle", "Nouvelle"),
        ("En_place", "En place"),
    )

    formalite = models.ForeignKey(Formalite,blank=True, null=True, on_delete=models.CASCADE, verbose_name=_('Formalité'))
    prenom = models.TextField(null=True, blank=True,verbose_name=_('Prenom'))
    nom = models.TextField(null=True, blank=True,verbose_name=_('Nom'))
    dateNaissance =  models.DateField(null=True, blank=True,verbose_name=_('Date naissance'))
    lieuNaissance = models.TextField(null=True, blank=True,verbose_name=_('Lieu naisssance'))
    nationnalite = models.TextField(null=True, blank=True,verbose_name=_('Nationnalité'))
    domicile = models.TextField(null=True, blank=True,verbose_name=_('Domicile personnel'))
    modeDomicilier = models.TextField(null=True, blank=True,choices=MODE_DOMICILIER,verbose_name=_('Mode domicilier'))
    objetModification = models.TextField(null=True, blank=True,verbose_name=_('Objet Modification'))
    dateModification2 =  models.DateField(null=True, blank=True,verbose_name=_('Date modification'))
    slug = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(null=True, blank=True,auto_now=True, verbose_name=_('Date de creation personne engager')) 


# Gerant
class Gerant(models.Model):

    TITRE_CIVIL = (
        ("M", "Monsieur"),
        ("Mme", "Madame"),
        ("Mlle", "Mademoiselle"),
    )

    DEMANDE = (
        ("Une_demande_de_modification_de_la_personne_physique_et_ou_de_son_etablissement_principale", "Une demande de modification de la personne physique et ou de son etablissement principale"),
        ("Une demande_de_modification_dun_etablissement_secondaire_ou_une_succursale", "Une demande de modification d'un etablissement secondaire ou une succursale"),
    )


    formalite = models.ForeignKey(Formalite,blank=True, null=True, on_delete=models.CASCADE, verbose_name=_('Formalité'))
    titreCivil = models.TextField(null=True, blank=True,choices=TITRE_CIVIL,verbose_name=_('Titre civil'))
    prenom = models.TextField(null=True, blank=True,verbose_name=_('Prenom'))
    nom = models.TextField(null=True, blank=True,verbose_name=_('Nom'))
    typeDemande = models.TextField(null=True, blank=True,choices=DEMANDE,verbose_name=_('Demande'))
    slug = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(null=True, blank=True,auto_now=True, verbose_name=_('Date de creation gerant')) 


class ActiviteAnterieure(models.Model):
    TYPE_ACTIVITE_CHOIX = [
        ('commercial', 'Commerciale'),
        ('other', 'Autre'),
    ]

    activite_precedente = models.BooleanField(verbose_name="Exercice d'une précédente activité", default=False)
    type_activite = models.CharField(verbose_name="Nature de l'activité", max_length=20, choices=TYPE_ACTIVITE_CHOIX, blank=True, null=True,)
    details_autre_activite = models.CharField(verbose_name="Détails sur l'autre activité", max_length=255, blank=True, null=True )
    periode_fin = models.DateField(verbose_name="Période fin (mois et année)", blank=True,null=True)
    rccm_precedent = models.CharField( verbose_name="Précédent RCCM (s'il y a lieu)",  max_length=100, blank=True, null=True)
    etablissement_principal = models.TextField(verbose_name="Établissement principal", blank=True, null=True )
    etablissements_secondaires = models.TextField(verbose_name="Établissements secondaires", blank=True, null=True)
    rccm_principal = models.CharField(verbose_name="RCCM principal (s'il y a lieu)", max_length=100,  blank=True, null=True )
    adresse = models.TextField(verbose_name="Adresse géographique et postale", blank=True, null=True)

    def __str__(self):
        return f"Activité précédente: {'Oui' if self.previous_activity else 'Non'}"

    class Meta:
        verbose_name = "Activité antérieure"
        verbose_name_plural = "Activités antérieures"