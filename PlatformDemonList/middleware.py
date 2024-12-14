"""Platformdemon list middleware catalog."""

# Django
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import F, Window, Sum, Case, When, CharField, Value, ExpressionWrapper, Func, IntegerField, BooleanField, Q
from django.http import HttpResponsePermanentRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin

# Django REST Framework
from rest_framework.exceptions import AuthenticationFailed

# Models
from django.contrib.auth.models import User, Group
from apps.users.models import Profile, Country, Notification
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import RefreshToken

# Utils
import jwt
from re import sub
from utils import translations

# Utils (Custom)
from utils.constants import hispanic_countries


class RedirectMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host()
        if host.startswith('www.demonlist.com'):
            new_url = request.build_absolute_uri().replace('www.demonlist.com', 'demonlist.com', 1)
            return HttpResponsePermanentRedirect(new_url)
        response = self.get_response(request)
        return response

class CustomAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        access_token = request.COOKIES.get('access_token')
        if access_token:
            header_token = f'Bearer {access_token}'
            request.META['HTTP_AUTHORIZATION'] = header_token

            try:
                token = header_token.split(' ')[1]
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                user = get_user_model().objects.get(id=payload['user_id'])
                request.user = user
            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, get_user_model().DoesNotExist):
                raise AuthenticationFailed('Invalid or expired token')

class MethodOverrideMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'POST' and '_method' in request.POST:
            request.method = request.POST['_method']
        response = self.get_response(request)
        return response

class GlobalContextMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        global_context = {}


        # if request.path != reverse('demonlist:countdown_timer') and not(request.build_absolute_uri()[:38] == "https://chuckygd24.pythonanywhere.com/"):
        #     return HttpResponseRedirect(reverse('demonlist:countdown_timer'))

        language = request.user.profile.language if not request.user.is_anonymous else "English"
        dark_mode = request.user.profile.dark_mode if not request.user.is_anonymous else True

        if not request.user.is_anonymous:

            notifications = Notification.objects.filter(profile=request.user.profile).order_by("-created")
            notifications_unreaden = notifications.filter(read=False).count()
            for notification in notifications[100:]:
                notification.delete()

            global_context["notifications"] = notifications
            global_context["notifications_unreaden"] = notifications_unreaden

            is_list_admin = False
            is_list_leader = False
            is_list_editor = False
            is_list_helper = False

            is_classic_list_leader = False
            is_platformer_list_leader = False
            is_classic_list_helper = False
            is_platformer_list_helper = False

            is_rated_list_leader = False
            is_unrated_list_leader = False
            is_challenge_list_leader = False
            is_shitty_list_leader = False
            is_future_list_leader = False
            is_tiny_list_leader = False
            is_deathless_list_leader = False
            is_impossible_list_leader = False
            is_spam_list_leader = False
            is_impossible_tiny_list_leader = False
            is_all_list_leader = False
            is_rated_list_helper = False
            is_unrated_list_helper = False
            is_challenge_list_helper = False
            is_shitty_list_helper = False
            is_tiny_list_helper = False
            is_deathless_list_helper = False
            is_impossible_list_helper = False
            is_spam_list_helper = False
            is_impossible_tiny_list_helper = False
            is_all_list_helper = False

            is_subscriber = False

            is_gd_lucky_leader = False

            list_admin_group = Group.objects.filter(name__in=[
                    'List Admin',
                ])
            if request.user.groups.filter(pk__in=list_admin_group.values_list('pk', flat=True)).exists():
                is_list_admin = True

            list_leader_group = Group.objects.filter(name__in=[
                    'List Admin',
                    'Classic Rated List Leader',
                    'Classic Unrated List Leader',
                    'Classic Tiny List Leader',
                    'Classic Shitty List Leader',
                    'Classic Spam List Leader',
                    'Classic Impossible Tiny List Leader',
                    'Platformer Rated List Leader',
                    'Platformer Unrated List Leader',
                    'Platformer Challenge List Leader',
                    'Platformer Deathless List Leader',
                    'Platformer Impossible List Leader',
                    'Platformer Tiny List Leader',
                    'TPL List Leader',
                ])
            if request.user.groups.filter(pk__in=list_leader_group.values_list('pk', flat=True)).exists():
                is_list_leader = True

            list_editor_group = Group.objects.filter(name__in=[
                    'List Admin',
                    'All DemonList Editor'
                ])
            if request.user.groups.filter(pk__in=list_editor_group.values_list('pk', flat=True)).exists():
                is_list_editor = True

            list_helper_groups = Group.objects.filter(name__in=[
                    'List Admin',
                    'Classic Rated List Leader',
                    'Classic Unrated List Leader',
                    'Classic Tiny List Leader',
                    'Classic Shitty List Leader',
                    'Classic Spam List Leader',
                    'Classic Impossible Tiny List Leader',
                    'Platformer Rated List Leader',
                    'Platformer Unrated List Leader',
                    'Platformer Challenge List Leader',
                    'Platformer Deathless List Leader',
                    'Platformer Impossible List Leader',
                    'Platformer Tiny List Leader',
                    'TPL List Leader',
                    'All DemonList Editor',
                    'Classic Rated List Helper',
                    'Classic Unrated List Helper',
                    'Classic Tiny List Helper',
                    'Classic Spam List Helper',
                    'Classic Impossible Tiny List Helper',
                    'Platformer Rated List Helper',
                    'Platformer Unrated List Helper',
                    'Platformer Challenge List Helper',
                    'Platformer Deathless List Helper',
                    'Platformer Impossible List Helper',
                    'Platformer Tiny List Helper',
                    'TPL List Helper',
                ])
            if request.user.groups.filter(pk__in=list_helper_groups.values_list('pk', flat=True)).exists():
                is_list_helper = True

            classic_list_leader_group = Group.objects.filter(name__in=[
                    'List Admin',
                    'Classic Rated List Leader',
                    'Classic Unrated List Leader',
                    'Classic Tiny List Leader',
                    'Classic Shitty List Leader',
                    'Classic Spam List Leader',
                    'Classic Impossible Tiny List Leader',
                ])
            if request.user.groups.filter(pk__in=classic_list_leader_group.values_list('pk', flat=True)).exists():
                is_classic_list_leader = True

            platformer_list_leader_group = Group.objects.filter(name__in=[
                    'List Admin',
                    'Platformer Rated List Leader',
                    'Platformer Unrated List Leader',
                    'Platformer Challenge List Leader',
                    'Platformer Deathless List Leader',
                    'Platformer Impossible List Leader',
                    'Platformer Tiny List Leader',
                    'TPL List Leader',
                ])
            if request.user.groups.filter(pk__in=platformer_list_leader_group.values_list('pk', flat=True)).exists():
                is_platformer_list_leader = True

            classic_list_helper_group = Group.objects.filter(name__in=[
                    'List Admin',
                    'Classic Rated List Leader',
                    'Classic Unrated List Leader',
                    'Classic Tiny List Leader',
                    'Classic Shitty List Leader',
                    'Classic Spam List Leader',
                    'Classic Impossible Tiny List Leader',
                    'Classic Rated List Helper',
                    'Classic Unrated List Helper',
                    'Classic Tiny List Helper',
                    'Classic Spam List Helper',
                    'Classic Impossible Tiny List Helper',
                    'All DemonList Editor'
                ])
            if request.user.groups.filter(pk__in=classic_list_helper_group.values_list('pk', flat=True)).exists():
                is_classic_list_helper = True

            platformer_list_helper_group = Group.objects.filter(name__in=[
                    'List Admin',
                    'Platformer Rated List Leader',
                    'Platformer Unrated List Leader',
                    'Platformer Challenge List Leader',
                    'Platformer Deathless List Leader',
                    'Platformer Impossible List Leader',
                    'Platformer Tiny List Leader',
                    'TPL List Leader',
                    'Platformer Rated List Helper',
                    'Platformer Unrated List Helper',
                    'Platformer Challenge List Helper',
                    'Platformer Deathless List Helper',
                    'Platformer Impossible List Helper',
                    'Platformer Tiny List Helper',
                    'TPL List Helper',
                    'All DemonList Editor'
                ])
            if request.user.groups.filter(pk__in=platformer_list_helper_group.values_list('pk', flat=True)).exists():
                is_platformer_list_helper = True

            rated_list_leader_group = Group.objects.filter(name__in=[
                    'List Admin',
                    'Classic Rated List Leader',
                    'Platformer Rated List Leader',
                ])
            if request.user.groups.filter(pk__in=rated_list_leader_group.values_list('pk', flat=True)).exists():
                is_rated_list_leader = True

            unrated_list_leader_group = Group.objects.filter(name__in=[
                    'List Admin',
                    'Classic Unrated List Leader',
                    'Platformer Unrated List Leader',
                ])
            if request.user.groups.filter(pk__in=unrated_list_leader_group.values_list('pk', flat=True)).exists():
                is_unrated_list_leader = True

            challenge_list_leader_group = Group.objects.filter(name__in=[
                    'List Admin',
                    'Platformer Challenge List Leader',
                ])
            if request.user.groups.filter(pk__in=challenge_list_leader_group.values_list('pk', flat=True)).exists():
                is_challenge_list_leader = True

            shitty_list_leader_group = Group.objects.filter(name__in=[
                    'List Admin',
                    'Classic Shitty List Leader',
                ])
            if request.user.groups.filter(pk__in=shitty_list_leader_group.values_list('pk', flat=True)).exists():
                is_shitty_list_leader = True

            future_list_leader_group = Group.objects.filter(name__in=[
                    'List Admin',
                    'Future List Leader',
                ])
            if request.user.groups.filter(pk__in=future_list_leader_group.values_list('pk', flat=True)).exists():
                is_future_list_leader = True

            tiny_list_leader_group = Group.objects.filter(name__in=[
                    'List Admin',
                    'Classic Tiny List Leader',
                    'Platformer Tiny List Leader',
                ])
            if request.user.groups.filter(pk__in=tiny_list_leader_group.values_list('pk', flat=True)).exists():
                is_tiny_list_leader = True

            deathless_list_leader_group = Group.objects.filter(name__in=[
                    'List Admin',
                    'Platformer Deathless List Leader',
                ])
            if request.user.groups.filter(pk__in=deathless_list_leader_group.values_list('pk', flat=True)).exists():
                is_deathless_list_leader = True

            impossible_list_leader_group = Group.objects.filter(name__in=[
                    'List Admin',
                    'Platformer Impossible List Leader',
                ])
            if request.user.groups.filter(pk__in=impossible_list_leader_group.values_list('pk', flat=True)).exists():
                is_impossible_list_leader = True

            spam_list_leader_group = Group.objects.filter(name__in=[
                    'List Admin',
                    'Classic Spam List Leader',
                ])
            if request.user.groups.filter(pk__in=spam_list_leader_group.values_list('pk', flat=True)).exists():
                is_spam_list_leader = True

            impossible_tiny_list_leader_group = Group.objects.filter(name__in=[
                    'List Admin',
                    'Classic Impossible Tiny List Leader',
                ])
            if request.user.groups.filter(pk__in=impossible_tiny_list_leader_group.values_list('pk', flat=True)).exists():
                is_impossible_tiny_list_leader = True

            all_list_leader_group = Group.objects.filter(name__in=[
                    'List Admin',
                    'TPL List Leader',
                ])
            if request.user.groups.filter(pk__in=all_list_leader_group.values_list('pk', flat=True)).exists():
                is_all_list_leader = True

            rated_list_helper_group = Group.objects.filter(name__in=[
                    'List Admin',
                    'Classic Rated List Leader',
                    'Platformer Rated List Leader',
                    'Classic Rated List Helper',
                    'Platformer Rated List Helper',
                    'All DemonList Editor'
                ])
            if request.user.groups.filter(pk__in=rated_list_helper_group.values_list('pk', flat=True)).exists():
                is_rated_list_helper = True

            unrated_list_helper_group = Group.objects.filter(name__in=[
                    'List Admin',
                    'Classic Unrated List Leader',
                    'Platformer Unrated List Leader',
                    'Classic Unrated List Helper',
                    'Platformer Unrated List Helper',
                ])
            if request.user.groups.filter(pk__in=unrated_list_helper_group.values_list('pk', flat=True)).exists():
                is_unrated_list_helper = True

            challenge_list_helper_group = Group.objects.filter(name__in=[
                    'List Admin',
                    'Platformer Challenge List Leader',
                    'Platformer Challenge List Helper',
                ])
            if request.user.groups.filter(pk__in=challenge_list_helper_group.values_list('pk', flat=True)).exists():
                is_challenge_list_helper = True

            shitty_list_helper_group = Group.objects.filter(name__in=[
                    'List Admin',
                    'Classic Shitty List Leader',
                    'Classic Shitty List Helper',
                ])
            if request.user.groups.filter(pk__in=shitty_list_helper_group.values_list('pk', flat=True)).exists():
                is_shitty_list_helper = True

            tiny_list_helper_group = Group.objects.filter(name__in=[
                    'List Admin',
                    'Classic Tiny List Leader',
                    'Classic Tiny List Helper',
                    'Platformer Tiny List Leader',
                    'Platformer Tiny List Helper',
                ])
            if request.user.groups.filter(pk__in=tiny_list_helper_group.values_list('pk', flat=True)).exists():
                is_tiny_list_helper = True

            deathless_list_helper_group = Group.objects.filter(name__in=[
                    'List Admin',
                    'Platformer Deathless List Leader',
                    'Platformer Deathless List Helper',
                ])
            if request.user.groups.filter(pk__in=deathless_list_helper_group.values_list('pk', flat=True)).exists():
                is_deathless_list_helper = True

            impossible_list_helper_group = Group.objects.filter(name__in=[
                    'List Admin',
                    'Platformer Impossible List Leader',
                    'Platformer Impossible List Helper',
                ])
            if request.user.groups.filter(pk__in=impossible_list_helper_group.values_list('pk', flat=True)).exists():
                is_impossible_list_helper = True

            spam_list_helper_group = Group.objects.filter(name__in=[
                    'List Admin',
                    'Classic Spam List Leader',
                    'Classic Spam List Helper',
                ])
            if request.user.groups.filter(pk__in=spam_list_helper_group.values_list('pk', flat=True)).exists():
                is_spam_list_helper = True

            impossible_tiny_list_helper_group = Group.objects.filter(name__in=[
                    'List Admin',
                    'Classic Impossible Tiny List Leader',
                    'Classic Impossible Tiny List Helper',
                ])
            if request.user.groups.filter(pk__in=impossible_tiny_list_helper_group.values_list('pk', flat=True)).exists():
                is_impossible_tiny_list_helper = True

            all_list_helper_group = Group.objects.filter(name__in=[
                    'List Admin',
                    'TPL List Leader',
                    'TPL List Helper',
                ])
            if request.user.groups.filter(pk__in=all_list_helper_group.values_list('pk', flat=True)).exists():
                is_all_list_helper = True

            subscriber_group = Group.objects.filter(name__in=[
                    'Subscriber',
                ])
            if request.user.groups.filter(pk__in=subscriber_group.values_list('pk', flat=True)).exists():
                is_subscriber = True

            gd_lucky_leader_group = Group.objects.filter(name__in=[
                    'GD Lucky Leader',
                ])
            if request.user.groups.filter(pk__in=gd_lucky_leader_group.values_list('pk', flat=True)).exists():
                is_gd_lucky_leader = True


            global_context["is_list_admin"] = is_list_admin
            global_context["is_list_leader"] = is_list_leader
            global_context["is_list_editor"] = is_list_editor
            global_context["is_list_helper"] = is_list_helper

            global_context["is_classic_list_leader"] = is_classic_list_leader
            global_context["is_platformer_list_leader"] = is_platformer_list_leader
            global_context["is_classic_list_helper"] = is_classic_list_helper
            global_context["is_platformer_list_helper"] = is_platformer_list_helper

            global_context["is_rated_list_leader"] = is_rated_list_leader
            global_context["is_unrated_list_leader"] = is_unrated_list_leader
            global_context["is_challenge_list_leader"] = is_challenge_list_leader
            global_context["is_shitty_list_leader"] = is_shitty_list_leader
            global_context["is_future_list_leader"] = is_future_list_leader
            global_context["is_tiny_list_leader"] = is_tiny_list_leader
            global_context["is_deathless_list_leader"] = is_deathless_list_leader
            global_context["is_impossible_list_leader"] = is_impossible_list_leader
            global_context["is_spam_list_leader"] = is_spam_list_leader
            global_context["is_impossible_tiny_list_leader"] = is_impossible_tiny_list_leader
            global_context["is_all_list_leader"] = is_all_list_leader
            global_context["is_rated_list_helper"] = is_rated_list_helper
            global_context["is_unrated_list_helper"] = is_unrated_list_helper
            global_context["is_challenge_list_helper"] = is_challenge_list_helper
            global_context["is_shitty_list_helper"] = is_shitty_list_helper
            global_context["is_tiny_list_helper"] = is_tiny_list_helper
            global_context["is_deathless_list_helper"] = is_deathless_list_helper
            global_context["is_impossible_list_helper"] = is_impossible_list_helper
            global_context["is_spam_list_helper"] = is_spam_list_helper
            global_context["is_impossible_tiny_list_helper"] = is_impossible_tiny_list_helper
            global_context["is_all_list_helper"] = is_all_list_helper

            global_context["is_subscriber"] = is_subscriber
            global_context["is_gd_lucky_leader"] = is_gd_lucky_leader

        global_list_words = translations.global_translation(language)

        if request.user.is_anonymous:
            is_hispanic = False
        elif not request.user.profile.country:
            is_hispanic = False
        elif request.user.profile.country.country in hispanic_countries:
            is_hispanic = True
        else:
            is_hispanic = False

        global_context["global_list_words"] = global_list_words
        global_context["language"] = language
        global_context["is_hispanic"] = is_hispanic
        global_context["dark_mode"] = dark_mode
        global_context['MEDIA_URL'] = settings.MEDIA_URL

        request.global_context = global_context

        response = self.get_response(request)

        return response