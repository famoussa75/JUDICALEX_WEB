from django.contrib import admin

# Register your models here.
from users.models import Account  # Importez votre modèle personnalisé

admin.site.register(Account)
