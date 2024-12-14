# Django
from django.conf import settings
from django.db.models import F, Window, Sum, Case, When, CharField, Value, ExpressionWrapper, Func, IntegerField, BooleanField, Q, OuterRef, Subquery, DurationField, Max, Exists
from django.http import HttpResponseRedirect, HttpRequest, HttpResponse
from django.http.response import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View

# Django REST Framework
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

# Models
from apps.demonlist.models import Demon, Record, Roulette
from django.contrib.auth.models import User, Group
from apps.users.models import Profile, Country, Notification, Team, TeamInvitation

# Functions
from apps.demonlist.functions import functions
from apps.users.functions import functions_discord

# Utils
import requests

# Vista para Vincular tu Discord
def discord_login(request):
    auth_url_discord = "https://discord.com/oauth2/authorize?client_id=1271128335988293652&response_type=code&redirect_uri=https%3A%2F%2Fwww.geomax.site%2Fusers%2Foauth2%2Flogin%2Fredirect&scope=identify"
    return redirect(auth_url_discord)

# Vista para verificar tu cuenta y redireccionar a la página

class DiscordLoginRedirectView(APIView):

    # DATA (GET)
    def get_data(self):
        """Obtiene los datos del contexto de la solicitud GET."""
        data = {
            "code": self.request.GET.get("code"),
        }
        return data
    
    # UTILS (GET)
    def verify_user(self, code):
        """Verifica al usuario si se encuentra en el server."""
        try:

            user = functions_discord.exchange_code(code)

            server_id = "1269343828075348064"
            user_id = user["id"]
            bot_token = ""

            member_response = requests.get(f"https://discord.com/api/v10/guilds/{server_id}/members/{user_id}",
                                            headers={"Authorization": f"Bot {bot_token}"},
                                            )
            
            profile = self.request.user.profile
            if member_response.status_code == 200:
                member = member_response.json()
                profile.verified = True
            else:
                profile.verified = False
            profile.id_discord = user_id
            profile.discord = user["username"]
            profile.save()

            functions.async_discord_functions(user_id, ["rated", "unrated"])

        except:
            pass

    # API METHODS
    def get(self, request, *args, **kwargs):
        """Método Get: Habilita el método Get a la vista."""
        data = self.get_data()
        self.verify_user(data["code"])
        return HttpResponseRedirect(reverse_lazy('users:update'))


# Vista para quitar la verificación a aquel que se salga del server de discord
class UpdateAccount(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        option = request.POST.get("option")
        discord_username = request.POST.get("discord_username")
        secret = request.POST.get("secret")
        if option == "unverified" and secret == "9omkF@j2^NNni5N^#6ahxY":
            profile = Profile.objects.get(discord=discord_username)
            profile.verified = False
            profile.save()

            response_data = {'success': True,}

            return JsonResponse(response_data)
        
        elif option == "unsubscribe" and secret == "9omkF@j2^NNni5N^#6ahxY":
            profile = Profile.objects.get(discord=discord_username)
            user = profile.user
            group = Group.objects.get(name='Subscriber')
            user.groups.remove(group)

            roulettes = Roulette.objects.filter(Q(player=profile) | Q(players_to_share__in=[profile])).distinct()[2:]
            for roulette in roulettes:
                roulette.players_to_share.remove(profile)
                if roulette.player == profile:
                    roulette.active = False
                    roulette.save()

            response_data = {'success': True,}

            return JsonResponse(response_data)
        
        elif option == "subscribe" and secret == "9omkF@j2^NNni5N^#6ahxY":
            user = Profile.objects.get(discord=discord_username).user
            group = Group.objects.get(name='Subscriber')
            user.groups.add(group)

            roulettes = Roulette.objects.filter(player=profile).distinct()
            for roulette in roulettes:
                roulette.active = True
                roulette.save()

            response_data = {'success': True,}

            return JsonResponse(response_data)