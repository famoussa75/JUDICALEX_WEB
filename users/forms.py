from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import re
from .models import ContributionRequest


User = get_user_model()

class AccountForm(forms.ModelForm):
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput,
        required=True
    )
    confirm_password = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput,
        required=True
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'juridiction', 'first_name', 'last_name', 'profession', 'tel1', 'tel2', 'photo', 'adresse', 'nationnalite')
        

class ProfileForm(forms.ModelForm):
     class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'profession', 'tel1', 'tel2', 'photo', 'adresse', 'nationnalite')



class ContributionRequestForm(forms.ModelForm):
    class Meta:
        model = ContributionRequest
        fields = ["nom", "email", "sujet", "motivation", "piece_identite"]
        widgets = {
            "nom": forms.TextInput(attrs={"class": "form-control", "placeholder": "Votre nom complet"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Votre e-mail"}),
            "sujet": forms.TextInput(attrs={"class": "form-control", "placeholder": "Sujet(s) souhaité(s)"}),
            "motivation": forms.Textarea(attrs={"class": "form-control", "rows": 5, "placeholder": "Expliquez votre motivation"}),
        }


class PasswordChangeForm(forms.Form):
    password = forms.CharField(label='Password', widget=forms.PasswordInput, required=False)
    confirm_password = forms.CharField(label='Confirm Password', widget=forms.PasswordInput, required=False)

