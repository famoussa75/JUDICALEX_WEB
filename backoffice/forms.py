from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import Group, Permission
from users.models import Account
from .models import Ad


# --- Mixin pour appliquer automatiquement les classes Bootstrap ---
class BootstrapFormMixin:
    def _bootstrapify(self):
        for name, field in self.fields.items():
            w = field.widget
            base = w.attrs.get("class", "")
            if isinstance(w, (forms.TextInput, forms.EmailInput, forms.URLInput,
                              forms.PasswordInput, forms.NumberInput, forms.Textarea,
                              forms.FileInput, forms.ClearableFileInput,
                              forms.DateInput, forms.DateTimeInput, forms.TimeInput)):
                w.attrs["class"] = (base + " form-control").strip()
            elif isinstance(w, (forms.Select,)):
                w.attrs["class"] = (base + " form-select").strip()
            elif isinstance(w, (forms.CheckboxInput,)):
                w.attrs["class"] = (base + " form-check-input").strip()
            elif isinstance(w, (forms.CheckboxSelectMultiple,)):
                # Note : ajoute la classe sur chaque input du rendu multiple (selon template)
                w.attrs["class"] = (base + " form-check-input").strip()


# --- Forms Comptes ---
class AccountCreateForm(BootstrapFormMixin, UserCreationForm):
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "form-check-input"}),
        label="Groupes",
    )

    class Meta(UserCreationForm.Meta):
        model = Account
        fields = (
            "username", "email", "first_name", "last_name",
            "profession", "adresse", "tel1", "tel2",
            "nationnalite", "photo",
            "is_active", "is_staff", "groups",
        )
        widgets = {
            "profession": forms.Select(attrs={"class": "form-select"}),  # ⬅️ Select
            "adresse": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "tel1": forms.TextInput(attrs={"class": "form-control"}),
            "tel2": forms.TextInput(attrs={"class": "form-control"}),
            "nationnalite": forms.TextInput(attrs={"class": "form-control"}),
            "photo": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_staff": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bootstrapify()
        # Placeholders utiles
        self.fields["username"].widget.attrs.setdefault("placeholder", "Identifiant")
        self.fields["email"].widget.attrs.setdefault("placeholder", "email@exemple.com")
        # Passwords hérités de UserCreationForm
        if "password1" in self.fields:
            self.fields["password1"].widget.attrs.setdefault("placeholder", "Mot de passe")
        if "password2" in self.fields:
            self.fields["password2"].widget.attrs.setdefault("placeholder", "Confirmer le mot de passe")


class AccountUpdateForm(BootstrapFormMixin, UserChangeForm):
    password = None  # masque le champ mot de passe

    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "form-check-input"}),
        label="Groupes",
    )

    class Meta(UserChangeForm.Meta):
        model = Account
        fields = (
            "username", "email", "first_name", "last_name",
            "profession", "adresse", "tel1", "tel2",
            "nationnalite", "photo",
            "is_active", "is_staff", "groups",
        )
        widgets = {
            "profession": forms.Select(attrs={"class": "form-select"}),  # ⬅️ Select au lieu de Textarea
            "adresse": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "tel1": forms.TextInput(attrs={"class": "form-control"}),
            "tel2": forms.TextInput(attrs={"class": "form-control"}),
            "nationnalite": forms.TextInput(attrs={"class": "form-control"}),
            "photo": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_staff": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bootstrapify()
        self.fields["email"].widget.attrs.setdefault("placeholder", "email@exemple.com")


# --- Form Groupes ---
class GroupForm(BootstrapFormMixin, forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all().select_related("content_type"),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "form-check-input"}),
        label="Permissions",
    )

    class Meta:
        model = Group
        fields = ("name", "permissions")
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nom du groupe"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bootstrapify()





class AdForm(forms.ModelForm):
    class Meta:
        model = Ad
        fields = ["title", "image", "link", "position", "start_date", "end_date", "active"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Titre de la publicité"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "link": forms.URLInput(attrs={"class": "form-control", "placeholder": "https://..."}),
            "position": forms.Select(attrs={"class": "form-select"}),
            "start_date": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
            "end_date": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
            "active": forms.CheckboxInput(attrs={"class": "form-check-input"}),

        }
        labels = {
            "title": "Titre",
            "image": "Image",
            "link": "Lien",
            "position": "Position",
            "active": "Actif",
            "start_date": "Date de début",
            "end_date": "Date de fin",
        }

