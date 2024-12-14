"""Demon List views."""

# Django
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import user_passes_test
from django.core.files.base import ContentFile
from django.core.files.images import ImageFile
from django.core.files.storage import default_storage
from django.core.paginator import Paginator
from django.db.models import F, Window, Sum, Case, When, CharField, Value, ExpressionWrapper, Func, IntegerField, BooleanField, Q, OuterRef, Subquery, DurationField, Max, Exists, Count
from django.db.models.functions import Rank, Cast
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.http.response import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DetailView, ListView, TemplateView
from django.views.generic.base import View
from django_cte import CTEManager, With

# Django REST Framework
from rest_framework.generics import RetrieveAPIView, ListAPIView, UpdateAPIView, GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

# Functions and Translations
from apps.demonlist.functions import functions
from apps.users.functions import functions_discord
from utils import translations

# Mixins
from apps.users.mixins import ListAdminMixin, ListModMixin, ListHelperMixin
from utils.mixins import CustomMethodsMixin

# Models
from django.contrib.auth.models import User, Group
from apps.demonlist.models import Demon, Record, Changelog, Roulette, RouletteDemon, LevelPack
from apps.users.models import Profile, Country, Notification, Team

# Models (Proxy)
from apps.demonlist.models.proxy import ExtendedDemon, ExtendedRecord
from apps.users.models.proxy import ExtendedCountry, ExtendedProfile, ExtendedTeam

# Permissions
from apps.demonlist.permissions import IsRecordOwnerAndAccepted, IsOwnerRoulette, IsLimitedRoulette
from apps.users.permissions import IsListHelper, IsListMod

# Serializers
from apps.demonlist.serializers import DemonModelSerializer, ChangelogModelSerializer, RecordModelSerializer, DemonSelect2Serializer, RouletteModelSerializer, DemonRouletteSerializer, RouletteDemonModelSerializer
from apps.users.serializers import UserModelSerializer, ProfileModelSerializer, CountryModelSerializer, ProfileSelect2Serializer, ProfileRouletteModelSerializer

# Utils
import ast
import calendar
import datetime
import json
import math
import random
import urllib.parse

# Utils (Custom)
from utils.constants import values_list_points_platformer

# Views
from PlatformDemonList import views as global_views
from apps.users.views import views as demonlist_views


# Vista para el error 404
def custom_404_view(request, exception):
    return render(request, '404.html', status=404)


# Vista para correr la función del rol diario
class DiaryRole(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request):

        secret = request.POST.get("secret")

        if secret == "9omkF@j2^NNni5N^#6ahxY":
            list_roles = []
            list_roles.append({"role_name": "ALL RATED LIST COMPLETED", "action":"confirm_role"})
            list_roles.append({"role_name": "List Points", "action":"confirm_role"})
            list_roles.append({"role_name": "Top Player", "action":"confirm_role"})
            list_roles.append({"role_name": "Top #1 Demon", "action":"confirm_role"})
            list_roles.append({"role_name": "All Unrated List Complete", "action":"confirm_role"})
            list_roles.append({"role_name": "Top #1 Unrated Demon", "action":"confirm_role"})
            list_roles.append({"role_name": "First Record", "action":"confirm_role"})

            functions.async_discord_functions_everyone(list_roles)
            return HttpResponse("Diary role done")

# Vista que te cambia el idioma
def change_language(request):
    profile = request.user.profile
    profile.language = request.POST.get("language")
    profile.save()
    pagina_anterior = request.META.get('HTTP_REFERER', '/')
    return HttpResponseRedirect(pagina_anterior)


