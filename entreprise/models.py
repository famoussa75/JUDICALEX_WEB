from django.db import models
from django.utils.text import slugify

class ModeleCourrier(models.Model):

    titre = models.TextField()
    slug = models.SlugField(unique=True,  blank=True)
    contenu = models.TextField(help_text="Utilisez {{ nom }}, {{ date }} pour les champs dynamiques")
    date_ajout = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.titre)
            slug = base_slug
            num = 1
            while ModeleCourrier.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{num}"
                num += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.titre}"