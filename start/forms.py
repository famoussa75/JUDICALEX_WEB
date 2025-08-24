from django import forms
from .models import MessageDefilant

class MessageForm(forms.ModelForm):
    class Meta:
        model = MessageDefilant
        fields = ['contenu', 'actif']
        widgets = {
            'contenu': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
