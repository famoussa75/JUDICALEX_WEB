from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import re


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



class PasswordChangeForm(forms.Form):
    password = forms.CharField(label='Password', widget=forms.PasswordInput, required=False)
    confirm_password = forms.CharField(label='Confirm Password', widget=forms.PasswordInput, required=False)
    