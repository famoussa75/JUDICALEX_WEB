from django import forms
from .models import Comment, Post
from django.utils.text import slugify
from .models import InternalComment


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


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "content", "image", "category", "status"]  # author retiré
    


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            # TextInput et Textarea de base
            if isinstance(field.widget, forms.TextInput):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.Textarea):
                # Ajout TinyMCE + classe bootstrap
                field.widget.attrs.update({'class': 'form-control tinymce-editor'})
                field.required = False  # <-- retire le required HTML
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select'})
            elif isinstance(field.widget, forms.ClearableFileInput):
                field.widget.attrs.update({'class': 'form-control'})

            # Placeholder par défaut
            field.widget.attrs.setdefault('placeholder', field.label)

    def save(self, commit=True, user=None):
        instance = super().save(commit=False)
        if not instance.slug:
            instance.slug = slugify(instance.title)
        if user:
            instance.author = user  # assigne l'utilisateur connecté
        if commit:
            instance.save()
        return instance


class InternalCommentForm(forms.ModelForm):
    class Meta:
        model = InternalComment
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Écrire un commentaire..."
            }),
        
        }