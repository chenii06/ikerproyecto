"""Demon List views."""

# Django
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import user_passes_test
from django.core.files.images import ImageFile
from django.core.mail import send_mail, EmailMultiAlternatives
from django.db.models import F, Window, Sum, Case, When, CharField, Value, ExpressionWrapper, Func, IntegerField, BooleanField, Q, OuterRef, Subquery, Count
from django.db.models.functions import Rank, Cast
from django.http import HttpResponseRedirect
from django.http.response import JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.html import strip_tags
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, DetailView, ListView, TemplateView
from django_cte import CTEManager, With

# Django REST Framework
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

# Forms
from apps.users import forms

# Mixins
from utils.mixins import CustomMethodsMixin

# Models
from django.contrib.auth.models import User
from apps.demonlist.models import Demon, Record, Changelog
from apps.users.models import Profile, Country, Notification, Team

# Utils
import ast
from utils.constants import list_choices

# Serializers
from apps.users.serializers import ProfileModelSerializer


# Translations
from utils import translations

# Vista de los Guidelines
class GuidelinesView(CustomMethodsMixin, APIView):
    template_name = 'guidelines.html'
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]
    
    # DJANGO METHODS
    def get_context_data(self, **kwargs):
        context = {}

        context["list_words"] = self.list_words
        return context

    # API METHODS
    def get(self, request, *args, **kwargs):
        """Método Get: Habilita el método Get a la vista."""
        context = self.get_context_data()
        return Response(context)


# Vista de los Términos y Condiciones
class TermsView(CustomMethodsMixin, APIView):
    template_name = 'terms.html'
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]
    
    # DJANGO METHODS
    def get_context_data(self, **kwargs):
        context = {}

        context["list_words"] = self.list_words
        return context

    # API METHODS
    def get(self, request, *args, **kwargs):
        """Método Get: Habilita el método Get a la vista."""
        context = self.get_context_data()
        return Response(context)


# Vista de los Créditos
class CreditsView(CustomMethodsMixin, GenericAPIView):
    template_name = 'credits.html'
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]
    serializer_class = ProfileModelSerializer

    # DJANGO METHODS
    def get_context_data(self, **kwargs):
        context = {}

        queryset = Profile.objects.filter(platformer_list_points__gte=0).annotate(
                position=Window(expression=Rank(), order_by=F("platformer_list_points").desc())
            ).order_by(f"-platformer_list_points")

        profiles = With(queryset).queryset().with_cte(With(queryset)).filter(
            id__in=[378, 388, 529, 1901, 2706, 3267, 4509, 5429, 5503, 5522, 6861, 6863, 6894]
        ).order_by(
            Case(
                When(id=388, then=Value(0)),
                When(id=6863, then=Value(1)),
                When(id=3267, then=Value(2)),
                When(id=4509, then=Value(3)),
                When(id=6861, then=Value(4)),
                When(id=6894, then=Value(5)),
                When(id=529, then=Value(6)),
                When(id=378, then=Value(7)),
                When(id=1901, then=Value(8)),
                When(id=5429, then=Value(9)),
                When(id=2706, then=Value(10)),
                When(id=5522, then=Value(11)),
                When(id=5503, then=Value(12)),
                output_field=IntegerField(),
            )
        )

        if "text/html" in self.request.accepted_media_type:
            context["profiles"] = profiles
        else:
            profiles_serializer = self.get_serializer_class()(profiles, many=True)
            context["profiles"] = profiles_serializer.data
        context["list_words"] = self.list_words
        return context

    # API METHODS
    def get(self, request, *args, **kwargs):
        """Método Get: Habilita el método Get a la vista."""
        context = self.get_context_data()
        return Response(context)