# Vista del Home
class HomeView(CustomMethodsMixin, APIView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = {}

        context["list_words"] = self.list_words
        return context
    
    def get(self, request, *args, **kwargs):
        """Método Get: Habilita el método Get a la vista."""
        context = self.get_context_data()
        # functions.update_players_tier(Profile.objects.get(user__username="Jopianos"))
        return Response(context)
    
# Vista para manejar las vistas de DemonListView y UserDetailView
class CategoryOrUsernameView(View):
    def get(self, request, value, *args, **kwargs):
        # Intenta obtener una categoría con el valor proporcionado
        categories = ["demons", "all", "rated", "unrated", "challenge", "easiest", "shitty", "future", "tiny", "deathless", "impossible", "spam", "impossible_tiny", "pemonlist", "platformer_challengelist", "tiny_demonlist", "platformer_deathlesslist", "impossible_platformerlist", "spam_challengelist", "impossible_tiny_list", "tiny_pemonlist", "tpl"]

        if value in categories:
            # Si se encuentra una categoría, usa la vista de lista de demonios
            view = DemonListView.as_view()
            kwargs['category'] = value
        else:
            # Si no se encuentra una categoría, asume que es un nombre de usuario
            user = get_object_or_404(User, username__iexact=value)
            view = demonlist_views.UserDetailView.as_view()
            kwargs['username'] = user.username
        return view(request, *args, **kwargs)

    def post(self, request, value, *args, **kwargs):
        # Si no se encuentra una categoría, asume que es un nombre de usuario
        user = get_object_or_404(User, username=value)
        view = demonlist_views.UserDetailView.as_view()
        kwargs['username'] = user.username
        return view(request, *args, **kwargs)

# Vista de la Lista de Demons
class DemonListView(CustomMethodsMixin, ListAPIView):
    template_name = "demonlist/list.html"
    serializer_class = DemonModelSerializer
    paginate_by = 200

    # CATEGORÍAS DISPONIBLES DE LISTAS
    AVAILABLE_CATEGORIES = ["all_demonlist", "all", "rated", "unrated", "challenge", "easiest", "future", "tiny", "deathless", "impossible", "spam", "impossible_tiny"]
    # PONER HASTA QUÉ TOP SE PUEDE VER UNA LISTA
    LIMITS = {
        "classic": {
            **{key: 100 for key in ("tiny",)},
            **{key: 250 for key in ("all",)},
            **{key: 75 for key in ("spam", "impossible_tiny")}
        },
        "platformer": {
            **{key: 100 for key in ("challenge", "deathless", "impossible", "tiny", "unrated", "all")},
            **{key: 200 for key in ("rated",)}
        }
    }

    # DATA (GET)
    def get_category_and_mode(self):
        """Obtiene el campo categoria y modo."""
        category = self.kwargs.get("category", "rated")
        category = "all_demonlist" if category == "demons" else category
        mode = self.kwargs.get("mode") or ("platformer" if not(category in ["all_demonlist", "future"]) else None)
        mode_and_category = False
        if category == "pemonlist":
            mode, category = "platformer", "rated"
        elif category == "platformer_challengelist":
            mode, category = "platformer", "challenge"
        elif category == "tiny_demonlist":
            mode, category = "classic", "tiny"
        elif category == "platformer_deathlesslist":
            mode, category = "platformer", "deathless"
        elif category == "impossible_platformerlist":
            mode, category = "platformer", "impossible"
        elif category == "spam_challengelist":
            mode, category = "classic", "spam"
        elif category == "impossible_tiny_list":
            mode, category = "classic", "impossible_tiny"
        elif category == "tiny_pemonlist":
            mode, category = "platformer", "tiny"
        elif category == "tpl":
            mode, category = "platformer", "all"
        else:
            mode_and_category = True
        return category, mode, mode_and_category
    
    def get_time_machine_date(self, year, month, day):
        """Obtiene la fecha obtenida por la time machine."""
        try:
            month = month or 12
            day = day or calendar.monthrange(int(year), int(month))[1]
            return datetime.datetime(int(year), int(month), int(day), 23, 59, 59)
        except (ValueError, TypeError):
            return None
    
    def get_list_leaders(self, mode, category):
        """Obtiene los list leaders."""
        if category not in ["all_demonlist", "all", "future"]:
            if category == "impossible_tiny":
                category_leader = f"{mode.capitalize()} Impossible Tiny List Leader"
            else:
                category_leader = f"{mode.capitalize()} {category.capitalize()} List Leader"
            group_leader = Group.objects.get(name=category_leader)
            list_leaders = User.objects.filter(groups=group_leader)
        elif category == "all":
            category_leader = [f"{mode.capitalize()} Rated List Leader", f"{mode.capitalize()} Unrated List Leader", "TPL List Leader"]
            list_leaders = User.objects.filter(groups__name__in=category_leader).distinct()
        elif category == "future":
            category_leader = f"{category.capitalize()} List Leader"
            group_leader = Group.objects.get(name=category_leader)
            list_leaders = User.objects.filter(groups=group_leader)
        else:
            list_leaders = None
        return list_leaders
    
    def get_is_legacy(self):
        """Obtiene si la lista es legacy o no."""
        if self.request.resolver_match.url_name == 'list':
            return False
        elif self.request.resolver_match.url_name == 'list_legacy':
            return True

    def get_record_demons(self):
        """Obtiene los demons pasados por el usuario con el que estás logueado.."""
        if not(self.request.user.is_anonymous):
            return Record.objects.filter(player=self.request.user.profile, accepted=True).values_list("demon__id", flat=True)
        else:
            return None

    def get_data(self):
        """Obtiene los datos del contexto de la solicitud GET."""
        category, mode, mode_and_category = self.get_category_and_mode()

        return {
            "mode": mode,
            "category": category,
            "mode_and_category": mode_and_category,
            "search": self.request.GET.get("search"),
            "demon_difficulty": self.get_list_from_request("demon_difficulty"),
            "verification_status": self.get_list_from_request("verification_status"),
            "status": self.get_list_from_request("status"),
            "year": self.request.GET.get("year"),
            "month": self.request.GET.get("month"),
            "day": self.request.GET.get("day"),
            "position_field": self.get_position_field(category),
            "time_machine_date": self.get_time_machine_date(self.request.GET.get("year"), self.request.GET.get("month"), self.request.GET.get("day")),
            "list_leaders": self.get_list_leaders(mode, category),
            "record_demons": self.get_record_demons(),
            "page": self.request.GET.get("page"),
            "is_legacy": self.get_is_legacy(),
        }
    
    # FILTERS
    def filter_queryset(self, data):
        """Este método aplica los filtros al queryset."""
        if data["time_machine_date"]:
            queryset = ExtendedDemon.objects.filter_by_time_machine_date(
                mode=data["mode"],
                position_field=data["position_field"],
                time_machine_date=data["time_machine_date"]
            )
        else:
            queryset = ExtendedDemon.objects.filter_by_category_list(data["mode"], data["category"])

        return queryset.filter_by_search(search=data["search"]
                        ).handler_filter_generics(
                            demon_difficulty=data["demon_difficulty"], 
                            verification_status=data["verification_status"],
                        ).filter_by_status(data).annotate_new(data["category"]).annotate_uuid().annotate_order_position(data["category"])

    # UTILS (GET)
    def get_list_from_request(self, param):
        """Convierte la data que está separada en comas en lista."""
        value = self.request.GET.getlist(param)
        return value[0].split(",") if value else None
    
    # DJANGO METHODS
    def get_queryset(self, data):
        queryset = self.filter_queryset(data)
        # Limitar queryset según la lista
        if data["mode"]:
            if data["is_legacy"]:
                queryset = queryset[self.LIMITS[data["mode"]][data["category"]]:]
            else:
                queryset = queryset[:self.LIMITS[data["mode"]][data["category"]]]
        return queryset

    def get_context_data(self, data, **kwargs):
        context = {}

        if not(data["category"] in self.AVAILABLE_CATEGORIES):
            raise Http404("La página que buscas no existe")
        
        demons = self.get_queryset(data)
        paginator = Paginator(demons, self.paginate_by)
        page_obj = paginator.get_page(data["page"])

        context.update({
            "category": data["category"],
            "mode": data["mode"],
            "mode_and_category": data["mode_and_category"],
            "demon_difficulty": data["demon_difficulty"],
            "time_machine_date": data["time_machine_date"],
            "verification_status": data["verification_status"],
            "status": data["status"],
            "is_legacy": data["is_legacy"],
            "has_previous": page_obj.has_previous(),
            "has_next": page_obj.has_next(),
            "has_other_pages": paginator.num_pages > 1,
            "page_number": page_obj.number,
            "page_max": paginator.num_pages,
            "view_name": "Collab"
        })

        if "text/html" in self.request.accepted_media_type:
            context.update({
                "demons": page_obj,
                "list_leaders": data["list_leaders"],
                "previous_page_number": page_obj.previous_page_number,
                "next_page_number": page_obj.next_page_number,
                "paginator": paginator,
            })
        else:
            demons_serializer = self.get_serializer(page_obj, many=True)
            list_leaders_serializer = UserModelSerializer(data["list_leaders"], many=True) if data["list_leaders"] else None
            context.update({
                "demons": self.paginate_queryset(demons_serializer.data),
                "list_leaders": list_leaders_serializer.data if list_leaders_serializer else None
            })

        context["list_words"] = self.list_words
        return context

    # API METHODS
    def list(self, request, *args, **kwargs):
        """Método List: lista los demons y pasa todo el contexto necesario para la vista."""
        data = self.get_data()
        context = self.get_context_data(data)
        return Response(context)

# Vista BASE del Detail de un Demon
class DemonDetailView(CustomMethodsMixin, RetrieveAPIView):
    template_name = "demonlist/detail.html"
    queryset = Demon.objects.all()
    serializer_class = DemonModelSerializer

    # DATA (GET)
    def get_category_and_mode(self):
        """Obtiene el campo categoria y modo."""
        category = self.kwargs.get("category", "rated")
        category = "all_demonlist" if category == "demons" else category
        mode = self.kwargs.get("mode") or ("platformer" if not(category in ["all_demonlist", "future"]) else None)
        if (mode == "classic" and category == "rated") or (category == "unrated") or (mode == "classic" and category == "challenge") or (category == "shitty") or (category == "future"):
            raise Http404("La página que buscas no existe")

        if category == "pemonlist":
            mode, category = "platformer", "rated"
        elif category == "platformer_challengelist":
            mode, category = "platformer", "challenge"
        elif category == "tiny_demonlist":
            mode, category = "classic", "tiny"
        elif category == "platformer_deathlesslist":
            mode, category = "platformer", "deathless"
        elif category == "impossible_platformerlist":
            mode, category = "platformer", "impossible"
        elif category == "spam_challengelist":
            mode, category = "classic", "spam"
        elif category == "impossible_tiny_list":
            mode, category = "classic", "impossible_tiny"
        elif category == "tiny_pemonlist":
            mode, category = "platformer", "tiny"
        elif category == "tpl":
            mode, category = "platformer", "all"
        return category, mode
    
    def get_changelog(self, position_field, demon):
        """Obtiene los changelogs relacionados con el demon."""
        return Changelog.objects.filter(
            Q(**{f"{position_field}__isnull": False}) | 
            Q(reason_option="removed", reason_demon=demon),
            demon=demon
        ).order_by("datetime")

    def get_records(self, demon, order_field, with_mods, deathless):
        """Obtiene los records aceptados para el demon y los ordena."""
        records = ExtendedRecord.objects.filter(demon=demon, accepted=True).annotate_video_platform().order_by(order_field)
        if deathless:
            records = records.filter(deathless=True)
        else:
            records = records.filter(deathless=False)

        if not(with_mods):
            records = records.filter(mods__isnull=True)
        return records

    def get_data(self):
        """Obtiene los datos del contexto de la solicitud GET."""
        category, mode = self.get_category_and_mode()
        data = {
            "level_id": self.kwargs.get("level_id"),
            "mode": mode,
            "category": category,
            "position": self.kwargs.get("position"),
            "position_field": self.get_position_field(category),
            "deathless": True if category == "deathless" else None,
        }
        return data
    
    # DATA (POST)
    def get_post_data(self):
        """Obtiene los datos del contexto de la solicitud POST."""
        category, mode = self.get_category_and_mode()

        return {
            "level_id": self.kwargs.get("level_id"),
            "mode": mode,
            "category": category,
            "position": self.kwargs.get("position"),
            "position_field": self.get_position_field(category),
            "action": self.request.POST.get("action"),
            "option": self.request.POST.get("option"),
            "deathless": True if category == "deathless" else None,
            "list_points": self.get_list_points(mode, category),
            "id": self.request.POST.get("id", None),
            "member": self.request.POST.get("member", None),
            "country_field": self.get_country_field(Record)
        }
    
    # UTILS (DISPATCH)
    def fix_data(self, data, demon):
        """Corrige ciertos datos del contexto cuando se accede a la URL mediante el Level ID."""
        data.update({
            "mode": demon.mode,
            "category": demon.category,
            "position_field": self.get_position_field(demon.category),
            "list_points": self.get_list_points(demon.mode, demon.category),
        })
        return data
    
    # UTILS (POST)
    def get_serializer_data(self, data, demon):
        """Obtiener el serializer data que se necesite en la solicitud POST."""
        if data.get("level_id"):
            self.fix_data(data, demon)

        if data["action"] == "show_team_members":
            team_members = self.get_team_members(data)
            team_members_serializer = ProfileModelSerializer(team_members, many=True)
            serializer_data = team_members_serializer.data
        elif data["action"] == "order_records":
            if data["option"] in ["best_time", "order"]:
                order_field = "datetime_submit" if data["option"] == "order" else "best_time"
                records = self.get_records(demon, order_field, False, data["deathless"])
            elif data["option"] == "with_mods":
                records = self.get_records(demon, "datetime_submit", True, data["deathless"])
            elif data["option"] == "without_mods":
                records = self.get_records(demon, "datetime_submit", False, data["deathless"])
            
            records_serializer = RecordModelSerializer(
                records,
                context={"country_field": data["country_field"]},
                many=True
            )
            serializer_data = records_serializer.data
        return serializer_data

    # DJANGO METHODS
    def get_object(self, data, queryset=None):
        if data["level_id"]:
            queryset = self.get_queryset().filter(level_id=data["level_id"])
        elif data["category"] == "future":
            queryset = self.get_queryset().filter(**{data["position_field"]: data["position"]})
        else:
            queryset = self.get_queryset().filter(mode=data["mode"], **{data["position_field"]: data["position"]})
        return get_object_or_404(queryset)

    def get_context_data(self, data, **kwargs):
        context = {}
        demon = self.get_object(data)
        if data.get("level_id"):
            self.fix_data(data, demon)

        changelog = self.get_changelog(data["position_field"], demon)
        order_field = "datetime_submit" if data["mode"] == "classic" else "best_time"
        records = self.get_records(demon, order_field, False, data["deathless"])

        context.update({
            "category": data["category"],
            "mode": data["mode"],
            "view_name": "Collab"
        })
        if "text/html" in self.request.accepted_media_type:
            context.update({
                "demon": demon,
                "changelog": changelog,
                "records": records,
            })
        else:
            demon_serializer = self.get_serializer(demon)
            changelog_serializer = ChangelogModelSerializer(changelog, many=True)
            records_serializer = RecordModelSerializer(records, many=True)
            context.update({
                "demon": demon_serializer.data,
                "changelog": changelog_serializer.data,
                "records": records_serializer.data,
            })
        context["list_words"] = self.list_words
        return context

    # API METHODS
    def retrieve(self, request, *args, **kwargs):
        """Método Retrieve: obtiene el demon y pasa todo el contexto necesario para la vista."""
        data = self.get_data()
        context = self.get_context_data(data)
        return Response(context)
    
    def post(self, request, **kwargs):
        """Método Post: maneja las operaciones de mostrar miembros de un equipo o ordenar records."""
        data = self.get_post_data()
        demon = self.get_object(data)
        serializer_data = self.get_serializer_data(data, demon)
        return JsonResponse(serializer_data, safe=False)

# Vista de la pantalla para Subir un Récord
class SubmitRecordView(CustomMethodsMixin, GenericAPIView):
    template_name = 'demonlist/submit_record.html'
    serializer_class = DemonModelSerializer

    # PONER HASTA QUÉ TOP SE PUEDE SUBIR UN RÉCORD POR LISTA
    LIMITS = {
        "classic": {
            **{key: 200 for key in ("rated", "tiny")},
            **{key: 75 for key in ("spam", "impossible_tiny")}
        },
        "platformer": {
            **{key: 100 for key in ("challenge", "deathless", "impossible", "tiny", "all")},
            **{key: 200 for key in ("rated",)},
        }
    }

    # DATA (POST)
    def get_demons(self, data):
        """Obtiene todos los demons que estén disponibles para subir un record."""
        demons = ExtendedDemon.objects.filter_demons_allowed_to_submit(
            data["mode"],
            data["category"],
            self.LIMITS
        ).annotate_order_position(data["category"]).order_by("order_position")
        return demons

    def get_demon(self):
        """Obtiene el demon del record a crear."""
        try:
            return Demon.objects.get(id=self.request.POST.get("demon", None))
        except:
            return None
    
    def get_mods(self):
        """Obtiene los mods que se usaron en el récord."""
        mods = self.request.POST.getlist("mods", None)
        if not(mods):
            mods = None
        return mods

    def get_post_data(self):
        """Obtiene los datos del contexto de la solicitud POST."""

        return {
            "demon": self.get_demon(),
            "player": self.request.POST.get("player", None),
            "video": self.request.POST.get("video", None),
            "raw_footage": self.request.POST.get("raw_footage", None),
            "notes": self.request.POST.get("notes", None),
            "mods": self.get_mods(),
            "enjoyment_stars": self.request.POST.get("enjoyment_stars", None),
            "gameplay_stars": self.request.POST.get("gameplay_stars", None),
            "decoration_stars": self.request.POST.get("decoration_stars", None),
            "balanced_stars": self.request.POST.get("balanced_stars", None),
            "atmosphere_stars": self.request.POST.get("atmosphere_stars", None),
            "deathless": self.request.POST.get("deathless", None),
            "option": self.request.POST.get("option", None),
            "mode": self.request.POST.get("mode", None),
            "category": self.request.POST.get("category", None),
        }

    # UTILS (POST)
    def validate_limits(self, demon):
        """Valida que el record sea de un demon de alguna lista disponible."""
        for mode, limits in self.LIMITS.items():
            for category, limit in limits.items():
                position_field = f"{category}_position"
                if getattr(demon, position_field) and demon.mode == mode and getattr(demon, position_field) > limit:
                    return HttpResponseRedirect(reverse_lazy('demonlist:list', kwargs={'mode': demon.mode, 'category': demon.category}))
        return None
    
    def assign_player_and_stars(self, data, record):
        """Asigna ya sea el tentative player o el player al record."""
        if data["player"]:
            record.tentative_player = data["player"]
        else:
            record.player = Profile.objects.get(id=self.request.user.profile.id)
            record.enjoyment_stars=data["enjoyment_stars"]
            record.gameplay_stars=data["gameplay_stars"]
            record.decoration_stars=data["decoration_stars"]
            record.balanced_stars=data["balanced_stars"]
            record.atmosphere_stars=data["atmosphere_stars"]
        return record

    def perform_create(self, data):
        """Ejecuta la creación del record."""
        record = Record.objects.create(
            demon=data["demon"],
            video=data["video"],
            raw_footage=data["raw_footage"],
            notes=data["notes"],
            mods=data["mods"],
            deathless=data["deathless"]
        )
        record = self.assign_player_and_stars(data, record)
        record = self.assign_percentage_or_best_time(data["demon"].mode, record)
        record.save()
        return record
    
    # DJANGO METHODS
    def get_context_data(self, **kwargs):
        context = {}
        context["list_words"] = self.list_words
        context["LIMITS"] = self.LIMITS
        return context

    # API METHODS
    def get(self, request):
        """Método Get: pasa todo el contexto necesario para la vista."""
        context = self.get_context_data()
        return Response(context)
    
    def post(self, request):
        """Método Post: Maneja la creación del record."""
        data = self.get_post_data()
        if data["option"] == "filter_demons":
            demons = self.get_demons(data)
            demons_serializer = self.get_serializer(demons, many=True)
            return JsonResponse(demons_serializer.data, safe=False)
        else:
            self.validate_limits(data["demon"])
            record = self.perform_create(data)
            if "text/html" in self.request.accepted_media_type:
                return HttpResponseRedirect(reverse_lazy('users:records_status'))
            else:
                return JsonResponse(RecordModelSerializer(record).data, safe=False)

# Vista de la pantalla para Votar Estrellas
class VoteStarsView(CustomMethodsMixin, RetrieveAPIView, UpdateAPIView):
    template_name = 'demonlist/vote_stars.html'
    queryset = Record.objects.all()
    serializer_class = RecordModelSerializer
    lookup_field = "pk"

    permission_classes = [IsAuthenticated, IsRecordOwnerAndAccepted]

    # DATA (POST)
    def get_post_data(self):
        """Obtiene los datos del contexto de la solicitud POST."""
        request_data_keys = ["enjoyment_stars", "gameplay_stars", "decoration_stars", "balanced_stars", "atmosphere_stars"]
        return {key: self.request.POST.get(key, None) for key in request_data_keys}

    # UTILS (POST)
    def perform_update(self, data):
        """Ejecuta la actualización de las stars del record."""
        record = self.get_object()

        request_data_keys = ["enjoyment_stars", "gameplay_stars", "decoration_stars", "balanced_stars", "atmosphere_stars"]
        for key in request_data_keys:
            setattr(record, key, data[key])
        record.save()
        return record

    def perform_automation_scripts(self, record):
        """Ejecuta los scripts que automáticamente actualizan la base de datos."""
        functions.upload_all_stars(record.demon)
    
    # DJANGO METHODS
    def get_context_data(self, **kwargs):
        context = {}
        record = self.get_object()

        context.update({
            'record': self.get_serializer_class()(record).data,
            'user': UserModelSerializer(self.request.user).data,
            'list_words': self.list_words
        })
        return context
    
    # API METHODS
    def retrieve(self, request, *args, **kwargs):
        """Método Retrieve: obtiene el record y pasa todo el contexto necesario para la vista."""
        context = self.get_context_data()
        return Response(context) 
    
    def patch(self, request, pk):
        """Método Patch: obtiene la calificación de stars y las asigna al record."""
        data = self.get_post_data()
        record = self.perform_update(data)
        self.perform_automation_scripts(record)
        if "text/html" in self.request.accepted_media_type:
            return HttpResponseRedirect(reverse_lazy('users:records_status'))
        else:
            return JsonResponse(self.get_serializer_class()(record).data, safe=False)

# Vista del Stats Viewer
class StatsViewerView(CustomMethodsMixin, ListAPIView):
    template_name = "demonlist/stats_viewer.html"
    serializer_class = ProfileModelSerializer
    paginate_by = 25

    # DATA (GET)
    def get_default_stats_viewer(self):
        """Obtiene lo que tenga el usuario en 'Default'."""
        if not self.request.user.is_anonymous:
            return self.request.user.profile.default_stats_viewer
        return None

    def get_mode_filter(self, mode, default_stats_viewer):
        """Obtiene el mode que se va a usar."""
        return mode or self.get_filter_part(0, default_stats_viewer)

    def get_category_filter(self, category, default_stats_viewer):
        """Obtiene la category que se va a usar."""
        return category or self.get_filter_part(1, default_stats_viewer)

    def get_list_filter(self, mode, category, default_stats_viewer):
        """Obtiene el campo de list_filter basado en el mode y la categoría."""
        if mode and category:
            return f"{mode} {category}"
        return default_stats_viewer
    
    def get_list_points(self, mode, category, default_stats_viewer):
        if mode and category:
            return f"{mode}_{category}_list_points" if category != 'rated' else f"{mode}_list_points"
        elif default_stats_viewer:
            return f"{default_stats_viewer.split(' ')[0]}_{default_stats_viewer.split(' ')[1]}_list_points" if default_stats_viewer.split(' ')[1] != 'rated' else f"{default_stats_viewer.split(' ')[0]}_list_points"

    def get_with_mods(self, mode):
        """Obtiene el campo de with_mods (solo si el mode es 'classic')."""
        if mode == "classic":
            return self.request.GET.get("with_mods", None)
        return None

    def get_data(self):
        """Obtiene los datos del contexto de la solicitud GET."""
        mode, category = self.request.GET.get("mode"), self.request.GET.get("category")
        default_stats_viewer = self.get_default_stats_viewer()
        return {
            "default_stats_viewer": default_stats_viewer,
            "mode_filter": self.get_mode_filter(mode, default_stats_viewer),
            "category_filter": self.get_category_filter(category, default_stats_viewer),
            "list_filter": self.get_list_filter(mode, category, default_stats_viewer),
            "list_points": self.get_list_points(mode, category, default_stats_viewer),
            "status_filter": self.request.GET.get("status", "Individual"),
            "country_filter": None if self.request.GET.get("country") == "None" else self.request.GET.get("country"),
            "search_filter": None if self.request.GET.get("search") == "None" else self.request.GET.get("search"),
            "with_mods": self.get_with_mods(mode),
            "countries": Country.objects.all().order_by(self.get_country_field(Country)),
            "page": self.request.GET.get("page")
        }

    # DATA (POST)
    def get_post_data(self):
        """Obtiene los datos del contexto de la solicitud POST."""
        mode, category = self.request.POST.get("list_filter").split()
        default_stats_viewer = self.get_default_stats_viewer()
        return {
            "option": self.request.POST.get("option"),
            "id": self.request.POST.get("id"),
            "member": self.request.POST.get("member"),
            "list_filter": self.request.POST.get("list_filter"),
            "list_points": self.get_list_points(mode, category, default_stats_viewer),
        }
    
    # FILTERS
    def filter_queryset(self, data, queryset):
        """Este método aplica los filtros al queryset."""

        # Se ordena por list_points (en caso de haber algún modo o categoría escogido)
        queryset = queryset.annotate_position(data).order_by(f"-list_points") if data["list_points"] else queryset

        if data["country_filter"] and data["status_filter"] == "Individual" and queryset:
            queryset = self.use_cte(queryset).filter_by_country(data).order_by(f"-list_points")

        if data["search_filter"] and queryset:
            queryset = self.use_cte(queryset).filter_by_search(data).order_by(f"-list_points")
        return queryset

    # UTILS (GET)
    def use_cte(self, queryset):
        """Empaquetar métodos para usar el Manager CTE de django-cte."""
        return With(queryset).queryset().with_cte(With(queryset))
    
    def get_filter_part(self, index, default_stats_viewer):
        """Obtiener lo que tenga el usuario en 'Default' en dado caso de no escoger un mode o category."""
        if default_stats_viewer:
            parts = default_stats_viewer.split()
            if len(parts) > index:
                return parts[index]
        return None

    # UTILS (POST)
    def get_serializer_data(self, data):
        """Obtiener el serializer data que se necesite en la solicitud POST."""
        if data["option"] == "show_team_members":
            team_members = self.get_team_members(data)
            team_members_serializer = ProfileModelSerializer(team_members, many=True)
            serializer_data = team_members_serializer.data
        return serializer_data
    
    # DJANGO METHODS
    def get_queryset(self, data):
        if data["status_filter"]  == "Nations":
            model = ExtendedCountry
        elif data["status_filter"] == "Teams":
            model = ExtendedTeam
        elif data["status_filter"] == "Individual":
            model = ExtendedProfile
        else:
            model = None
        
        if model and data["list_points"]:
            queryset = model.objects.filter_by_list(data)
        else:
            queryset = model.objects.none()

        queryset = self.filter_queryset(data, queryset)
        return queryset

    def get_context_data(self, data, **kwargs):
        context = {}

        players = self.get_queryset(data)
        paginator = Paginator(players, self.paginate_by)
        page_obj = paginator.get_page(data["page"])

        country_filter_url = urllib.parse.quote(data["country_filter"].encode()) if data["country_filter"] else None

        context.update({
            "has_previous": page_obj.has_previous(),
            "has_next": page_obj.has_next(),
            "has_other_pages": paginator.num_pages > 1,
            "number": page_obj.number,
            "page_max": paginator.num_pages,
            "country_filter": data["country_filter"],
            "country_filter_url": country_filter_url,
            "mode_filter": data["mode_filter"],
            "category_filter": data["category_filter"],
            "list_filter": data["list_filter"],
            "status_filter": data["status_filter"],
            "search_filter": data["search_filter"],
            "with_mods": data["with_mods"],
        })
        if "text/html" in self.request.accepted_media_type:
            context.update({
                "previous_page_number": page_obj.previous_page_number,
                "next_page_number": page_obj.next_page_number,
                "paginator": paginator,
                "players": page_obj,
                "countries": data["countries"],
            })
        else:
            players_serializer = ProfileModelSerializer(page_obj, many=True)
            countries_serializer = CountryModelSerializer(data["countries"], many=True)
            context.update({
                "players": players_serializer.data,
                "countries": countries_serializer.data,
            })
        context["list_words"] = self.list_words
        return context
    
    # API METHODS
    def list(self, request, *args, **kwargs):
        """Método List: lista los players y pasa todo el contexto necesario para la vista."""
        data = self.get_data()
        context = self.get_context_data(data)
        return Response(context)

    def post(self, request):
        """Método Post: maneja la operación de mostrar miembros de un equipo."""
        data = self.get_post_data()
        serializer_data = self.get_serializer_data(data)
        return JsonResponse(serializer_data, safe=False)

# Vista de la pantalla para Revisar Récords
class CheckRecordsView(CustomMethodsMixin, ListAPIView, UpdateAPIView):
    # Return check records view
    template_name = "demonlist/check_records.html"
    queryset = Record.objects.all()
    serializer_class = RecordModelSerializer
    lookup_field = "pk"
    paginate_by = 25

    permission_classes = [IsAuthenticated, IsListHelper]

    # CATEGORÍAS DISPONIBLES DE LISTAS
    AVAILABLE_CATEGORIES = ["rated", "unrated", "challenge", "shitty", "tiny", "deathless", "impossible", "spam", "impossible_tiny", "all"]
    # OPCIONES DE ACCIONES DISPONIBLES
    ACTION_OPTIONS = ["accepted", "rejected", "under_consideration"]

    # DATA (GET)
    def get_data(self):
        """Obtiene los datos del contexto de la solicitud GET."""
        data = {
            "status_filter": None if self.request.GET.get("status", "Pending") == "None" else self.request.GET.get("status"),
            "search_filter": None if self.request.GET.get("search") == "None" else self.request.GET.get("search"),
            "mode_filter": None if self.request.GET.get("mode") == "None" else self.request.GET.get("mode"),
            "category_filter": None if self.request.GET.get("category") == "None" else self.request.GET.get("category"),
            "demon_filter": None if self.request.GET.get("demon") == "None" else self.request.GET.get("demon"),
            "page": self.request.GET.get("page")
        }
        data.update({
            "demon_filter_url": self.get_demon_filter_url(data["demon_filter"])
        })
        return data

    # DATA (POST)
    def get_record(self, id):
        """Obtiene el record sobre el cual se realizará una acción."""
        return Record.objects.get(id=id)

    def get_post_data(self):
        """Obtiene los datos del contexto de la solicitud POST."""
        request_data_keys = ["option", "id", "mod_notes", "mods", "percentage", "hours", "minutes", "seconds", "milliseconds"]
        data = {key: self.request.POST.get(key, None) for key in request_data_keys}
        record = self.get_record(data["id"])
        data.update({
            "record": record,
            "mode": record.demon.mode,
            "category": "deathless" if record.deathless else record.demon.category,
            "was_accepted": record.accepted,
        })
        return data
    
    # FILTERS
    def filter_queryset(self, data, queryset):
        """Este método aplica los filtros al queryset."""

        if data["search_filter"]:
            queryset = queryset.filter(player__user__username__icontains=data["search_filter"])

        if data["mode_filter"]:
            queryset = queryset.filter(demon__mode=data["mode_filter"])

        if data["category_filter"]:
            queryset = queryset.filter(demon__category=data["category_filter"])

        if data["demon_filter"]:
            queryset = queryset.filter(demon=Demon.objects.get(level=data["demon_filter"]))

        if not(self.request.global_context["is_list_admin"]):
            queryset = queryset.exclude(player__user__username="GuitarHeroStyles")

        # Excluir los records que no pertenecen al rol del usuario list helper
        if not(self.request.global_context["is_classic_list_helper"]):
            queryset = queryset.exclude(demon__mode="classic")
        if not(self.request.global_context["is_platformer_list_helper"]):
            queryset = queryset.exclude(demon__mode="platformer")

        if not(self.request.global_context["is_rated_list_helper"]):
            queryset = queryset.exclude(demon__category="rated")
        if not(self.request.global_context["is_unrated_list_helper"]):
            queryset = queryset.exclude(demon__category="unrated")
        if not(self.request.global_context["is_challenge_list_helper"]):
            queryset = queryset.exclude(demon__category="challenge")
        if not(self.request.global_context["is_shitty_list_helper"]):
            queryset = queryset.exclude(demon__category="shitty")
        if not(self.request.global_context["is_tiny_list_helper"]):
            queryset = queryset.exclude(demon__category="tiny")
        if not(self.request.global_context["is_deathless_list_helper"]):
            queryset = queryset.exclude(demon__category="deathless")
        if not(self.request.global_context["is_impossible_list_helper"]):
            queryset = queryset.exclude(demon__category="impossible")
        if not(self.request.global_context["is_spam_list_helper"]):
            queryset = queryset.exclude(demon__category="spam")
        if not(self.request.global_context["is_impossible_tiny_list_helper"]):
            queryset = queryset.exclude(demon__category="impossible_tiny")
        if not(self.request.global_context["is_all_list_helper"]):
            queryset = queryset.exclude(demon__category="all")

        queryset = queryset.exclude(Q(demon__mode="classic", demon__category="rated") | Q(demon__category="unrated") | Q(demon__mode="classic", demon__category="challenge") | Q(demon__category="shitty") | Q(demon__category="future"))

        queryset = queryset.exclude_tentative_player().annotate_order_position(data["category_filter"])
        
        # Ordenar por datetime y prioridad a suscriptores
        queryset = queryset.order_by("datetime_submit").order_by(Case(
                When(player__user__groups__name__in=['Subscriber'], then=Value(0)),
                default=Value(1),
                output_field=BooleanField(),
            )).distinct()
        return queryset
   
    # UTILS (POST)
    """PASO 1"""
    def validate_percentage(self, data):
        """Valida que el porcentaje sea válido en caso de que el demon sea clásico."""
        if data["mode"] == "classic":
            if data["record"].demon.min_percentage:
                if int(data["percentage"]) < data["record"].demon.min_percentage:
                    return HttpResponseRedirect(reverse_lazy("demonlist:list", kwargs={"mode": data["mode"], "category": data["category"]}))
            else:
                if int(data["percentage"]) < 100:
                    return HttpResponseRedirect(reverse_lazy("demonlist:list", kwargs={"mode": data["mode"], "category": data["category"]}))

    """PASO 2"""
    def verify_existing_record(self, record):
        """Verifica si ya existe un record aceptado para el mismo usuario y demon."""
        return Record.objects.exclude(id=record.id).get(demon=record.demon, player=record.player, accepted=True)

    """PASO 3"""
    def handle_old_record(self, data, old_record, record):
        """Maneja la acción de 'aceptar record' y  sobrescribir la info del nuevo record en el anterior."""
        old_record = self.perform_update(data, old_record, "accepted", old=True)

        # Eliminar el record nuevo, ya que la información del record nuevo ya se sobrescribió en el viejo
        if not record.accepted:
            record.delete()

        self.create_record_notification(old_record, "accepted")
        self.perform_automation_scripts(old_record, data["mode"], data["category"])
        return old_record
    
    def handle_record(self, data, record, option):
        """Maneja las acciones a realizar en el record."""
        record = self.perform_update(data, record, option, old=False)

        """
        Entra al condicional si el record no es aceptado, o también si sí es aceptado pero que no
        sea el mismo record que ya había sido aceptado.
        """
        if (option != "accepted") or (option == "accepted" and not(data["was_accepted"])):
            # Crear la notificación de la opción elegida
            self.create_record_notification(record, option)
            # Eliminar las notificaciones de las opciones no elegidas
            for action in self.ACTION_OPTIONS:
                if option != action:
                    self.delete_record_by_option_notification(record, action)

        self.perform_automation_scripts(record, data["mode"], data["category"])
        return record
    
    """PASO 4"""
    def perform_update(self, data, record, option, old):
        """Ejecuta la actualización de la info pasada al record tras ser revisado."""
        record = self.assign_percentage_or_best_time(data["mode"], record)
        if old:
            record = self.assign_old_record_data(data, record)
        else:
            record = self.assign_record_data(data, record, option)
        record.save()
        return record
    
    """PASO 5"""
    def assign_old_record_data(self, data, old_record):
        """Asigna la info necesaria al old record que se aceptará."""
        old_record.video = data["record"].video
        old_record.raw_footage = data["record"].raw_footage
        old_record.enjoyment_stars = data["record"].enjoyment_stars
        old_record.gameplay_stars = data["record"].gameplay_stars
        old_record.decoration_stars = data["record"].decoration_stars
        old_record.balanced_stars = data["record"].balanced_stars
        old_record.atmosphere_stars = data["record"].atmosphere_stars
        old_record.notes = data["record"].notes
        old_record.mod_notes = data["mod_notes"]
        old_record.mod = self.request.user.profile
        if data["mods"] == "Yes":
            old_record.mods = '["click_between_frames"]'
        else:
            old_record.mods = None
        old_record.datetime_checked = datetime.datetime.now()
        return old_record
    
    def assign_record_data(self, data, record, option):
        """Asigna la info necesaria al record sobre el cual se realizará una acción."""
        if option == "accepted":
            record.accepted = True
        elif option == "rejected":
            record.accepted = False
        elif option == "under_consideration":
            record.accepted = None
        
        if option == "under_consideration":
            record.under_consideration = True
        else:
            record.under_consideration = False

        record.mod_notes = data["mod_notes"]
        record.mod = self.request.user.profile
        if data["mods"] == "Yes":
            record.mods = '["click_between_frames"]'
        else:
            record.mods = None
        record.datetime_checked = datetime.datetime.now()
        return record
    
    """PASO 6"""
    def create_record_notification(self, record, option):
        """Crea la notificación basada en la acción realizada sobre el record."""
        try:
            notification = Notification.objects.get(profile=record.player, action=f"record_{option}", parameter=record.demon, record_parameter=record.id, option="Profile", profile_parameter=record.player, demon_parameter=record.demon)
        except:
            Notification.objects.create(profile=record.player, action=f"record_{option}", parameter=record.demon, record_parameter=record.id, option="Profile", profile_parameter=record.player, demon_parameter=record.demon)

            # En caso de ser un record aceptado, crear la notificación para todos los followers del usuario
            if option == "accepted":
                Notification.objects.bulk_create([
                    Notification(profile=follower, action="demon_beaten", parameter=record.demon, record_parameter=record.id, option="Profile", profile_parameter=record.player)
                    for follower in record.player.followers.all()
                ])
    
    """PASO 7"""
    def delete_record_by_option_notification(self, record, option):
        """Eliminar la notificación basada en la acción no realizada sobre el record."""
        try:
            notification = Notification.objects.get(profile=record.player, action=f"record_{option}", parameter=record.demon, record_parameter=record.id, option="Profile", profile_parameter=record.player, demon_parameter=record.demon)
            notification.delete()
        except Notification.DoesNotExist:
            pass

        # En caso de ser un record aceptado, eliminar la notificación para todos los followers del usuario
        if option == "accepted":
            notifications = Notification.objects.filter(
                action="demon_beaten", parameter=record.demon, record_parameter=record.id, option="Profile", profile_parameter=record.player)
            if notifications.exists():
                notifications.delete()

    """PASO 8"""
    def perform_automation_scripts(self, record, mode, category):
        """Ejecuta los scripts que automáticamente actualizan la base de datos."""
        functions.update_top_order(record.demon)
        if mode == "platformer":
            functions.update_top_best_time(record.demon)
        functions.update_players_list_points(record.player, record.demon.mode, category)
        functions.update_countries_list_points(record.player.country, record.demon.mode, category)
        functions.update_teams_list_points(record.player.team, record.demon.mode, category)
        functions.upload_all_stars(record.demon)

        functions.async_discord_functions(record.player.id_discord, [category])
    
    # DJANGO METHODS
    def get_queryset(self, data):

        if data["status_filter"] == "Cancelled":
            queryset = ExtendedRecord.objects.filter(accepted=False)
        elif data["status_filter"] == "Accepted":
            queryset = ExtendedRecord.objects.filter(accepted=True)
        elif data["status_filter"] == "Under Consideration":
            queryset = ExtendedRecord.objects.filter(accepted=None, under_consideration=True)
        else:
            queryset = ExtendedRecord.objects.filter(accepted=None, under_consideration=False)

        queryset = self.filter_queryset(data, queryset)
        return queryset

    def get_context_data(self, data, **kwargs):
        context = {}

        if data["mode_filter"] and data["category_filter"]:
            demons = ExtendedDemon.objects.filter_by_categories(self.AVAILABLE_CATEGORIES).annotate_order_position(data["category_filter"]).order_by("order_position")
        else:
            demons = ExtendedDemon.objects.none()

        records = self.get_queryset(data)
        paginator = Paginator(records, self.paginate_by)
        page_obj = paginator.get_page(data["page"])

        context.update({
            'has_previous': page_obj.has_previous(),
            'has_next': page_obj.has_next(),
            'has_other_pages': paginator.num_pages > 1,
            'number': page_obj.number,
            'page_max': paginator.num_pages,
            'category_filter': data["category_filter"],
            'demon_filter': data["demon_filter"],
            'demon_filter_url': data["demon_filter"],
            'mode_filter': data["mode_filter"],
            'status_filter': data["status_filter"],
            'search_filter': data["search_filter"],
        })
        if "text/html" in self.request.accepted_media_type:
            context.update({
                'previous_page_number': page_obj.previous_page_number,
                'next_page_number': page_obj.next_page_number,
                'paginator': paginator,
                'demons': demons,
                'records': page_obj,
            })
        else:
            records_serializer = self.get_serializer_class()(page_obj, many=True)
            demons_serializer = DemonModelSerializer(demons, many=True)
            context.update({
                'demons': demons_serializer.data,
                'records': records_serializer.data,
            })
        return context
    
    # API METHODS
    def list(self, request, *args, **kwargs):
        """Método List: lista los records y pasa todo el contexto necesario para la vista."""
        data = self.get_data()
        context = self.get_context_data(data)
        return Response(context)
    
    def post(self, request):
        """Método Post: maneja las operaciones de aceptar records, rechazarlos y ponerlos bajo consideración."""
        data = self.get_post_data()
        record = data["record"]
        
        if data["option"] == "accepted":
            if data["mode"] == "classic":
                self.validate_percentage(data)

            """
            Si el usuario ya tiene un record aceptado del mismo nivel, sobrescribe la información del 
            nuevo record en el existente y borra el nuevo. Si el usuario NO tiene un record aceptado 
            del mismo nivel, simplemente acepta el nuevo record.
            """
            try:
                old_record = self.verify_existing_record(record)
                record = self.handle_old_record(data, old_record, record)
            except Record.DoesNotExist:
                record = self.handle_record(data, record, data["option"])

            record_serializer = self.get_serializer_class()(record)
            return JsonResponse(record_serializer.data, safe=False)
        
        elif data["option"] == "rejected":
            record = self.handle_record(data, record, data["option"])
            record_serializer = self.get_serializer_class()(record)
            return JsonResponse(record_serializer.data, safe=False)
        
        elif data["option"] == "under_consideration":
            record = self.handle_record(data, record, data["option"])
            record_serializer = self.get_serializer_class()(record)
            return JsonResponse(record_serializer.data, safe=False)

# Vista de la pantalla para Revisar los Perfiles de los Récords ajenos
class CheckProfilesView(CustomMethodsMixin, ListAPIView, UpdateAPIView):
    # Return check profiles view
    template_name = "demonlist/check_profiles.html"
    queryset = Record.objects.all()
    serializer_class = RecordModelSerializer
    lookup_field = "pk"
    paginate_by = 25

    permission_classes = [IsAuthenticated, IsListHelper]

    # CATEGORÍAS DISPONIBLES DE LISTAS
    CLASSIC_CATEGORIES = ["rated", "unrated", "shitty", "tiny", "spam", "impossible_tiny"]
    PLATFORMER_CATEGORIES = ["rated", "unrated", "challenge", "deathless", "impossible", "tiny", "all"]

    # DATA (GET)
    def get_is_assigned(self, data):
        """Obtiene si está el filtro de asignado o no."""
        return (True if data["assigned_filter"] == "Assigned" 
                            else False if data["assigned_filter"] == "Not Assigned" 
                            else None)
    
    def get_data(self):
        """Obtiene los datos del contexto de la solicitud GET."""
        data = {
            "status_filter": None if self.request.GET.get("status", "Records") == "None" else self.request.GET.get("status", "Records"),
            "assigned_filter": None if self.request.GET.get("assigned", "Not Assigned") == "None" else self.request.GET.get("assigned", "Not Assigned"),
            "search_filter": None if self.request.GET.get("search") == "None" else self.request.GET.get("search"),
            "mode_filter": None if self.request.GET.get("mode") == "None" else self.request.GET.get("mode"),
            "category_filter": None if self.request.GET.get("category") == "None" else self.request.GET.get("category"),
            "demon_filter": None if self.request.GET.get("demon") == "None" else self.request.GET.get("demon"),
            "page": self.request.GET.get("page")
        }
        data.update({
            "is_assigned": self.get_is_assigned(data),
            "demon_filter_url": self.get_demon_filter_url(data["demon_filter"])
        })
        return data

    # DATA (POST)
    def get_post_data(self):
        """Obtiene los datos del contexto de la solicitud POST."""
        data = {
            "search_filter": self.request.POST.get("search"),
            "record_id": self.request.POST.get("record_id"),
            "demon_id": self.request.POST.get("demon_id"),
            "player_id": self.request.POST.get("player_id"),
            "option": self.request.POST.get("option"),
            "assigned_filter": self.request.POST.get("assigned")
        }
        data.update({
            "is_assigned": self.get_is_assigned(data),
        })
        return data

    # FILTERS
    def filter_queryset(self, data, queryset):
        """Este método aplica los filtros al queryset."""
        if data["search_filter"]:
            if data["status_filter"] == "Verifiers":
                queryset = queryset.filter(Q(verifier__icontains=data["search_filter"]) | Q(verifier_profile__user__username__icontains=data["search_filter"]) | Q(level__icontains=data["search_filter"]), level_id__isnull=False)
            elif data["status_filter"] == "Creators":
                queryset = queryset.filter(Q(creator__icontains=data["search_filter"]) | Q(creator_profile__user__username__icontains=data["search_filter"]) | Q(level__icontains=data["search_filter"]), level_id__isnull=False)
            elif data["status_filter"] == "Records":
                queryset = queryset.filter(Q(tentative_player__icontains=data["search_filter"]) | Q(demon__level__icontains=data["search_filter"]), demon__level_id__isnull=False)

        if data["mode_filter"]:
            if data["status_filter"] != "Records":
                queryset = queryset.filter(mode=data["mode_filter"])
            else:
                queryset = queryset.filter(demon__mode=data["mode_filter"])

        if data["category_filter"]:
            if data["status_filter"] != "Records":
                queryset = queryset.filter(category=data["category_filter"])
            else:
                queryset = queryset.filter(demon__category=data["category_filter"])

        return queryset
    
    # UTILS (POST)
    def assign_player_to_record(self, data):
        """Asigna un perfil a un record."""
        player = Profile.objects.get(id=data["player_id"])

        record = Record.objects.get(id=data["record_id"])
        record.player = player
        record.tentative_player = None
        record.admin = self.request.user.profile
        record.save()
        return record
    
    def assign_verifier_or_creator(self, data, option):
        """Asigna un verificador o un creador a un demon."""
        player = Profile.objects.get(id=data["player_id"])
        demon_selected = Demon.objects.get(id=data["demon_id"])

        """
        Si el demon ya tiene un verificador o creador asignado, solo se actualiza el perfil en este demon específico.
        En caso de no estar asignado, se asigna este perfil a todos los demons que tienen el mismo nombre de usuario 
        como creador o verificador que el perfil proporcionado.
        """
        if option == "verifier":
            demon_selected_tentative_profile = demon_selected.verifier
        elif option == "creator":
            demon_selected_tentative_profile = demon_selected.creator

        if data["is_assigned"]:
            Demon.objects.filter(Q(id=data["demon_id"]) | Q(verifier=demon_selected_tentative_profile)).update(verifier=player.user.username, verifier_profile=player)
            Demon.objects.filter(Q(id=data["demon_id"]) | Q(creator=demon_selected_tentative_profile)).update(creator=player.user.username, creator_profile=player)
        else:
            Demon.objects.filter(verifier=demon_selected_tentative_profile).update(verifier=player.user.username, verifier_profile=player)
            Demon.objects.filter(creator=demon_selected_tentative_profile).update(creator=player.user.username, creator_profile=player)

        self.perform_automation_scripts(player)
        return demon_selected

    def perform_delete(self, data):
        """Ejecuta la eliminación de un record por su id."""
        record = Record.objects.get(id=data["record_id"])
        record.delete()
    
    def perform_automation_scripts(self, player):
        """Ejecuta los scripts que automáticamente actualizan la base de datos (en segundo plano)."""
        functions.update_players_list_points_all("classic", self.CLASSIC_CATEGORIES)
        functions.update_countries_list_points_all("classic", self.CLASSIC_CATEGORIES)
        functions.update_teams_list_points_all("classic", self.CLASSIC_CATEGORIES)

        functions.update_players_list_points_all("platformer", self.PLATFORMER_CATEGORIES)
        functions.update_countries_list_points_all("platformer", self.PLATFORMER_CATEGORIES)
        functions.update_teams_list_points_all("platformer", self.PLATFORMER_CATEGORIES)

        functions.async_discord_functions(player.id_discord, self.CLASSIC_CATEGORIES)

    # DJANGO METHODS
    def get_queryset(self, data):

        if data["status_filter"] == "Verifiers":
            field = "verifier"
        elif data["status_filter"] == "Creators":
            field = "creator"

        if data["status_filter"] in ["Verifiers", "Creators"]:
            queryset = ExtendedDemon.objects.filter(**{f"{field}_profile__isnull": not(data["is_assigned"])}).order_by("created")
        elif data["status_filter"] == "Records":
            queryset = ExtendedRecord.objects.filter(accepted=None, tentative_player__isnull=False).order_by("datetime_submit")

        queryset = self.filter_queryset(data, queryset)
        if data["status_filter"] in ["Verifiers", "Creators"]:
            queryset = queryset.annotate_order_position(data["category_filter"])
        elif data["status_filter"] == "Records":
            queryset = queryset.annotate_order_position(data["category_filter"])
        return queryset
    
    def get_context_data(self, data, **kwargs):
        context = {}

        queryset = self.get_queryset(data)
        if data["status_filter"] == "Records":
            queryset_model = "records"
        elif data["status_filter"] in ["Verifiers", "Creators"]:
            queryset_model = "demons"
        
        paginator = Paginator(queryset, self.paginate_by)
        page_obj = paginator.get_page(data["page"])

        context.update({
            'has_previous': page_obj.has_previous(),
            'has_next': page_obj.has_next(),
            'has_other_pages': paginator.num_pages > 1,
            'number': page_obj.number,
            'page_max': paginator.num_pages,
            'category_filter': data["category_filter"],
            'demon_filter': data["demon_filter"],
            'demon_filter_url': data["demon_filter_url"],
            'mode_filter': data["mode_filter"],
            'status_filter': data["status_filter"],
            'assigned_filter': data["assigned_filter"],
            'search_filter': data["search_filter"]
        })

        if "text/html" in self.request.accepted_media_type:
            context.update({
                'previous_page_number': page_obj.previous_page_number,
                'next_page_number': page_obj.next_page_number,
                'paginator': paginator,
                'objects': page_obj,
            })
        else:
            if queryset_model == "records":
                queryset_serializer = self.get_serializer_class()(page_obj, many=True)
            elif queryset_model == "demons":
                queryset_serializer = DemonModelSerializer(page_obj, many=True)
            context.update({
                queryset_model: queryset_serializer.data,
            })
        return context
    
    # API METHODS
    def list(self, request, *args, **kwargs):
        """Método List: lista los demons o records y pasa todo el contexto necesario para la vista."""
        data = self.get_data()
        context = self.get_context_data(data)
        return Response(context)
    
    def post(self, request):
        """
        Método POST: Maneja las siguientes operaciones:
        
        - Busca perfiles por username.
        - Asigna un perfil a un record.
        - Asigna un perfil como verificador o creador de un nivel.
        - Elimina un record.
        """
        data = self.get_post_data()

        if data["option"] == "search":
            players = Profile.objects.filter(user__username__icontains=data["search_filter"])[:100]
            players_serializer = ProfileSelect2Serializer(players, many=True)
            return JsonResponse({"results": players_serializer.data})
        elif data["option"] == "send_player":
            """A un record se le asigna un player donde antes tenía un tentative_player."""
            record = self.assign_player_to_record(data)
        elif data["option"] == "send_verifier":
            demon = self.assign_verifier_or_creator(data, "verifier")
        elif data["option"] == "send_creator":
            demon = self.assign_verifier_or_creator(data, "creator")
        elif data["option"] == "delete":
            record = self.perform_delete(data)

        if "text/html" in self.request.accepted_media_type:
            return HttpResponseRedirect(reverse_lazy('demonlist:check_profiles'))
        else:
            if data["option"] in ["send_player"]:
                record_serializer = self.get_serializer_class()(record)
                return JsonResponse(record_serializer.data, safe=False)
            elif data["option"] in ["send_verifier", "send_creator"]:
                demon_serializer = DemonModelSerializer(demon)
                return JsonResponse(demon_serializer.data, safe=False)
            elif data["option"] == "delete":
                return JsonResponse({"message": "Record deleted"}, safe=False)

# Vista de la pantalla para Agregar o Editar un Demon
class AddEditDemonView(CustomMethodsMixin, UpdateAPIView):
    template_name = "demonlist/add_edit_demon.html"
    serializer_class = DemonSelect2Serializer

    permission_classes = [IsAuthenticated, IsListMod]

    # DATA (POST)
    def get_demons(self, data):
        """Filtra los demons para el Select2."""
        
        if data["action"] == "Recover":
            # Filtrar los demons que se hayan removido
            demons = ExtendedDemon.objects.filter(removed=True, mode=data["mode"], category=data["category"]).annotate_order_position(data["category"])
        else:
            demons = ExtendedDemon.objects.filter_by_category_list(data["mode"], data["category"]).annotate_order_position(data["category"])

        if data["search_filter"]:
            demons = demons.filter_by_search(data["search_filter"])
        return demons[:100]

    def get_demon(self, data):
        """Obtener la info de un demon."""
        demon = ExtendedDemon.objects.filter_with_removed(id=data["demon_id"]).annotate_alternative_order_position(data["category"])
        return demon
    
    def get_alternative_position_field(self, category):
        """
        Obtiene el campo de posición basado en la categoría (a excepción de
        'rated' y 'unrated', que más bien traen la 'all_position').
        """
        if category in ["rated", "unrated"]:
            return "all_position"
        else:
            return f"{category}_position"
    
    def get_verification_video_embed(self, verification_video):
        """Obtiene el link del video a link embebido."""
        if verification_video:
            if verification_video[:16] == "https://youtu.be":
                verification_video_embed = 'https://www.youtube.com/embed/' + verification_video.split('/')[3]
            elif verification_video[:29] == "https://www.youtube.com/watch":
                verification_video_embed = 'https://www.youtube.com/embed/' + verification_video.split('=')[1]
            else:
                verification_video_embed = None
        else:
            verification_video_embed = None
        return verification_video_embed
    
    def get_list_demons(self, data):
        """
        Obtiene todos los demons de la lista por debajo de la posición enviada desde el form.
        """
        list_demons = Demon.objects.filter(
            mode=data["mode"],
            **{f"{data['alternative_position_field']}__gte": int(data["position"])},
        ).order_by(data["alternative_position_field"])

        if data["category"] == "deathless":
            list_demons = list_demons.filter(deathless=True)
        elif data["category"] == "all":
            list_demons = list_demons.filter(all_position__isnull=False)
        else:
            list_demons = list_demons.filter(category=data["category"])

        """
        Si es 'Add' o 'Recover', significa que el changelog sería 'Added to list', por lo tanto
        para sacar su placement correcto, se excluye el nivel actual a añadir del queryset.
        """
        if data["option"] in ["Add", "Recover"]:
            list_demons = list_demons.exclude(level_id=data["level_id"])
        return list_demons
    
    def get_exclude_demons(self, data):
        """
        Obtiene todos los demons de la 'all' category que no estén en la lista actual (rated o unrated)
        y que estén por debajo de la posición enviada desde el form.
        """
        exclude_demons = Demon.objects.filter(
            mode=data["mode"],
            **{f"{data['alternative_position_field']}__gte": int(data["position"])}
        ).exclude(category=data["category"])
        return exclude_demons

    def get_category_position(self, data, list_demons, old_demon=None):
        """Si tiene 'all_position', obtener la posición de la categoría por separado."""
        if data["category"] in ["rated", "unrated"]:
            try:
                category_position = getattr(list_demons.first(), data["position_field"])

                """
                Tener la anterior 'category_position' en caso de que la 'all_position' se haya mantenido igual
                o que haya bajado de posición (solo en el 'Edit').
                """
                if old_demon:
                    new_all_position = getattr(list_demons.first(), "all_position")
                    old_all_position = getattr(old_demon, "all_position")
                    if new_all_position != int(data["position"]) and int(data["position"]) > old_all_position:
                        category_position -= 1
            except:
                """
                Se hace esto en dado caso de que la posición puesta en el formulario sea la última de la lista,
                ya que de ser así, 'list_demons' no tendrá ningún demon.
                """
                filter_demons = Demon.objects.filter(
                    mode=data["mode"],
                    category=data["category"]
                ).exclude(level_id=data["level_id"]).order_by(data["position_field"])

                try:
                    category_position = getattr(filter_demons.last(), data["position_field"]) + 1
                except:
                    category_position = 1
        else:
            category_position = data["position"]
        return category_position

    def get_old_demon_info(self, data, old_demon):
        """
        Obtener la info del demon antes de asignarle nueva info. Es decir, obtener la 'old_info'.
        """
        if old_demon.deathless and data["category"] == "deathless":
            old_demon_info = {
                "category": "deathless",
                "position_field": self.get_position_field("deathless"),
                data["alternative_position_field"]: getattr(old_demon, data["alternative_position_field"]),
            }
        else:
            old_demon_info = {
                "category": old_demon.category,
                "position_field": self.get_position_field(old_demon.category),
                data["alternative_position_field"]: getattr(old_demon, data["alternative_position_field"]),
            }

        if data["category"] in ["rated", "unrated"]:
            old_demon_info.update({
                data["position_field"]: getattr(old_demon, data["position_field"]),
            })
        return old_demon_info

    def get_filter_category(self, data, old_demon_info):
        """Obtener la(s) categoría(s) para realizar los 'automation_scripts'."""
        if old_demon_info["category"] == data["category"]:
            if data["category"] != "future":
                filter_category = [data["category"]]
            else:
                filter_category = []
        else:
            filter_category = ["rated", "unrated"]
            if data["mode"] == "classic":
                filter_category.append("shitty")
                filter_category.append("tiny")
                filter_category.append("spam")
                filter_category.append("impossible_tiny")
            elif data["mode"] == "platformer":
                filter_category.append("challenge")
                filter_category.append("deathless")
                filter_category.append("impossible")
                filter_category.append("tiny")
                filter_category.append("all")
        return filter_category
    
    def get_post_data(self):
        """Obtiene los datos del contexto de la solicitud POST."""
        try:
            photo = self.request.FILES["photo"]
        except:
            photo = None
        
        data = {
            "search_filter": self.request.POST.get("search"),
            "action": self.request.POST.get("action"),
            "mode": self.request.POST.get("mode"),
            "category": self.request.POST.get("category"),
            "demon_id": self.request.POST.get("demon_id"),
            "option": self.request.POST.get("option"),
            "level": self.request.POST.get("level"),
            "id": self.request.POST.get("edit_demon"),
            "photo": photo,
            "position": self.request.POST.get("position"),
            "verification_status": self.request.POST.get("verification_status"),
            "verification_record": self.request.POST.get("verification_record"),
            "creator": self.request.POST.get("creator"),
            "verifier": self.request.POST.get("verifier"),
            "verification_video": self.request.POST.get("verification_video"),
            "level_id": self.request.POST.get("level_id"),
            "level_id_ldm": self.request.POST.get("level_id_ldm") if self.request.POST.get("level_id_ldm") else None,
            "object_count": self.request.POST.get("object_count"),
            "demon_difficulty": self.request.POST.get("demon_difficulty"),
            "level_password": self.request.POST.get("level_password") if self.request.POST.get("level_password") else None,
            "type": self.request.POST.get("type"),
            "version": self.request.POST.get("version"),
        }
        data.update({
            "alternative_position_field": self.get_alternative_position_field(data["category"]),
            "position_field": self.get_position_field(data["category"]),
            "verification_video_embed": self.get_verification_video_embed(data["verification_video"]),
            "is_all_demonlist": True if data["mode"] == "all_demonlist" else None,
        })
        return data

    # UTILS (POST)
    def fix_mode(self, data, old_demon):
        """Si el modo es 'all_demonlist', obtener el modo real del demon (classic o platformer)."""
        data["mode"] = old_demon.mode
        return data
    
    def validate_roles(self, data):
        """Validar que el usuario realmente tenga el rol para poder realizar acciones en la lista seleccionada."""
        if not(self.request.global_context["is_platformer_list_leader"]):
            if data["mode"] == "platformer":
                return HttpResponseRedirect(reverse_lazy('demonlist:list', kwargs={'mode': 'platformer', 'category': 'rated'}))
        if not(self.request.global_context["is_classic_list_leader"]):
            if data["mode"] == "classic":
                return HttpResponseRedirect(reverse_lazy('demonlist:list', kwargs={'mode': 'classic', 'category': 'rated'}))

        categories = ["rated", "unrated", "challenge", "shitty", "future", "tiny", "deathless", "impossible", "spam", "impossible_tiny", "all"]

        for category in categories:
            if not(self.request.global_context[f"is_{category}_list_leader"]) and data["category"] == category:
                if category == "future":
                    return HttpResponseRedirect(reverse_lazy('demonlist:category_or_username', kwargs={'value': 'future'}))
                return HttpResponseRedirect(reverse_lazy('demonlist:list', kwargs={'mode': data["mode"], 'category': category}))

        if not(self.request.global_context["is_list_editor"]):
            if data["category"] == "all_demonlist":
                return HttpResponseRedirect(reverse_lazy('demonlist:category_or_username', kwargs={'value': 'demons'}))
    
    def assign_creator_profile_and_verifier_profile(self, data, demon):
        """
        Asignar el perfil del creador y del verificador al demon (en dado caso
        de que existan, tomando otros demons como referencia).
        """
        try:
            creator_profile = Demon.objects.filter(creator=data["creator"]).first().creator_profile
        except:
            creator_profile = None
        try:
            verifier_profile = Demon.objects.filter(verifier=data["verifier"]).first().verifier_profile
        except:
            verifier_profile = None

        demon.creator_profile=creator_profile
        demon.verifier_profile=verifier_profile
        return demon
    
    def assign_info_to_demon(self, data, demon, category_position, level=None):
        """Asignar la info al demon y guardarlo."""
        if data["photo"]:
            old_photo = demon.photo.path if demon.photo else None
            if old_photo and default_storage.exists(old_photo):
                default_storage.delete(old_photo)
            demon.photo=data["photo"]
        if level:
            demon.level=level
        demon.mode=data["mode"]
        if (data["category"] not in ["deathless", "impossible", "all"]) or data["option"] == "Add":
            demon.category=data["category"]
        demon.creator=data["creator"]
        demon.verifier=data["verifier"]
        demon = self.assign_creator_profile_and_verifier_profile(data, demon)
        if data["category"] == "deathless":
            demon.verification_video_deathless=data["verification_video"]
            demon.verification_video_embed_deathless=data["verification_video_embed"]
        elif not(demon.verification_video) or data["category"] not in ["impossible"]:
            demon.verification_video=data["verification_video"]
            demon.verification_video_embed=data["verification_video_embed"]

        demon.level_id=data["level_id"]
        demon.level_id_ldm=data["level_id_ldm"]
        demon.object_count=data["object_count"]
        demon.demon_difficulty=data["demon_difficulty"]
        demon.level_password=data["level_password"]
        demon.type=data["type"]
        demon.update_created=data["version"]

        if data["category"] == "deathless":
            demon.deathless = True

        setattr(demon, data["alternative_position_field"], data["position"])
        if data["category"] in ["rated", "unrated"]:
            setattr(demon, data["position_field"], category_position)
        elif data["category"] == "future":
            demon.verification_status=data["verification_status"]
            demon.verification_record=data["verification_record"]
        demon.save()
        return demon
    
    def perform_add_demon(self, data, category_position):
        """Creación de demon."""
        try:
            new_demon = Demon.objects.get(level_id=data["level_id"])
            new_demon = self.assign_info_to_demon(data, new_demon, category_position, level=data["level"])
        except:
            new_demon = Demon.objects.create()
            new_demon = self.assign_info_to_demon(data, new_demon, category_position, level=data["level"])
        return new_demon

    def perform_edit_demon(self, data, old_demon, category_position):
        """Edición de demon."""
        old_demon_info = self.get_old_demon_info(data, old_demon)
        old_demon = self.assign_info_to_demon(data, old_demon, category_position)
        return old_demon, old_demon_info

    def perform_remove_demon(self, data, removed_demon):
        """Eliminación de demon."""
        setattr(removed_demon, data["position_field"], None)
        if removed_demon.category in ["rated", "unrated"]:
            setattr(removed_demon, data["alternative_position_field"], None)
        removed_demon.removed = True
        removed_demon.save()
        return removed_demon

    def perform_recover_demon(self, data, recovered_demon, category_position):
        """Recuperación de demon."""
        setattr(recovered_demon, data["position_field"], category_position)
        if recovered_demon.category in ["rated", "unrated"]:
            recovered_demon.all_position = data["position"]
        recovered_demon.removed = False
        recovered_demon.save()
        return recovered_demon

    def handle_add_changelogs(self, data, list_demons, new_demon, category_position):
        """Se crean los changelogs para todos los demons que cambian de posición al agregar un nivel."""
        for demon in list_demons:
            changelog = Changelog.objects.create(
                demon=demon,
                reason=f"{data['level']} was added above",
                reason_option="added_above",
                reason_demon=new_demon,
                change_number=1,
                change_type="Down"
            )
            setattr(changelog, data["position_field"], getattr(demon, data["position_field"]) + 1)
            changelog.save()

            # Se aumenta una posición a cada demon
            setattr(demon, data["position_field"], getattr(demon, data["position_field"]) + 1)

            # Si tiene 'all_position', se aumenta una posición en la 'all_position' de cada demon
            if data["category"] in ["rated", "unrated"]:
                Changelog.objects.create(demon=demon,
                            reason=f"{data['level']} was added above",
                            reason_option="added_above",
                            reason_demon=new_demon,
                            all_position=demon.all_position + 1,
                            change_number=1,
                            change_type="Down"
                            )
                demon.all_position += 1
            demon.save()

        """
        Si tiene 'all_position', se crean los changelogs para todos los exclude_demons que cambian de posición.
        (Los exclude_demons son todos aquellos demons que no son de la categoría actual).
        """
        if data["category"] in ["rated", "unrated"]:
            exclude_demons = self.get_exclude_demons(data)
            for demon in exclude_demons:
                Changelog.objects.create(demon=demon,
                            reason=f"{data['level']} was added above",
                            reason_option="added_above",
                            reason_demon=new_demon,
                            all_position=demon.all_position + 1,
                            change_number=1,
                            change_type="Down"
                            )
                demon.all_position += 1
                demon.save()

        # Crear changelog para el demon actual
        changelog = Changelog.objects.create(demon=new_demon,
                                reason="Added to list",
                                reason_option="added_to_list",
                                reason_demon=new_demon,
                                )
        setattr(changelog, data["alternative_position_field"], data["position"])
        changelog.save()

        # Si tiene 'all_position', crear category_changelog para el demon actual
        if data["category"] in ["rated", "unrated"]:
            category_changelog = Changelog.objects.create(demon=new_demon,
                                    reason="Added to list",
                                    reason_option="added_to_list",
                                    reason_demon=new_demon,
                                    )
            setattr(category_changelog, data["position_field"], category_position)
            category_changelog.save()
    
    def handle_edit_changelogs(self, data, old_demon, old_demon_info, category_position):
        """Se crean los changelogs para todos los demons que cambian de posición al editar la posición de un nivel."""
        if old_demon_info["category"] != data["category"]:
            changelog = Changelog.objects.create(
                demon=old_demon,
                reason_option=data["category"],
                reason_demon=old_demon,
            )
            if data["category"] in ["rated", "unrated"]:
                setattr(changelog, "reason", f"{old_demon.level} was {data['category']}")
            else:
                setattr(changelog, "reason", f"{old_demon.level} was moved to {data['category']} list")
            setattr(changelog, data["position_field"], category_position)
            changelog.save()

            demons = Demon.objects.filter(
                **{f"{old_demon_info['position_field']}__gt": int(old_demon_info[old_demon_info["position_field"]])},
                mode=data["mode"]
            )
            for demon in demons:
                changelog = Changelog.objects.create(
                    demon=demon,
                    reason_option=data["category"],
                    reason_demon=old_demon,
                    change_number=1,
                    change_type="Up"
                )
                if data["category"] in ["rated", "unrated"]:
                    setattr(changelog, "reason", f"{old_demon.level} was {data['category']}")
                else:
                    setattr(changelog, "reason", f"{old_demon.level} was moved to {data['category']} list")
                setattr(changelog, old_demon_info["position_field"], getattr(demon, old_demon_info["position_field"]) - 1)
                changelog.save()

                setattr(demon, old_demon_info["position_field"], getattr(demon, old_demon_info["position_field"]) - 1)
                demon.save()

            demons = Demon.objects.filter(
                **{f"{data['position_field']}__gte": int(category_position)},
                mode=data["mode"]
            )
            for demon in demons:
                changelog = Changelog.objects.create(
                    demon=demon,
                    reason_option=data["category"],
                    reason_demon=old_demon,
                    change_number=1,
                    change_type="Down"
                )
                if data["category"] in ["rated", "unrated"]:
                    setattr(changelog, "reason", f"{old_demon.level} was {data['category']}")
                else:
                    setattr(changelog, "reason", f"{old_demon.level} was moved to {data['category']} list")
                setattr(changelog, data["position_field"], getattr(demon, data["position_field"]) + 1)
                changelog.save()

                setattr(demon, data["position_field"], getattr(demon, data["position_field"]) + 1)
                demon.save()

        else:
            if old_demon_info[data["position_field"]] > int(category_position):
                changelog = Changelog.objects.create(
                    demon=old_demon,
                    reason="Moved",
                    reason_option="moved",
                    reason_demon=old_demon,
                    change_type="Up"
                )
                setattr(changelog, data["position_field"], category_position)
                setattr(changelog, "change_number", old_demon_info[data["position_field"]] - int(category_position))
                changelog.save()

                demons = Demon.objects.filter(
                    **{f"{data['position_field']}__lt": old_demon_info[data["position_field"]]},
                    **{f"{data['position_field']}__gte": int(category_position)},
                    mode=data["mode"]
                ).exclude(level_id=data["level_id"])
                for demon in demons:
                    changelog = Changelog.objects.create(demon=demon,
                                reason=f"{old_demon.level} was moved up past this demon",
                                reason_option="moved_up",
                                reason_demon=old_demon,
                                change_number=1,
                                change_type="Down"
                                )
                    setattr(changelog, data["position_field"], getattr(demon, data["position_field"]) + 1)
                    changelog.save()

                    setattr(demon, data["position_field"], getattr(demon, data["position_field"]) + 1)
                    demon.save()

            elif old_demon_info[data["position_field"]] < int(category_position):
                changelog = Changelog.objects.create(
                    demon=old_demon,
                    reason="Moved",
                    reason_option="moved",
                    reason_demon=old_demon,
                    change_type="Down"
                )
                setattr(changelog, data["position_field"], category_position)
                setattr(changelog, "change_number", int(category_position) - old_demon_info[data["position_field"]])
                changelog.save()

                demons = Demon.objects.filter(
                    **{f"{data['position_field']}__lte": int(category_position)},
                    **{f"{data['position_field']}__gt": old_demon_info[data["position_field"]]},
                    mode=data["mode"]
                ).exclude(level_id=data["level_id"])

                for demon in demons:
                    changelog = Changelog.objects.create(
                        demon=demon,
                        reason=f"{old_demon.level} was moved down past this demon",
                        reason_option="moved_down",
                        reason_demon=old_demon,
                        change_number=1,
                        change_type="Up"
                    )
                    setattr(changelog, data["position_field"], getattr(demon, data["position_field"]) - 1)
                    changelog.save()

                    setattr(demon, data["position_field"], getattr(demon, data["position_field"]) - 1)
                    demon.save()

        if data["category"] in ["rated", "unrated"]:
            if old_demon_info["all_position"] > int(data["position"]):
                Changelog.objects.create(demon=old_demon,
                                reason="Moved",
                                reason_option="moved",
                                reason_demon=old_demon,
                                all_position=data["position"],
                                change_number=old_demon_info["all_position"] - int(data["position"]),
                                change_type="Up"
                                )
                demons = Demon.objects.filter(
                    all_position__lt=old_demon_info["all_position"],
                    all_position__gte=data["position"],
                    mode=data["mode"]
                ).exclude(level_id=data["level_id"])
                for demon in demons:
                    Changelog.objects.create(
                        demon=demon,
                        reason=f"{old_demon.level} was moved up past this demon",
                        reason_option="moved_up",
                        reason_demon=old_demon,
                        all_position=demon.all_position + 1,
                        change_number=1,
                        change_type="Down"
                    )
                    demon.all_position += 1
                    demon.save()
            elif old_demon_info["all_position"] < int(data["position"]):
                Changelog.objects.create(
                    demon=old_demon,
                    reason="Moved",
                    reason_option="moved",
                    reason_demon=old_demon,
                    all_position=int(data["position"]),
                    change_number=int(data["position"]) - old_demon_info["all_position"],
                    change_type="Down"
                )
                demons = Demon.objects.filter(
                    all_position__lte=data["position"],
                    all_position__gt=old_demon_info["all_position"],
                    mode=data["mode"]
                ).exclude(level_id=data["level_id"])
                for demon in demons:
                    Changelog.objects.create(
                        demon=demon,
                        reason=f"{old_demon.level} was moved down past this demon",
                        reason_option="moved_down",
                        reason_demon=old_demon,
                        all_position=demon.all_position - 1,
                        change_number=1,
                        change_type="Up"
                    )
                    demon.all_position -= 1
                    demon.save()

    def handle_remove_changelogs(self, data, removed_demon):
        """Se crean los changelogs para todos los demons que cambian de posición al remover un nivel."""
        demons = Demon.objects.filter(
            **{f"{data['position_field']}__gte": getattr(removed_demon, data["position_field"])},
            mode=removed_demon.mode
        ).exclude(id=removed_demon.id)
        for demon in demons:
            changelog = Changelog.objects.create(
                demon=demon,
                reason=f"{removed_demon.level} has been removed",
                reason_option="removed",
                reason_demon=removed_demon,
                change_number=1,
                change_type="Up"
            )
            setattr(changelog, data["position_field"], getattr(demon, data["position_field"]) - 1)
            changelog.save()

            setattr(demon, data["position_field"], getattr(demon, data["position_field"]) - 1)
            demon.save()

        if removed_demon.category in ["rated", "unrated"]:
            demons = Demon.objects.filter(
                all_position__gte=removed_demon.all_position,
                mode=removed_demon.mode
            ).exclude(id=removed_demon.id)
            for demon in demons:
                Changelog.objects.create(demon=demon,
                            reason=f"{removed_demon.level} has been removed",
                            reason_option="removed",
                            reason_demon=removed_demon,
                            all_position=demon.all_position - 1,
                            change_number=1,
                            change_type="Up"
                            )
                demon.all_position -= 1
                demon.save()

        Changelog.objects.create(
            demon=removed_demon,
            reason=f"{removed_demon.level} has been removed",
            reason_option="removed",
            reason_demon=removed_demon,
        )

    def handle_recover_changelogs(self, data, list_demons, recovered_demon, category_position):
        """Se crean los changelogs para todos los demons que cambian de posición al recuperar un nivel."""
        for demon in list_demons:
            changelog = Changelog.objects.create(
                demon=demon,
                reason=f"{recovered_demon.level} was added above",
                reason_option="added_above",
                reason_demon=recovered_demon,
                change_number=1,
                change_type="Down"
            )
            setattr(changelog, data["position_field"], getattr(demon, data["position_field"]) + 1)
            changelog.save()

            if recovered_demon.category in ["rated", "unrated"]:
                Changelog.objects.create(demon=demon,
                            reason=f"{recovered_demon.level} was added above",
                            reason_option="added_above",
                            reason_demon=recovered_demon,
                            all_position=demon.all_position + 1,
                            change_number=1,
                            change_type="Down"
                            )
                demon.all_position += 1

            setattr(demon, data["position_field"], getattr(demon, data["position_field"]) + 1)
            demon.save()

        if data["category"] in ["rated", "unrated"]:
            exclude_demons = self.get_exclude_demons(data)
            for demon in exclude_demons:
                Changelog.objects.create(
                    demon=demon,
                    reason=f"{recovered_demon.level} was added above",
                    reason_option="added_above",
                    reason_demon=recovered_demon,
                    all_position=demon.all_position + 1,
                    change_number=1,
                    change_type="Down"
                )
                demon.all_position += 1
                demon.save()

        changelog = Changelog.objects.create(
            demon=recovered_demon,
            reason="Added to list",
            reason_option="added_to_list",
            reason_demon=recovered_demon,
        )
        setattr(changelog, data["position_field"], category_position)
        changelog.save()

        if data["category"] in ["rated", "unrated"]:
            Changelog.objects.create(
                demon=recovered_demon,
                reason="Added to list",
                reason_option="added_to_list",
                reason_demon=recovered_demon,
                all_position=data["position"],
            )

    def perform_automation_scripts(self, mode, filter_category):
        """
        Si la categoría no es 'future', ejecuta los scripts que automáticamente actualizan 
        la base de datos (en segundo plano).
        """
        if filter_category != ["future"]:
            functions.order_list_points(mode, filter_category)
            functions.update_players_list_points_all(mode, filter_category)
            functions.update_countries_list_points_all(mode, filter_category)
            functions.update_teams_list_points_all(mode, filter_category)

    # API METHODS
    def get(self, request, *args, **kwargs):
        """Método Get: Habilita el método Get a la vista."""
        return Response()

    def post(self, request):
        """
        Método POST: Maneja las siguientes operaciones:

        - Busca demons por lista y por nombre del nivel.
        - Obtiene la info de un demon.
        - Agrega un demon.
        - Edita un demon.
        - Remueve un demon.
        - Elimina un demon.
        """

        data = self.get_post_data()

        if data["option"] == "Filter":
            demons = self.get_demons(data)
            demons_serializer = self.get_serializer_class()(demons, many=True)
            return JsonResponse({"results": demons_serializer.data})
        
        if data["option"] == "Get":
            demon = self.get_demon(data)
            demon_serializer = DemonModelSerializer(demon, many=True)
            return JsonResponse({"results": demon_serializer.data})

        if data["option"] == "Add":

            self.validate_roles(data)
            list_demons = self.get_list_demons(data)
            category_position = self.get_category_position(data, list_demons)
            new_demon = self.perform_add_demon(data, category_position)

            self.handle_add_changelogs(data, list_demons, new_demon, category_position)
            self.perform_automation_scripts(data["mode"], [data["category"]])
            if "text/html" in self.request.accepted_media_type:
                if data["category"] == "future":
                    return HttpResponseRedirect(reverse_lazy('demonlist:category_or_username', kwargs={'value': 'future'}))
                else:
                    return HttpResponseRedirect(reverse_lazy('demonlist:list', kwargs={'mode': data["mode"], 'category': data["category"]}))
            else:
                demon_serializer = DemonModelSerializer(new_demon)
                return JsonResponse(demon_serializer.data, safe=False)

        if data["option"] == "Edit":

            old_demon = Demon.objects.get(id=data["id"])
            if data["is_all_demonlist"]:
                old_demon, old_demon_info = self.perform_edit_demon(data, old_demon, category_position)
            else:
                self.validate_roles(data)
                list_demons = self.get_list_demons(data)
                category_position = self.get_category_position(data, list_demons, old_demon=old_demon)
                old_demon, old_demon_info = self.perform_edit_demon(data, old_demon, category_position)

                data = self.fix_mode(data, old_demon)

                self.handle_edit_changelogs(data, old_demon, old_demon_info, category_position)
                filter_category = self.get_filter_category(data, old_demon_info)
                self.perform_automation_scripts(data["mode"], filter_category)

            if "text/html" in self.request.accepted_media_type:
                if data["is_all_demonlist"]:
                    return HttpResponseRedirect(reverse_lazy('demonlist:category_or_username', kwargs={'value': 'demons'}))
                elif data["category"] == "future":
                    return HttpResponseRedirect(reverse_lazy('demonlist:category_or_username', kwargs={'value': 'future'}))
                else:
                    return HttpResponseRedirect(reverse_lazy('demonlist:list', kwargs={'mode': data["mode"], 'category': data["category"]}))
            else:
                demon_serializer = DemonModelSerializer(old_demon)
                return JsonResponse(demon_serializer.data, safe=False)

        if data["option"] == "Remove":

            removed_demon = Demon.objects.get(id=data["id"])

            self.handle_remove_changelogs(data, removed_demon)
            removed_demon = self.perform_remove_demon(data, removed_demon)
            self.perform_automation_scripts(removed_demon.mode, [removed_demon.category])

            if "text/html" in self.request.accepted_media_type:
                return HttpResponseRedirect(reverse_lazy("demonlist:list", kwargs={"mode": removed_demon.mode, "category": removed_demon.category}))
            else:
                demon_serializer = DemonModelSerializer(removed_demon)
                return JsonResponse(demon_serializer.data, safe=False)

        if data["option"] == "Recover":
            self.validate_roles(data)
            list_demons = self.get_list_demons(data)
            category_position = self.get_category_position(data, list_demons)

            recovered_demon = Demon.objects.get(id=data["id"])
            recovered_demon = self.perform_recover_demon(data, recovered_demon, category_position)

            self.handle_recover_changelogs(data, list_demons, recovered_demon, category_position)
            self.perform_automation_scripts(recovered_demon.mode, [recovered_demon.category])

            if "text/html" in self.request.accepted_media_type:
                return HttpResponseRedirect(reverse_lazy('demonlist:list', kwargs={'mode': recovered_demon.mode, 'category': recovered_demon.category}))
            else:
                demon_serializer = DemonModelSerializer(recovered_demon)
                return JsonResponse(demon_serializer.data, safe=False)

# Vista de la pantalla para Agregar o Editar un Perfil
class AddEditProfileView(CustomMethodsMixin, UpdateAPIView):
    template_name = "demonlist/add_edit_profile.html"
    serializer_class = CountryModelSerializer

    permission_classes = [IsAuthenticated, IsListMod]

    # DATA (POST)
    def get_post_data(self):
        """Obtiene los datos del contexto de la solicitud POST."""
        try:
            picture = self.request.FILES["picture"]
        except:
            picture = None

        data = {
            "option": self.request.POST.get("option"),
            "search_filter": self.request.POST.get("search"),
            "previous_profile": self.request.POST.get("previous_profile"),
            "username": self.request.POST.get("username"),
            "new_username": self.request.POST.get("new_username"),
            "picture": picture,
            "country": self.request.POST.get("country"),
            "youtube_channel": self.request.POST.get("youtube_channel"),
            "twitch": self.request.POST.get("twitch"),
            "twitter": self.request.POST.get("twitter"),
            "facebook": self.request.POST.get("facebook"),
        }
        data.update({
            "country_object": self.get_country_object(data["country"]),
        })
        return data
    
    # UTILS (POST)
    def perform_add_profile(self, data):
        """Creación de perfil reclamable."""
        user = User.objects.create(username=data["username"])

        profile = Profile.objects.create(
            user=user,
            country=data["country_object"],
            claimable=True
        )

        profile = self.assign_social_media(data, profile)
        profile = self.assign_profile_picture(data, profile)
        profile.save()
        return profile

    def perform_edit_profile(self, data):
        """Edición de perfil reclamable."""
        user = User.objects.get(profile__id=data["previous_profile"])
        if data["new_username"]:
            user.username = data["new_username"]
        user.save()

        profile = Profile.objects.get(user=user)
        profile.country = data["country_object"]
        profile = self.assign_social_media(data, profile)
        profile = self.assign_profile_picture(data, profile)
        profile.save()
        return profile
    
    # DJANGO METHODS
    def get_context_data(self, **kwargs):
        context = {}
        countries = self.get_countries_without_korea()

        if "text/html" in self.request.accepted_media_type:
            context["countries"] = countries
        else:
            countries_serializer = self.get_serializer_class()(countries, many=True)
            context["countries"] = countries_serializer.data
        return context

    # API METHODS
    def get(self, request, *args, **kwargs):
        """Método Get: Habilita el método Get a la vista."""
        context = self.get_context_data()
        return Response(context)

    def post(self, request):
        """
        Método POST: Maneja las siguientes operaciones:

        - Busca perfiles reclamables por username.
        - Obtiene la info de un perfil reclamable.
        - Agrega un perfil reclamable.
        - Edita un perfil reclamable.
        """

        data = self.get_post_data()

        if data["option"] == "Search":
            players = Profile.objects.filter(claimable=True, user__username__icontains=data["search_filter"])
            players_serializer = ProfileSelect2Serializer(players, many=True)
            return JsonResponse({"results": players_serializer.data})

        if data["option"] == "Get":
            previous_profile = Profile.objects.filter(id=data["previous_profile"])
            profile_serializer = ProfileModelSerializer(previous_profile, many=True)
            return JsonResponse({"results": profile_serializer.data})

        if data["option"] == "Add":
            self.perform_add_profile(data)

        if data["option"] == "Edit":
            self.perform_edit_profile(data)
        
        return HttpResponseRedirect(reverse_lazy('demonlist:check_profiles'))
        

# Vista de la pantalla para Crear una Ruleta
class CreateRouletteView(CustomMethodsMixin, UpdateAPIView):
    """Create Roulette view."""

    template_name = 'roulette/create_roulette.html'
    serializer_class = RouletteModelSerializer

    permission_classes = [IsAuthenticated, IsLimitedRoulette]

    # DATA (POST)
    def get_category(self):
        """
        Si la lista category tienen 'rated' y 'unrated', entonces la category es 'all',
        sino, significa que la lista solo tiene un elemento, por lo tanto, la category
        es este primer elemento.
        """
        category = self.request.POST.getlist("category")
        if "rated" in category and "unrated" in category:
            category = "all"
        else:
            category = category[0]
        return category

    def get_mode_name(self, mode):
        """Obtiene el 'mode name' (el 'mode' de la ruleta "platformer_best_time" tiene el 'mode name' "platformer")."""
        if mode in ["platformer", "classic"]:
            mode_name = mode
        elif mode == "platformer_best_time":
            mode_name = "platformer"
        return mode_name

    def get_creation_roulette_info(self, data):
        """Obtiene los datos que se necesitarán para la creación de la ruleta."""
        if data["mode"] in ["platformer", "platformer_best_time"]:
            if data["category"] == "all":
                demons = Demon.objects.filter(all_position__gte=81, all_position__lte=100, mode=data["mode_name"]).filter(Q(category="rated") | Q(category="unrated")).exclude(all_position__isnull=True)
            elif data["category"] == "rated":
                demons = Demon.objects.filter(rated_position__gte=81, rated_position__lte=100, mode=data["mode_name"], category=data["category"])
            elif data["category"] == "unrated":
                demons = Demon.objects.filter(unrated_position__gte=41, unrated_position__lte=50, mode=data["mode_name"], category=data["category"])
            max_demons = int(data["number_demons"])*5
        elif data["mode"] == "classic":
            if data["category"] == "all":
                demons = Demon.objects.filter(mode=data["mode_name"]).filter(Q(category="rated") | Q(category="unrated")).exclude(all_position__isnull=True)
            else:
                demons = Demon.objects.filter(mode=data["mode_name"], category=data["category"])

            demons = demons.filter(demon_difficulty__in=data["demon_difficulty"])
            if data["extreme_filter"]:
                if "All Extremes" in data["extreme_filter"]:
                    pass
                elif "Extended List" in data["extreme_filter"]:
                    demons = demons.filter(rated_position__lte=200)
                elif "Main List" in data["extreme_filter"]:
                    demons = demons.filter(rated_position__lte=100)
                elif "1-500" in data["extreme_filter"]:
                    demons = demons.filter(rated_position__lte=500)
                elif "1-250" in data["extreme_filter"]:
                    demons = demons.filter(rated_position__lte=250)
                elif "1-150" in data["extreme_filter"]:
                    demons = demons.filter(rated_position__lte=150)
                elif "1-75" in data["extreme_filter"]:
                    demons = demons.filter(rated_position__lte=75)
                elif "1-50" in data["extreme_filter"]:
                    demons = demons.filter(rated_position__lte=50)
                elif "1-25" in data["extreme_filter"]:
                    demons = demons.filter(rated_position__lte=25)
            max_demons = 100
        return demons, max_demons

    def get_post_data(self):
        """Obtiene los datos del contexto de la solicitud POST."""
        data = {
            "name": self.request.POST.get("name"),
            "mode": self.request.POST.get("mode"),
            "ronda": self.request.POST.get("ronda"),
            "category": self.get_category(),
            "demon_difficulty": self.request.POST.getlist("demon_difficulty"),
            "extreme_filter": self.request.POST.getlist("extreme_filter"),
            "number_demons": self.request.POST.get("number_demons"),
        }
        data.update({
            "mode_name": self.get_mode_name(data["mode"]),
        })
        return data
    
    # UTILS (POST)
    def validate_demon_difficulty(self, data):
        """Ejecuta la creación de la ruleta."""
        difficulties = ["Easy demon", "Medium demon", "Hard demon", "Insane demon", "Extreme demon"]
        if data["mode"] == "classic" and not(data["demon_difficulty"] and any(difficulty in difficulties for difficulty in data["demon_difficulty"])):
            return redirect(reverse('demonlist:roulette_menu'))
    
    def perform_create(self, data, max_demons):
        """Ejecuta la creación de la ruleta."""
        # random_number = random.randint(1, len(demons))
        # demon = demons[random_number - 1]
        roulette = Roulette.objects.create(
            name=data["name"],
            mode=data["mode"],
            category=data["category"],
            max_demons=max_demons,
            player=self.request.user.profile
        )
        if data["mode_name"] == "platformer":
            stage = 1
        elif data["mode_name"] == "classic":
            roulette.demon_difficulty=data["demon_difficulty"]
            roulette.extreme_filter=data["extreme_filter"]
            roulette.save()
            stage = None
        # roulette_demon = RouletteDemon.objects.create(
        #     roulette=roulette,
        #     demon=demon,
        #     demon_index=roulette.demons.count(),
        #     stage=stage,
        #     num_level=1
        # )

        # if data["mode"] == "platformer_best_time":
        #     random_number_best_time = random.choice([10, 20, 30, 40, 50, 60, 70, 80, 90, 100, False])
        #     if random_number_best_time:
        #         records = Record.objects.filter(demon=demon, accepted=True).order_by("best_time")
        #         if random_number_best_time > len(records):
        #             best_time = records.last().best_time
        #         else:
        #             best_time = records[random_number_best_time].best_time
        #     else:
        #         best_time = None
        #     roulette_demon.best_time = best_time
        #     roulette_demon.save()
        return roulette

    # DJANGO METHODS
    def get_context_data(self, **kwargs):
        context = {}
        context["view_name"] = "Roulette"
        context["list_words"] = self.list_words
        return context

    # API METHODS
    def get(self, request, *args, **kwargs):
        """Método Get: Habilita el método Get a la vista."""
        context = self.get_context_data()
        return Response(context)

    def post(self, request):
        """Método POST: Maneja la creación de la ruleta."""
        data = self.get_post_data()

        self.validate_demon_difficulty(data)
        demons, max_demons = self.get_creation_roulette_info(data)
        roulette = self.perform_create(data, max_demons)
        if "text/html" in self.request.accepted_media_type:
            return redirect(reverse('demonlist:roulette', kwargs={"pk": roulette.id}))
        else:
            roulette_serializer = self.get_serializer_class()(roulette)
            return JsonResponse(roulette_serializer.data, safe=False)


# Vista de la pantalla de la Ruleta
class RouletteView(CustomMethodsMixin, RetrieveAPIView):
    """Roulette view."""

    template_name = 'roulette/roulette.html'
    queryset = Roulette.objects.all()
    serializer_class = RouletteModelSerializer
    lookup_field = "pk"

    permission_classes = [IsAuthenticated, IsOwnerRoulette]
    
    # DATA (GET)
    def get_demons(self, roulette):
        """Obtiene los demons de la ruleta."""
        return RouletteDemon.objects.filter(roulette=roulette).order_by("demon_index")

    def get_last_demon(self, roulette, demons, highest_percent):
        """Obtiene si el siguiente demon es el último demon de la ruleta o no."""
        last_demon = False

        if roulette.mode == "classic":
            if highest_percent == 99:
                last_demon = True
        elif roulette.mode == "platformer" or roulette.mode == "platformer_best_time":
            if (demons.count() / roulette.max_demons) == 1:
                last_demon = True
        return last_demon

    # DATA (POST)
    def get_num_difficulty(self, roulette, data):
        """
        Obtiene la num_difficulty, que es la división de la cantidad de demons de una ruleta
        entre el 'max_demons' que tenga asignado la ruleta.
        """
        if roulette.mode == "platformer" or roulette.mode == "platformer_best_time":
            num_demons = roulette.demons.count()
        elif roulette.mode == "classic":
            num_demons = self.get_num_demons(data)
        num_difficulty = num_demons / roulette.max_demons
        return num_difficulty

    def get_num_demons(self, data):
        """
        Esta función es para el modo clásico, declara 'num_demons' como el porcentaje actual de
        la ruleta, en caso de no tener porcentaje, significa que es el primer demon de la ruleta.
        """
        if data.get("percentage"):
            num_demons = int(data.get("percentage"))
        else:
            num_demons = 1
        return num_demons

    def get_demons_out_of_roulette_info(self, roulette, num_difficulty, need_stage=False):
        """
        Obtiene la info que se necesitará para obtener los demons que no están en la ruleta,
        esta info se conforma del 'mode_name', el 'range_top' y, si se requiere, la 'stage'.
        """

        if roulette.mode == "platformer" or roulette.mode == "platformer_best_time":
            mode_name = "platformer"
            if num_difficulty < 0.2:
                range_top = [81, 100]
                stage = 1
            elif num_difficulty < 0.4:
                range_top = [61, 80]
                stage = 2
            elif num_difficulty < 0.6:
                range_top = [41, 60]
                stage = 3
            elif num_difficulty < 0.8:
                range_top = [21, 40]
                stage = 4
            elif num_difficulty < 1:
                range_top = [1, 20]
                stage = 5
        else:
            mode_name = roulette.mode
            range_top = None
            stage = None
        if need_stage:
            return mode_name, range_top, stage
        else:
            return mode_name, range_top
    
    def get_demons_out_of_roulette(self, roulette, mode_name, range_top):
        """
        Obtiene los demons que no están en la ruleta y, si se requiere, también la cantidad de
        demons que sí estén en la ruleta.
        """
        if roulette.mode == "platformer" or roulette.mode == "platformer_best_time":
            if roulette.category == "all":
                demons = Demon.objects.filter(all_position__gte=range_top[0], all_position__lte=range_top[1], mode=mode_name).filter(Q(category="rated") | Q(category="unrated")).exclude(level__in=list(roulette.demons.all())).exclude(all_position__isnull=True)
            elif roulette.category == "rated":
                demons = Demon.objects.filter(rated_position__gte=range_top[0], rated_position__lte=range_top[1], mode=mode_name, category=roulette.category).exclude(level__in=list(roulette.demons.all()))
            elif roulette.category == "unrated":
                demons = Demon.objects.filter(unrated_position__gte=math.ceil(range_top[0]/2), unrated_position__lte=range_top[1]//2, mode=mode_name, category=roulette.category).exclude(level__in=list(roulette.demons.all()))
        elif roulette.mode == "classic":
            if roulette.category == "all":
                demons = Demon.objects.filter(mode=roulette.mode).filter(Q(category="rated") | Q(category="unrated")).exclude(level__in=list(roulette.demons.all())).exclude(all_position__isnull=True)
            else:
                demons = Demon.objects.filter(category=roulette.category, mode=roulette.mode).exclude(level__in=list(roulette.demons.all()))
            demons = self.filter_by_demon_difficulty(roulette, demons)
        return demons

    def get_demons_to_spin(self, demons):
        """Obtiene los demons a girar."""
        if len(demons) >= 6:
            num_max_demons = 6
        else:
            num_max_demons = len(demons)

        random_number = random.sample(range(len(demons)), num_max_demons)
        demons_to_spin = [demons[num] for num in random_number]
        return demons_to_spin

    def get_demons_to_spin_info(self, demons_to_spin):
        """Obtiene la info de los demons a girar, como si fuera un serializer."""
        demons_to_spin_info = []
        if self.request.user.profile.roulette_animation:
            for d in demons_to_spin[:6]:  # Limitar a los primeros 6 elementos de demon
                demon_a_girar = {
                    "level": d.level,
                    "level_id": str(d.level_id),
                    "verification_video": d.verification_video,
                    "photo__url": d.photo.url if d.photo else None,
                    "category": d.category,
                    "rated_position": str(d.rated_position),
                    "unrated_position": str(d.unrated_position),
                    "creator": d.creator,
                    "type": d.type,
                    "demon_difficulty": d.demon_difficulty,
                    "stage": "1",
                    "num_level": "1"
                }
                demons_to_spin_info.append(demon_a_girar)
        else:
            demon_a_girar = {
                    "level": demons_to_spin[0].level,
                    "level_id": str(demons_to_spin[0].level_id),
                    "verification_video": demons_to_spin[0].verification_video,
                    "photo__url": demons_to_spin[0].photo.url if demons_to_spin[0].photo else None,
                    "category": demons_to_spin[0].category,
                    "rated_position": str(demons_to_spin[0].rated_position),
                    "unrated_position": str(demons_to_spin[0].unrated_position),
                    "creator": demons_to_spin[0].creator,
                    "type": demons_to_spin[0].type,
                    "demon_difficulty": demons_to_spin[0].demon_difficulty,
                    "stage": "1",
                    "num_level": "1"
                }
            demons_to_spin_info.append(demon_a_girar)
        return demons_to_spin_info

    def get_num_level(self, num_level_demons):
        """
        Obtiene el 'num_level', que varía su definición dependiendo del modo:
        
        - Plataforma: Obtiene el número de nivel del demon actual dentro de su etapa actual.
        - Clásico: Obtiene el número de nivel del demon actual.
        """
        num_level = len(num_level_demons) + 1
        return num_level
    
    def get_num_level_demons(self, roulette, stage):
        """Obtiene los demons que se encuentran en la ruleta."""
        if roulette.mode == "platformer" or roulette.mode == "platformer_best_time":
            num_level_demons = RouletteDemon.objects.filter(roulette=roulette, stage=stage)
        elif roulette.mode == "classic":
            num_level_demons = Demon.objects.filter(level__in=list(roulette.demons.all()))
        return num_level_demons

    # DATA (BOTH)
    def get_highest_percent(self, roulette):
        """Obtiene el porcentaje en el que se encuentra la ruleta actualmente."""
        highest_percent = None
        if roulette.demons.count() == 1:
            highest_percent = 0
        else:
            if roulette.mode == "classic":
                try:
                    roulette_demon_previous = RouletteDemon.objects.get(roulette=roulette, demon_index=(roulette.demons.count() - 2))
                    highest_percent = roulette_demon_previous.percentage
                except:
                    highest_percent = 0
        return highest_percent
    
    # FILTERS
    def filter_by_extreme_filter(self, queryset, extreme_filter):
        """Filtra por las opciones de Extreme demons ('All Extremes', 'Extended List' y 'Main List')."""
        if "All Extremes" not in extreme_filter:
            if "Extended List" in extreme_filter:
                return queryset.filter(rated_position__lte=200)
            elif "Main List" in extreme_filter:
                return queryset.filter(rated_position__lte=100)
            elif "1-500" in extreme_filter:
                return queryset.filter(rated_position__lte=500)
            elif "1-250" in extreme_filter:
                return queryset.filter(rated_position__lte=250)
            elif "1-150" in extreme_filter:
                return queryset.filter(rated_position__lte=150)
            elif "1-75" in extreme_filter:
                return queryset.filter(rated_position__lte=75)
            elif "1-50" in extreme_filter:
                return queryset.filter(rated_position__lte=50)
            elif "1-25" in extreme_filter:
                return queryset.filter(rated_position__lte=25)
        return queryset

    def filter_by_demon_difficulty(self, roulette, demons):
        """Filtra por la dificultad del demon."""
        demon_difficulty = ast.literal_eval(roulette.demon_difficulty)
        extreme_filter = ast.literal_eval(roulette.extreme_filter)

        if demon_difficulty:
            demons = demons.filter(demon_difficulty__in=demon_difficulty)

            if extreme_filter:
                demons = self.filter_by_extreme_filter(demons, extreme_filter)
        return demons
        
    # UTILS (POST)
    def validate_percentage(self, roulette, data, highest_percent):
        """Validar que el porcentaje esté dentro del rango necesario."""
        try:
            percentage = int(data.get("percentage"))
            if percentage:
                if not(highest_percent < percentage <= 100):
                    return HttpResponseRedirect(reverse_lazy('demonlist:roulette', kwargs={'pk': roulette.id}))
        except ValueError:
            return HttpResponseRedirect(reverse_lazy('demonlist:roulette', kwargs={'pk': roulette.id}))
    
    def assign_percentage_to_last_demon_roulette(self, roulette, data):
        """Asigna el porcentaje al último demon de la ruleta (para el modo 'clásico')."""
        try:
            roulette_demon_previous = RouletteDemon.objects.get(roulette=roulette, demon_index=(roulette.demons.count() - 1))

            roulette_demon_previous.percentage = int(data.get("percentage"))
            roulette_demon_previous.save()
        except:
            pass
    
    def perform_add_demon_roulette(self, roulette, data, stage, num_level):
        """Ejecuta la adición de un nuevo demon en la ruleta."""
        demon = Demon.objects.get(level_id=data.get("level_id"))

        """
        Se hace este try except porque a veces el React se buguea y manda doble solicitud, por lo
        cual se creaba doble vez el demon en la ruleta, pero ya con el try except se parchea este error.
        """
        try:
            roulette_demon = RouletteDemon.objects.get(roulette=roulette, demon=demon, demon_index=roulette.demons.count(), stage=stage, num_level=num_level)
        except:
            roulette_demon = RouletteDemon.objects.create(roulette=roulette, demon=demon, demon_index=roulette.demons.count(), stage=stage, num_level=num_level)

        if roulette.mode == "platformer_best_time":
            self.assign_best_time_to_roulette_demon(demon, roulette_demon)
    
    def assign_best_time_to_roulette_demon(self, demon, roulette_demon):
        """Asignar el best time al demon actual (para el modo 'platformer_best_time')."""
        random_number_best_time = random.choice([10, 20, 30, 40, 50, 60, 70, 80, 90, 100, False])

        if random_number_best_time:
            records = Record.objects.filter(demon=demon, accepted=True).order_by("best_time")
            if not(records.exists()):
                best_time = None
            elif random_number_best_time > len(records):
                best_time = records.last().best_time
            else:
                best_time = records[random_number_best_time].best_time
        else:
            best_time = None

        roulette_demon.best_time = best_time
        roulette_demon.save()
        return roulette_demon

    def perform_finish_roulette(self, roulette, data):
        """Ejecuta la finalización de la ruleta."""
        roulette.completed = True
        roulette.save()
        roulette_demon_previous = RouletteDemon.objects.get(roulette=roulette, demon_index=(roulette.demons.count() - 1))
        roulette_demon_previous.percentage = int(data.get("percentage"))
        roulette_demon_previous.save()
    
    # DJANGO METHODS
    def get_context_data(self, **kwargs):
        context = {}

        roulette = self.get_object()
        if not(roulette.active):
            raise Http404()

        if "text/html" in self.request.accepted_media_type:
            context = {
                "roulette": roulette
            }
        else:
            roulette_serializer = self.get_serializer_class()(roulette)
            demons = self.get_demons(roulette)
            highest_percent = self.get_highest_percent(roulette)
            last_demon = self.get_last_demon(roulette, demons, highest_percent)

            context = {
                "roulette": roulette_serializer.data,
                'fast_animation': self.request.user.profile.fast_animation,
                'demons': list(demons.values("demon__photo", "demon__level", "demon__creator", "demon__level_id", "demon__type", "demon__demon_difficulty", "stage", "num_level", "percentage", "best_time")),
                'highest_percent': highest_percent,
                'number_demons': demons.count(),
                'max_demons': roulette.max_demons,
                'complete': roulette.completed,
                'mode': roulette.mode,
                'last_demon': last_demon,
                'media_url': self.request.global_context["MEDIA_URL"],
                'aspect_mode': "dark" if self.request.global_context["dark_mode"] else "light",
                'background': "#14141A" if self.request.global_context["dark_mode"] else "#ebf0f7",
            }
        context["view_name"] = "Roulette"
        context["list_words"] = self.list_words
        return context

    # API METHODS
    def get(self, request, *args, **kwargs):
        """Método Get: Habilita el método Get a la vista."""
        context = self.get_context_data()
        return Response(context)
    
    def post(self, request, pk):
        """
        Método POST: Maneja las siguientes operaciones:

        - Obtiene la info de los niveles que se girarán en la ruleta.
        - Agrega un nivel a la ruleta.
        - Finaliza la ruleta.
        """
        
        data = request.data

        roulette = self.get_object()
        if not(roulette.active):
            raise Http404("La página que buscas no existe")

        if data.get("get_levels"):

            num_difficulty = self.get_num_difficulty(roulette, data)
            if num_difficulty != 1:
                mode_name, range_top = self.get_demons_out_of_roulette_info(roulette, num_difficulty)
                demons = self.get_demons_out_of_roulette(roulette, mode_name, range_top)
                if demons.exists():
                    demons_to_spin = self.get_demons_to_spin(demons)
                    demons_to_spin_info = self.get_demons_to_spin_info(demons_to_spin)
                    return JsonResponse(demons_to_spin_info, safe=False)
            roulette_serializer = self.get_serializer_class()(roulette)
            return JsonResponse(roulette_serializer.data, safe=False)
        elif data.get("level_id"):

            if roulette.mode == "classic":
                highest_percent = self.get_highest_percent(roulette)
                self.validate_percentage(roulette, data, highest_percent)

            num_difficulty = self.get_num_difficulty(roulette, data)
            mode_name, range_top, stage = self.get_demons_out_of_roulette_info(roulette, num_difficulty, need_stage=True)

            num_level_demons = self.get_num_level_demons(roulette, stage)
            if roulette.mode == "classic":
                self.assign_percentage_to_last_demon_roulette(roulette, data)

            num_level = self.get_num_level(num_level_demons)
            self.perform_add_demon_roulette(roulette, data, stage, num_level)
            roulette_serializer = self.get_serializer_class()(roulette)
            return JsonResponse(roulette_serializer.data, safe=False)
    
        elif data.get("gg"):
            self.perform_finish_roulette(roulette, data)
            return JsonResponse({"gg": True}, safe=False)

# Vista de la pantalla del Menú la Ruleta
class RouletteMenuView(CustomMethodsMixin, GenericAPIView):
    """Roulette Menu view."""

    template_name = 'roulette/roulette_menu.html'
    serializer_class = RouletteModelSerializer

    # DATA (GET)
    def get_roulettes(self):
        """Obtiene todas las ruletas del usuario logueado."""
        if not(self.request.user.is_anonymous):
            roulettes = Roulette.objects.filter(Q(player=self.request.user.profile) | Q(players_to_share__in=[self.request.user.profile])).order_by("id").distinct()
            if not(self.request.global_context["is_subscriber"]):
                roulettes = roulettes[:2]
        else:
            roulettes = None
        return roulettes

    # DATA (POST)
    def get_followers(self, data):
        """
        Obtiene los seguidores del usuario logueado, además, les hace un annotate para
        saber si están dentro de la ruleta o no.
        """
        roulette_players = Roulette.objects.get(id=data["id"]).players_to_share.all()
        followers = self.request.user.profile.followers.annotate(
            in_roulette=Case(
                When(id__in=roulette_players, then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            ))
        if data["search_user"]:
            followers = followers.filter(user__username__icontains=data["search_user"])
        return followers
    
    def get_follower_and_player_roulettes(self, data):
        """
        Obtiene el perfil del follower según el id del follower y también obtiene
        las ruletas de este follower.
        """
        follower = Profile.objects.get(id=data["follower"])
        player_roulettes = Roulette.objects.filter(Q(player=follower) | Q(players_to_share__in=[follower])).distinct()
        return follower, player_roulettes

    def get_roulette(self, id):
        """Obtiene un objeto de ruleta según su id."""
        if id:
            return Roulette.objects.get(id=id)
        return None
    
    def get_post_data(self):
        """Obtiene los datos del contexto de la solicitud POST."""
        data = {
            "option": self.request.POST.get("option"),
            "id": self.request.POST.get("id"),
            "follower": self.request.POST.get("follower", None),
            "search_user": self.request.POST.get("user", None)
        }
        data.update({
            "roulette": self.get_roulette(data["id"]),
        })
        return data

    # UTILS (POST)
    def perform_delete(self, data):
        """Ejecuta la eliminación de una ruleta."""
        data["roulette"].delete()

    def perform_get_out(self, data):
        """Ejecuta la acción de salirse de una ruleta."""
        data["roulette"].players_to_share.remove(self.request.user.profile)
    
    def perform_share(self, data):
        """Ejecuta la acción de compartir una ruleta."""
        follower, player_roulettes = self.get_follower_and_player_roulettes(data)

        if player_roulettes.count() >= 2:
            messages.error(self.request, "This follower currently possesses two roulettes in their account. The maximum limit for roulettes per account is two.")
        else:
            data["roulette"].players_to_share.add(follower)
        return follower, data["roulette"]

    def perform_unshare(self, data):
        """Ejecuta la acción de dejar de compartir una ruleta."""
        follower = Profile.objects.get(id=data["follower"])
        data["roulette"].players_to_share.remove(follower)
        return follower, data["roulette"]

    def handle_create_notificacion(self, follower, roulette):
        """Maneja la notificación creada."""
        Notification.objects.create(
            profile=follower,
            action="roulette_shared",
            parameter=roulette.name,
            option="Profile",
            id_roulette_parameter=roulette.id,
            profile_parameter=self.request.user.profile
        )

    def handle_delete_notificacion(self, follower, roulette):
        """Maneja la notificación eliminada."""
        try:
            notification = Notification.objects.get(profile=follower,
                                action="roulette_shared",
                                parameter=roulette.name,
                                option="Profile",
                                id_roulette_parameter=roulette.id,
                                profile_parameter=self.request.user.profile
                                )
            notification.delete()
        except:
            pass

    # DJANGO METHODS
    def get_context_data(self, **kwargs):
        context = {}

        roulettes = self.get_roulettes()

        if "text/html" in self.request.accepted_media_type:
            context['roulettes'] = roulettes
        else:
            roulettes_serializer = self.get_serializer_class()(roulettes, many=True)
            context['roulettes'] = roulettes_serializer.data
        context["view_name"] = "Roulette"
        context['list_words'] = self.list_words
        return context

    # API METHODS
    def get(self, request, *args, **kwargs):
        """Método Get: Habilita el método Get a la vista."""
        context = self.get_context_data()
        return Response(context)
    
    def post(self, request):
        """
        Método POST: Maneja las siguientes operaciones:

        - Filtra seguidores.
        - Elimina una ruleta.
        - Te saca de una ruleta compartida.
        - Comparte la ruleta.
        - Deja de compartir la ruleta.
        """

        data = self.get_post_data()

        if data["option"] == "filter_followers":
            followers = self.get_followers(data)
            followers_serializer = ProfileRouletteModelSerializer(followers, many=True)
            return JsonResponse(followers_serializer.data, safe=False)
        elif data["option"] == "delete":
            self.perform_delete(data)
            roulette_serializer = self.get_serializer_class()(data["roulette"])
            return JsonResponse(roulette_serializer.data, safe=False)
        elif data["option"] == "get_out":
            self.perform_get_out(data)
            roulette_serializer = self.get_serializer_class()(data["roulette"])
            return JsonResponse(roulette_serializer.data, safe=False)
        elif data["option"] == "share":
            follower, roulette = self.perform_share(data)
            self.handle_create_notificacion(follower, roulette)
            return HttpResponseRedirect(reverse_lazy('demonlist:roulette_menu'))
        elif data["option"] == "unshare":
            follower, roulette = self.perform_unshare(data)
            self.handle_delete_notificacion(follower, roulette)
            return HttpResponseRedirect(reverse_lazy('demonlist:roulette_menu'))

class LevelPacksView(CustomMethodsMixin, ListAPIView):
    template_name = "demonlist/level_packs.html"
    serializer_class = DemonModelSerializer
    paginate_by = 50

    # DATA (GET)
    def get_category_and_mode(self):
        """Obtiene el campo categoria y modo."""
        category = self.kwargs.get("category", "rated")
        category = "all_demonlist" if category == "demons" else category
        mode = self.kwargs.get("mode") or ("platformer" if not(category in ["all_demonlist", "future"]) else None)
        if category == "pemonlist":
            mode, category = "platformer", "rated"
        elif category == "platformer_challengelist":
            mode, category = "platformer", "challenge"
        elif category == "tiny_demonlist":
            mode, category = "classic", "tiny"
        elif category == "platformer_deathlesslist":
            mode, category = "platformer", "deathless"
        elif category == "impossible_platformerlist":
            mode, category = "platformer", "impossible"
        elif category == "spam_challengelist":
            mode, category = "classic", "spam"
        elif category == "impossible_tiny_list":
            mode, category = "classic", "impossible_tiny"
        elif category == "tiny_pemonlist":
            mode, category = "platformer", "tiny"
        elif category == "tpl":
            mode, category = "platformer", "all"
        return category, mode

    def get_level_packs(self, mode, category):
        """Obtiene los level packs del mode y category en el que estás."""
        return LevelPack.objects.filter(mode=mode, category=category).order_by('color_index', "id")

    def get_demons_beaten(self, mode, category):
        """Obtiene los demons que ya he hayas pasado."""
        if not(self.request.user.is_anonymous):
            demons_beaten = Record.objects.filter(player=self.request.user.profile, demon__mode=mode, demon__category=category).values_list("demon__id", flat=True)
        else:
            demons_beaten = None
        return demons_beaten

    def get_data(self):
        """Obtiene los datos del contexto de la solicitud GET."""
        category, mode = self.get_category_and_mode()

        data = {
            "mode": mode,
            "category": category,
        }
        data.update({
            "level_packs": self.get_level_packs(data["mode"], data["category"]),
            "demons_beaten": self.get_demons_beaten(data["mode"], data["category"]),
        })
        return data

    # DJANGO METHODS
    def get_context_data(self, data, **kwargs):
        context = {}
            
        context.update({
            "level_packs": data["level_packs"],
            "demons_beaten": data["demons_beaten"],
            "mode": data["mode"],
            "category": data["category"],
            "view_name": "Collab"
        })
        return context

    # API METHODS
    def get(self, request, *args, **kwargs):
        """Método Get: Habilita el método Get a la vista."""
        data = self.get_data()
        context = self.get_context_data(data)
        return Response(context)
