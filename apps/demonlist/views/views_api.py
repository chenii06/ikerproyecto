"""Demon List views."""

# Django
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, Window, Sum, Case, When, CharField, Value, ExpressionWrapper, Func, IntegerField, BooleanField, Q
from django.http.response import JsonResponse, HttpResponse
from django.views.generic.base import View

# Models
from django.contrib.auth.models import User
from apps.demonlist.models import Demon, Record, Changelog, Roulette

# Utils
import json

# API que usa el Ingame List Mod
class DemonApi(View):

    def get(self, request):

        level_id = request.GET.get('level_id', None)

        demon = Demon.objects.annotate(position=F("rated_position")).values("id", "position", "level", "list_points", "level_id", "level_password", "creator", "description", "verifier", "photo", "verification_video_embed", "verification_video", "level_id_ldm", "object_count", "demon_difficulty", "update_created", "created", "modified").get(level_id=level_id)

        json_context = json.dumps(demon, indent=None, sort_keys=False, default=str)

        return HttpResponse(json_context, content_type='application/json')