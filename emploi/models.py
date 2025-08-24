from django.db import models
from django.utils.text import slugify

class ModeleDoc(models.Model):

    TYPE_DOC = [
        ('contrat_travail', 'Contrat de travail'),
        ('convention_stage', 'Convention de stage'),
        ('lettre_embauche', 'Lettre d\'embauche'),
        ('lettre_convocation', 'Lettre de convocation'),
        ('lettre_licenciement', 'Lettre de licenciement'),
        ('reglement_interieur', 'Modèle règlement intérieur'),
    ]

    CATEGORIE = [
        ('employeur', 'Employeur'),
        ('employe', 'Employé'),
    ]

    titre = models.TextField()
    slug = models.SlugField(unique=True,  blank=True)
    type_document = models.TextField(choices=TYPE_DOC, default='lettre')
    categorie = models.TextField(choices=CATEGORIE, default='employeur')
    contenu = models.TextField(help_text="Utilisez {{ nom }}, {{ date }} pour les champs dynamiques")
    date_ajout = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.titre)
            slug = base_slug
            num = 1
            while ModeleDoc.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{num}"
                num += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.titre} ({self.get_type_document_display()})"