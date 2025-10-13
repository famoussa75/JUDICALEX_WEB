# views.py
from email.mime.text import MIMEText
import smtplib
from django.conf import settings
from django.http import JsonResponse
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes
from rest_framework import generics, permissions
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime
from django.contrib.auth import authenticate, login
from users.models import Account, Notification
from backoffice.models import Ad
from .serializers import AdSerializer, NotificationSerializer,AccountSerializer, AffaireRolesSerializer, DecisionsSerializer, SuivreAffaireSerializer, SuivreAffaireSerializerMesAffaires
from django.contrib.auth import logout
from blog.models import Post, Comment
from start.models import MessageDefilant
from start.forms import MessageForm
from role.models import AffaireRoles, Decisions, Roles, SuivreAffaire
from .serializers import PostSerializer, CommentSerializer, RolesSerializer
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.shortcuts import render,redirect,get_object_or_404
from email.mime.multipart import MIMEMultipart
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes  # ✅ ajoute ceci
from rest_framework.permissions import AllowAny




@api_view(['POST'])
@permission_classes([AllowAny])  # ✅ aucun token requis pour se connecter
def api_sign_in(request):
    email = request.data.get('email')
    password = request.data.get('password')

    
    user = Account.objects.filter(email=email).first()
    if user:
        auth_user = authenticate(username=user.username, password=password)
        if auth_user is not None:
            login(request, auth_user)
            # Sérialiser les données de l'utilisateur
            user_data = AccountSerializer(auth_user).data

             # Récupérer ou créer un token pour l'utilisateur
            token, created = Token.objects.get_or_create(user=auth_user)

            return Response({
                'message': 'Login successful',
                'user': user_data,
                'token': token.key 
            }, status=status.HTTP_200_OK)
        
        else:
            return Response({'error': 'Invalid email or password'}, status=400)
    else:
        return Response({'error': 'Account not found'}, status=404)
    

