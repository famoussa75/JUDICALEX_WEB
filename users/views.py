from django.contrib import messages
from django.shortcuts import render,redirect
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.utils.http import urlencode
from urllib.parse import urlparse, parse_qs, urlunparse
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login, logout
from .forms import AccountForm, ContributionRequestForm, PasswordChangeForm, ProfileForm
from .models import Account, ContributionRequest, Notification, ProfessionChoices
from role.models import AffaireRoles,SuivreAffaire
from start.models import Juridictions
from django.contrib.auth.decorators import login_required
from django.conf import settings
import re
from blog.models import Post
from blog.forms import PostForm
from django.core.paginator import Paginator
from backoffice.utils import create_notification

# users/views.py
from allauth.account.views import ConfirmEmailView


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
from allauth.account.models import EmailAddress

from allauth.socialaccount.models import SocialApp

def google_login_page(request):
    app = SocialApp.objects.filter(provider='google').first()
    return render(request, 'login.html', {'google_app': app})



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
                next_url = request.POST.get("next") or request.GET.get("next") or "home"
                return redirect(next_url)
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

            existing_user = Account.objects.filter(email=email).first()

            if existing_user:
                if existing_user.is_active:
                    messages.error(request, "Désolé, cet email est déjà utilisé.")
                    return redirect('home')
                else:
                    # Si l'utilisateur existe mais n'a pas confirmé son email
                    email_address = EmailAddress.objects.filter(user=existing_user, email=email).first()
                    if email_address:
                        email_address.send_confirmation(request)
                    messages.success(request, "Vous n'avez pas encore confirmé votre email. Un nouveau mail a été envoyé.")
                    return redirect('home')

            if password != confirm_password:
                messages.error(request, "Les mots de passe ne correspondent pas.")
                return redirect('home')

            # Créer l'utilisateur désactivé
            user = form.save(commit=False)
            user.set_password(password)
            user.is_active = False

            # Superadmin si premier utilisateur
            if not Account.objects.exists():
                user.is_superuser = True
                user.is_staff = True
                user.is_active = True

            user.save()

            # Ajouter au groupe Visiteur si pas superadmin
            if not user.is_superuser:
                group, _ = Group.objects.get_or_create(name='Visiteur')
                group.user_set.add(user)

            # Créer EmailAddress et envoyer confirmation
            email_address, _ = EmailAddress.objects.get_or_create(
                user=user,
                email=user.email,
                primary=True,
                verified=False
            )
            email_address.send_confirmation(request)

            messages.success(request, "Un email de confirmation vous a été envoyé. Vérifiez également votre dossier spam ou courrier indésirable.")
            return redirect('home')
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
    account = request.user  # L'utilisateur actuellement connecté
    contribution_form = ContributionRequestForm()

    # ----- Formulaire de profil -----
    if request.method == 'POST' and 'update_profile' in request.POST:
        profile_form = ProfileForm(request.POST, request.FILES, instance=account)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Votre profil a été mis à jour !')
            return redirect('profile')
        else:
            # Message général
            messages.error(request, 'Veuillez corriger les erreurs dans votre profil.')

            # Boucler sur chaque champ et ses erreurs
            for field, errors in profile_form.errors.items():
                for error in errors:
                    if field == "__all__":
                        messages.error(request, f"Erreur générale : {error}")
                    else:
                        messages.error(request, f"Erreur dans {field} : {error}")
    else:
        profile_form = ProfileForm(instance=account)


    # ----- Formulaire de demande de contribution -----
    if not request.user.groups.filter(name="Contributeur").exists():
        demande_existante = ContributionRequest.objects.filter(demandeur=request.user, status='pending').exists()
        if request.method == 'POST' and 'demande_contribution' in request.POST:
            if demande_existante:
                messages.info(request, "Vous avez déjà soumis une demande de contribution. Elle est en cours de traitement.")
            else:
                contribution_form = ContributionRequestForm(request.POST, request.FILES)
                if contribution_form.is_valid():
                    contribution_request = contribution_form.save(commit=False)
                    contribution_request.demandeur = request.user
                    contribution_request.save()
                     # --- Notifier tous les administrateurs ---
                    admins = Account.objects.filter(groups__name="Administrateur")
                    for admin in admins:
                        create_notification(
                            recipient=admin,
                            sender=request.user,
                            type="info",
                            message=f"{request.user.get_full_name()} a soumis une nouvelle demande de contribution.",
                            objet_cible=contribution_request.id,
                            url=reverse("details_demande", args=[contribution_request.id])  # lien vers l'admin pour voir la demande
                        )

                       # Notifier Demandeur
                        create_notification(
                            recipient=request.user,
                            sender=request.user,
                            type="success",
                            message=f"Votre demande a été enregistrée avec succès. Vous recevrez une réponse prochainement.",
                            url='profile/'
                        )
                    messages.success(request, 'Votre demande de contribution a été envoyée !')
                    return redirect('profile')
                else:
                    messages.error(request, 'Veuillez corriger les erreurs dans le formulaire de contribution.')
    else:
        contribution_form = ContributionRequestForm()

    # ----- Vérification si Contributeur -----
    user_is_contributeur = request.user.groups.filter(name="Contributeur").exists()

    # ----- Gestion des contributions (create) -----
    post_form = PostForm()
    if user_is_contributeur and request.method == 'POST' and 'create_contribution' in request.POST:
        post_form = PostForm(request.POST, request.FILES)
        if post_form.is_valid():
            post = post_form.save(commit=False)
            post.author = request.user
            post.type = 'contribution'
            post.status = request.POST.get('status')
            post.save()
            messages.success(request, "Votre article a été publiée avec succès !")
            return redirect('profile')
        else:
            messages.error(request, "Veuillez corriger les erreurs dans votre contribution.")

    # ----- Notifications et affaires suivies -----
    _notifications = Notification.objects.filter(recipient=account)
    paginator = Paginator(_notifications, 15)  # 10 notifications par page

    page_number = request.GET.get("page")
    notifications = paginator.get_page(page_number)

    mesAffairesSuivies = SuivreAffaire.objects.select_related('affaire__role__juridiction').filter(account=account)

    # ----- Contributions de l’utilisateur -----
    user_posts = Post.objects.filter(author=request.user).order_by('-id')

    # Pagination
    paginator = Paginator(user_posts, 5)  # 5 posts par page
    page_number = request.GET.get("page")
    page_obj_user_post = paginator.get_page(page_number)
    professions = ProfessionChoices.choices  # ✅ pas besoin de query

    context = {
        'form': profile_form,
        'contribution_form': contribution_form,
        'post_form': post_form,
        'mesAffairesSuivies': mesAffairesSuivies,
        'notifications': notifications,
        'user_is_contributeur': user_is_contributeur,
        'page_obj_user_post': page_obj_user_post,
        'professions': professions,
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
    return redirect(f"{reverse('profile')}?tab=tab-notifs")

def delete_notifications(request):
    # Supprimer toutes les notifications non lues pour cet utilisateur
    Notification.objects.filter(recipient=request.user).delete()
    return redirect('profile')


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre article a été mise à jour avec succès !")
            return redirect('profile')
        else:
            messages.error(request, "Veuillez corriger les erreurs dans votre contribution.")
    else:
        form = PostForm(instance=post)

    return render(request, 'posts/edit_post.html', {'form': form, 'post': post})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)

    if request.method == 'POST':
        post.delete()
        messages.success(request, "Votre article a été supprimée avec succès !")
        return redirect('profile')

    return render(request, 'posts/confirm_delete.html', {'post': post})



class AutoLoginConfirmEmailView(ConfirmEmailView):
    def post(self, *args, **kwargs):
        # Appelle la logique d’allauth
        response = super().post(*args, **kwargs)

        # Récupère l'utilisateur lié à l'email
        if self.object and self.object.email_address.user:
            user = self.object.email_address.user
            user.is_active = True  # active le compte
            user.save()

            # Auto-login avec backend spécifié
            login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')

        return response
