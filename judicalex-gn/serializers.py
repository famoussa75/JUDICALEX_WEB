# serializers.py
from rest_framework import serializers
from start.models import Juridictions
from users.models import Account
from blog.models import Post, Comment
from role.models import Decisions, Roles,AffaireRoles, SuivreAffaire
from users.models import Notification
from backoffice.models import Ad


from django.contrib.auth.models import Group


class AdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ad
        fields = ['id', 'title', 'image', 'link', 'position', 'active']  # ajouter les champs que tu veux exposer


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'recipient', 'is_read', 'message', 'url', 'objet_cible', 'timestamp']  # Adaptez les champs à votre modèle.

class AccountSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True, required=False)  # Optionnel, seulement pour validation
    password = serializers.CharField(write_only=True, required=False)  # Optionnel, seulement pour mise à jour
    groups = serializers.SlugRelatedField(
        many=True,
        slug_field="name",
        read_only=True  # ✅ en lecture seule pour ne pas casser la création
    )

    class Meta:
        model = Account
        fields = ['id', 'username', 'first_name', 'last_name', 'photo', 'password', 'confirm_password', 'email', 'juridiction', 'is_superuser', 'is_staff', 'groups', ]
        extra_kwargs = {
            'password': {'write_only': True}  # Assurez-vous que le mot de passe n'est pas renvoyé
        }

    def validate(self, data):
        """
        Valide la correspondance des mots de passe uniquement si le mot de passe est fourni.
        """
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        # Vérifier si un des mots de passe est fourni
        if password or confirm_password:
            if password != confirm_password:
                raise serializers.ValidationError({"password": "Les mots de passe ne correspondent pas."})
        return data

    def create(self, validated_data):
        """
        Crée un nouvel utilisateur en retirant `confirm_password` avant de sauvegarder.
        """
        validated_data.pop('confirm_password', None)  # Retirer `confirm_password` des données validées
        account = Account.objects.create(**validated_data)
        if 'password' in validated_data:
            account.set_password(validated_data['password'])  # Hasher le mot de passe
        account.save()
        return account

    def update(self, instance, validated_data):
        """
        Met à jour un utilisateur existant, en ne modifiant le mot de passe que s'il est fourni.
        """
        # Supprimer `confirm_password` des données
        validated_data.pop('confirm_password', None)
        
        # Si le mot de passe est fourni, le mettre à jour et le hasher
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        
        # Mise à jour des autres champs
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance

    



class CommentSerializer(serializers.ModelSerializer):
    user_first_name = serializers.CharField(source="user.first_name", read_only=True)
    user_last_name = serializers.CharField(source="user.last_name", read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'post', 'user', 'user_first_name', 'user_last_name', 'content', 'created_at']


    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, "user"):
            validated_data['user'] = request.user  # Attribuer automatiquement l'utilisateur connecté
        return super().create(validated_data)

class PostSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    author = AccountSerializer(read_only=True)  # auteur du post

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'created_at', 'category', 'comments','image', 'author', 'slug']


# API ROLES
class RolesSerializer(serializers.ModelSerializer):
    juridiction_name = serializers.CharField(source='juridiction.name', read_only=True)
    total_affaire = serializers.SerializerMethodField()

    class Meta:
        model = Roles
        fields = ['id','idRole', 'section', 'juridiction_name', 'juridiction', 'president', 'greffier', 'juge', 'assesseur','assesseur1','assesseur2' , 'conseillers', 'ministerePublic', 'procureurMilitaire', 'subtituts','typeAudience', 'dateEnreg', 'total_affaire', 'created_at']

    def get_total_affaire(self, obj):
        return AffaireRoles.objects.filter(role=obj).count()
    
class JuridictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Juridictions
        fields = ['id','idJuridiction', 'name', 'address']  # Ajoutez les champs nécessaires

class AffaireRolesSerializer(serializers.ModelSerializer):
    class Meta:
        model = AffaireRoles
        fields = [
            'id',
            'idAffaire',  # UUIDField
            'numOrdre',  # Numéro d'ordre
            'numRg',     # Numéro Rg
            'objet',     # Objet
            'mandatDepot',  # Mandat de dépôt
            'detention',    # Detention
            'prevention',   # Prévention
            'natureInfraction',  # Nature des infractions
            'decision',     # Décision
            'prevenus',     # Prévenus
            'demandeurs',   # Demandeurs
            'defendeurs',   # Défendeurs
            'appelants',    # Appelants
            'intimes',      # Intimés
            'partieCiviles',  # Parties civiles
            'civileResponsables',  # Civiles responsables
            'role',         # Role (ForeignKey)
            'created_at'    # Date de création
        ]  # Ajoutez les champs nécessaires

class SuivreAffaireSerializer(serializers.ModelSerializer):

    class Meta:
        model = SuivreAffaire
        fields = ['id', 'idSuivre', 'affaire','account','juridiction','created_at']  # Ajoutez les champs nécessaires

class SuivreAffaireSerializerMesAffaires(serializers.ModelSerializer):
    
    affaire = AffaireRolesSerializer()  # Utiliser AffaireSerializer pour inclure toutes les informations liées
    class Meta:
        model = SuivreAffaire
        fields = ['id', 'idSuivre', 'affaire','account','juridiction','created_at']  # Ajoutez les champs nécessaires

class DecisionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Decisions
        fields = ['id','idDecision', 'juridiction', 'affaire','decision','typeDecision','objet','president','greffier','dateDecision','prochaineAudience','created_at']  # Ajoutez les champs que vous souhaitez exposer

