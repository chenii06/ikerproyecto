# Django
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth import authenticate, password_validation
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import connection
from django.db.models import F, Window, Sum, Case, When, CharField, Value, ExpressionWrapper, Func, IntegerField, BooleanField, Q, OuterRef, Subquery, FloatField, Count
from django.db.models.expressions import RawSQL
from django.db.models.functions import Rank, Lag, Lead
from django.http import HttpResponseRedirect, HttpRequest, HttpResponse
from django.http.response import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy, resolve, Resolver404, get_resolver
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, FormView, UpdateView, TemplateView
from django.views.generic.base import View
from django_cte import CTEManager, With

# Django REST Framework
from rest_framework import status
from rest_framework.generics import RetrieveAPIView, ListAPIView, UpdateAPIView, GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

# Mixins
from utils.mixins import CustomMethodsMixin

# Models
from apps.users.models import Profile, Country, Notification, Team, TeamInvitation
from apps.demonlist.models import Demon, Record, Changelog

# Models (Proxy)
from apps.demonlist.models.proxy import ExtendedDemon, ExtendedRecord
from apps.users.models.proxy import ExtendedCountry, ExtendedProfile, ExtendedTeam

# Forms
from apps.users.forms import SignupForm, CustomAuthenticationForm

# Functions and Bot
from apps.demonlist.functions import functions
from apps.users.functions import functions_discord

# Serializers
from apps.demonlist.serializers import DemonModelSerializer, RecordModelSerializer
from apps.users.serializers import UserModelSerializer, ProfileModelSerializer, CountryModelSerializer, ProfileSelect2Serializer, ProfileRouletteModelSerializer, ProfileTeamModelSerializer, TeamModelSerializer, TeamInvitationModelSerializer

# Utils
import ast
import asyncio
import re
from utils.constants import list_choices


def demo_recaptcha(request):
    return render(request, 'demo_recaptcha.html', {
        "key": settings.RECAPTCHA_PUBLIC_KEY
    })


