from django.contrib import admin

# Register your models here.

# Register your models here.
from .models import Post, Category  # Importez votre modèle personnalisé

admin.site.register(Category)
admin.site.register(Post)
