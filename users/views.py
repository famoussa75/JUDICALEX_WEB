from django.contrib import messages
from django.shortcuts import render,redirect
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.utils.http import urlencode
from urllib.parse import urlparse, parse_qs, urlunparse
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login, logout
from .forms import AccountForm, PasswordChangeForm, ProfileForm
from .models import Account, Notification
from role.models import AffaireRoles,SuivreAffaire
from start.models import Juridictions
from django.contrib.auth.decorators import login_required
from django.conf import settings
import re



from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import SetPasswordForm

import smtplib
from email.mime.text import MIMEText


# Create your views here.
def signIn(request):
  
    error = False
    msg = ""
   
    if request.method == 'POST':
        email = request.POST.get('email', None)
        password = request.POST.get('password', None)
        user = Account.objects.filter(email=email).first()
        if user:
            auth_user = authenticate(username=user.username, password=password)
            if auth_user is not None:
                login(request, auth_user)
                return redirect('home')
            else:
                error = True
                msg_error_login = "Email ou mot de passe incorrecte."
                params = urlencode({'msg_error_login': msg_error_login})
                referer = request.META.get('HTTP_REFERER', '/')
                parsed_url = urlparse(referer)
                query_params = parse_qs(parsed_url.query)
                query_params['msg_error_login'] = msg_error_login
                new_query_string = urlencode(query_params, doseq=True)
                cleaned_url = urlunparse(parsed_url._replace(query=''))  # Réinitialiser les paramètres précédents
                redirect_url = f"{cleaned_url}?{params}"
                return HttpResponseRedirect(redirect_url)
        else:
            error = True
            msg_error_login = "Désolé nous n\'avons pas pu trouvé ce compte."
            params = urlencode({'msg_error_login': msg_error_login})
            referer = request.META.get('HTTP_REFERER', '/')
            parsed_url = urlparse(referer)
            query_params = parse_qs(parsed_url.query)
            query_params['msg_error_login'] = msg_error_login
            new_query_string = urlencode(query_params, doseq=True)
            cleaned_url = urlunparse(parsed_url._replace(query=''))  # Réinitialiser les paramètres précédents
            redirect_url = f"{cleaned_url}?{params}"
            return HttpResponseRedirect(redirect_url)
           
    else:
       return redirect('home')

def signUp(request):
    if request.method == 'POST':
        form = AccountForm(request.POST)
        
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            confirm_password = form.cleaned_data['confirm_password']
            
            # Vérifiez si l'email existe déjà
            if Account.objects.filter(email=email).exists():
                messages.error(request, "Désolé cet email est déjà utilisé.")
                return redirect('home')  # Redirection vers la page d'inscription
            
            # Validation de la correspondance des mots de passe
            if password != confirm_password:
                messages.error(request, "Les mots de passe ne correspondent pas.")
                return redirect('home')

            # Validation de la complexité du mot de passe
            if len(password) < 8:
                messages.error(request, "Le mot de passe doit comporter au moins 8 caractères.")
                return redirect('home')
            
            if not re.search(r'[A-Z]', password):
                messages.error(request, "Le mot de passe doit contenir au moins une lettre majuscule.")
                return redirect('home')
            
            if not re.search(r'[a-z]', password):
                messages.error(request, "Le mot de passe doit contenir au moins une lettre minuscule.")
                return redirect('home')
            
            if not re.search(r'\d', password):
                messages.error(request, "Le mot de passe doit contenir au moins un chiffre.")
                return redirect('home')
            
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                messages.error(request, "Le mot de passe doit contenir au moins un caractère spécial.")
                return redirect('home')
            
            # Créez l'utilisateur
            user = form.save(commit=False)
            user.set_password(password)  # Hash le mot de passe
            
            # Déterminer si l'utilisateur est un superadmin
            if not Account.objects.exists():  # Aucun utilisateur n'existe, donc c'est le superadmin
                user.is_superuser = True
                user.is_staff = True
            
            user.save()

            # Ajouter l'utilisateur au groupe 'Visiteur' si ce n'est pas un superadmin
            if not user.is_superuser:
                group, created = Group.objects.get_or_create(name='Visiteur')
                group.user_set.add(user)
            
            login(request, user)  # Connecter l'utilisateur après l'inscription
            messages.success(request, "Félicitation! vous êtes inscri sur judicalex-gn !")
            return redirect('home')  # Redirection vers la page d'accueil après l'inscription
        
    else:
        form = AccountForm()
    
    return redirect('home')

def signOut(request):
    logout(request)
    return redirect('home')



def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = Account.objects.filter(email=email).first()
        
        if user:
            # Génération du jeton de réinitialisation
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            domain = get_current_site(request).domain
            reset_link = reverse('reset_password', kwargs={'uidb64': uid, 'token': token})
            reset_url = f"http://{domain}{reset_link}"
            
            # Envoyer l'email
            subject = "Réinitialisation de votre mot de passe"
            message = render_to_string('users/reset_password_email.html', {
                'user': user,
                'reset_url': reset_url
            })

            msg = MIMEText(message, 'html')
            msg['Subject'] = subject
            msg['From'] = settings.DEFAULT_FROM_EMAIL
            msg['To'] = email
            try:
                with smtplib.SMTP_SSL('vps106526.serveur-vps.net', 465) as server:
                    server.login(settings.DEFAULT_FROM_EMAIL, settings.EMAIL_HOST_PASSWORD)
                    server.sendmail(settings.DEFAULT_FROM_EMAIL, [email], msg.as_string())
                    print("Email envoyé avec succès.")
            except Exception as e:
                    print("Erreur d'envoi d'email :", e)
                    
            return render(request, 'users/password_reset_done.html', {'email': email})
        else:
            error_msg = "Aucun compte trouvé avec cet email."
            return render(request, 'users/forgot_password.html', {'error_msg': error_msg})
    
    return render(request, 'users/forgot_password.html')


def reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Account.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                update_session_auth_hash(request, user)  # Maintient la session après modification du mot de passe
                messages.success(request, "Votre mot de passe a été modifié avec succès !")
                return redirect('home')
        else:
            form = SetPasswordForm(user)
        
        return render(request, 'users/reset_password.html', {'form': form})
    else:
        return render(request, 'users/password_reset_invalid.html')



def updatePassword(request):
    pass

def usersControl(request):
    
    juridictions = Juridictions.objects.all()
    users_with_groups = []
    users = Account.objects.all()
    for user in users:
        # Récupérer les groupes associés à chaque utilisateur
        groups = user.groups.all()

        # Créer un dictionnaire avec l'utilisateur et ses groupes
        user_info = {
            'user': user,
            'groups': groups
        }
        users_with_groups.append(user_info)

    form = AccountForm()
    error = False
    msg = ''
   
    if request.method == 'POST':
       form = AccountForm(request.POST or None)
       if form.is_valid():
            
            if form.cleaned_data['password'] == form.cleaned_data.get('confirm_password'):
                juridiction_id = request.POST.get('juridiction_id')
                juridiction = Juridictions.objects.get(pk=juridiction_id)
                user = form.save(commit=False)
                user.set_password(form.cleaned_data['password'])
                user.juridiction = juridiction
                user.save()

                # Ajouter l'utilisateur au groupe 'User'
                group, created = Group.objects.get_or_create(name='Greffe')
                group.user_set.add(user)
                messages.success(request, "Utilisateur créer avec succès !")
            else:
                error = True
                msg = "Erreur de création, les mot de passes doivent être identiques."

    context = {
        'juridictions':juridictions,
        'error':error,
        'msg':msg,
        'form':form,
        'users_with_groups':users_with_groups,
    }
    return render(request, 'users/users-control.html',context)

@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Votre profile a été mis à jour!')
            return redirect('profile')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"Erreur dans le champ {field}: {error}")
    else:
        form = AccountForm(instance=request.user)
    
    emailConnected = request.user.email
    user = Account.objects.filter(email=emailConnected).first()
    account = request.user  # Utilisateur actuel
    notifications = Notification.objects.filter(recipient=user)

    # Récupérer les affaires suivies avec les jointures optimisées
    mesAffairesSuivies = SuivreAffaire.objects.select_related('affaire__role__juridiction').filter(account=account)

    context = {
        'form': form,
        'user': user,
        'mesAffairesSuivies':mesAffairesSuivies,
        'notifications':notifications
    }
    return render(request, 'users/profile.html', context)

@login_required
def change_password(request):
    if request.method == 'POST':
        password_form = PasswordChangeForm(request.POST)
        
        if password_form.is_valid():
            user = request.user
            password = password_form.cleaned_data.get('password')
            confirm_password = password_form.cleaned_data.get('confirm_password')
            print(password)
            print(confirm_password)
            if password and confirm_password and password != confirm_password:
                msg_error_update_password = "Erreur de modification, les mots de passe ne correspondent pas."
                params = urlencode({'msg_error_update_password': msg_error_update_password})
                referer = request.META.get('HTTP_REFERER', '/')
                parsed_url = urlparse(referer)
                query_params = parse_qs(parsed_url.query)
                query_params['msg_error_update_password'] = msg_error_update_password
                new_query_string = urlencode(query_params, doseq=True)
                cleaned_url = urlunparse(parsed_url._replace(query=''))  # Réinitialiser les paramètres précédents
                redirect_url = f"{cleaned_url}?{params}"
                return HttpResponseRedirect(redirect_url) 
            else:
                user.set_password(password)
                user.save()
                messages.success(request, 'Votre mot de passe a été mis à jour!')
                return redirect('home')
               


        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
            for field, errors in password_form.errors.items():
                for error in errors:
                    print(f"Erreur dans le champ {field}: {error}")
    else:
        password_form = PasswordChangeForm()
    
    emailConnected = request.user.email
    user = Account.objects.filter(email=emailConnected).first()
    notifications = Notification.objects.filter(recipient=user)

    context = {
        'password_form': password_form,
        'user': user,
        'notifications':notifications
    }
    return render(request, 'users/profile.html', context)


def get_notifications(request):
    if not request.user.is_authenticated:
        return JsonResponse({'notifications': []})  # Ou {'error': 'Not authenticated'} si tu veux gérer l'erreur côté JS

    notifications = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).order_by('-timestamp')

    return JsonResponse({'notifications': list(notifications.values())})

def mark_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({'success': True})

def delete_notifications(request):
    # Supprimer toutes les notifications non lues pour cet utilisateur
    Notification.objects.filter(recipient=request.user).delete()
    return redirect('profile')
