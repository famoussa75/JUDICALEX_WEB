from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from users.models import Account
from django.utils.translation import gettext_lazy as _
from django.conf import settings


# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name=_('Nom de la catégorie'))
    description = models.TextField(blank=True, null=True, verbose_name=_('Description de la catégorie'))

    def __str__(self):
        return self.name


class Post(models.Model):
    
    class Status(models.TextChoices):
        DRAFT = "draft", _("En attente")
        PUBLISHED = "published", _("Publié")
        ARCHIVED = "archived", _("Archivé")
    
    class TypePost(models.TextChoices):
        NEWS = "news", _("News")
        CONTRIBUTION = "contribution", _("Contribution")

    title = models.CharField(
        max_length=200,
        verbose_name=_("Titre"),
        help_text=_("Titre du post (max 200 caractères).")
    )
    slug = models.SlugField(
        max_length=220,
        unique=True,
        verbose_name=_("Slug"),
        null=True,
        blank=True,
        help_text=_("Identifiant unique utilisé dans l’URL.")
    )
    content = models.TextField(
        verbose_name=_("Contenu"),
        help_text=_("Contenu principal de l’article.")
    )
    author = models.ForeignKey(
        "users.Account",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Créateur du post"),
        related_name="posts"
    )
    image = models.ImageField(
        upload_to="blog_images/",
        blank=True,
        null=True,
        verbose_name=_("Image"),
        help_text=_("Image illustrant l’article (optionnel).")
    )
    category = models.ForeignKey(
        "Category",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Catégorie"),
        related_name="posts"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name=_("Statut"),
        help_text=_("Définir si l’article est brouillon, publié ou archivé.")
    )
    type = models.CharField(
        max_length=20,
        choices=TypePost.choices,
        default=TypePost.NEWS,
        verbose_name=_("Type"),
        help_text=_("Définir si l’article est une actualité ou contribution.")
    )
    rejection_reason = models.TextField(
        verbose_name=_("Motif de refus"),
        help_text=_("Explication fournie en cas de refus de l’article."),
        null=True,
        blank=True
    )

    views = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Vues"),
        help_text=_("Nombre de fois que l’article a été consulté.")
    )

    # Relation ManyToMany pour les likes
    liked_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="liked_posts",
        verbose_name=_("Utilisateurs ayant liké"),
        help_text=_("Utilisateurs qui ont aimé cet article.")
    )

    shares = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Partages"),
        help_text=_("Nombre de fois que l’article a été partagé.")
    )

    is_published = models.BooleanField(
        default=False,
        verbose_name=_("Diffusé"),
        help_text=_("Indique si l’article est diffusé ou non.")
    )

    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("Date de création")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Dernière mise à jour")
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Article")
        verbose_name_plural = _("Articles")

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    def short_content(self, length=100):
        """Retourne un aperçu du contenu limité à `length` caractères."""
        return (self.content[:length] + "...") if len(self.content) > length else self.content

    @property
    def total_likes(self):
        """Retourne le nombre total de likes."""
        return self.liked_by.count()

    def liked_by_user(self, user):
        """Vérifie si un utilisateur a déjà liké cet article."""
        if not user.is_authenticated:
            return False
        return self.liked_by.filter(pk=user.pk).exists()


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    user =  models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_('Commentateur'))
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Commentaire par {self.user} sur {self.post.title}"
    

class InternalComment(models.Model):
    post = models.ForeignKey(Post, related_name="internal_comments", on_delete=models.CASCADE)
    user =  models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_('Commentateur interne'))
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Commentaire par {self.user} sur {self.post.title}"