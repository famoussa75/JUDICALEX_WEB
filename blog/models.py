from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from users.models import Account
from django.utils.translation import gettext_lazy as _


# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name=_('Nom de la catégorie'))
    description = models.TextField(blank=True, null=True, verbose_name=_('Description de la catégorie'))

    def __str__(self):
        return self.name

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_('Createur_de_post'))
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True)  # Champ pour l'image
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('Catégorie'))
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    

class Comment(models.Model):
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    user =  models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_('Commentateur'))
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Commentaire par {self.user} sur {self.post.title}"