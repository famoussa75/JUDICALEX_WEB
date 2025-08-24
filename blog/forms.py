from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',  # Classe Bootstrap par exemple
                'placeholder': 'Écrivez votre commentaire ici...',  # Placeholder pour guider l'utilisateur
                'rows': 4,  # Nombre de lignes visibles
                'style': 'resize:none;',  # Empêche le redimensionnement du champ de texte
            }),
        }
        labels = {
            'content': '',  # Label personnalisé
        }