# Vista que marca una notificación como leída
class ReadNotifications(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        notifications = Notification.objects.filter(profile=request.user.profile)
        for notification in notifications:
            notification.read = True
            notification.save()

        response_data = {'success': True,}

        return JsonResponse(response_data)

# Vista de Login
class LoginView(TokenObtainPairView):
    # Login View

    template_name = "users/login.html"
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        return Response()

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if '@' in username:
            try:
                user_obj = User.objects.get(email=username)
                username = user_obj.username
            except User.DoesNotExist:
                username = None

        user = authenticate(username=username, password=password)

        if user is not None:
            print(f'Authenticated user: {user.username}')  # Debugging line

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            
            response_data = {
                'refresh': refresh_token,
                'access': access_token,
            }
            response = Response(response_data, status=status.HTTP_200_OK)
            
            if response.status_code == status.HTTP_200_OK:
                response.set_cookie(
                    key='access_token',
                    value=access_token,
                    httponly=True,
                    secure=True,
                    samesite='Lax',
                    max_age=settings.ACCESS_TOKEN_EXPIRATION,  # 1 day
                )
                response.set_cookie(
                    key='refresh_token',
                    value=refresh_token,
                    httponly=True,
                    secure=True,
                    samesite='Lax',
                    max_age=settings.ACCESS_TOKEN_EXPIRATION,  # 1 day
                )
                print(f'Set access_token: {access_token}')  # Debugging line
                print(f'Set refresh_token: {refresh_token}')  # Debugging line

                # Redirect to a specific URL after successful login
                redirect_response = HttpResponseRedirect(reverse_lazy('demonlist:home'))
                redirect_response.set_cookie(
                    key='access_token',
                    value=access_token,
                    httponly=True,
                    secure=True,
                    samesite='Lax',
                    max_age=settings.ACCESS_TOKEN_EXPIRATION,  # 5 minutes
                )
                redirect_response.set_cookie(
                    key='refresh_token',
                    value=refresh_token,
                    httponly=True,
                    secure=True,
                    samesite='Lax',
                    max_age=settings.ACCESS_TOKEN_EXPIRATION,  # 1 day
                )
                if "text/html" in self.request.accepted_media_type:
                    return redirect_response
                else:
                    return response
            else:
                print(f'Error in super() response: {response.status_code}')  # Debugging line
                return response
        else:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

# Vista de Logout
class LogoutView(GenericAPIView):

    def post(self, request):
        try:
            # Obtener el token de refresco del request
            refresh_token = request.COOKIES.get('refresh_token')
            if refresh_token:
                # Invalidar el token de refresco
                token = RefreshToken(refresh_token)
                token.blacklist()
                print(f"Refresh token invalidated: {refresh_token}")  # Debugging line
        except Exception as e:
            print(f"Error invalidating token: {e}")  # Debugging line

        # Crear la respuesta y eliminar las cookies
        if "text/html" in self.request.headers.get('Accept'):
            response = HttpResponseRedirect(reverse_lazy('users:login'))  # Redirigir al login
        else:
            response = JsonResponse({"message": "Logout success!"}, safe=False)  # Mostrar deslogueo exitoso
        response.delete_cookie('access_token', path='/', domain=None)
        response.delete_cookie('refresh_token', path='/', domain=None)
        print("Cookies deleted and user redirected to login")  # Debugging line
        return response

# Vista para Registrarse
class SignupView(APIView):
    # Users sign up view

    template_name = "users/signup.html"

    def get_context_data(self, **kwargs):
        form = SignupForm()

        context = {}
        if "text/html" in self.request.accepted_media_type:
            context["form"] = form

        context["help_text"] = password_validation.password_validators_help_text_html()
        return context
    
    def get(self, request, *args, **kwargs):
        """Método Get: Habilita el método Get a la vista."""
        context = self.get_context_data()
        return Response(context)

    def post(self, request, *args, **kwargs):
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Optional: You can log in the user directly after signup or send a confirmation email
            if self.request.accepted_renderer.media_type == "text/html":
                return HttpResponseRedirect(reverse_lazy('users:login'))
            else:
                return Response({'detail': 'User created successfully'}, status=status.HTTP_201_CREATED)
        else:
            if self.request.accepted_renderer.media_type == "text/html":
                return Response({'form': form}, template_name=self.template_name)
            else:
                return Response({'errors': form.errors}, status=status.HTTP_400_BAD_REQUEST)


# Vista para Editar tu Perfil
class UpdateProfileView(CustomMethodsMixin, GenericAPIView):
    template_name = 'users/update_profile.html'
    serializer_class = CountryModelSerializer

    permission_classes = [IsAuthenticated]

    # DATA (GET)
    def get_data(self):
        """Obtiene los datos del contexto de la solicitud GET."""
        return {
            "records": self.get_records(),
            "device": self.get_device(),
            "countries": self.get_countries_without_korea(),
        }

    # DATA (POST)
    def get_post_data(self):
        """Obtiene los datos del contexto de la solicitud POST."""
        try:
            picture = self.request.FILES["picture"]
        except:
            picture = None
        try:
            banner = self.request.FILES["banner"]
        except:
            banner = None

        data = {
            "records": self.get_records(),
            "device": self.get_device(),
            "countries": self.get_countries_without_korea(),
            "username": self.request.POST.get("username"),
            "country": self.request.POST.get("country"),
            "youtube_channel": self.request.POST.get("youtube_channel"),
            "twitter": self.request.POST.get("twitter"),
            "twitch": self.request.POST.get("twitch"),
            "facebook": self.request.POST.get("facebook"),
            "device": self.request.POST.getlist("device"),
            "preferences": self.request.POST.get("preferences"),
            "bio": self.request.POST.get("bio"),
            "picture": picture,
            "banner": banner,

            "delete_picture": self.request.POST.get("delete_picture"),
            "delete_banner": self.request.POST.get("delete_banner"),
        }
        data.update({
            "country_object": self.get_country_object(data["country"]),
        })
        return data

    # DATA (BOTH)
    def get_records(self):
        """Obtiene los records del perfil logueado."""
        return Record.objects.filter(player=self.request.user.profile)

    def get_device(self):
        """Obtiene los 'devices' del perfil logueado."""
        if self.request.user.profile.device:
            device = ast.literal_eval(self.request.user.profile.device)
        else:
            device = None
        return device
    
    # UTILS (POST)
    def get_path(self, option):
        """Obtiene el path de una imagen (ya se la foto de perfil o el banner)."""
        if getattr(self.request.user.profile, option):
            return getattr(getattr(self.request.user.profile, option), "path")
        return None
    
    def perform_delete(self, picture, option):
        """Ejecuta la eliminación de una imagen (ya se la foto de perfil o el banner)."""
        if picture and default_storage.exists(picture):
            default_storage.delete(picture)
        setattr(self.request.user.profile, option, None)
        self.request.user.profile.save()

    def validate_username(self, username):
        """Valida si el username es válido, sino, devuelve un 'error_message'."""
        error_message = None
        username_taken = User.objects.filter(username__iexact=username).exists()
        if not username:
            error_message = "The username cannot be empty."
        elif len(username) > 20:
            error_message = "Username must be at most 20 characters long"
        elif not re.match("^\w+$", username):
            error_message = "Username must be alphanumeric"
        elif ' ' in username or '/' in username:
            error_message = "Username cannot contain spaces or '/'"
        elif username_taken and not(self.request.user.username == username):
            error_message = "The username is already in use. Please choose another."
        else:
            resolver = get_resolver()

            # Obtener todas las URLs
            urls = []
            for url_pattern in resolver.url_patterns:
                if hasattr(url_pattern, 'url_patterns'):  # Verificar si es un include()
                    for sub_url_pattern in url_pattern.url_patterns:
                        if hasattr(sub_url_pattern, 'pattern'):
                            url = sub_url_pattern.pattern.describe()
                            url_without_name = url.split('[name=')[0].strip().strip("'")
                            urls.append(url_without_name)

            # Crear una respuesta con la lista de URLs

            categories = [r'^demons/?$', r'^all/?$', r'^rated/?$', r'^unrated/?$', r'^challenge/?$', r'^easiest/?$', r'^shitty/?$', r'^future/?$', r'^tiny/?$', r'^deathless/?$', r'^impossible/?$', r'^spam/?$', r'^impossible_tiny/?$', r'^pemonlist/?$', r'^platformer_challengelist/?$', r'^tiny_demonlist/?$', r'^platformer_deathlesslist/?$', r'^impossible_platformerlist/?$', r'^spam_challengelist/?$', r'^impossible_tiny_list/?$', r'^tiny_pemonlist/?$', r'^platformerlist/?$']

            urls.remove('')
            urls.remove('')
            urls.remove('')
            urls.remove('^(?P<value>[^/]+)/?$')
            urls.remove('(?P<url>.*)$')
            urls.extend(categories)

            is_error = False

            for pattern in urls:
                if re.match(pattern, username):
                    is_error = True
            
            if is_error:
                error_message = "The username is already in use. Please choose another."
            else:
                self.request.user.username = username
                self.request.user.save()
        return error_message

    def assign_info(self, data, profile):
        """Asigna la info al perfil."""
        profile.country = data["country_object"]

        if len(data["bio"]) <= 100:
            profile.bio = data["bio"]
        
        if all(word in ["mouse", "keyboard", "mobile", "controller"] for word in data["device"]):
            profile.device = str(data["device"])

        if data["preferences"]:
            profile.preferences = data["preferences"]
        else:
            profile.preferences = None
        return profile

    def perform_automation_scripts(self, profile):
        """Ejecuta los scripts que automáticamente actualizan la base de datos."""
        functions.update_countries_list_points(profile.country, "classic", "rated")
        functions.update_countries_list_points(profile.country, "platformer", "rated")
        functions.update_countries_list_points(profile.country, "platformer", "unrated")
        functions.update_countries_list_points(profile.country, "platformer", "challenge")

    # DJANGO METHODS
    def get_context_data(self, data, **kwargs):
        context = {}

        if self.request.accepted_renderer.media_type == "text/html":
            context.update({
                "countries": data["countries"],
                "device": data["device"],
                "records": data["records"]
            })
        else:
            countries_serializer = self.get_serializer_class()(data["countries"], many=True)
            records_serializer = RecordModelSerializer(data["records"], many=True)
            context.update({
                "countries": countries_serializer.data,
                "device": data["device"],
                "records": records_serializer.data
            })
        context["list_words"] = self.list_words
        return context

    # API METHODS
    def get(self, request, *args, **kwargs):
        """Método Get: Habilita el método Get a la vista."""
        data = self.get_data()
        context = self.get_context_data(data)
        return Response(context)

    def post(self, request, *args, **kwargs):
        """
        Método POST: Maneja las siguientes operaciones:

        - Elimina la foto de perfil.
        - Elimina el banner.
        - Edita la información del perfil.
        """
        data = self.get_post_data()

        if data["delete_picture"]:
            old_picture = self.get_path("picture")
            self.perform_delete(old_picture, "picture")
            return JsonResponse({"success": True})
        if data["delete_banner"]:
            old_banner = self.get_path("banner")
            self.perform_delete(old_banner, "banner")
            return JsonResponse({"success": True})

        error_message = self.validate_username(data["username"])

        profile = self.request.user.profile

        self.assign_profile_picture(data, profile)
        self.assign_profile_banner(data, profile)

        profile = self.assign_social_media(data, profile)
        profile = self.assign_info(data, profile)
        profile.save()

        if profile.country:
            self.perform_automation_scripts(profile)
            
        context = self.get_context_data(data)
        context["error_message"] = error_message
        if self.request.accepted_renderer.media_type == "text/html":
            return render(request, 'users/update_profile.html', context)
        else:
            return Response(context)


# Vista para la pantalla de Teams
class TeamsView(CustomMethodsMixin, ListAPIView):
    # Teams view
    template_name = 'users/teams.html'
    serializer_class = ProfileModelSerializer

    permission_classes = [IsAuthenticated]

    # DATA (GET)
    def get_team(self):
        """Obtiene el equipo en el que te encuentras."""
        try:
            team = Team.objects.get(owner=self.request.user.profile)
        except:
            try:
                team = Team.objects.get(members=self.request.user.profile)
            except:
                team = None
        return team

    def get_team_invitations(self):
        """Obtiene tus invitaciones a equipos."""
        return TeamInvitation.objects.filter(player=self.request.user.profile)

    def get_team_players(self, team):
        """Obtiene los miembros del equipo en el que te encuentras."""
        return team.members.all()

    def get_team_invitation_players(self, team):
        """Obtiene las invitaciones del equipo en el que te encuentras."""
        return TeamInvitation.objects.filter(team=team).values("player__id")
    
    def get_followers(self, team_players, team_invitation_players):
        """
        Obtiene tus seguidores y les hace un annotate para saber si se encuentran
        en el equipo, o si solamente han sido invitados, o ninguna de las dos.
        """
        return self.request.user.profile.followers.annotate(
            in_team=Case(
                When(id__in=team_players, then=Value(1)),
                When(id__in=team_invitation_players, then=Value(2)),
                default=Value(0),
                output_field=IntegerField(),
            )
        )

    def get_data(self):
        """Obtiene los datos del contexto de la solicitud GET."""
        data = {
            "team": self.get_team(),
            "team_invitations": self.get_team_invitations(),
        }
        if data["team"]:
            data.update({
                "team_players": self.get_team_players(data["team"]),
                "team_invitation_players": self.get_team_invitation_players(data["team"]),
            })
            data.update({
                "followers": self.get_followers(data["team_players"], data["team_invitation_players"]),
            })
        return data

    # DATA (POST)
    def get_follower_profile(self, follower):
        """Obtiene el perfil del seguidor seleccionado."""
        follower_profile = Profile.objects.get(id=follower)
        return follower_profile

    def get_team_player(self, follower_profile):
        """Obtiene el equipo del perfil del seguidor seleccionado."""
        try:
            team_player = Team.objects.get(owner=follower_profile)
        except:
            try:
                team_player = Team.objects.get(members=follower_profile)
            except:
                team_player = None
        return team_player
    
    def get_team_invitation(self, id):
        """Obtiene la invitación seleccionada (para aceptar o rechazar)."""
        return TeamInvitation.objects.get(id=id)
    
    def get_team_taken(self, name):
        """Obtiene si el nombre del equipo ya es existente o no."""
        return Team.objects.filter(name=name).exists()
    
    def get_post_data(self):
        """Obtiene los datos del contexto de la solicitud POST."""
        data = {
            "id":self.request.POST.get("id"),
            "name":self.request.POST.get("name", None),
            "option":self.request.POST.get("option", None),
            "follower":self.request.POST.get("follower", None),

            "search_user":self.request.POST.get("user", None)
        }
        return data

    # UTILS (POST)
    def perform_invite(self, owner, follower_profile):
        """Ejecuta la creación de la invitación."""
        TeamInvitation.objects.create(team=owner.team, player=follower_profile)
        self.handle_create_notification(owner, follower_profile)
    
    def perform_uninvite(self, owner, follower_profile):
        """Ejecuta la eliminación de la invitación."""
        self.handle_delete_invitation(owner, follower_profile)
        self.handle_delete_notification(owner, follower_profile)

    def perform_eject(self, owner, follower_profile):
        """Ejecuta la expulsión de un usuario de tu equipo."""
        follower_profile.team = None
        follower_profile.save()

        owner.team.members.remove(follower_profile)
        self.perform_automation_scripts(owner)
        self.handle_delete_invitation(owner, follower_profile)
        self.handle_delete_notification(owner, follower_profile)

    def perform_transfer(self, owner, follower_profile):
        """Ejecuta la transferencia de propiedad del equipo."""
        team = owner.team
        team.owner = follower_profile
        team.save()
        team.members.remove(follower_profile)
        team.members.add(owner)
        self.handle_delete_invitation(owner, follower_profile)
        self.handle_delete_notification(owner, follower_profile)

    def perform_accept_invitation(self, owner, team_invitation):
        """Ejecuta la aceptación de una invitación de equipo."""
        team = team_invitation.team
        player = team_invitation.player
        player.team = team
        player.save()
        team.members.add(player)
        self.perform_automation_scripts(owner)
        try:
            team_invitation.delete()
        except:
            pass
        self.handle_delete_notification(owner, player)

    def perform_reject_invitation(self, owner, team_invitation):
        """Ejecuta el rechazo de una invitación de equipo."""
        team = team_invitation.team
        player = team_invitation.player
        team.members.remove(player)
        try:
            team_invitation.delete()
        except:
            pass
        self.handle_delete_notification(owner, player)

    def perform_get_out(self, owner):
        """Ejecuta la salida de un usuario del equipo."""
        team = owner.team
        team.members.remove(owner)
        owner.team = None
        owner.save()
        self.perform_automation_scripts(owner)
        self.handle_delete_invitation(team.owner, owner)
        self.handle_delete_notification(team.owner, owner)
    
    def perform_delete(self, owner):
        """Ejecuta la eliminación del equipo."""
        team = owner.team
        if team.owner == owner:
            Profile.objects.filter(team=team).update(team=None)
            try:
                team_invitation = TeamInvitation.objects.filter(team=team)
                team_invitation.delete()
            except:
                pass
            try:
                notification = Notification.objects.filter(action="team_invitation",
                                    parameter=team.name,
                                    id_team_parameter=team.id,
                                    )
                notification.delete()
            except:
                pass
            team.delete()
    
    def perform_create_team(self, owner, name):
        """Ejecuta la creación del equipo."""
        try:
            team_invitation = TeamInvitation.objects.filter(player=owner)
            team_invitation.delete()
        except:
            pass
        try:
            notification = Notification.objects.filter(profile=owner,
                                action="team_invitation",
                                )
            notification.delete()
        except:
            pass
        team = Team.objects.create(name=name, owner=owner)
        owner.team = team
        owner.save()
        self.perform_automation_scripts(owner)

    def handle_create_notification(self, owner, follower_profile):
        """Ejecuta la creación de la notificación de la invitacíon."""
        notification = Notification.objects.create(
            profile=follower_profile,
            action="team_invitation",
            parameter=owner.team.name,
            option="Profile",
            id_team_parameter=owner.team.id,
            profile_parameter=owner
        )
        return notification

    def handle_delete_invitation(self, owner, follower_profile):
        """Ejecuta la eliminación de la invitacíon."""
        try:
            team_invitation = TeamInvitation.objects.get(team=owner.team, player=follower_profile)
            team_invitation.delete()
        except:
            pass
    
    def handle_delete_notification(self, owner, follower_profile):
        """Ejecuta la eliminación de la notificación de la invitacíon."""
        try:
            notification = Notification.objects.get(profile=follower_profile,
                                action="team_invitation",
                                parameter=owner.team.name,
                                option="Profile",
                                id_team_parameter=owner.team.id,
                                profile_parameter=owner
                                )
            notification.delete()
        except:
            pass

    def validate_name(self, name, team_taken):
        """Valida el nombre del equipo que vas a crear."""
        is_validate = False
        if not name:
            messages.error(self.request, "The name of team cannot be empty.")
        elif len(name) > 20:
            messages.error(self.request, "The name of team must be at most 20 characters long")
        elif not re.match("^[a-zA-Z0-9 ]+$", name):
            messages.error(self.request, "The name of team must be alphanumeric")
        elif '/' in name:
            messages.error(self.request, "The name of team cannot contain spaces or '/'")
        elif team_taken:
            messages.error(self.request, "The name of team is already in use. Please choose another.")
        else:
            is_validate = True
        return is_validate

    def perform_automation_scripts(self, owner):
        """Ejecuta los scripts que automáticamente actualizan la base de datos."""
        functions.update_teams_list_points(owner.team, "classic", "rated")
        functions.update_teams_list_points(owner.team, "platformer", "rated")
        functions.update_teams_list_points(owner.team, "platformer", "unrated")
        functions.update_teams_list_points(owner.team, "platformer", "challenge")

    # DJANGO METHODS
    def get_context_data(self, data, **kwargs):
        context = {}

        if data["team"]:
            if "text/html" in self.request.accepted_media_type:
                context.update({
                    "followers": data["followers"],
                    "team": data["team"],
                })
            else:
                followers_serializer = self.get_serializer_class()(data["followers"], many=True)
                team_serializer = TeamModelSerializer(data["team"])
                context.update({
                    "followers": followers_serializer.data,
                    "team": team_serializer.data,
                })

        if "text/html" in self.request.accepted_media_type:
            context.update({
                "team_invitations": data["team_invitations"]
            })
        else:
            team_invitations_serializer = TeamInvitationModelSerializer(data["team_invitations"], many=True)
            context.update({
                "team_invitations": team_invitations_serializer.data
            })
        context["list_words"] = self.list_words
        return context

    # API METHODS
    def get(self, request, *args, **kwargs):
        """Método Get: Habilita el método Get a la vista."""
        data = self.get_data()
        context = self.get_context_data(data)
        return Response(context)

    def post(self, request, *args, **kwargs):
        """
        Método POST: Maneja las siguientes operaciones:

        - Filtra los seguidores del usuario.
        - Invita a un usuario al equipo.
        - Deja de invitar a un usuario al equipo.
        - Expulsa a un usuario del equipo.
        - Transfiere a un usuario la propiedad del equipo.
        - Acepta la invitación de un equipo.
        - Rechaza la invitación de un equipo.
        - Te sales del equipo.
        - Elimina el equipo.
        - Crea un equipo.
        """
        data = self.get_post_data()
        owner = self.request.user.profile

        if data["option"] == "filter_followers":
            
            team_players = self.get_team_players(owner.team)
            team_invitation_players = self.get_team_invitation_players(owner.team)
            followers = self.get_followers(team_players, team_invitation_players)

            if data["search_user"]:
                followers = followers.filter(user__username__icontains=data["search_user"])

            followers_serializer = ProfileTeamModelSerializer(followers, many=True)
            return JsonResponse(followers_serializer.data, safe=False)
        
        elif data["option"] == "invite":
            follower_profile = self.get_follower_profile(data["follower"])
            team_player = self.get_team_player(follower_profile)

            if team_player:
                messages.error(request, "This follower currently possesses a team.")
            else:
                self.perform_invite(owner, follower_profile)
            return HttpResponseRedirect(reverse_lazy('users:teams'))
        
        elif data["option"] == "uninvite":
            follower_profile = self.get_follower_profile(data["follower"])
            self.perform_uninvite(owner, follower_profile)
            return HttpResponseRedirect(reverse_lazy('users:teams'))
        
        elif data["option"] == "eject":
            follower_profile = self.get_follower_profile(data["follower"])
            self.perform_eject(owner, follower_profile)
            return HttpResponseRedirect(reverse_lazy('users:teams'))
        elif data["option"] == "transfer":
            follower_profile = self.get_follower_profile(data["follower"])
            self.perform_transfer(owner, follower_profile)
            return HttpResponseRedirect(reverse_lazy('users:teams'))
        elif data["option"] == "accept_invitation":
            team_invitation = self.get_team_invitation(data["id"])
            self.perform_accept_invitation(owner, team_invitation)
            return HttpResponseRedirect(reverse_lazy('users:teams'))
        elif data["option"] == "reject_invitation":
            team_invitation = self.get_team_invitation(data["id"])
            self.perform_reject_invitation(owner, team_invitation)
            return HttpResponseRedirect(reverse_lazy('users:teams'))
        elif data["option"] == "get_out":
            self.perform_get_out(owner)
            return HttpResponseRedirect(reverse_lazy('users:teams'))
        elif data["option"] == "delete":
            self.perform_delete(owner)
            return HttpResponseRedirect(reverse_lazy('users:teams'))
        elif data["name"]:
            team_taken = self.get_team_taken(data["name"])
            is_validate = self.validate_name(data["name"], team_taken)
            if is_validate:
                self.perform_create_team(owner, data["name"])
            return HttpResponseRedirect(reverse_lazy('users:teams'))
        return HttpResponseRedirect(reverse_lazy("users:teams"))


# Vista para ver el Estado de tus Récords
class RecordsStatusView(CustomMethodsMixin, GenericAPIView):
    # Records status view
    template_name = 'users/records_status.html'
    serializer_class = RecordModelSerializer

    permission_classes = [IsAuthenticated]

    # DJANGO METHODS
    def get_context_data(self, **kwargs):
        context = {}
        records = ExtendedRecord.objects.filter(player=self.request.user.profile).order_by("id")

        if self.request.accepted_renderer.media_type == "text/html":
            context["records"] = records
        else:
            records_serializer = self.get_serializer_class()(records, many=True)
            context["records"] = records_serializer.data
        context["list_words"] = self.list_words
        return context
    
    # API METHODS
    def get(self, request, *args, **kwargs):
        """Método Get: Habilita el método Get a la vista."""
        context = self.get_context_data()
        return Response(context)


# Vista del Detail de un Usuario
class UserDetailView(CustomMethodsMixin, RetrieveAPIView):
    # User Detail View
    template_name = "users/detail.html"
    queryset = User.objects.all()
    serializer_class = ProfileModelSerializer
    lookup_field = "id"

    # DATA (GET)
    def get_following(self, user):
        """Obtiene si sigues al usuario o no."""
        if not(self.request.user.is_anonymous):
            following = self.request.user.profile.followings.all()
            if user.profile in following:
                following = True
            else:
                following = False
        else:
            following = False
        return following

    def get_mode_and_category(self, user, records_list):
        """Obtiene la categoría y modo que se mostrarán en el perfil."""
        if records_list:
            mode = records_list.split()[0]
            category = records_list.split()[1]
        elif user.profile.preferences:
            mode = user.profile.preferences.split()[0]
            category = user.profile.preferences.split()[1]
        else:
            look_records = Record.objects.filter(player=user.profile, accepted=True).values(
                            'demon__mode',
                            'demon__category'
                        ).annotate(
                            count=Count('id')
                        ).order_by(
                            'demon__mode',
                            'demon__category'
                        )
            if look_records:
                mode_category_dict = {}
                for count in look_records:
                    mode = count['demon__mode']
                    category = count['demon__category']
                    total = count['count']

                    mode_category_dict[f"{mode} {category}"] = total

                look_demons_verified = Demon.objects.filter(verifier_profile=user.profile).values(
                            'mode',
                            'category'
                        ).annotate(
                            count=Count('id')
                        ).order_by(
                            'mode',
                            'category'
                        )

                for count in look_demons_verified:
                    mode = count['mode']
                    category = count['category']
                    total = count['count']

                    try:
                        mode_category_dict[f"{mode} {category}"] += total
                    except:
                        mode_category_dict[f"{mode} {category}"] = total

                mejor_categoria = max(mode_category_dict, key=mode_category_dict.get)
                mode = mejor_categoria.split()[0]
                category = mejor_categoria.split()[1]
            else:
                mode = "classic"
                category = "tiny"
        if mode == "classic" and category == "rated":
            category = "tiny"
        return mode, category

    def get_num_list_points(self, user, list_points_string):
        """Obtiene la cantidad de list points que tiene el usuario en la categoría y modo en cuestión."""
        return getattr(user.profile, list_points_string)

    def get_records(self, data):
        """Obtiene los records del usuario en la categoría y modo en cuestión."""
        return ExtendedRecord.objects.filter_by_category_list(data).order_by(f"demon__{data['category']}_position")
    
    def get_demons_created_and_verified(self, user):
        """Obtiene los demons que el usuario ha creado y verificado."""
        week_duration = timezone.now() - timezone.timedelta(weeks=1)

        demons_created = Demon.objects.filter(creator_profile=user.profile).exclude(category="future").annotate(last_changelog_datetime=Subquery(
                Changelog.objects.filter(demon=OuterRef("id")).order_by('-datetime').values('datetime')[:1]
            ), last_changelog_reason_option=Subquery(
                Changelog.objects.filter(demon=OuterRef("id")).order_by('-datetime').values('reason_option')[:1]
            ), last_changelog_reason_demon=Subquery(
                Changelog.objects.filter(demon=OuterRef("id")).order_by('-datetime').values('reason_demon')[:1]
            ), new=Case(
                    When(Q(all_position__isnull=False) | Q(challenge_position__isnull=False) | Q(shitty_position__isnull=False) | Q(tiny_position__isnull=False) | Q(deathless_position__isnull=False) | Q(impossible_position__isnull=False) | Q(spam_position__isnull=False) | Q(impossible_tiny_position__isnull=False), created__gt=week_duration, then=Value(True)),
                    When(last_changelog_datetime__gt=week_duration, last_changelog_reason_option__in=["added_to_list", "rated", "unrated", "challenge", "shitty", "tiny", "deathless", "impossible", "spam", "impossible_tiny", "all"], last_changelog_reason_demon=F("id"), then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField()
                )
            ).order_by('all_position', 'challenge_position', 'shitty_position', 'tiny_position', 'deathless_position', 'impossible_position', 'spam_position', 'impossible_tiny_position')
        demons_verified = Demon.objects.filter(verifier_profile=user.profile).exclude(category="future").annotate(last_changelog_datetime=Subquery(
                Changelog.objects.filter(demon=OuterRef("id")).order_by('-datetime').values('datetime')[:1]
            ), last_changelog_reason_option=Subquery(
                Changelog.objects.filter(demon=OuterRef("id")).order_by('-datetime').values('reason_option')[:1]
            ), last_changelog_reason_demon=Subquery(
                Changelog.objects.filter(demon=OuterRef("id")).order_by('-datetime').values('reason_demon')[:1]
            ), new=Case(
                    When(Q(all_position__isnull=False) | Q(challenge_position__isnull=False) | Q(shitty_position__isnull=False) | Q(tiny_position__isnull=False) | Q(deathless_position__isnull=False) | Q(impossible_position__isnull=False) | Q(spam_position__isnull=False) | Q(impossible_tiny_position__isnull=False), created__gt=week_duration, then=Value(True)),
                    When(last_changelog_datetime__gt=week_duration, last_changelog_reason_option__in=["added_to_list", "rated", "unrated", "challenge", "shitty", "tiny", "deathless", "impossible", "spam", "impossible_tiny", "all"], last_changelog_reason_demon=F("id"), then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField()
                )
            ).order_by('all_position', 'challenge_position', 'shitty_position', 'tiny_position', 'deathless_position', 'impossible_position', 'spam_position', 'impossible_tiny_position')
        return demons_created, demons_verified

    def get_demons_verified_category(self, data, demons_verified):
        """Obtiene los demons que el usuario ha verificado en la categoría y modo en cuestión."""
        return demons_verified.filter(mode=data["mode"], category=data["category"])

    def get_ranking_info(self, user, list_points_string):
        """
        Obtiene la info que se necesitará para posteriormente obtener el ranking. Esta
        info contiene: 'players_filtered', 'original_positions', 'players_list', 'index'.
        """
        try:
            players_annotated =  Profile.objects.annotate(
                list_points=F(list_points_string)
            ).filter(list_points__gte=1).annotate(
                order_position=Window(expression=Rank(), order_by=F('list_points').desc())
            ).order_by("order_position")
            players_filtered = players_annotated.filter(user__username=user.profile)
            original_positions = {player.id: player.order_position for player in players_annotated}
            players_list = list(players_annotated.values_list("user__username", flat=True))
            index = players_list.index(players_filtered.values_list("user__username", flat=True)[0])
        except:
            players_filtered = None
            original_positions = None
            players_list = None
            index = None
        return players_filtered, original_positions, players_list, index
    
    def get_ranking(self, players_filtered, original_positions):
        """Obtiene el ranking del usuario en la categoría y modo en cuestión."""
        try:
            players_final = sorted(players_filtered, key=lambda player: original_positions[player.id])
            ranking = original_positions[players_final[0].id]
        except:
            ranking = "-"
        return ranking

    def get_previous_player_and_ranking(self, original_positions, players_list, index):
        """
        Obtiene el ranking del usuario que esté un puesto debajo de ti en el
        leaderboard en la categoría y modo en cuestión.
        """
        return self.handle_other_player_and_other_ranking(original_positions, players_list, index, -1)
    
    def get_next_player_and_ranking(self, original_positions, players_list, index):
        """
        Obtiene el ranking del usuario que esté un puesto arriba de ti en el
        leaderboard en la categoría y modo en cuestión.
        """
        return self.handle_other_player_and_other_ranking(original_positions, players_list, index, 1)

    def get_hardest(self, category, records, demons_verified_category):
        """Obtiene el hardest del usuario en la categoría y modo en cuestión."""
        try:
            hardest=records.order_by(f"demon__{category}_position")[0].demon
            if demons_verified_category.exists():
                verified_hardest=demons_verified_category.order_by(f"{category}_position")[0]
                if getattr(hardest, f"{category}_position") > getattr(verified_hardest, f"{category}_position"):
                    hardest = verified_hardest
        except:
            if demons_verified_category.exists():
                hardest=demons_verified_category.order_by(f"{category}_position")[0]
            else:
                hardest = "-"
        return hardest

    def get_team_members(self, user):
        """Obtiene los miembros del equipo en el que se encuentra el usuario."""
        team_members = None
        team = user.profile.team
        if team:
            team_members = Profile.objects.filter(team=team).annotate(
                if_owner=Case(
                    When(id=team.owner.id, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField(),
                ))
        return team_members
    
    def get_device(self, user):
        """Obtiene los 'devices' que usa el usuario."""
        if user.profile.device:
            device = ast.literal_eval(user.profile.device)
        else:
            device = None
        return device

    def get_data(self):
        """Obtiene los datos del contexto de la solicitud GET."""
        if self.kwargs.get("user"):
            user = self.get_object(user=self.kwargs.get("user"))
        else:
            user = self.get_object(username=self.kwargs.get("username"))

        data = {
            "user": user,
            "records_list": self.request.GET.get('list'),
        }
        mode, category = self.get_mode_and_category(data["user"], data["records_list"])
        data.update({
            "mode": mode,
            "category": category,
            "list_points_string": self.get_list_points(mode, category),
        })
        records = self.get_records(data)
        demons_created, demons_verified = self.get_demons_created_and_verified(data["user"])
        demons_verified_category = self.get_demons_verified_category(data, demons_verified)
        players_filtered, original_positions, players_list, index = self.get_ranking_info(data["user"], data["list_points_string"])
        previous_player, previous_ranking = self.get_previous_player_and_ranking(original_positions, players_list, index)
        next_player, next_ranking = self.get_next_player_and_ranking(original_positions, players_list, index)
        data.update({
            "following": self.get_following(data["user"]),
            "list_points": self.get_num_list_points(data["user"], data["list_points_string"]),
            "records": records,
            "demons_created": demons_created,
            "demons_verified": demons_verified,
            "ranking": self.get_ranking(players_filtered, original_positions),
            "previous_player": previous_player,
            "previous_ranking": previous_ranking,
            "next_player": next_player,
            "next_ranking": next_ranking,
            "demons_verified_category": demons_verified_category,
            "team_members": self.get_team_members(data["user"]),
            "device": self.get_device(data["user"]),
            "hardest": self.get_hardest(category, records, demons_verified_category),
        })
        return data
    
    # DATA (POST)
    def get_post_data(self):
        """Obtiene los datos del contexto de la solicitud POST."""
        if self.kwargs.get("user"):
            user = self.get_object(user=self.kwargs.get("user"))
        else:
            user = self.get_object(username=self.kwargs.get("username"))

        data = {
            "user": user,
            "action": self.request.POST.get("action", None),
            "search_user": self.request.POST.get("user", None),
            "option": self.request.POST.get("option", None),
            "show_team_members": self.request.POST.get("show_team_members", None),
            "member": self.request.POST.get("member", None),
            "team_id": self.request.POST.get("team_id", None)
        }
        return data
    
    # UTILS (GET)
    def handle_other_player_and_other_ranking(self, original_positions, players_list, index, offset):
        """
        Maneja la lógica al sacar el ranking de otro usuario
        (el anterior o el siguiente de tu ranking).
        """
        try:
            target_index = index + offset
            if 0 <= target_index < len(players_list):
                player = Profile.objects.get(user__username=players_list[target_index])
                ranking = original_positions[player.id]
            else:
                player = None
                ranking = None
        except:
            player = None
            ranking = None
        return player, ranking

    def validate_not_same_user(self, user):
        """Valida que el usuario no sea el mismo que el usuario con el que estás logueado."""
        if user != self.request.user:
            return True
        else:
            return False

    def perform_follow(self, user):
        """Ejecuta la acción de seguir al usuario."""
        user.profile.followers.add(self.request.user.profile)
        self.request.user.profile.followings.add(user.profile)

    def handle_create_notification(self, user):
        """Maneja la creación de la notificación que avisa al usuario que lo han seguido."""
        Notification.objects.create(
            profile=user.profile,
            action=f"following",
            parameter=self.request.user.username,
            option="Profile",
            profile_parameter=self.request.user.profile
        )
    
    def perform_unfollow(self, user):
        """Ejecuta la acción de dejar de seguir al usuario."""
        user.profile.followers.remove(self.request.user.profile)
        self.request.user.profile.followings.remove(user.profile)

    def handle_delete_notification(self, user):
        """Maneja la eliminación de la notificación que avisa al usuario que lo han seguido."""
        try:
            notification = Notification.objects.get(
                profile=user.profile,
                action=f"following",
                profile_parameter=self.request.user.profile,
            )
            notification.delete()
        except:
            pass
    
    # DJANGO METHODS
    def get_object(self, user=None, username=None, queryset=None):
        if user:
            queryset = self.get_queryset().filter(id=user)
        elif username:
            queryset = self.get_queryset().filter(username=username)
        return get_object_or_404(queryset)

    def get_context_data(self, data, **kwargs):
        context = {
            "device": data["device"],
            "following": data["following"],
            "next_player": data["next_player"],
            "next_ranking": data["next_ranking"],
            "previous_player": data["previous_player"],
            "previous_ranking": data["previous_ranking"],
            "ranking": data["ranking"],
            "demons_beaten": len(data["records"]) + len(data["demons_verified_category"]),
            "mode": data["mode"],
            "category": data["category"],
            "list_points": data["list_points"],
            "team_members": data["team_members"],
        }
        if self.request.accepted_renderer.media_type == "text/html":
            context.update({
                "user": data["user"],
                "hardest": data["hardest"],
                "demons_created": data["demons_created"],
                "demons_verified": data["demons_verified"],
                "records": data["records"],
            })
        else:
            user_serializer = UserModelSerializer(data["user"])
            demons_created_serializer = DemonModelSerializer(data["demons_created"], many=True)
            demons_verified_serializer = DemonModelSerializer(data["demons_verified"], many=True)
            records_serializer = RecordModelSerializer(data["records"], many=True)
            context.update({
                "user": user_serializer.data,
                "demons_created": demons_created_serializer.data,
                "demons_verified": demons_verified_serializer.data,
                "records": records_serializer.data,
            })
            if data["hardest"] != "-":
                hardest_serializer = DemonModelSerializer(data["hardest"])
                context["hardest"] = hardest_serializer.data
        context["list_words"] = self.list_words
        print("records")
        print(list(data["records"].values_list("demon__level", flat=True)))
        return context
    
    # API METHODS
    def retrieve(self, request, *args, **kwargs):
        """Método Retrieve: obtiene el usuario y pasa todo el contexto necesario para la vista."""
        data = self.get_data()
        context = self.get_context_data(data)
        return Response(context) 
    
    def post(self, request, *args, **kwargs):
        """
        Método POST: Maneja las siguientes operaciones:

        - Realiza la acción de seguir al usuario.
        - Realiza la acción de dejar de seguir al usuario.
        - Filtra los seguidores del usuario.
        - Filtra los seguidos del usuario.
        - Filtra los miembros del equipo en el que se encuentra el usuario.
        """
        data = self.get_post_data()
        if data["action"]:
            validation_user = self.validate_not_same_user(data["user"])
            if validation_user:
                if data["action"] == "follow":
                    self.perform_follow(data["user"])
                    self.handle_create_notification(data["user"])
                elif data["action"] == "unfollow":
                    self.perform_unfollow(data["user"])
                    self.handle_delete_notification(data["user"])
            return super().get(request, *args, **kwargs)
        elif data["user"]:
            if data["option"] == "followers":
                profiles = data["user"].profile.followers.all()
            elif data["option"] == "following":
                profiles = data["user"].profile.followings.all()
            elif data["option"] == "members":
                profiles = Profile.objects.filter(team=data["user"].profile.team).annotate(
                    if_owner=Case(
                        When(id=data["user"].profile.team.owner.id, then=Value(True)),
                        default=Value(False),
                        output_field=BooleanField(),
                    ))
            if data["search_user"]:
                profiles = profiles.filter(user__username__icontains=data["search_user"])
            profiles_serializer = self.get_serializer_class()(profiles, many=True)
            return JsonResponse(profiles_serializer.data, safe=False)