# Vista para el Settings
class SettingsView(CustomMethodsMixin, APIView):
    template_name = 'settings.html'
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]
    permission_classes = [IsAuthenticated]

    # DATA (POST)
    def get_post_data(self):
        return {
            "dark_mode": self.request.POST.get("dark_mode"),
            "roulette_animation": self.request.POST.get("roulette_animation"),
            "fast_animation": self.request.POST.get("fast_animation"),
            "default_submit_record": self.request.POST.get("default_submit_record"),
            "default_stats_viewer": self.request.POST.get("default_stats_viewer"),
        }
    
    # DJANGO METHODS
    def get_context_data(self, **kwargs):
        context = {}
        context["list_words"] = self.list_words
        return context

    # API METHODS
    def get(self, request, *args, **kwargs):
        """Método Get: Habilita el método Get a la vista."""
        context = self.get_context_data()
        return Response(context)

    def post(self, request, *args, **kwargs):
        data = self.get_post_data()
        user = self.request.user
        profile = user.profile

        if data["dark_mode"]:
            profile.dark_mode = True
        else:
            profile.dark_mode = False

        if data["roulette_animation"]:
            profile.roulette_animation = True
        else:
            profile.roulette_animation = False

        if data["fast_animation"]:
            profile.fast_animation = True
        else:
            profile.fast_animation = False

        if data["default_submit_record"]:
            valid_choices = [choice[0] for choice in list_choices]
            if data["default_submit_record"] in valid_choices:
                profile.default_submit_record = data["default_submit_record"]
            else:
                profile.default_submit_record = None
        else:
            profile.default_submit_record = None

        if data["default_stats_viewer"]:
            valid_choices = [choice[0] for choice in list_choices]
            if data["default_stats_viewer"] in valid_choices:
                profile.default_stats_viewer = data["default_stats_viewer"]
            else:
                profile.default_stats_viewer = None
        else:
            profile.default_stats_viewer = None

        profile.save()

        if "text/html" in self.request.accepted_media_type:
            return HttpResponseRedirect(reverse_lazy("settings"))

        else:
            return Response({'list_words': self.list_words})

class CustomPasswordResetView(auth_views.PasswordResetView):
    html_email_template_name = "users/reset/email_content.html"
    template_name = "users/reset/password_reset/password_reset.html"
    form_class = forms.PasswordResetForm
    subject_template_name = "users/reset/email_subject.html"
    success_url = reverse_lazy("password_reset_done")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        language = "English"

        if not(self.request.user.is_anonymous):
            language = self.request.user.profile.language
   
        list_words = translations.reset_password_translation(language)

        context["list_words"] = list_words
        return context
    
class CustomPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name="users/reset/password_reset/password_reset_done.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        language = "English"

        if not(self.request.user.is_anonymous):
            language = self.request.user.profile.language
   
        list_words = translations.reset_password_translation(language)

        context["list_words"] = list_words
        return context

class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = "users/reset/password_reset/password_reset_confirm.html"
    form_class = forms.SetPasswordForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        language = "English"

        if not(self.request.user.is_anonymous):
            language = self.request.user.profile.language
   
        list_words = translations.reset_password_translation(language)

        context["list_words"] = list_words
        return context
    
class CustomPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = "users/reset/password_reset/password_reset_complete.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        language = "English"

        if not(self.request.user.is_anonymous):
            language = self.request.user.profile.language
   
        list_words = translations.reset_password_translation(language)

        context["list_words"] = list_words
        return context

class CustomEmailResetView(auth_views.PasswordResetView):
    html_email_template_name = "users/reset/email_content.html"
    template_name = "users/reset/email_reset/email_reset.html"
    form_class = forms.EmailResetForm
    subject_template_name = "users/reset/email_subject.html"
    success_url = reverse_lazy("email_reset_done")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        language = "English"

        if not(self.request.user.is_anonymous):
            language = self.request.user.profile.language
   
        list_words = translations.reset_email_translation(language)

        context["list_words"] = list_words
        return context
    
class CustomEmailResetDoneView(auth_views.PasswordResetDoneView):
    template_name="users/reset/email_reset/email_reset_done.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        language = "English"

        if not(self.request.user.is_anonymous):
            language = self.request.user.profile.language
   
        list_words = translations.reset_email_translation(language)

        context["list_words"] = list_words
        return context

class CustomEmailResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = "users/reset/email_reset/email_reset_confirm.html"
    form_class = forms.SetEmailForm
    success_url = reverse_lazy("email_reset_complete")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        language = "English"

        if not(self.request.user.is_anonymous):
            language = self.request.user.profile.language
   
        list_words = translations.reset_email_translation(language)

        context["list_words"] = list_words
        return context
    
class CustomEmailResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = "users/reset/email_reset/email_reset_complete.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        language = "English"

        if not(self.request.user.is_anonymous):
            language = self.request.user.profile.language
   
        list_words = translations.reset_email_translation(language)
        context["list_words"] = list_words
        return context