@api_view(['GET'])
def get_user(request, user_id):
  
    if user_id:
        user = Account.objects.filter(id=user_id).first()
    else:
        return Response({'error': 'ID must be provided'}, status=status.HTTP_400_BAD_REQUEST)

    if user:
        user_data = AccountSerializer(user).data
        return Response(user_data, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def api_sign_up(request):
    serializer = AccountSerializer(data=request.data)
    
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')
        
        if password != confirm_password:
            return Response({'error': 'Passwords do not match'}, status=400)
        
        if Account.objects.filter(email=email).exists():
            return Response({'error': 'Email already exists'}, status=400)
        
        # Create user
        user = serializer.save()
        user.set_password(password)
        if not Account.objects.exists():
            user.is_superuser = True
            user.is_staff = True
        user.save()

        return Response({'message': 'Account created successfully'}, status=201)
    
    return Response(serializer.errors, status=400)

@api_view(['PUT'])
def api_update_account(request, user_id):
    # Récupérer l'utilisateur à partir de l'ID
    user = Account.objects.filter(id=user_id).first()
    
    if not user:
        return Response({'error': 'User not found'}, status=404)
    
    # Initialiser le sérialiseur avec les données de l'utilisateur et celles soumises
    serializer = AccountSerializer(user, data=request.data, partial=True)

    if serializer.is_valid():
        # Validation supplémentaire des mots de passe si fournis
        password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')

        if password and confirm_password:
            if password != confirm_password:
                return Response({'error': 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                user.set_password(password)
        
        # Vérifier si l'email existe déjà pour un autre utilisateur
        email = serializer.validated_data.get('email', None)
        if email and Account.objects.filter(email=email).exclude(id=user_id).exists():
            return Response({'error': 'Email already in use'}, status=status.HTTP_400_BAD_REQUEST)

        # Gérer la mise à jour de l'image de profil
        if 'photo' in request.FILES:
            user.photo = request.FILES['photo']

        # Enregistrer les modifications
        serializer.save()
        
        return Response({'message': 'Account updated successfully'}, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def api_delete_account(request, user_id):
    # Récupérer l'utilisateur par son ID
    user = Account.objects.filter(id=user_id).first()
    
    if not user:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Supprimer l'utilisateur
    user.delete()
    
    return Response({'message': 'Account deleted successfully'}, status=status.HTTP_200_OK)

@api_view(['POST'])
def api_sign_out(request):
    logout(request)
    return Response({'message': 'Logout successful'}, status=200)


# API pour lister tous les posts
class PostListAPIView(generics.ListAPIView):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer

# API pour afficher les détails d'un post
class PostDetailAPIView(generics.RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    lookup_field = 'pk'



@api_view(['POST'])
def create_comment_api(request, post_id):
    """
    Crée un commentaire sur un post.
    ✅ Authentification par Token
    ✅ Pas besoin de CSRF
    """
    try:
        data = request.data
        content = data.get('content')

        if not content:
            return Response(
                {'status': 'error', 'message': 'Le contenu du commentaire est requis.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        post = get_object_or_404(Post, id=post_id)

        comment = Comment.objects.create(
            user=request.user,
            post=post,
            content=content
        )

        # Retour JSON complet avec les infos du commentaire
        return Response(
            {
                'status': 'success',
                'message': 'Commentaire créé avec succès.',
                'comment': {
                    'id': comment.id,
                    'content': comment.content,
                    'post_id': post.id,
                    'user_id': request.user.id,
                    'created_at': comment.created_at
                }
            },
            status=status.HTTP_201_CREATED
        )

    except Exception as e:
        return Response(
            {'status': 'error', 'message': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )



@api_view(['GET'])
def get_comments_api(request, post_id):
    """
    ✅ Récupère tous les commentaires d’un post
    """
    post = get_object_or_404(Post, id=post_id)
    comments = Comment.objects.filter(post=post).order_by('-created_at')
    serializer = CommentSerializer(comments, many=True)

    return Response({
        'status': 'success',
        'post_id': post.id,
        'comments_count': len(serializer.data),
        'comments': serializer.data
    }, status=status.HTTP_200_OK)

# 🟡 Modifier un commentaire (seulement par son auteur)
@api_view(['PUT', 'PATCH'])
def update_comment_api(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if comment.user != request.user:
        return Response({
            'status': 'error',
            'message': "Vous n'êtes pas autorisé à modifier ce commentaire."
        }, status=status.HTTP_403_FORBIDDEN)

    serializer = CommentSerializer(comment, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'status': 'success',
            'message': 'Commentaire modifié avec succès.',
            'comment': serializer.data
        })
    return Response({'status': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


# 🔴 Supprimer un commentaire (seulement par son auteur)
@api_view(['DELETE'])
def delete_comment_api(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if comment.user != request.user:
        return Response({
            'status': 'error',
            'message': "Vous n'êtes pas autorisé à supprimer ce commentaire."
        }, status=status.HTTP_403_FORBIDDEN)

    comment.delete()
    return Response({
        'status': 'success',
        'message': 'Commentaire supprimé avec succès.'
    }, status=status.HTTP_204_NO_CONTENT)

class RolesPagination(PageNumberPagination):
    page_size = 10

class RolesListAPI(generics.ListAPIView):
    queryset = Roles.objects.select_related('juridiction').all().order_by('-created_at')
    serializer_class = RolesSerializer
    pagination_class = RolesPagination

    def get(self, request, *args, **kwargs):
        today = datetime.today().strftime('%Y-%m-%d')

        # Pagination des rôles
        response = super().get(request, *args, **kwargs)
        roles_data = response.data

        # Retourner également la date actuelle et autres infos si nécessaire
        return Response({
            'today': today,
            'roles': roles_data,
        })
    
@api_view(['GET'])
def role_detail_api(request, pk):
    role = Roles.objects.filter(id=pk).first()
    if role is None:
        return Response({'error': 'Role not found'}, status=404)

    detail_role = AffaireRoles.objects.filter(role=role).order_by('numOrdre')
    is_greffe = request.user.groups.filter(name='Greffe').exists()
    
    if request.user:
        affaire_suivis = SuivreAffaire.objects.filter(account=request.user)
    else:
        affaire_suivis = SuivreAffaire.objects.none()

    role_serializer = RolesSerializer(role)
    detail_role_serializer = AffaireRolesSerializer(detail_role, many=True)
    affaire_suivis_serializer = SuivreAffaireSerializer(affaire_suivis, many=True)

    response_data = {
        'role': role_serializer.data,
        'detailRole': detail_role_serializer.data,
        'is_greffe': is_greffe,
        'affaireSuivis': affaire_suivis_serializer.data
    }

    return Response(response_data)


@api_view(['GET', 'POST'])
def detail_affaire_api(request, idAffaire):
    affaire = AffaireRoles.objects.filter(id=idAffaire).first()
    if affaire is None:
        return Response({'error': 'Affaire not found'}, status=404)

    decisions = Decisions.objects.select_related('affaire').filter(
        affaire__objet=affaire.objet,
        affaire__demandeurs=affaire.demandeurs,
        affaire__defendeurs=affaire.defendeurs,
        affaire__mandatDepot=affaire.mandatDepot,
        affaire__detention=affaire.detention,
        affaire__prevention=affaire.prevention,
        affaire__natureInfraction=affaire.natureInfraction,
        affaire__prevenus=affaire.prevenus,
        affaire__appelants=affaire.appelants,
        affaire__intimes=affaire.intimes,
        affaire__partieCiviles=affaire.partieCiviles,
        affaire__civileResponsables=affaire.civileResponsables
    )
    affaire_role = AffaireRoles.objects.select_related('role__juridiction').get(id=affaire.id)
    is_suivi = SuivreAffaire.objects.filter(
        affaire=affaire, juridiction=affaire_role.role.juridiction, account=request.user
    )
    is_greffe = request.user.groups.filter(name='Greffe').exists()

    affaire_serializer = AffaireRolesSerializer(affaire)
    decisions_serializer = DecisionsSerializer(decisions, many=True)
    is_suivi_serializer = SuivreAffaireSerializer(is_suivi, many=True)

    response_data = {
        'affaire': affaire_serializer.data,
        'decisions': decisions_serializer.data,
        'is_greffe': is_greffe,
        'is_suivi': is_suivi_serializer.data
    }

    return Response(response_data)

@api_view(['POST'])
def suivre_affaire_api(request):
    try:
        data = request.data  # DRF automatically parses JSON
        selected_ids = data.get('selected', [])
        account = request.user  # L'utilisateur actuel

        for id_affaire in selected_ids:
            is_suivi = SuivreAffaire.objects.filter(affaire_id=id_affaire, account=request.user).exists()
            if not is_suivi:
                affaire = AffaireRoles.objects.select_related('role__juridiction').get(id=id_affaire)
                SuivreAffaire.objects.create(
                    affaire=affaire,
                    account=account,
                    juridiction=affaire.role.juridiction
                )

        return Response({'status': 'success', 'message': 'Vous suivez désormais ces affaires.'}, status=200)

    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=400)
    

@api_view(['POST'])
def ne_pas_suivre_affaire_api(request):
    try:
        data = request.data  # DRF automatiquement parse le JSON
        selected_ids = data.get('selected', [])
        account = request.user  # L'utilisateur actuel

        for id_affaire in selected_ids:
            is_suivi = SuivreAffaire.objects.filter(affaire_id=id_affaire, account=account)
            if is_suivi.exists():
                is_suivi.delete()

        return Response({'status': 'success', 'message': 'Vous ne suivez plus ces affaires.'}, status=200)

    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=400)
    

@api_view(['GET'])
def mes_affaires_suivies_api(request):
    # Récupérer l'utilisateur connecté
    account = request.user

    # Récupérer les affaires suivies avec jointures optimisées
    mes_affaires_suivies = SuivreAffaire.objects.select_related('affaire__role__juridiction').filter(account=account)

    # Sérialiser les données
    serializer = SuivreAffaireSerializerMesAffaires(mes_affaires_suivies, many=True)

    # Retourner la réponse JSON
    return Response(serializer.data)


@csrf_exempt  # Si vous utilisez un frontend JS, vous pouvez ajouter cette exception, mais attention aux risques de sécurité.
def send_contact_email(request):
    if request.method == 'POST':
        # Récupérer les données du formulaire
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject', 'Sans sujet')  # Sujet par défaut
        message = request.POST.get('message')

        # Construire le message complet
        full_message = f"""
        Vous avez reçu un nouveau message via le formulaire de contact.

        Nom : {name}
        Email : {email}

        Sujet : {subject}
        Message : 
        {message}
        """

        try:
            # Création du message email
            msg = MIMEMultipart()
            msg['From'] = settings.DEFAULT_FROM_EMAIL
            msg['To'] = 'contact@judicalex-gn.org'  # Adresse du destinataire fixe
            msg['Subject'] = f"[Contact Form] {subject}"
            msg.attach(MIMEText(full_message, 'plain'))

            # Envoyer l'email via SMTP
            with smtplib.SMTP_SSL('vps106526.serveur-vps.net', 465) as server:
                server.login(settings.DEFAULT_FROM_EMAIL, settings.EMAIL_HOST_PASSWORD)
                server.sendmail(
                    settings.DEFAULT_FROM_EMAIL, 
                    ['contact@judicalex-gn.org'],  # Destinataire fixe
                    msg.as_string()
                )

            return JsonResponse({'success': True, 'message': 'Merci pour votre message. Nous l\'avons bien reçu et traiterons votre demande dans les plus brefs délais.'})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
        
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée.'})


def about_us(request):
    return render(request, 'start/about.html')

def condition_generale(request):
    return render(request, 'start/contrat/condition_general.html')

def politique(request):
    return render(request, 'start/contrat/politique_confidentialite.html')


@api_view(['GET'])
def notificationAPIView(request):
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-timestamp')
    serializer = NotificationSerializer(notifications, many=True)
    return Response({'notifications': serializer.data})

@api_view(['GET'])
def allNotificationAPIView(request):
    notifications = Notification.objects.filter(recipient=request.user).order_by('-timestamp')
    serializer = NotificationSerializer(notifications, many=True)
    return Response({'notifications': serializer.data})
    
class MarkNotificationAsReadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, notification_id):
        notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
        notification.is_read = True
        notification.save()
        return Response({'success': True})
    
class DeleteNotificationsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        # Supprimer toutes les notifications pour l'utilisateur connecté
        Notification.objects.filter(recipient=request.user).delete()
        return Response({'success': True, 'message': 'Toutes les notifications ont été supprimées.'})
    

def ges_message(request, pk=None, action=None):
    messages = MessageDefilant.objects.all().order_by('-date_creation')

    # Créer ou éditer
    if pk and action == 'edit':
        instance = get_object_or_404(MessageDefilant, pk=pk)
        form = MessageForm(request.POST or None, instance=instance)
        form_title = "Modifier le message"
    else:
        instance = None
        form = MessageForm(request.POST or None)
        form_title = "Ajouter un message"

    if request.method == 'POST':
        if 'delete_id' in request.POST:
            message_to_delete = get_object_or_404(MessageDefilant, pk=request.POST['delete_id'])
            message_to_delete.delete()
            return redirect('ges_message')

        if form.is_valid():
            form.save()
            return redirect('ges_message')

    return render(request, 'start/gestion-message.html', {
        'messages': messages,
        'form': form,
        'form_title': form_title,
        'edit_mode': pk and action == 'edit',
        'instance_id': instance.pk if instance else None,
    })


@api_view(['GET'])
def ads_list(request):
    ads_header = Ad.objects.filter(active=True, position='header').order_by('?')
    ads_lateral = Ad.objects.filter(active=True, position='sidebar').order_by('?')

    serializer_header = AdSerializer(ads_header, many=True)
    serializer_lateral = AdSerializer(ads_lateral, many=True)

    return Response({
        'header': serializer_header.data,
        'sidebar': serializer_lateral.data
    })