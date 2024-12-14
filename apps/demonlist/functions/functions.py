# Django
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import UploadedFile
from django.core.validators import URLValidator
from django.db import transaction
from django.db.models import Sum, Q, F, Avg, Subquery, OuterRef, Value, IntegerField, Case, When, DecimalField, FloatField
from django.db.models.functions import Coalesce, Round, Cast, Substr

# Models
from django.contrib.auth.models import User, Group
from apps.users.models import Profile, Country, Team, Notification
from apps.demonlist.models import Demon, Record, Changelog, LevelPack

# Models (Proxy)
from apps.demonlist.models.proxy import ExtendedDemon, ExtendedRecord
from apps.users.models.proxy import ExtendedCountry, ExtendedProfile, ExtendedTeam

# Functions
from apps.users.functions import functions_discord

# Utils
from asgiref.sync import sync_to_async
from background_task import background
from bs4 import BeautifulSoup
from datetime import datetime
from googletrans import Translator
import os
import pandas as pd
from PIL import Image
import re
import requests
import send2trash
import shutil
import base64
from urllib.parse import unquote
import time
from pytube import YouTube
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains


# Utils (Custom)
from utils.constants import values_list_points_classic, values_list_points, values_list_points_platformer, values_list_points_spam


"""
    Funciones para los roles de Discord
"""

@background(schedule=0)
def async_discord_functions_everyone(list_roles):
    for role in list_roles:
        functions_discord.members_rol(role["role_name"], role["action"])

@background(schedule=0)
def async_discord_functions(id_discord, category):
    members = list(Profile.objects.filter(id_discord__isnull=False, verified=True).values_list("id_discord", flat=True))
    if "rated" in category:
        functions_discord.check_all_rated_list([id_discord], "platformer")
        functions_discord.check_list_points([id_discord], "platformer")
        functions_discord.check_top_1_rated([id_discord])
        functions_discord.check_top_player([id_discord], "platformer")
    if "unrated" in category:
        functions_discord.check_all_unrated_list([id_discord], "platformer")
        functions_discord.check_top_1_unrated([id_discord])
    functions_discord.check_first_victor([id_discord])

@background(schedule=0)
def async_discord_function_diary():
    members = list(Profile.objects.filter(id_discord__isnull=False, verified=True).values_list("id_discord", flat=True))
    functions_discord.check_top_player(members, "platformer")





"""
    Función para actualizar los list points de todos los rated demons
"""   

def order_list_points(mode, category):
    demons = Demon.objects.filter(Q(all_position__isnull=False) | Q(challenge_position__isnull=False) | Q(shitty_position__isnull=False) | Q(tiny_position__isnull=False) | Q(deathless_position__isnull=False) | Q(impossible_position__isnull=False) | Q(spam_position__isnull=False) | Q(impossible_tiny_position__isnull=False), mode=mode, category__in=category)
    if ("deathless" in category):
        demons = demons | Demon.objects.filter(mode=mode, deathless_position__isnull=False)
    if ("impossible" in category):
        demons = demons | Demon.objects.filter(mode=mode, impossible_position__isnull=False)

    for demon in demons:
        if demon.rated_position:
            position = demon.rated_position - 1
        elif demon.unrated_position:
            position = demon.unrated_position - 1
        elif demon.challenge_position:
            position = demon.challenge_position - 1
        elif demon.shitty_position:
            position = demon.shitty_position - 1
        elif demon.tiny_position:
            position = demon.tiny_position - 1
        elif demon.spam_position:
            position = demon.spam_position - 1
        elif demon.impossible_tiny_position:
            position = demon.impossible_tiny_position - 1

        if mode == "classic":
            if demon.category == "spam" or demon.category == "impossible_tiny":
                try:
                    demon.list_points = values_list_points_spam[position]
                except:
                    demon.list_points = 0
            else:
                try:
                    demon.list_points = values_list_points_classic[position]
                except:
                    demon.list_points = 0
        else:
            try:
                demon.list_points = values_list_points_platformer[position]
            except:
                demon.list_points = 0

        if demon.deathless_position:
            position = demon.deathless_position - 1
            try:
                demon.deathless_list_points = values_list_points_platformer[position]
            except:
                demon.deathless_list_points = 0
        if demon.impossible_position:
            position = demon.impossible_position - 1
            try:
                demon.impossible_list_points = values_list_points_platformer[position]
            except:
                demon.impossible_list_points = 0
        if demon.all_position:
            position = demon.all_position - 1
            try:
                demon.all_list_points = values_list_points[position]
            except:
                demon.all_list_points = 0
        demon.save()


"""
    Funciones para actualizar los tiers
"""   

def update_players_tier(player):
    data = {
        "user": player.user,
        "mode": "platformer",
        "category": "all",
    }
    records = ExtendedRecord.objects.filter_by_category_list(data).order_by(f"demon__{data['category']}_position")
    hardest=records.order_by(f"demon__all_position")[0].demon

    top_tier_0 = Demon.objects.get(level_id=97536552).all_position - 1
    top_tier_1 = Demon.objects.get(level_id=97910718).rated_position - 1
    top_tier_2 = Demon.objects.get(level_id=101899067).rated_position - 1
    top_tier_3 = Demon.objects.get(level_id=98741640).all_position - 1
    top_tier_4 = Demon.objects.get(level_id=97543536).all_position - 1
    top_tier_5 = Demon.objects.get(level_id=97713011).all_position - 1

    print("hardest")
    print(hardest)



"""
    Funciones para actualizar los list points
"""   

def update_players_list_points(player, mode, category):
    demons = ExtendedRecord.objects.annotate_category_position(category).filter(
        demon__mode=mode, category_position__isnull=False,
        player=player, accepted=True, mods__isnull=True
    )
    if category == "deathless":
        demons = demons.filter(deathless=True)
    else:
        demons = demons.filter(deathless=False)
    demons = demons.distinct().annotate_category_list_points(category).values("category_list_points")

    list_points = 0
    for demon in demons:
        list_points += demon["category_list_points"]
    
    demons = ExtendedDemon.objects.annotate_category_position(category).filter(
        mode=mode, category_position__isnull=False,
        verifier_profile=player
    ).distinct().annotate_category_list_points(category).values("category_list_points")

    for demon in demons:
        list_points += demon["category_list_points"]

    if mode == "classic":
        if category == "rated":
            player.classic_list_points = list_points
        elif category == "unrated":
            player.classic_unrated_list_points = list_points
        elif category == "tiny":
            player.classic_tiny_list_points = list_points
        elif category == "shitty":
            player.classic_shitty_list_points = list_points
        elif category == "spam":
            player.classic_spam_list_points = list_points
        elif category == "impossible_tiny":
            player.classic_impossible_tiny_list_points = list_points
    elif mode == "platformer":
        if category == "rated":
            player.platformer_list_points = list_points
        elif category == "unrated":
            player.platformer_unrated_list_points = list_points
        elif category == "challenge":
            player.platformer_challenge_list_points = list_points
        elif category == "deathless":
            player.platformer_deathless_list_points = list_points
        elif category == "impossible":
            player.platformer_impossible_list_points = list_points
        elif category == "tiny":
            player.platformer_tiny_list_points = list_points
        elif category == "all":
            player.platformer_all_list_points = list_points

    if mode == "classic":
        demons = ExtendedRecord.objects.annotate_category_position(category).filter(
            demon__mode=mode, category_position__isnull=False,
            player=player, accepted=True, mods__isnull=False
        ).distinct().annotate_category_list_points(category).values("category_list_points")

        for demon in demons:
            list_points += demon["category_list_points"]
        if category == "rated":
            player.classic_list_points_with_mods = list_points
        elif category == "unrated":
            player.classic_unrated_list_points_with_mods = list_points
        elif category == "tiny":
            player.classic_tiny_list_points_with_mods = list_points
        elif category == "shitty":
            player.classic_shitty_list_points_with_mods = list_points
        elif category == "spam":
            player.classic_spam_list_points_with_mods = list_points
        elif category == "impossible_tiny":
            player.classic_impossible_tiny_list_points_with_mods = list_points
    player.save()

def update_countries_list_points(country, mode, category):
    if country:
        demons = ExtendedRecord.objects.annotate_category_position(category).filter(
            demon__mode=mode, category_position__isnull=False,
            player__country=country, accepted=True, mods__isnull=True
        )
        if category == "deathless":
            demons = demons.filter(deathless=True)
        else:
            demons = demons.filter(deathless=False)
        demons = demons.values("demon").distinct().annotate_category_list_points(category).values("category_list_points")

        list_points = 0
        for demon in demons:
            list_points += demon["category_list_points"]

        demons = ExtendedDemon.objects.annotate_category_position(category).filter(
            mode=mode, category_position__isnull=False, verifier_profile__country=country
        ).distinct().annotate_category_list_points(category).values("category_list_points")
        for demon in demons:
            list_points += demon["category_list_points"]

        if mode == "classic":
            if category == "rated":
                country.classic_list_points = list_points
            elif category == "unrated":
                country.classic_unrated_list_points = list_points
            elif category == "tiny":
                country.classic_tiny_list_points = list_points
            elif category == "shitty":
                country.classic_shitty_list_points = list_points
            elif category == "spam":
                country.classic_spam_list_points = list_points
            elif category == "impossible_tiny":
                country.classic_impossible_tiny_list_points = list_points
        elif mode == "platformer":
            if category == "rated":
                country.platformer_list_points = list_points
            elif category == "unrated":
                country.platformer_unrated_list_points = list_points
            elif category == "challenge":
                country.platformer_challenge_list_points = list_points
            elif category == "deathless":
                country.platformer_deathless_list_points = list_points
            elif category == "impossible":
                country.platformer_impossible_list_points = list_points
            elif category == "tiny":
                country.platformer_tiny_list_points = list_points
            elif category == "all":
                country.platformer_all_list_points = list_points

        demons = ExtendedRecord.objects.annotate_category_position(category).filter(
            demon__mode=mode, category_position__isnull=False,
            player__country=country, accepted=True, mods__isnull=False
        ).values("demon").distinct().annotate_category_list_points(category).values("category_list_points")
        for demon in demons:
            list_points += demon["category_list_points"]
        if mode == "classic":
            if category == "rated":
                country.classic_list_points_with_mods = list_points
            elif category == "unrated":
                country.classic_unrated_list_points_with_mods = list_points
            elif category == "tiny":
                country.classic_tiny_list_points_with_mods = list_points
            elif category == "shitty":
                country.classic_shitty_list_points_with_mods = list_points
            elif category == "spam":
                country.classic_spam_list_points_with_mods = list_points
            elif category == "impossible_tiny":
                country.classic_impossible_tiny_list_points_with_mods = list_points
        country.save()

def update_teams_list_points(team, mode, category):
    if team:
        demons = ExtendedRecord.objects.annotate_category_position(category).filter(
            demon__mode=mode, category_position__isnull=False,
            player__team=team, accepted=True, mods__isnull=True
        )
        if category == "deathless":
            demons = demons.filter(deathless=True)
        else:
            demons = demons.filter(deathless=False)
        demons = demons.values("demon").distinct().annotate_category_list_points(category).values("category_list_points")

        list_points = 0
        for demon in demons:
            list_points += demon["category_list_points"]

        demons = ExtendedDemon.objects.annotate_category_position(category).filter(
            mode=mode, category_position__isnull=False, verifier_profile__team=team
        ).distinct().annotate_category_list_points(category).values("category_list_points")
        for demon in demons:
            list_points += demon["category_list_points"]

        if mode == "classic":
            if category == "rated":
                team.classic_list_points = list_points
            elif category == "unrated":
                team.classic_unrated_list_points = list_points
            elif category == "tiny":
                team.classic_tiny_list_points = list_points
            elif category == "shitty":
                team.classic_shitty_list_points = list_points
            elif category == "spam":
                team.classic_spam_list_points = list_points
            elif category == "impossible_tiny":
                team.classic_impossible_tiny_list_points = list_points
        elif mode == "platformer":
            if category == "rated":
                team.platformer_list_points = list_points
            elif category == "unrated":
                team.platformer_unrated_list_points = list_points
            elif category == "challenge":
                team.platformer_challenge_list_points = list_points
            elif category == "deathless":
                team.platformer_deathless_list_points = list_points
            elif category == "impossible":
                team.platformer_impossible_list_points = list_points
            elif category == "tiny":
                team.platformer_tiny_list_points = list_points
            elif category == "all":
                team.platformer_all_list_points = list_points

        demons = ExtendedRecord.objects.annotate_category_position(category).filter(
            demon__mode=mode, category_position__isnull=False,
            player__team=team, accepted=True, mods__isnull=False
        ).values("demon").distinct().annotate_category_list_points(category).values("category_list_points")
        list_points = 0
        for demon in demons:
            list_points += demon["category_list_points"]
        if mode == "classic":
            if category == "rated":
                team.classic_list_points_with_mods = list_points
            elif category == "unrated":
                team.classic_unrated_list_points_with_mods = list_points
            elif category == "tiny":
                team.classic_tiny_list_points_with_mods = list_points
            elif category == "shitty":
                team.classic_shitty_list_points_with_mods = list_points
            elif category == "spam":
                team.classic_spam_list_points_with_mods = list_points
            elif category == "impossible_tiny":
                team.classic_impossible_tiny_list_points_with_mods = list_points
        team.save()

def update_players_list_points_all(mode, categories):

    for category in categories:

        list_points_string = f"{mode}_{category}_list_points" if category != 'rated' else f"{mode}_list_points"

        if category == "deathless":
            case_1 = [When(Q(record__demon__deathless=True), then=F('record__demon__deathless_position'))]
            case_2 = [When(Q(verifier_profile__deathless=True), then=F('verifier_profile__deathless_position'))]
            filter_1 = Q(record__deathless=True)
            category_list_points = "deathless_list_points"
        elif category == "impossible":
            case_1 = [When(Q(record__demon__impossible_position__isnull=False), then=F('record__demon__impossible_position'))]
            case_2 = [When(Q(verifier_profile__impossible_position__isnull=False), then=F('verifier_profile__impossible_position'))]
            filter_1 = Q()  # Sin filtros adicionales
            category_list_points = "impossible_list_points"
        elif category == "all":
            case_1 = [When(Q(record__demon__all_position__isnull=False), then=F('record__demon__all_position'))]
            case_2 = [When(Q(verifier_profile__all_position__isnull=False), then=F('verifier_profile__all_position'))]
            filter_1 = Q()  # Sin filtros adicionales
            category_list_points = "all_list_points"
        else:
            case_1 = [When(Q(record__demon__category=category), then=F(f'record__demon__{category}_position'))]
            case_2 = [When(Q(verifier_profile__category=category), then=F(f'verifier_profile__{category}_position'))]
            filter_1 = Q(record__demon__category=category)
            category_list_points = "list_points"

        queryset = Profile.objects.annotate(
                    list_points_records=Round(
                        Coalesce(
                            Subquery(
                                Profile.objects.annotate(
                                    cat_position=Case(*case_1, default=None, output_field=IntegerField())
                                ).filter(filter_1, id=(OuterRef("id")), record__demon__mode=mode, cat_position__isnull=False, record__accepted=True, record__mods__isnull=True)
                                .annotate(sum_list_points=Sum(f"record__demon__{category_list_points}", distinct=True))
                                .values("sum_list_points")[:1]
                            ),
                            Value(0, output_field=FloatField())
                        ),
                        2
                    ), list_points_verifications=Round(
                        Coalesce(
                            Subquery(
                                Profile.objects.annotate(
                                    cat_position=Case(*case_2, output_field=IntegerField())
                                ).filter(id=(OuterRef("id")), verifier_profile__mode=mode, cat_position__isnull=False)
                                .annotate(sum_list_points=Sum(f"verifier_profile__{category_list_points}", distinct=True))
                                .values("sum_list_points")[:1]
                            ),
                            Value(0, output_field=FloatField())
                        ),
                        2
                    ), list_points_records_with_mods=Round(
                        Coalesce(
                            Subquery(
                                Profile.objects.annotate(
                                    cat_position=Case(*case_1, output_field=IntegerField())
                                ).filter(filter_1, id=(OuterRef("id")), record__demon__mode=mode, cat_position__isnull=False, record__accepted=True, record__mods__isnull=False)
                                .annotate(sum_list_points=Sum(f"record__demon__{category_list_points}", distinct=True))
                                .values("sum_list_points")[:1]
                            ),
                            Value(0, output_field=FloatField())
                        ),
                        2
                    )
                )
        queryset.update(
            **{list_points_string: Round(F('list_points_records') + F('list_points_verifications'), 2)}
        )
        if mode == "classic":
            queryset.update(
                **{f"{list_points_string}_with_mods": Round(
                    F('list_points_records') + F('list_points_verifications') + F('list_points_records_with_mods'), 2
                )}
            )

def update_countries_list_points_all(mode, categories):

    for category in categories:

        list_points_string = f"{mode}_{category}_list_points" if category != 'rated' else f"{mode}_list_points"

        if category == "deathless":
            case_1 = [When(Q(profile__record__demon__deathless=True), then=F('profile__record__demon__deathless_position'))]
            case_2 = [When(Q(profile__verifier_profile__deathless=True), then=F('profile__verifier_profile__deathless_position'))]
            filter_1 = Q(profile__record__deathless=True)
            category_list_points = "deathless_list_points"
        elif category == "impossible":
            case_1 = [When(Q(profile__record__demon__impossible_position__isnull=False), then=F('profile__record__demon__impossible_position'))]
            case_2 = [When(Q(profile__verifier_profile__impossible_position__isnull=False), then=F('profile__verifier_profile__impossible_position'))]
            filter_1 = Q()
            category_list_points = "impossible_list_points"
        elif category == "all":
            case_1 = [When(Q(profile__record__demon__all_position__isnull=False), then=F('profile__record__demon__all_position'))]
            case_2 = [When(Q(profile__verifier_profile__all_position__isnull=False), then=F('profile__verifier_profile__all_position'))]
            filter_1 = Q()  # Sin filtros adicionales
            category_list_points = "all_list_points"
        else:
            case_1 = [When(Q(profile__record__demon__category=category), then=F(f'profile__record__demon__{category}_position'))]
            case_2 = [When(Q(profile__verifier_profile__category=category), then=F(f'profile__verifier_profile__{category}_position'))]
            filter_1 = Q(profile__record__demon__category=category)
            category_list_points = "list_points"

        queryset = Country.objects.annotate(
                    list_points_records=Round(
                        Coalesce(
                            Subquery(
                                Country.objects.annotate(
                                    cat_position=Case(*case_1, output_field=IntegerField())
                                ).filter(filter_1, id=(OuterRef("id")), profile__record__demon__mode=mode, cat_position__isnull=False, profile__record__accepted=True, profile__record__mods__isnull=True)
                                .annotate(sum_list_points=Sum(f"profile__record__demon__{category_list_points}", distinct=True))
                                .values("sum_list_points")[:1]
                            ),
                            Value(0, output_field=FloatField())
                        ),
                        2
                    ), list_points_verifications=Round(
                        Coalesce(
                            Subquery(
                                Country.objects.annotate(
                                    cat_position=Case(*case_2, output_field=IntegerField())
                                ).filter(id=(OuterRef("id")), profile__verifier_profile__mode=mode, cat_position__isnull=False)
                                .annotate(sum_list_points=Sum(f"profile__verifier_profile__{category_list_points}", distinct=True))
                                .values("sum_list_points")[:1]
                            ),
                            Value(0, output_field=FloatField())
                        ),
                        2
                    ), list_points_records_with_mods=Round(
                        Coalesce(
                            Subquery(
                                Country.objects.annotate(
                                    cat_position=Case(*case_1, output_field=IntegerField())
                                ).filter(filter_1, id=(OuterRef("id")), profile__record__demon__mode=mode, cat_position__isnull=False, profile__record__accepted=True, profile__record__mods__isnull=False)
                                .annotate(sum_list_points=Sum(f"profile__record__demon__{category_list_points}", distinct=True))
                                .values("sum_list_points")[:1]
                            ),
                            Value(0, output_field=FloatField())
                        ),
                        2
                    )
                )
        queryset.update(**{list_points_string: Round(F('list_points_records') + F('list_points_verifications'), 2)})
        if mode == "classic":
            queryset.update(
                **{f"{list_points_string}_with_mods": Round(
                    F('list_points_records') + F('list_points_verifications') + F('list_points_records_with_mods'), 2
                )}
            )

def update_teams_list_points_all(mode, categories):

    for category in categories:

        list_points_string = f"{mode}_{category}_list_points" if category != 'rated' else f"{mode}_list_points"

        if category == "deathless":
            case_1 = [When(Q(profile__record__demon__deathless=True), then=F('profile__record__demon__deathless_position'))]
            case_2 = [When(Q(profile__verifier_profile__deathless=True), then=F('profile__verifier_profile__deathless_position'))]
            filter_1 = Q(profile__record__deathless=True)
            category_list_points = "deathless_list_points"
        elif category == "impossible":
            case_1 = [When(Q(profile__record__demon__impossible_position__isnull=False), then=F('profile__record__demon__impossible_position'))]
            case_2 = [When(Q(profile__verifier_profile__impossible_position__isnull=False), then=F('profile__verifier_profile__impossible_position'))]
            filter_1 = Q()
            category_list_points = "impossible_list_points"
        elif category == "all":
            case_1 = [When(Q(profile__record__demon__all_position__isnull=False), then=F('profile__record__demon__all_position'))]
            case_2 = [When(Q(profile__verifier_profile__all_position__isnull=False), then=F('profile__verifier_profile__all_position'))]
            filter_1 = Q()  # Sin filtros adicionales
            category_list_points = "all_list_points"
        else:
            case_1 = [When(Q(profile__record__demon__category=category), then=F(f'profile__record__demon__{category}_position'))]
            case_2 = [When(Q(profile__verifier_profile__category=category), then=F(f'profile__verifier_profile__{category}_position'))]
            filter_1 = Q(profile__record__demon__category=category)
            category_list_points = "list_points"

        queryset = Team.objects.annotate(
                    list_points_records=Round(
                        Coalesce(
                            Subquery(
                                Team.objects.annotate(
                                    cat_position=Case(*case_1, output_field=IntegerField())
                                ).filter(filter_1, id=(OuterRef("id")), profile__record__demon__mode=mode, cat_position__isnull=False, profile__record__accepted=True, profile__record__mods__isnull=True)
                                .annotate(sum_list_points=Sum(f"profile__record__demon__{category_list_points}", distinct=True))
                                .values("sum_list_points")[:1]
                            ),
                            Value(0, output_field=FloatField())
                        ),
                        2
                    ), list_points_verifications=Round(
                        Coalesce(
                            Subquery(
                                Team.objects.annotate(
                                    cat_position=Case(*case_2, output_field=IntegerField())
                                ).filter(id=(OuterRef("id")), profile__verifier_profile__mode=mode, cat_position__isnull=False)
                                .annotate(sum_list_points=Sum(f"profile__verifier_profile__{category_list_points}", distinct=True))
                                .values("sum_list_points")[:1]
                            ),
                            Value(0, output_field=FloatField())
                        ),
                        2
                    ), list_points_records_with_mods=Round(
                        Coalesce(
                            Subquery(
                                Team.objects.annotate(
                                    cat_position=Case(*case_1, output_field=IntegerField())
                                ).filter(filter_1, id=(OuterRef("id")), profile__record__demon__mode=mode, cat_position__isnull=False, profile__record__accepted=True, profile__record__mods__isnull=False)
                                .annotate(sum_list_points=Sum(f"profile__record__demon__{category_list_points}", distinct=True))
                                .values("sum_list_points")[:1]
                            ),
                            Value(0, output_field=FloatField())
                        ),
                        2
                    )
                )
        queryset.update(**{list_points_string: Round(F('list_points_records') + F('list_points_verifications'), 2)})
        if mode == "classic":
            queryset.update(
                **{f"{list_points_string}_with_mods": Round(
                    F('list_points_records') + F('list_points_verifications') + F('list_points_records_with_mods'), 2
                )}
            )


"""
    Función para actualizar el promedio del rating stars de un demon
"""   

def upload_all_stars(demon):
    records = Record.objects.filter(demon=demon, accepted=True).annotate(sum_enjoyment_stars=Sum("enjoyment_stars"),
    sum_gameplay_stars=Sum("gameplay_stars"),
    sum_decoration_stars=Sum("decoration_stars"),
    sum_balanced_stars=Sum("balanced_stars"),
    sum_atmosphere_stars=Sum("atmosphere_stars")).aggregate(avg_enjoyment_stars=Avg("sum_enjoyment_stars"),
                                                            avg_gameplay_stars=Avg("sum_gameplay_stars"),
                                                            avg_decoration_stars=Avg("sum_decoration_stars"),
                                                            avg_balanced_stars=Avg("sum_balanced_stars"),
                                                            avg_atmosphere_stars=Avg("sum_atmosphere_stars")
                                                           )
    
    if not(records["avg_enjoyment_stars"]):
        records["avg_enjoyment_stars"] = 0
    if not(records["avg_gameplay_stars"]):
        records["avg_gameplay_stars"] = 0
    if not(records["avg_decoration_stars"]):
        records["avg_decoration_stars"] = 0
    if not(records["avg_balanced_stars"]):
        records["avg_balanced_stars"] = 0
    if not(records["avg_atmosphere_stars"]):
        records["avg_atmosphere_stars"] = 0

    all_stars = (records["avg_enjoyment_stars"] + records["avg_gameplay_stars"] + records["avg_decoration_stars"] + records["avg_balanced_stars"] + records["avg_atmosphere_stars"]) / 5
    demon.enjoyment_stars = records["avg_enjoyment_stars"]
    demon.gameplay_stars = records["avg_gameplay_stars"]
    demon.decoration_stars = records["avg_decoration_stars"]
    demon.balanced_stars = records["avg_balanced_stars"]
    demon.atmosphere_stars = records["avg_atmosphere_stars"]
    demon.all_stars = all_stars
    demon.save()







"""
    Funciones para ordenar los récords por best time y por order
"""   


def update_top_best_time(demon):
    records = Record.objects.filter(demon=demon, accepted=True).order_by("best_time")
    top_best_time = 1

    records_to_update = [record for record in records]
    for record in records_to_update:
        record.top_best_time = top_best_time
        top_best_time += 1

    Record.objects.bulk_update(records_to_update, ['top_best_time'])

def update_top_order(demon):
    records = Record.objects.filter(demon=demon, accepted=True).order_by("id")
    top_order = 1

    records_to_update = [record for record in records]
    for record in records_to_update:
        record.top_order = top_order
        top_order += 1

    Record.objects.bulk_update(records_to_update, ['top_order'])

def update_top_all():
    demons = Demon.objects.all()

    for demon in demons:
        records = Record.objects.filter(demon=demon, accepted=True).order_by("best_time")
        top_best_time = 1

        records_to_update = [record for record in records]
        for record in records_to_update:
            record.top_best_time = top_best_time
            top_best_time += 1

        Record.objects.bulk_update(records_to_update, ['top_best_time'])

        records = Record.objects.filter(demon=demon, accepted=True).order_by("id")
        top_order = 1

        records_to_update = [record for record in records]
        for record in records_to_update:
            record.top_order = top_order
            top_order += 1

        Record.objects.bulk_update(records_to_update, ['top_order'])














"""
    Verifica que un archivo sea de imagen
"""


def is_valid_image(file):
    if not isinstance(file, UploadedFile):
        return False
    if file.size > 5 * 1024 * 1024:
        return False

    # Obtener la extensión del archivo
    _, ext = os.path.splitext(file.name)
    ext = ext.lower()

    # Verificar si la extensión corresponde a PNG, JPG o JPEG
    if ext not in [".png", ".jpg", ".jpeg"]:
        return False

    # Verificar si el archivo es una imagen leyendo los primeros bytes
    header = file.read(11)
    file.seek(0)

    image_formats = [b"\x89\x50\x4E\x47\x0D\x0A\x1A\x0A",  # PNG
                     b"\xFF\xD8\xFF",  # JPEG/JPG
                     b"\xFF\xD9"]  # JPEG/JPG

    for format in image_formats:
        if header.startswith(format):
            return True

    return False












"""
    Función para arreglar la posición de los demons por si se bugea
"""

def subir_una_posicion_rated(mode, all_position):
    demons = Demon.objects.filter(mode=mode, all_position__gte=all_position)
    for demon in demons:
        demon.all_position -= 1
        if demon.rated_position:
            demon.rated_position -= 1
        demon.save()

def subir_una_posicion_unrated(mode, all_position):
    demons = Demon.objects.filter(mode=mode, all_position__gte=all_position)
    for demon in demons:
        demon.all_position -= 1
        if demon.unrated_position:
            demon.unrated_position -= 1
        demon.save()

def bajar_una_posicion_unrated(mode, all_position):
    demons = Demon.objects.filter(mode=mode, all_position__gte=all_position)
    for demon in demons:
        demon.all_position += 1
        if demon.unrated_position:
            demon.unrated_position += 1
        demon.save()

def bajar_una_posicion_rated(mode, all_position):
    demons = Demon.objects.filter(mode=mode, all_position__gte=all_position)
    for demon in demons:
        if demon.rated_position:
            demon.rated_position += 1
        demon.save()

def crear_rated_changelog(mode, rated_position1, rated_position2):
    demons = Demon.objects.filter(mode=mode, rated_position__gte=rated_position1, rated_position__lte=rated_position2)
    for demon in demons:
        Changelog.objects.create(demon=demon, reason="DownWell was moved up past this demon", reason_option="moved_down",
            reason_demon=Demon.objects.get(level="DownWell"), rated_position=demon.rated_position, change_number=1, change_type="Down")


def crear_deleted_changelog(mode, all_position):
    demons = Demon.objects.filter(mode=mode, all_position__gte=all_position, category="unrated")
    for demon in demons:
        Changelog.objects.create(demon=demon, reason="i wanna be the girl has been removed", reason_option="removed",
            reason_demon=Demon.objects.get(level="i wanna be the girl"), unrated_position=demon.unrated_position, change_number=1, change_type="Up")

    demons = Demon.objects.filter(mode=mode, all_position__gte=all_position)
    for demon in demons:
        Changelog.objects.create(demon=demon, reason="i wanna be the girl has been removed", reason_option="removed",
            reason_demon=Demon.objects.get(level="i wanna be the girl"), all_position=demon.all_position, change_number=1, change_type="Up")


def crear_added_changelog(mode, all_position):
    demons = Demon.objects.filter(mode=mode, all_position__gte=all_position, category="unrated")
    for demon in demons:
        Changelog.objects.create(demon=demon, reason="i wanna be the girl was added above", reason_option="added_above",
            reason_demon=Demon.objects.get(level="i wanna be the girl"), unrated_position=demon.unrated_position, change_number=1, change_type="Down")

    demons = Demon.objects.filter(mode=mode, all_position__gte=all_position)
    for demon in demons:
        Changelog.objects.create(demon=demon, reason="i wanna be the girl was added above", reason_option="added_above",
            reason_demon=Demon.objects.get(level="i wanna be the girl"), all_position=demon.all_position, change_number=1, change_type="Down")








"""
    Función para hacer pruebas masivas de usuarios
"""   

def upload_bots_albania():
    for i in range(10000, 20000):
        user = User.objects.create(username=f"i-user{i}", password=f"i-password{i}")
        Profile.objects.create(user=user,
                               classic_list_points=3400,
                               platformer_list_points=3400,
                               country=Country.objects.get(country="Albania")
                               )
        
"""
    Función para agregar los 150 niveles de la demonlist clásica
"""

def add_challengelist_levels():
    counter_level_password = 0
    counter_level_length = 0
    counter_object_count = 0
    counter_update_created = 0

    # Hacer la solicitud GET a la página
    url = 'https://challengelist.gd/challenges/'
    response = requests.get(url)

    # Analizar el contenido HTML de la página
    soup = BeautifulSoup(response.content, 'html.parser')

    # Encontrar los elementos que contienen los demons
    demon_elements = soup.find_all('section', class_='panel fade')

    # Iterar sobre los elementos y obtener la información de cada demon
    demons = []
    for element in demon_elements:
        name = ' '.join(element.find('h2').text.strip().split(" ")[2:])
        position = element.find('h2').text.strip().split(" ")[0][1:]
        creator = element.find('h3').text.strip()
        demons.append({'name': name, 'position': position, 'creator': creator})

    for demon in demons:
        url = f'https://challengelist.gd/challenges/{demon["position"]}'
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        iframe = soup.find('iframe')
        src = iframe['data-attr-value']
        demon["verification_video_embed"] = src

        # Expresión regular para extraer el código de video de YouTube
        pattern = re.compile(r'^https://www\.youtube\.com/embed/([A-Za-z0-9_-]+)$')


        # Buscar el código de video en la URL de YouTube
        match = pattern.match(src)

        if match:
            video_code = match.group(1)
            normal_url = f"https://www.youtube.com/watch?v={video_code}"
            demon["verification_video"] = normal_url

            yt = YouTube(normal_url)
            thumbnail_url = yt.thumbnail_url
            response_thumbnail = requests.get(thumbnail_url)

            directory = os.path.expanduser(r"c:\Users\elias\OneDrive\Imágenes\Challenges")

            if response_thumbnail.status_code == 200:
                file_path = os.path.join(directory, f"#{demon['position']} - {demon['name']}.jpg")
                with open(file_path, "wb") as f:
                    f.write(response_thumbnail.content)
                with open(file_path, 'rb') as file:
                    photo = ContentFile(file.read(), name=os.path.basename(file_path))
                print(f"Miniatura descargada con éxito como '{demon['name']}.jpg'")
            else:
                photo = None
                print("Error al descargar la miniatura")
        else:
            demon["verification_video"] = None
            photo = None







        list_points = values_list_points_platformer[int(demon["position"]) - 1]
        demon["list_points"] = list_points
        for info in demon:
            print(f"{info} - {demon[info]}")


        Demon.objects.create(
            level = demon["name"],
            creator = demon["creator"],
            list_points = demon["list_points"],
            photo = photo,
            verification_video_embed = demon["verification_video_embed"],
            verification_video = demon["verification_video"],
            category = "challenge",
            mode = "classic",
            challenge_position = demon["position"],
        )
        print()
        print()
        print()










def add_changelogs():
    demons = Demon.objects.filter(mode="platformer", created__lte=datetime(2024, 2, 20, 20, 30)).filter(Q(category="rated") | Q(category="unrated"))
    for demon in demons:
        last_changelog = Changelog.objects.filter(demon=demon, all_position__isnull=False, datetime__lte=datetime(2024, 2, 20, 20, 30)).last()
        changelog = Changelog.objects.create(demon=demon,
                                             reason="Smelvin Teahouse was moved to challenge list",
                                             reason_option="challenge",
                                             reason_demon=Demon.objects.get(level="Smelvin Teahouse"),
                                             all_position=last_changelog.all_position - 1,
                                             change_number=1,
                                             change_type="Up",
                                             datetime=datetime(2024, 2, 20, 15, 30, 0)
                                             )
        

def countries_translations_czech():
    countries = Country.objects.all()

    translations = {
        'Mexico': 'Mexiko',
        'United States': 'Spojené státy',
        'Albania': 'Albánie',
        'Argentina': 'Argentina',
        'Armenia': 'Arménie',
        'Australia': 'Austrálie',
        'Austria': 'Rakousko',
        'Belarus': 'Bělorusko',
        'Brazil': 'Brazílie',
        'Bulgaria': 'Bulharsko',
        'Canada': 'Kanada',
        'Chile': 'Chile',
        'China': 'Čína',
        'Colombia': 'Kolumbie',
        'Cuba': 'Kuba',
        'Denmark': 'Dánsko',
        'Slovakia': 'Slovensko',
        'Philippines': 'Filipíny',
        'France': 'Francie',
        'Germany': 'Německo',
        'Greece': 'Řecko',
        'India': 'Indie',
        'Ireland': 'Irsko',
        'Iceland': 'Island',
        'Japan': 'Japonsko',
        'Kazakhstan': 'Kazachstán',
        'Korea': 'Korea',
        'Moldova': 'Moldavsko',
        'Netherlands': 'Nizozemsko',
        'Pakistan': 'Pákistán',
        'Poland': 'Polsko',
        'Portugal': 'Portugalsko',
        'Czech Republic': 'Česká republika',
        'Romania': 'Rumunsko',
        'Russia': 'Rusko',
        'Serbia': 'Srbsko',
        'Spain': 'Španělsko',
        'Sweden': 'Švédsko',
        'Ukraine': 'Ukrajina',
        'United Kingdom': 'Spojené království',
        'Uruguay': 'Uruguay',
        'Venezuela': 'Venezuela',
        'Ecuador': 'Ekvádor',
        'El Salvador': 'Salvador',
        'Algeria': 'Alžírsko',
        'Aruba': 'Aruba',
        'Azerbaijan': 'Ázerbájdžán',
        'Bahrain': 'Bahrajn',
        'Bangladesh': 'Bangladéš',
        'Belgium': 'Belgie',
        'Bolivia': 'Bolívie',
        'Bosnia and Herzegovina': 'Bosna a Hercegovina',
        'Cambodia': 'Kambodža',
        'Costa Rica': 'Kostarika',
        'Croatia': 'Chorvatsko',
        'Dominican Republic': 'Dominikánská republika',
        'Egypt': 'Egypt',
        'Estonia': 'Estonsko',
        'Finland': 'Finsko',
        'Georgia': 'Gruzie',
        'Guatemala': 'Guatemala',
        'Guernsey': 'Guernsey',
        'Guyana': 'Guyana',
        'Haiti': 'Haiti',
        'Honduras': 'Honduras',
        'Hong Kong': 'Hongkong',
        'Hungary': 'Maďarsko',
        'Indonesia': 'Indonésie',
        'Iran': 'Írán',
        'Iraq': 'Irák',
        'Israel': 'Izrael',
        'Italy': 'Itálie',
        'Jamaica': 'Jamajka',
        'Kuwait': 'Kuvajt',
        "Lao People's Democratic Republic": 'Laos',
        'Latvia': 'Lotyšsko',
        'Lebanon': 'Libanon',
        'Lithuania': 'Litva',
        'Malaysia': 'Malajsie',
        'Malta': 'Malta',
        'Montenegro': 'Černá Hora',
        'Morocco': 'Maroko',
        'New Zealand': 'Nový Zéland',
        'Norway': 'Norsko',
        'Oman': 'Omán',
        'Palestine': 'Palestina',
        'Panama': 'Panama',
        'Paraguay': 'Paraguay',
        'Peru': 'Peru',
        'Puerto Rico': 'Portoriko',
        'Saint Vincent and the Grenadines': 'Svatý Vincenc a Grenadiny',
        'Singapore': 'Singapur',
        'Slovenia': 'Slovinsko',
        'Somalia': 'Somálsko',
        'South Africa': 'Jihoafrická republika',
        'Switzerland': 'Švýcarsko',
        'Taiwan': 'Tchaj-wan',
        'Thailand': 'Thajsko',
        'Trinidad and Tobago': 'Trinidad a Tobago',
        'Tunisia': 'Tunisko',
        'Turkey': 'Turecko',
        'Turkmenistan': 'Turkmenistán',
        'United Arab Emirates': 'Spojené arabské emiráty',
        'Uzbekistan': 'Uzbekistán',
        'Vietnam': 'Vietnam',
        'Libya': 'Libye',
        'South Korea': 'Jižní Korea',
        'North Macedonia': 'Severní Makedonie',
        'North Korea': 'Severní Korea',
        'Nicaragua': 'Nikaragua',
        'Saudi Arabia': 'Saúdská Arábie',
    }

    for country in countries:
        country.country_czech = translations[country.country]
        country.save()
        print(country)
        print(country.country_czech)


def countries_translations_turkish():
    countries = Country.objects.all()

    translations = {
        'Mexico': 'Meksika',
        'United States': 'Amerika Birleşik Devletleri',
        'Albania': 'Arnavutluk',
        'Argentina': 'Arjantin',
        'Armenia': 'Ermenistan',
        'Australia': 'Avustralya',
        'Austria': 'Avusturya',
        'Belarus': 'Belarus',
        'Brazil': 'Brezilya',
        'Bulgaria': 'Bulgaristan',
        'Canada': 'Kanada',
        'Chile': 'Şili',
        'China': 'Çin',
        'Colombia': 'Kolombiya',
        'Cuba': 'Küba',
        'Denmark': 'Danimarka',
        'Slovakia': 'Slovakya',
        'Philippines': 'Filipinler',
        'France': 'Fransa',
        'Germany': 'Almanya',
        'Greece': 'Yunanistan',
        'India': 'Hindistan',
        'Ireland': 'İrlanda',
        'Iceland': 'İzlanda',
        'Japan': 'Japonya',
        'Kazakhstan': 'Kazakistan',
        'Korea': 'Kore',
        'Moldova': 'Moldova',
        'Netherlands': 'Hollanda',
        'Pakistan': 'Pakistan',
        'Poland': 'Polonya',
        'Portugal': 'Portekiz',
        'Czech Republic': 'Çek Cumhuriyeti',
        'Romania': 'Romanya',
        'Russia': 'Rusya',
        'Serbia': 'Sırbistan',
        'Spain': 'İspanya',
        'Sweden': 'İsveç',
        'Ukraine': 'Ukrayna',
        'United Kingdom': 'Birleşik Krallık',
        'Uruguay': 'Uruguay',
        'Venezuela': 'Venezuela',
        'Ecuador': 'Ekvador',
        'El Salvador': 'El Salvador',
        'Algeria': 'Cezayir',
        'Aruba': 'Aruba',
        'Azerbaijan': 'Azerbaycan',
        'Bahrain': 'Bahreyn',
        'Bangladesh': 'Bangladeş',
        'Belgium': 'Belçika',
        'Bolivia': 'Bolivya',
        'Bosnia and Herzegovina': 'Bosna Hersek',
        'Cambodia': 'Kamboçya',
        'Costa Rica': 'Kosta Rika',
        'Croatia': 'Hırvatistan',
        'Dominican Republic': 'Dominik Cumhuriyeti',
        'Egypt': 'Mısır',
        'Estonia': 'Estonya',
        'Finland': 'Finlandiya',
        'Georgia': 'Gürcistan',
        'Guatemala': 'Guatemala',
        'Guernsey': 'Guernsey',
        'Guyana': 'Guyana',
        'Haiti': 'Haiti',
        'Honduras': 'Honduras',
        'Hong Kong': 'Hong Kong',
        'Hungary': 'Macaristan',
        'Indonesia': 'Endonezya',
        'Iran': 'İran',
        'Iraq': 'Irak',
        'Israel': 'İsrail',
        'Italy': 'İtalya',
        'Jamaica': 'Jamaika',
        'Kuwait': 'Kuveyt',
        "Lao People's Democratic Republic": 'Laos',
        'Latvia': 'Letonya',
        'Lebanon': 'Lübnan',
        'Lithuania': 'Litvanya',
        'Malaysia': 'Malezya',
        'Malta': 'Malta',
        'Montenegro': 'Karadağ',
        'Morocco': 'Fas',
        'New Zealand': 'Yeni Zelanda',
        'Norway': 'Norveç',
        'Oman': 'Umman',
        'Palestine': 'Filistin',
        'Panama': 'Panama',
        'Paraguay': 'Paraguay',
        'Peru': 'Peru',
        'Puerto Rico': 'Porto Riko',
        'Saint Vincent and the Grenadines': 'Saint Vincent ve Grenadinler',
        'Singapore': 'Singapur',
        'Slovenia': 'Slovenya',
        'Somalia': 'Somali',
        'South Africa': 'Güney Afrika',
        'Switzerland': 'İsviçre',
        'Taiwan': 'Tayvan',
        'Thailand': 'Tayland',
        'Trinidad and Tobago': 'Trinidad ve Tobago',
        'Tunisia': 'Tunus',
        'Turkey': 'Türkiye',
        'Turkmenistan': 'Türkmenistan',
        'United Arab Emirates': 'Birleşik Arap Emirlikleri',
        'Uzbekistan': 'Özbekistan',
        'Vietnam': 'Vietnam',
        'Libya': 'Libya',
        'South Korea': 'Güney Kore',
        'North Macedonia': 'Kuzey Makedonya',
        'North Korea': 'Kuzey Kore',
        'Nicaragua': 'Nikaragua',
        'Saudi Arabia': 'Suudi Arabistan',
    }

    for country in countries:
        country.country_turkish = translations[country.country]
        country.save()
        print(country)
        print(country.country_turkish)

def countries_translations_danish():
    countries = Country.objects.all()

    translations = {
        'Mexico': 'Mexico',
        'United States': 'USA',
        'Albania': 'Albanien',
        'Argentina': 'Argentina',
        'Armenia': 'Armenien',
        'Australia': 'Australien',
        'Austria': 'Østrig',
        'Belarus': 'Hviderusland',
        'Brazil': 'Brasilien',
        'Bulgaria': 'Bulgarien',
        'Canada': 'Canada',
        'Chile': 'Chile',
        'China': 'Kina',
        'Colombia': 'Colombia',
        'Cuba': 'Cuba',
        'Denmark': 'Danmark',
        'Slovakia': 'Slovakiet',
        'Philippines': 'Filippinerne',
        'France': 'Frankrig',
        'Germany': 'Tyskland',
        'Greece': 'Grækenland',
        'India': 'Indien',
        'Ireland': 'Irland',
        'Iceland': 'Island',
        'Japan': 'Japan',
        'Kazakhstan': 'Kasakhstan',
        'Korea': 'Korea',
        'Moldova': 'Moldova',
        'Netherlands': 'Holland',
        'Pakistan': 'Pakistan',
        'Poland': 'Polen',
        'Portugal': 'Portugal',
        'Czech Republic': 'Tjekkiet',
        'Romania': 'Rumænien',
        'Russia': 'Rusland',
        'Serbia': 'Serbien',
        'Spain': 'Spanien',
        'Sweden': 'Sverige',
        'Ukraine': 'Ukraine',
        'United Kingdom': 'Storbritannien',
        'Uruguay': 'Uruguay',
        'Venezuela': 'Venezuela',
        'Ecuador': 'Ecuador',
        'El Salvador': 'El Salvador',
        'Algeria': 'Algeriet',
        'Aruba': 'Aruba',
        'Azerbaijan': 'Aserbajdsjan',
        'Bahrain': 'Bahrain',
        'Bangladesh': 'Bangladesh',
        'Belgium': 'Belgien',
        'Bolivia': 'Bolivia',
        'Bosnia and Herzegovina': 'Bosnien-Hercegovina',
        'Cambodia': 'Cambodja',
        'Costa Rica': 'Costa Rica',
        'Croatia': 'Kroatien',
        'Dominican Republic': 'Den Dominikanske Republik',
        'Egypt': 'Egypten',
        'Estonia': 'Estland',
        'Finland': 'Finland',
        'Georgia': 'Georgien',
        'Guatemala': 'Guatemala',
        'Guernsey': 'Guernsey',
        'Guyana': 'Guyana',
        'Haiti': 'Haiti',
        'Honduras': 'Honduras',
        'Hong Kong': 'Hongkong',
        'Hungary': 'Ungarn',
        'Indonesia': 'Indonesien',
        'Iran': 'Iran',
        'Iraq': 'Irak',
        'Israel': 'Israel',
        'Italy': 'Italien',
        'Jamaica': 'Jamaica',
        'Kuwait': 'Kuwait',
        "Lao People's Democratic Republic": 'Laos',
        'Latvia': 'Letland',
        'Lebanon': 'Libanon',
        'Lithuania': 'Litauen',
        'Malaysia': 'Malaysia',
        'Malta': 'Malta',
        'Montenegro': 'Montenegro',
        'Morocco': 'Marokko',
        'New Zealand': 'New Zealand',
        'Norway': 'Norge',
        'Oman': 'Oman',
        'Palestine': 'Palæstina',
        'Panama': 'Panama',
        'Paraguay': 'Paraguay',
        'Peru': 'Peru',
        'Puerto Rico': 'Puerto Rico',
        'Saint Vincent and the Grenadines': 'Saint Vincent og Grenadinerne',
        'Singapore': 'Singapore',
        'Slovenia': 'Slovenien',
        'Somalia': 'Somalia',
        'South Africa': 'Sydafrika',
        'Switzerland': 'Schweiz',
        'Taiwan': 'Taiwan',
        'Thailand': 'Thailand',
        'Trinidad and Tobago': 'Trinidad og Tobago',
        'Tunisia': 'Tunesien',
        'Turkey': 'Tyrkiet',
        'Turkmenistan': 'Turkmenistan',
        'United Arab Emirates': 'Forenede Arabiske Emirater',
        'Uzbekistan': 'Usbekistan',
        'Vietnam': 'Vietnam',
        'Libya': 'Libyen',
        'South Korea': 'Sydkorea',
        'North Macedonia': 'Nordmakedonien',
        'North Korea': 'Nordkorea',
        'Nicaragua': 'Nicaragua',
        'Saudi Arabia': 'Saudi-Arabien',
    }

    for country in countries:
        country.country_danish = translations[country.country]
        country.save()
        print(country)
        print(country.country_danish)

def countries_translations_portuguese():
    countries = Country.objects.all()

    translations = {
        'Mexico': 'México',
        'United States': 'Estados Unidos',
        'Albania': 'Albânia',
        'Argentina': 'Argentina',
        'Armenia': 'Armênia',
        'Australia': 'Austrália',
        'Austria': 'Áustria',
        'Belarus': 'Bielorrússia',
        'Brazil': 'Brasil',
        'Bulgaria': 'Bulgária',
        'Canada': 'Canadá',
        'Chile': 'Chile',
        'China': 'China',
        'Colombia': 'Colômbia',
        'Cuba': 'Cuba',
        'Denmark': 'Dinamarca',
        'Slovakia': 'Eslováquia',
        'Philippines': 'Filipinas',
        'France': 'França',
        'Germany': 'Alemanha',
        'Greece': 'Grécia',
        'India': 'Índia',
        'Ireland': 'Irlanda',
        'Iceland': 'Islândia',
        'Japan': 'Japão',
        'Kazakhstan': 'Cazaquistão',
        'Korea': 'Coreia',
        'Moldova': 'Moldávia',
        'Netherlands': 'Holanda',
        'Pakistan': 'Paquistão',
        'Poland': 'Polônia',
        'Portugal': 'Portugal',
        'Czech Republic': 'República Checa',
        'Romania': 'Romênia',
        'Russia': 'Rússia',
        'Serbia': 'Sérvia',
        'Spain': 'Espanha',
        'Sweden': 'Suécia',
        'Ukraine': 'Ucrânia',
        'United Kingdom': 'Reino Unido',
        'Uruguay': 'Uruguai',
        'Venezuela': 'Venezuela',
        'Ecuador': 'Equador',
        'El Salvador': 'El Salvador',
        'Algeria': 'Argélia',
        'Aruba': 'Aruba',
        'Azerbaijan': 'Azerbaijão',
        'Bahrain': 'Bahrein',
        'Bangladesh': 'Bangladesh',
        'Belgium': 'Bélgica',
        'Bolivia': 'Bolívia',
        'Bosnia and Herzegovina': 'Bósnia e Herzegovina',
        'Cambodia': 'Camboja',
        'Costa Rica': 'Costa Rica',
        'Croatia': 'Croácia',
        'Dominican Republic': 'República Dominicana',
        'Egypt': 'Egito',
        'Estonia': 'Estônia',
        'Finland': 'Finlândia',
        'Georgia': 'Geórgia',
        'Guatemala': 'Guatemala',
        'Guernsey': 'Guernsey',
        'Guyana': 'Guiana',
        'Haiti': 'Haiti',
        'Honduras': 'Honduras',
        'Hong Kong': 'Hong Kong',
        'Hungary': 'Hungria',
        'Indonesia': 'Indonésia',
        'Iran': 'Irã',
        'Iraq': 'Iraque',
        'Israel': 'Israel',
        'Italy': 'Itália',
        'Jamaica': 'Jamaica',
        'Kuwait': 'Kuwait',
        "Lao People's Democratic Republic": 'Laos',
        'Latvia': 'Letônia',
        'Lebanon': 'Líbano',
        'Lithuania': 'Lituânia',
        'Malaysia': 'Malásia',
        'Malta': 'Malta',
        'Montenegro': 'Montenegro',
        'Morocco': 'Marrocos',
        'New Zealand': 'Nova Zelândia',
        'Norway': 'Noruega',
        'Oman': 'Omã',
        'Palestine': 'Palestina',
        'Panama': 'Panamá',
        'Paraguay': 'Paraguai',
        'Peru': 'Peru',
        'Puerto Rico': 'Porto Rico',
        'Saint Vincent and the Grenadines': 'São Vicente e Granadinas',
        'Singapore': 'Singapura',
        'Slovenia': 'Eslovênia',
        'Somalia': 'Somália',
        'South Africa': 'África do Sul',
        'Switzerland': 'Suíça',
        'Taiwan': 'Taiwan',
        'Thailand': 'Tailândia',
        'Trinidad and Tobago': 'Trindade e Tobago',
        'Tunisia': 'Tunísia',
        'Turkey': 'Turquia',
        'Turkmenistan': 'Turcomenistão',
        'United Arab Emirates': 'Emirados Árabes Unidos',
        'Uzbekistan': 'Uzbequistão',
        'Vietnam': 'Vietnã',
        'Libya': 'Líbia',
        'South Korea': 'Coreia do Sul',
        'North Macedonia': 'Macedônia do Norte',
        'North Korea': 'Coreia do Norte',
        'Nicaragua': 'Nicarágua',
        'Saudi Arabia': 'Arábia Saudita',
    }

    for country in countries:
        country.country_portuguese = translations[country.country]
        country.save()
        print(country)
        print(country.country_portuguese)

def countries_translations_french():
    countries = Country.objects.all()

    translations = {
        'Mexico': 'Mexique',
        'United States': 'États-Unis',
        'Albania': 'Albanie',
        'Argentina': 'Argentine',
        'Armenia': 'Arménie',
        'Australia': 'Australie',
        'Austria': 'Autriche',
        'Belarus': 'Biélorussie',
        'Brazil': 'Brésil',
        'Bulgaria': 'Bulgarie',
        'Canada': 'Canada',
        'Chile': 'Chili',
        'China': 'Chine',
        'Colombia': 'Colombie',
        'Cuba': 'Cuba',
        'Denmark': 'Danemark',
        'Slovakia': 'Slovaquie',
        'Philippines': 'Philippines',
        'France': 'France',
        'Germany': 'Allemagne',
        'Greece': 'Grèce',
        'India': 'Inde',
        'Ireland': 'Irlande',
        'Iceland': 'Islande',
        'Japan': 'Japon',
        'Kazakhstan': 'Kazakhstan',
        'Korea': 'Corée',
        'Moldova': 'Moldavie',
        'Netherlands': 'Pays-Bas',
        'Pakistan': 'Pakistan',
        'Poland': 'Pologne',
        'Portugal': 'Portugal',
        'Czech Republic': 'République Tchèque',
        'Romania': 'Roumanie',
        'Russia': 'Russie',
        'Serbia': 'Serbie',
        'Spain': 'Espagne',
        'Sweden': 'Suède',
        'Ukraine': 'Ukraine',
        'United Kingdom': 'Royaume-Uni',
        'Uruguay': 'Uruguay',
        'Venezuela': 'Venezuela',
        'Ecuador': 'Équateur',
        'El Salvador': 'Salvador',
        'Algeria': 'Algérie',
        'Aruba': 'Aruba',
        'Azerbaijan': 'Azerbaïdjan',
        'Bahrain': 'Bahreïn',
        'Bangladesh': 'Bangladesh',
        'Belgium': 'Belgique',
        'Bolivia': 'Bolivie',
        'Bosnia and Herzegovina': 'Bosnie-Herzégovine',
        'Cambodia': 'Cambodge',
        'Costa Rica': 'Costa Rica',
        'Croatia': 'Croatie',
        'Dominican Republic': 'République Dominicaine',
        'Egypt': 'Égypte',
        'Estonia': 'Estonie',
        'Finland': 'Finlande',
        'Georgia': 'Géorgie',
        'Guatemala': 'Guatemala',
        'Guernsey': 'Guernesey',
        'Guyana': 'Guyana',
        'Haiti': 'Haïti',
        'Honduras': 'Honduras',
        'Hong Kong': 'Hong Kong',
        'Hungary': 'Hongrie',
        'Indonesia': 'Indonésie',
        'Iran': 'Iran',
        'Iraq': 'Irak',
        'Israel': 'Israël',
        'Italy': 'Italie',
        'Jamaica': 'Jamaïque',
        'Kuwait': 'Koweït',
        "Lao People's Democratic Republic": 'Laos',
        'Latvia': 'Lettonie',
        'Lebanon': 'Liban',
        'Lithuania': 'Lituanie',
        'Malaysia': 'Malaisie',
        'Malta': 'Malte',
        'Montenegro': 'Monténégro',
        'Morocco': 'Maroc',
        'New Zealand': 'Nouvelle-Zélande',
        'Norway': 'Norvège',
        'Oman': 'Oman',
        'Palestine': 'Palestine',
        'Panama': 'Panama',
        'Paraguay': 'Paraguay',
        'Peru': 'Pérou',
        'Puerto Rico': 'Porto Rico',
        'Saint Vincent and the Grenadines': 'Saint-Vincent-et-les-Grenadines',
        'Singapore': 'Singapour',
        'Slovenia': 'Slovénie',
        'Somalia': 'Somalie',
        'South Africa': 'Afrique du Sud',
        'Switzerland': 'Suisse',
        'Taiwan': 'Taïwan',
        'Thailand': 'Thaïlande',
        'Trinidad and Tobago': 'Trinité-et-Tobago',
        'Tunisia': 'Tunisie',
        'Turkey': 'Turquie',
        'Turkmenistan': 'Turkménistan',
        'United Arab Emirates': 'Émirats Arabes Unis',
        'Uzbekistan': 'Ouzbékistan',
        'Vietnam': 'Vietnam',
        'Libya': 'Libye',
        'South Korea': 'Corée du Sud',
        'North Macedonia': 'Macédoine du Nord',
        'North Korea': 'Corée du Nord',
        'Nicaragua': 'Nicaragua',
        'Saudi Arabia': 'Arabie Saoudite',
    }

    for country in countries:
        country.country_french = translations[country.country]
        country.save()
        print(country)
        print(country.country_french)




def countries_abbreviations():
    countries = Country.objects.all()

    abbreviations = {
        'Mexico': 'MEX',
        'United States': 'USA',
        'Albania': 'ALB',
        'Argentina': 'ARG',
        'Armenia': 'ARM',
        'Australia': 'AUS',
        'Austria': 'AUT',
        'Belarus': 'BLR',
        'Brazil': 'BRA',
        'Bulgaria': 'BGR',
        'Canada': 'CAN',
        'Chile': 'CHL',
        'China': 'CHN',
        'Colombia': 'COL',
        'Cuba': 'CUB',
        'Denmark': 'DNK',
        'Slovakia': 'SVK',
        'Philippines': 'PHL',
        'France': 'FRA',
        'Germany': 'DEU',
        'Greece': 'GRC',
        'India': 'IND',
        'Ireland': 'IRL',
        'Iceland': 'ISL',
        'Japan': 'JPN',
        'Kazakhstan': 'KAZ',
        'Korea': 'KOR',
        'Moldova': 'MDA',
        'Netherlands': 'NLD',
        'Pakistan': 'PAK',
        'Poland': 'POL',
        'Portugal': 'PRT',
        'Czech Republic': 'CZE',
        'Romania': 'ROU',
        'Russia': 'RUS',
        'Serbia': 'SRB',
        'Spain': 'ESP',
        'Sweden': 'SWE',
        'Ukraine': 'UKR',
        'United Kingdom': 'GBR',
        'Uruguay': 'URY',
        'Venezuela': 'VEN',
        'Ecuador': 'ECU',
        'El Salvador': 'SLV',
        'Algeria': 'DZA',
        'Aruba': 'ABW',
        'Azerbaijan': 'AZE',
        'Bahrain': 'BHR',
        'Bangladesh': 'BGD',
        'Belgium': 'BEL',
        'Bolivia': 'BOL',
        'Bosnia and Herzegovina': 'BIH',
        'Cambodia': 'KHM',
        'Costa Rica': 'CRI',
        'Croatia': 'HRV',
        'Dominican Republic': 'DOM',
        'Egypt': 'EGY',
        'Estonia': 'EST',
        'Finland': 'FIN',
        'Georgia': 'GEO',
        'Guatemala': 'GTM',
        'Guernsey': 'GGY',
        'Guyana': 'GUY',
        'Haiti': 'HTI',
        'Honduras': 'HND',
        'Hong Kong': 'HKG',
        'Hungary': 'HUN',
        'Indonesia': 'IDN',
        'Iran': 'IRN',
        'Iraq': 'IRQ',
        'Israel': 'ISR',
        'Italy': 'ITA',
        'Jamaica': 'JAM',
        'Kuwait': 'KWT',
        "Lao People's Democratic Republic": 'LAO',
        'Latvia': 'LVA',
        'Lebanon': 'LBN',
        'Lithuania': 'LTU',
        'Malaysia': 'MYS',
        'Malta': 'MLT',
        'Montenegro': 'MNE',
        'Morocco': 'MAR',
        'New Zealand': 'NZL',
        'Norway': 'NOR',
        'Oman': 'OMN',
        'Palestine': 'PSE',
        'Panama': 'PAN',
        'Paraguay': 'PRY',
        'Peru': 'PER',
        'Puerto Rico': 'PRI',
        'Saint Vincent and the Grenadines': 'VCT',
        'Singapore': 'SGP',
        'Slovenia': 'SVN',
        'Somalia': 'SOM',
        'South Africa': 'ZAF',
        'Switzerland': 'CHE',
        'Taiwan': 'TWN',
        'Thailand': 'THA',
        'Trinidad and Tobago': 'TTO',
        'Tunisia': 'TUN',
        'Turkey': 'TUR',
        'Turkmenistan': 'TKM',
        'United Arab Emirates': 'ARE',
        'Uzbekistan': 'UZB',
        'Vietnam': 'VNM',
        'Libya': 'LBY',
        'South Korea': 'KOR',
        'North Macedonia': 'MKD',
        'North Korea': 'PRK',
        'Nicaragua': 'NIC',
        'Saudi Arabia': 'SAU',
    }    
    
    for country in countries:
        country.abbreviation = abbreviations[country.country]
        country.save()
        print(country)
        print(country.abbreviation)

def add_all_demons(page):
    difficulty_map = {
        0: "unrated",
        10: "easy",
        20: "normal",
        30: "hard",
        40: "harder",
        50: "insane/demon"
    }

    song_map = {
        0: "Stereo Madness",
        1: "Back on Track",
        2: "Polargeist",
        3: "Dry Out",
        4: "Base After Base",
        5: "Can't Let Go",
        6: "Jumper",
        7: "Time Machine",
        8: "Cycles",
        9: "xStep",
        10: "Clutterfunk",
        11: "Theory of Everything",
        12: "Electroman Adventures",
        13: "Clubstep",
        14: "Electrodynamix",
        15: "Hexagon Force",
        16: "Blast Processing",
        17: "Theory of Everything 2",
        18: "Geometrical Dominator",
        19: "Deadlocked",
        20: "Fingerdash",
        21: "Dash"
    }

    version_map = {
        1: "1.0",
        2: "1.1",
        3: "1.2",
        4: "1.3",
        5: "1.4",
        6: "1.5",
        7: "1.6",
        10: "1.7",
        18: "1.8",
        19: "1.9",
        20: "2.0",
        21: "2.1",
        22: "2.2",
    }

    demon_difficulty_map = {
        3: "Easy demon",
        4: "Medium demon",
        0: "Hard demon",
        5: "Insane demon",
        6: "Extreme demon",
    }

    epic_difficulty_map = {
        1: "epic",
        2: "legendary",
        3: "mythic",
    }

    length_difficulty_map = {
        0: "tiny",
        1: "short",
        2: "medium",
        3: "long",
        4: "xl",
        5: "platformer",
    }

    headers = {
        "User-Agent": ""
    }


    for j in range(page, 747):

        # REQUEST TO VIEW FIRST PAGE OF 10 LEVELS
        data = {
            "diff": -2,
            "type": "1",
            "page": f"{j}",
            "secret": "Wmfd2893gb7",
        }

        url = "http://www.boomlings.com/database/getGJLevels21.php"

        req = requests.post(url=url, data=data, headers=headers)
        all_text = req.text.split("#")
        for i in range(10):

            # CONVERT THE STRANGE TEXT TO A DICT
            level_data = re.findall(r'[^:]+:[^:]+', all_text[0].split("|")[i])
            level_dictionary = {}
            for item in level_data:
                key, value = item.split(':')
                level_dictionary[key] = value

            # DO ANOTHER REQUEST TO GET THE CREATOR_DATA AND THE SONG_DATA
            data = {
                "str": level_dictionary["1"],
                "type": "0",
                "secret": "Wmfd2893gb7",
            }

            url = "http://www.boomlings.com/database/getGJLevels21.php"

            req = requests.post(url=url, data=data, headers=headers)
            text = req.text.split("#")
            creator_data = text[1]
            song_data = text[2].split("~|~")

            if song_data != ['']:
                song_dictionary = {song_data[i]: song_data[i + 1] for i in range(0, len(song_data), 2)}
            else:
                song_dictionary = {}

            print("level_dictionary")
            print(level_dictionary)

            # DO THE DICTIONARY WITH THE CORRECT KEY NAMES
            level_dict = {"level_id": level_dictionary["1"],
                        "level_name": level_dictionary["2"],
                        "level_version": level_dictionary["5"],
                        "creator_id": level_dictionary["6"],
                        "if_difficulty": int(level_dictionary["8"]) == 10,
                        "difficulty": difficulty_map.get(int(level_dictionary["9"]), "unknown"),
                        "downloads": level_dictionary["10"],
                        "official_song": song_map.get(int(level_dictionary["12"]), "unknown") if not(song_dictionary) else None,
                        "version_game": version_map.get(int(level_dictionary["13"]), None),
                        "likes": level_dictionary["14"],
                        "demon": int(level_dictionary.get("17", 0)) == 1 if level_dictionary.get("17") else False,
                        "demon_difficulty": demon_difficulty_map.get(int(level_dictionary["43"]), "unknown") if level_dictionary.get("17") else None,
                        "stars": level_dictionary["18"],
                        "feature_score": level_dictionary["19"],
                        "epic": epic_difficulty_map.get(int(level_dictionary["42"]), None) if level_dictionary.get("42") else None,
                        "object_count": level_dictionary["45"],
                        "description": base64.urlsafe_b64decode(level_dictionary.get("3") + "==").decode('utf-8') if level_dictionary.get("3") else None,
                        "length": length_difficulty_map.get(int(level_dictionary["15"]), "unknown"),
                        "original_level_id": level_dictionary["30"],
                        "two_players": int(level_dictionary["31"]) == 1,
                        "number_of_coins": level_dictionary["37"],
                        "verified_coins": int(level_dictionary["38"]) == 1,
                        "stars_requested": level_dictionary["39"],
                        "custom_song_id": level_dictionary["35"],
                        "mode": "platformer" if int(level_dictionary.get("15")) == 5 else "classic",
                        }

            if creator_data:
                creator_dict = {"user_id": creator_data.split(":")[0],
                            "username": creator_data.split(":")[1],
                            "account_id": creator_data.split(":")[2],
                            }
            else:
                creator_dict = {}

            if song_dictionary:
                song_dict = {"song_id": song_dictionary["1"],
                                "name": song_dictionary["2"],
                                "artist_id": song_dictionary["3"],
                                "artist_name": song_dictionary["4"],
                                "size_mb": song_dictionary["5"],
                                "link": unquote(song_dictionary["10"]),
                                "youtube_channel_url": f'https://www.youtube.com/channel/{song_dictionary.get("7")}' if song_dictionary.get("7") else None,
                                "is_verified": int(song_dictionary["8"]) == 1,
                                }
            else:
                song_dict = {"song_id": None,
                                "name": level_dict["official_song"],
                                "artist_id": None,
                                "artist_name": None,
                                "size_mb": None,
                                "link": None,
                                "youtube_channel_url": None,
                                "is_verified": None,
                                }

            page_dict = {"total_pages": all_text[3].split(":")[0],
                        "actual_page": all_text[3].split(":")[1],
                        "number_of_levels": all_text[3].split(":")[2],
                        }

            hash_dict = {"hash": all_text[4].split(":")[0]}

            print()
            print()
            print()
            print()
            print()
            print(f"Level {i + 1} - Page {j + 1}")
            print()
            print(level_dict)
            print()
            print(creator_dict)
            print()
            print(song_dict)

            if level_dict["epic"]:
                type = level_dict["epic"]
            else:
                if int(level_dict["feature_score"]) > 0:
                    type = "featured"
                else:
                    type = None
            try:
                demon = Demon.objects.get(level_id=int(level_dict["level_id"]))
                demon.category = "rated"
                demon.downloads = level_dict["downloads"]
                demon.likes = level_dict["likes"]
                demon.type = type
                demon.length = level_dict["length"]
                demon.two_players = level_dict["two_players"]
                demon.number_of_coins = level_dict["number_of_coins"]
                demon.song_id = song_dict["song_id"]
                demon.song_name = song_dict["name"]
                demon.artist_name = song_dict["artist_name"]
                demon.song_size = song_dict["size_mb"]
                if song_dict["song_id"]:
                    demon.song_link = f'https://www.newgrounds.com/audio/listen/{song_dict["song_id"]}'
                demon.save()

            except:
                demon = Demon.objects.create(level=level_dict["level_name"],
                                            description=level_dict["description"],
                                            creator=creator_dict.get("username", None),
                                            verifier=creator_dict.get("username", None),
                                            photo="",
                                            verification_video_embed="",
                                            verification_video="",
                                            level_id=level_dict["level_id"],
                                            object_count=level_dict["object_count"] if level_dict["object_count"] else None,
                                            demon_difficulty=level_dict["demon_difficulty"],
                                            update_created=level_dict["version_game"],
                                            category="rated",
                                            mode=level_dict["mode"],
                                            downloads=level_dict["downloads"],
                                            likes=level_dict["likes"],
                                            type=type,
                                            length=level_dict["length"],
                                            two_players=level_dict["two_players"],
                                            number_of_coins=level_dict["number_of_coins"],
                                            song_id=song_dict["song_id"],
                                            song_name=song_dict["name"],
                                            artist_name=song_dict["artist_name"],
                                            song_size=song_dict["size_mb"],
                                            song_link=f'https://www.newgrounds.com/audio/listen/{song_dict["song_id"]}' if song_dict["song_id"] else None,
                                            )

        time.sleep(20)

def fix_demons_of_all_lists():
    difficulty_map = {
        0: "unrated",
        10: "easy",
        20: "normal",
        30: "hard",
        40: "harder",
        50: "insane/demon"
    }

    song_map = {
        0: "Stereo Madness",
        1: "Back on Track",
        2: "Polargeist",
        3: "Dry Out",
        4: "Base After Base",
        5: "Can't Let Go",
        6: "Jumper",
        7: "Time Machine",
        8: "Cycles",
        9: "xStep",
        10: "Clutterfunk",
        11: "Theory of Everything",
        12: "Electroman Adventures",
        13: "Clubstep",
        14: "Electrodynamix",
        15: "Hexagon Force",
        16: "Blast Processing",
        17: "Theory of Everything 2",
        18: "Geometrical Dominator",
        19: "Deadlocked",
        20: "Fingerdash",
        21: "Dash"
    }

    version_map = {
        1: "1.0",
        2: "1.1",
        3: "1.2",
        4: "1.3",
        5: "1.4",
        6: "1.5",
        7: "1.6",
        10: "1.7",
        18: "1.8",
        19: "1.9",
        20: "2.0",
        21: "2.1",
        22: "2.2",
    }

    demon_difficulty_map = {
        3: "Easy demon",
        4: "Medium demon",
        0: "Hard demon",
        5: "Insane demon",
        6: "Extreme demon",
    }

    epic_difficulty_map = {
        1: "epic",
        2: "legendary",
        3: "mythic",
    }

    length_difficulty_map = {
        0: "tiny",
        1: "short",
        2: "medium",
        3: "long",
        4: "xl",
        5: "platformer",
    }

    headers = {
        "User-Agent": ""
    }

    demons_of_lists = Demon.objects.filter(Q(all_position__isnull=False) | Q(challenge_position__isnull=False) | Q(easiest_position__isnull=False) | Q(shitty_position__isnull=False)).order_by("level_id")

    for j in range(len(demons_of_lists)):

        data = {
            "str": demons_of_lists[j].level_id,
            "type": "0",
            "secret": "Wmfd2893gb7",
        }

        url = "http://www.boomlings.com/database/getGJLevels21.php"

        req = requests.post(url=url, data=data, headers=headers)
        text = req.text.split("#")

        print("demons_of_lists[j].level_id")
        print(demons_of_lists[j].level_id)
        print("req.text")
        print(req.text)
        print("text[0]")
        print(text[0])

        level_data = re.findall(r'[^:]+:[^:]+', text[0])

        level_dictionary = {}
        for item in level_data:
            key, value = item.split(':')
            level_dictionary[key] = value

        creator_data = text[1]
        song_data = text[2].split("~|~")

        if song_data != ['']:
            song_dictionary = {song_data[i]: song_data[i + 1] for i in range(0, len(song_data), 2)}
        else:
            song_dictionary = {}

        print("level_dictionary")
        print(level_dictionary)

        level_dict = {"level_id": level_dictionary["1"],
                    "level_name": level_dictionary["2"],
                    "level_version": level_dictionary["5"],
                    "creator_id": level_dictionary["6"],
                    "if_difficulty": int(level_dictionary["8"]) == 10,
                    "difficulty": difficulty_map.get(int(level_dictionary["9"]), "unknown"),
                    "downloads": level_dictionary["10"],
                    "official_song": song_map.get(int(level_dictionary["12"]), "unknown") if not(song_dictionary) else None,
                    "version_game": version_map.get(int(level_dictionary["13"]), None),
                    "likes": level_dictionary["14"],
                    "demon": int(level_dictionary.get("17", 0)) == 1 if level_dictionary.get("17") else False,
                    "demon_difficulty": demon_difficulty_map.get(int(level_dictionary["43"]), "unknown") if level_dictionary.get("17") else None,
                    "stars": level_dictionary["18"],
                    "feature_score": level_dictionary["19"],
                    "epic": epic_difficulty_map.get(int(level_dictionary["42"]), None) if level_dictionary.get("42") else None,
                    "object_count": level_dictionary["45"],
                    "description": base64.urlsafe_b64decode(level_dictionary.get("3") + "==").decode('utf-8') if level_dictionary.get("3") else None,
                    "length": length_difficulty_map.get(int(level_dictionary["15"]), "unknown"),
                    "original_level_id": level_dictionary["30"],
                    "two_players": int(level_dictionary["31"]) == 1,
                    "number_of_coins": level_dictionary["37"],
                    "verified_coins": int(level_dictionary["38"]) == 1,
                    "stars_requested": level_dictionary["39"],
                    "custom_song_id": level_dictionary["35"],
                    "mode": "platformer" if int(level_dictionary.get("15")) == 5 else "classic",
                    }

        if creator_data:
            creator_dict = {"user_id": creator_data.split(":")[0],
                        "username": creator_data.split(":")[1],
                        "account_id": creator_data.split(":")[2],
                        }
        else:
            creator_dict = {}

        print(level_dict["feature_score"])
        print(level_dict["feature_score"])
        print(level_dict["feature_score"])
        print(level_dict["feature_score"])
        print(level_dict["feature_score"])

        if song_dictionary:
            song_dict = {"song_id": song_dictionary["1"],
                            "name": song_dictionary["2"],
                            "artist_id": song_dictionary["3"],
                            "artist_name": song_dictionary["4"],
                            "size_mb": song_dictionary["5"],
                            "link": unquote(song_dictionary["10"]),
                            "youtube_channel_url": f'https://www.youtube.com/channel/{song_dictionary.get("7")}' if song_dictionary.get("7") else None,
                            "is_verified": int(song_dictionary["8"]) == 1,
                            }
        else:
            song_dict = {"song_id": None,
                            "name": level_dict["official_song"],
                            "artist_id": None,
                            "artist_name": None,
                            "size_mb": None,
                            "link": None,
                            "youtube_channel_url": None,
                            "is_verified": None,
                            }

        page_dict = {"total_pages": text[3].split(":")[0],
                    "actual_page": text[3].split(":")[1],
                    "number_of_levels": text[3].split(":")[2],
                    }

        hash_dict = {"hash": text[4].split(":")[0]}

        print()
        print()
        print()
        print()
        print()
        print(f"Level {j + 1}")
        print()
        print(level_dict)
        print()
        print(creator_dict)
        print()
        print(song_dict)

        if level_dict["epic"]:
            type = level_dict["epic"]
        else:
            if int(level_dict["feature_score"]) > 0:
                type = "featured"
            else:
                type = None
        demon = Demon.objects.get(level_id=int(level_dict["level_id"]))

        demon.downloads = level_dict["downloads"]
        demon.likes = level_dict["likes"]
        demon.type = type
        demon.length = level_dict["length"]
        demon.two_players = level_dict["two_players"]
        demon.number_of_coins = level_dict["number_of_coins"]
        demon.song_id = song_dict["song_id"]
        demon.song_name = song_dict["name"]
        demon.artist_name = song_dict["artist_name"]
        demon.song_size = song_dict["size_mb"]
        if song_dict["song_id"]:
            demon.song_link = f'https://www.newgrounds.com/audio/listen/{song_dict["song_id"]}'
        demon.save()

        if j % 10 == 0:
            time.sleep(5)

def easiest_demon_list():


    difficulty_map = {
        0: "unrated",
        10: "easy",
        20: "normal",
        30: "hard",
        40: "harder",
        50: "insane/demon"
    }

    song_map = {
        0: "Stereo Madness",
        1: "Back on Track",
        2: "Polargeist",
        3: "Dry Out",
        4: "Base After Base",
        5: "Can't Let Go",
        6: "Jumper",
        7: "Time Machine",
        8: "Cycles",
        9: "xStep",
        10: "Clutterfunk",
        11: "Theory of Everything",
        12: "Electroman Adventures",
        13: "Clubstep",
        14: "Electrodynamix",
        15: "Hexagon Force",
        16: "Blast Processing",
        17: "Theory of Everything 2",
        18: "Geometrical Dominator",
        19: "Deadlocked",
        20: "Fingerdash",
        21: "Dash"
    }

    version_map = {
        1: "1.0",
        2: "1.1",
        3: "1.2",
        4: "1.3",
        5: "1.4",
        6: "1.5",
        7: "1.6",
        10: "1.7",
        18: "1.8",
        19: "1.9",
        20: "2.0",
        21: "2.1",
        22: "2.2",
    }

    demon_difficulty_map = {
        3: "Easy demon",
        4: "Medium demon",
        0: "Hard demon",
        5: "Insane demon",
        6: "Extreme demon",
    }

    epic_difficulty_map = {
        1: "epic",
        2: "legendary",
        3: "mythic",
    }

    length_difficulty_map = {
        0: "tiny",
        1: "short",
        2: "medium",
        3: "long",
        4: "xl",
        5: "platformer",
    }

    headers = {
        "User-Agent": ""
    }

    df = pd.read_excel(r'c:\Users\elias\Downloads\Easiest DemonList.xlsx')

    data_dict = {}

    for columna in df.columns:
        data_dict[columna] = df[columna].tolist()

    for i in range(len(data_dict["Posición"])):
        data = {
            "str": data_dict["ID"][i],
            "type": "0",
            "secret": "Wmfd2893gb7",
        }

        url = "http://www.boomlings.com/database/getGJLevels21.php"

        req = requests.post(url=url, data=data, headers=headers)
        text = req.text.split("#")

        print("text[0]")
        print(text[0])

        level_data = re.findall(r'[^:]+:[^:]+', text[0])

        level_dictionary = {}
        for item in level_data:
            key, value = item.split(':')
            level_dictionary[key] = value

        creator_data = text[1]
        song_data = text[2].split("~|~")

        if song_data != ['']:
            song_dictionary = {song_data[i]: song_data[i + 1] for i in range(0, len(song_data), 2)}
        else:
            song_dictionary = {}

        print("level_dictionary")
        print(level_dictionary)

        level_dict = {"level_id": level_dictionary["1"],
                    "level_name": level_dictionary["2"],
                    "level_version": level_dictionary["5"],
                    "creator_id": level_dictionary["6"],
                    "if_difficulty": int(level_dictionary["8"]) == 10,
                    "difficulty": difficulty_map.get(int(level_dictionary["9"]), "unknown"),
                    "downloads": level_dictionary["10"],
                    "official_song": song_map.get(int(level_dictionary["12"]), "unknown") if not(song_dictionary) else None,
                    "version_game": version_map.get(int(level_dictionary["13"]), None),
                    "likes": level_dictionary["14"],
                    "demon": int(level_dictionary.get("17", 0)) == 1 if level_dictionary.get("17") else False,
                    "demon_difficulty": demon_difficulty_map.get(int(level_dictionary["43"]), "unknown") if level_dictionary.get("17") else None,
                    "stars": level_dictionary["18"],
                    "feature_score": level_dictionary["19"],
                    "epic": epic_difficulty_map.get(int(level_dictionary["42"]), None) if level_dictionary.get("42") else None,
                    "object_count": level_dictionary["45"],
                    "description": base64.urlsafe_b64decode(level_dictionary.get("3") + "==").decode('utf-8') if level_dictionary.get("3") else None,
                    "length": length_difficulty_map.get(int(level_dictionary["15"]), "unknown"),
                    "original_level_id": level_dictionary["30"],
                    "two_players": int(level_dictionary["31"]) == 1,
                    "number_of_coins": level_dictionary["37"],
                    "verified_coins": int(level_dictionary["38"]) == 1,
                    "stars_requested": level_dictionary["39"],
                    "custom_song_id": level_dictionary["35"],
                    "mode": "platformer" if int(level_dictionary.get("15")) == 5 else "classic",
                    }

        if creator_data:
            creator_dict = {"user_id": creator_data.split(":")[0],
                        "username": creator_data.split(":")[1],
                        "account_id": creator_data.split(":")[2],
                        }
        else:
            creator_dict = {}

        print(level_dict["feature_score"])
        print(level_dict["feature_score"])
        print(level_dict["feature_score"])
        print(level_dict["feature_score"])
        print(level_dict["feature_score"])

        if song_dictionary:
            song_dict = {"song_id": song_dictionary["1"],
                            "name": song_dictionary["2"],
                            "artist_id": song_dictionary["3"],
                            "artist_name": song_dictionary["4"],
                            "size_mb": song_dictionary["5"],
                            "link": unquote(song_dictionary["10"]),
                            "youtube_channel_url": f'https://www.youtube.com/channel/{song_dictionary.get("7")}' if song_dictionary.get("7") else None,
                            "is_verified": int(song_dictionary["8"]) == 1,
                            }
        else:
            song_dict = {"song_id": None,
                            "name": level_dict["official_song"],
                            "artist_id": None,
                            "artist_name": None,
                            "size_mb": None,
                            "link": None,
                            "youtube_channel_url": None,
                            "is_verified": None,
                            }

        page_dict = {"total_pages": text[3].split(":")[0],
                    "actual_page": text[3].split(":")[1],
                    "number_of_levels": text[3].split(":")[2],
                    }

        hash_dict = {"hash": text[4].split(":")[0]}

        print()
        print()
        print()
        print()
        print()
        print(f"Level {i + 1}")
        print()
        print(level_dict)
        print()
        print(creator_dict)
        print()
        print(song_dict)

        if level_dict["epic"]:
            type = level_dict["epic"]
        else:
            if int(level_dict["feature_score"]) > 0:
                type = "featured"
            else:
                type = None
        try:
            demon = Demon.objects.get(level_id=int(level_dict["level_id"]))

            try:
                with open(f"c:/Users/elias/OneDrive/Imágenes/Easiest/{demon.level_id}.png", "rb") as archivo:
                    archivo_django = File(archivo)

                    demon.photo.save(f"{demon.level_id}.png", archivo_django, save=True)
            except:
                pass
            demon.level = data_dict["Nombre"][i]
            demon.category = "rated"
            demon.downloads = level_dict["downloads"]
            demon.likes = level_dict["likes"]
            demon.type = type
            demon.length = level_dict["length"]
            demon.two_players = level_dict["two_players"]
            demon.number_of_coins = level_dict["number_of_coins"]
            demon.song_id = song_dict["song_id"]
            demon.song_name = song_dict["name"]
            demon.artist_name = song_dict["artist_name"]
            demon.song_size = song_dict["size_mb"]
            if song_dict["song_id"]:
                demon.song_link = f'https://www.newgrounds.com/audio/listen/{song_dict["song_id"]}'
            demon.easiest_position = data_dict["Posición"][i]
            demon.verification_video = data_dict["Vídeo"][i]
            if data_dict["Vídeo"][i][:16] == "https://youtu.be":
                verification_video_embed = 'https://www.youtube.com/embed/' + data_dict["Vídeo"][i].split('/')[3]
            elif data_dict["Vídeo"][i][:29] == "https://www.youtube.com/watch":
                verification_video_embed = 'https://www.youtube.com/embed/' + data_dict["Vídeo"][i].split('=')[1]
            demon.verification_video_embed = verification_video_embed
            demon.save()
        except:
            demon = Demon.objects.create(level=level_dict["level_name"],
                                        description=level_dict["description"],
                                        creator=creator_dict.get("username", None),
                                        verifier=creator_dict.get("username", None),
                                        photo="",
                                        verification_video_embed="",
                                        verification_video="",
                                        level_id=level_dict["level_id"],
                                        object_count=level_dict["object_count"] if level_dict["object_count"] else None,
                                        demon_difficulty=level_dict["demon_difficulty"],
                                        update_created=level_dict["version_game"],
                                        category="rated",
                                        mode=level_dict["mode"],
                                        downloads=level_dict["downloads"],
                                        likes=level_dict["likes"],
                                        type=type,
                                        length=level_dict["length"],
                                        two_players=level_dict["two_players"],
                                        number_of_coins=level_dict["number_of_coins"],
                                        song_id=song_dict["song_id"],
                                        song_name=song_dict["name"],
                                        artist_name=song_dict["artist_name"],
                                        song_size=song_dict["size_mb"],
                                        song_link=f'https://www.newgrounds.com/audio/listen/{song_dict["song_id"]}' if song_dict["song_id"] else None,
                                        )
            
            try:
                with open(f"c:/Users/elias/OneDrive/Imágenes/Easiest/{demon.level_id}.png", "rb") as archivo:
                    archivo_django = File(archivo)

                    demon.photo.save(f"{demon.level_id}.png", archivo_django, save=True)
            except:
                pass
            demon.easiest_position = data_dict["Posición"][i]
            demon.verification_video = data_dict["Vídeo"][i]
            if data_dict["Vídeo"][i][:16] == "https://youtu.be":
                verification_video_embed = 'https://www.youtube.com/embed/' + data_dict["Vídeo"][i].split('/')[3]
            elif data_dict["Vídeo"][i][:29] == "https://www.youtube.com/watch":
                verification_video_embed = 'https://www.youtube.com/embed/' + data_dict["Vídeo"][i].split('=')[1]
            demon.verification_video_embed = verification_video_embed
            demon.save()

        if i % 10 == 0:
            time.sleep(5)

def shitty_list():

    difficulty_map = {
        0: "unrated",
        10: "easy",
        20: "normal",
        30: "hard",
        40: "harder",
        50: "insane/demon"
    }

    song_map = {
        0: "Stereo Madness",
        1: "Back on Track",
        2: "Polargeist",
        3: "Dry Out",
        4: "Base After Base",
        5: "Can't Let Go",
        6: "Jumper",
        7: "Time Machine",
        8: "Cycles",
        9: "xStep",
        10: "Clutterfunk",
        11: "Theory of Everything",
        12: "Electroman Adventures",
        13: "Clubstep",
        14: "Electrodynamix",
        15: "Hexagon Force",
        16: "Blast Processing",
        17: "Theory of Everything 2",
        18: "Geometrical Dominator",
        19: "Deadlocked",
        20: "Fingerdash",
        21: "Dash"
    }

    version_map = {
        1: "1.0",
        2: "1.1",
        3: "1.2",
        4: "1.3",
        5: "1.4",
        6: "1.5",
        7: "1.6",
        10: "1.7",
        18: "1.8",
        19: "1.9",
        20: "2.0",
        21: "2.1",
        22: "2.2",
    }

    demon_difficulty_map = {
        3: "Easy demon",
        4: "Medium demon",
        0: "Hard demon",
        5: "Insane demon",
        6: "Extreme demon",
    }

    epic_difficulty_map = {
        1: "epic",
        2: "legendary",
        3: "mythic",
    }

    length_difficulty_map = {
        0: "tiny",
        1: "short",
        2: "medium",
        3: "long",
        4: "xl",
        5: "platformer",
    }

    headers = {
        "User-Agent": ""
    }

    df = pd.read_excel(r'c:\Users\elias\Downloads\Shitty List.xlsx')

    data_dict = {}

    for columna in df.columns:
        data_dict[columna] = df[columna].tolist()

    for i in range(len(data_dict["Posición"])):

        data = {
            "str": data_dict["ID"][i],
            "type": "0",
            "secret": "Wmfd2893gb7",
        }

        url = "http://www.boomlings.com/database/getGJLevels21.php"

        req = requests.post(url=url, data=data, headers=headers)
        text = req.text.split("#")

        print("text[0]")
        print(text[0])

        level_data = re.findall(r'[^:]+:[^:]+', text[0])

        level_dictionary = {}
        for item in level_data:
            key, value = item.split(':')
            level_dictionary[key] = value

        creator_data = text[1]
        song_data = text[2].split("~|~")

        if song_data != ['']:
            song_dictionary = {song_data[i]: song_data[i + 1] for i in range(0, len(song_data), 2)}
        else:
            song_dictionary = {}

        print("level_dictionary")
        print(level_dictionary)

        level_dict = {"level_id": level_dictionary["1"],
                    "level_name": level_dictionary["2"],
                    "level_version": level_dictionary["5"],
                    "creator_id": level_dictionary["6"],
                    "if_difficulty": int(level_dictionary["8"]) == 10,
                    "difficulty": difficulty_map.get(int(level_dictionary["9"]), "unknown"),
                    "downloads": level_dictionary["10"],
                    "official_song": song_map.get(int(level_dictionary["12"]), "unknown") if not(song_dictionary) else None,
                    "version_game": version_map.get(int(level_dictionary["13"]), None),
                    "likes": level_dictionary["14"],
                    "demon": int(level_dictionary.get("17", 0)) == 1 if level_dictionary.get("17") else False,
                    "demon_difficulty": demon_difficulty_map.get(int(level_dictionary["43"]), "unknown") if level_dictionary.get("17") else None,
                    "stars": level_dictionary["18"],
                    "feature_score": level_dictionary["19"],
                    "epic": epic_difficulty_map.get(int(level_dictionary["42"]), None) if level_dictionary.get("42") else None,
                    "object_count": level_dictionary["45"],
                    "description": base64.urlsafe_b64decode(level_dictionary.get("3") + "==").decode('utf-8') if level_dictionary.get("3") else None,
                    "length": length_difficulty_map.get(int(level_dictionary["15"]), "unknown"),
                    "original_level_id": level_dictionary["30"],
                    "two_players": int(level_dictionary["31"]) == 1,
                    "number_of_coins": level_dictionary["37"],
                    "verified_coins": int(level_dictionary["38"]) == 1,
                    "stars_requested": level_dictionary["39"],
                    "custom_song_id": level_dictionary["35"],
                    "mode": "platformer" if int(level_dictionary.get("15")) == 5 else "classic",
                    }

        if creator_data:
            creator_dict = {"user_id": creator_data.split(":")[0],
                        "username": creator_data.split(":")[1],
                        "account_id": creator_data.split(":")[2],
                        }
        else:
            creator_dict = {}

        if song_dictionary:
            song_dict = {"song_id": song_dictionary["1"],
                            "name": song_dictionary["2"],
                            "artist_id": song_dictionary["3"],
                            "artist_name": song_dictionary["4"],
                            "size_mb": song_dictionary["5"],
                            "link": unquote(song_dictionary["10"]),
                            "youtube_channel_url": f'https://www.youtube.com/channel/{song_dictionary.get("7")}' if song_dictionary.get("7") else None,
                            "is_verified": int(song_dictionary["8"]) == 1,
                            }
        else:
            song_dict = {"song_id": None,
                            "name": level_dict["official_song"],
                            "artist_id": None,
                            "artist_name": None,
                            "size_mb": None,
                            "link": None,
                            "youtube_channel_url": None,
                            "is_verified": None,
                            }

        page_dict = {"total_pages": text[3].split(":")[0],
                    "actual_page": text[3].split(":")[1],
                    "number_of_levels": text[3].split(":")[2],
                    }

        hash_dict = {"hash": text[4].split(":")[0]}

        print()
        print()
        print()
        print()
        print()
        print(f"Level {i + 1}")
        print()
        print(level_dict)
        print()
        print(creator_dict)
        print()
        print(song_dict)

        if level_dict["epic"]:
            type = level_dict["epic"]
        else:
            if int(level_dict["feature_score"]) > 0:
                type = "featured"
            else:
                type = None
        try:
            demon = Demon.objects.get(level_id=int(level_dict["level_id"]))

            with open(f"c:/Users/elias/Downloads/Miniaturas ShittyList/Miniaturas ShittyList/{level_dict['level_id']}.png", "rb") as archivo:
                archivo_django = File(archivo)

                demon.photo.save(f"{level_dict['level_id']}.png", archivo_django, save=True)
            demon.level = data_dict["Nombre"][i]
            demon.category = "shitty"
            demon.downloads = level_dict["downloads"]
            demon.likes = level_dict["likes"]
            demon.type = type
            demon.length = level_dict["length"]
            demon.two_players = level_dict["two_players"]
            demon.number_of_coins = level_dict["number_of_coins"]
            demon.song_id = song_dict["song_id"]
            demon.song_name = song_dict["name"]
            demon.artist_name = song_dict["artist_name"]
            demon.song_size = song_dict["size_mb"]
            if song_dict["song_id"]:
                demon.song_link = f'https://www.newgrounds.com/audio/listen/{song_dict["song_id"]}'
            demon.save()
        except:
            demon = Demon.objects.create(level=data_dict["Nombre"][i],
                                        description=level_dict["description"],
                                        creator=creator_dict.get("username", None),
                                        verifier=creator_dict.get("username", None),
                                        photo="",
                                        verification_video_embed="",
                                        verification_video="",
                                        level_id=level_dict["level_id"],
                                        object_count=level_dict["object_count"] if level_dict["object_count"] else None,
                                        demon_difficulty=level_dict["demon_difficulty"],
                                        update_created=level_dict["version_game"],
                                        category="shitty",
                                        mode=level_dict["mode"],
                                        downloads=level_dict["downloads"],
                                        likes=level_dict["likes"],
                                        type=type,
                                        length=level_dict["length"],
                                        two_players=level_dict["two_players"],
                                        number_of_coins=level_dict["number_of_coins"],
                                        song_id=song_dict["song_id"],
                                        song_name=song_dict["name"],
                                        artist_name=song_dict["artist_name"],
                                        song_size=song_dict["size_mb"],
                                        song_link=f'https://www.newgrounds.com/audio/listen/{song_dict["song_id"]}' if song_dict["song_id"] else None,
                                        )

            with open(f"c:/Users/elias/Downloads/Miniaturas ShittyList/Miniaturas ShittyList/{level_dict['level_id']}.png", "rb") as archivo:
                archivo_django = File(archivo)

                demon.photo.save(f"{level_dict['level_id']}.png", archivo_django, save=True)
            demon.shitty_position = data_dict["Posición"][i]
            demon.verification_video = data_dict["Vídeo"][i]
            if data_dict["Vídeo"][i][:16] == "https://youtu.be":
                verification_video_embed = 'https://www.youtube.com/embed/' + data_dict["Vídeo"][i].split('/')[3]
            elif data_dict["Vídeo"][i][:29] == "https://www.youtube.com/watch":
                verification_video_embed = 'https://www.youtube.com/embed/' + data_dict["Vídeo"][i].split('=')[1]
            demon.verification_video_embed = verification_video_embed
            demon.save()

        if i % 10 == 0:
            time.sleep(5)

def future_list():

    df = pd.read_excel(r'c:\Users\elias\Downloads\FutureList.xlsx')

    data_dict = {}


    for columna in df.columns:
        data_dict[columna] = df[columna].tolist()

    for i in range(len(data_dict["Name"])):
        try:
            demon = Demon.objects.get(level=data_dict["Name"][i],
                                        creator=data_dict["Level Creator"][i],
                                        category="future",
                                        )
            demon.verifier=str(data_dict["Verifying by"][i]) if not(str(data_dict["Verifying by"][i]) in ["Open verification", "nan"]) else "Open verification" if (data_dict["Level Status"][i] != "Not finished") and not(str(data_dict["Verifying by"][i]) in ["nan"]) else None
            demon.verification_status=data_dict["Level Status"][i]
            demon.verification_record = int(data_dict["Level Record"][i]) if str(data_dict["Level Record"][i]).isdigit() else None
            demon.verification_video=data_dict["Video"][i]
            demon.level_id = data_dict["ID"][i] if not pd.isnull(data_dict["ID"][i]) else None
            demon.demon_difficulty="Extreme demon"
            demon.update_created="2.2"
            demon.category="future"
            demon.mode=data_dict["Mode"][i].lower()
            demon.future_position=i+1
        except:
            demon = Demon.objects.create(level=data_dict["Name"][i],
                                        creator=data_dict["Level Creator"][i],
                                        verifier=str(data_dict["Verifying by"][i]) if str(data_dict["Verifying by"][i]) != "Open verification" else "Open verification" if data_dict["Level Status"][i] != "Not finished" else None,
                                        verification_status=data_dict["Level Status"][i],
                                        verification_record = int(data_dict["Level Record"][i]) if str(data_dict["Level Record"][i]).isdigit() else None,
                                        verification_video=data_dict["Video"][i],
                                        level_id = data_dict["ID"][i] if not pd.isnull(data_dict["ID"][i]) else None,
                                        demon_difficulty="Extreme demon",
                                        update_created="2.2",
                                        category="future",
                                        mode=data_dict["Mode"][i].lower(),
                                        future_position=i+1
                                        )

        if data_dict["Video"][i][:16] == "https://youtu.be":
            verification_video_embed = 'https://www.youtube.com/embed/' + data_dict["Video"][i].split('/')[3]
        elif data_dict["Video"][i][:29] == "https://www.youtube.com/watch":
            verification_video_embed = 'https://www.youtube.com/embed/' + data_dict["Video"][i].split('=')[1]
        demon.verification_video_embed = verification_video_embed
        demon.save()

def deathless_list():

    df = pd.read_excel(r'c:\Users\IK\Downloads\Platformer Demon Deathless List (1) (3).xlsx')

    data_dict = {}

    for columna in df.columns:
        data_dict[columna] = df[columna].tolist()

    for i in range(105):
        print(f"Level id: {int(data_dict['ID:'][i])}")
        try:
            deathless_list_points = values_list_points_platformer[int(data_dict["Placement:"][i][1:]) - 1]
        except:
            deathless_list_points = 0
        try:
            demon = Demon.objects.get(level_id=int(data_dict["ID:"][i]))
            demon.deathless_list_points = deathless_list_points
            demon.deathless = True
            demon.deathless_position = int(data_dict["Placement:"][i][1:])
            if demon.category == "unrated":
                demon.removed = False
            demon.save()
        except:
            demon = Demon.objects.create(
                level=data_dict["Level"][i],
                deathless_list_points=deathless_list_points,
                level_id=int(data_dict["ID:"][i]),
                update_created="2.2",
                deathless=True,
                mode="platformer",
                deathless_position=int(data_dict["Placement:"][i][1:]),
                length="platformer"
            )
        print(f"Demon creado: {demon.id} - {demon.level}")




def limpiar_fotos():
    profiles = Profile.objects.all()

    parent_dir = os.path.dirname(settings.BASE_DIR)

    for profile in profiles:

        if profile.picture or profile.banner:
            if profile.picture:
                picture_filename = profile.picture.url.split("/")[-1]
                folder_path = "/".join(profile.picture.url.split("/")[:5])
            banner_filename = None
            if profile.banner:
                banner_filename = profile.banner.url.split("/")[-1]
                folder_path = "/".join(profile.banner.url.split("/")[:5])

            ruta_completa = os.path.join(parent_dir, *folder_path.split("/"))

            if os.path.exists(ruta_completa):
                for filename in os.listdir(ruta_completa):

                    if filename != picture_filename and filename != banner_filename:
                        file_path = os.path.join(ruta_completa, filename)
                        if os.path.isfile(file_path):
                            send2trash.send2trash(file_path)

    demons = Demon.objects.all()

    pictures_filenames = []
    for demon in demons:

        if demon.photo:
            picture_filename = demon.photo.url.split("/")[-1]
            pictures_filenames.append(picture_filename)

            folder_path = "/".join(demon.photo.url.split("/")[:4])

    ruta_completa = os.path.join(parent_dir, *folder_path.split("/"))

    if os.path.exists(ruta_completa):
        for filename in os.listdir(ruta_completa):

            if not(filename in pictures_filenames):
                file_path = os.path.join(ruta_completa, filename)
                if os.path.isfile(file_path):
                    send2trash.send2trash(file_path)

    countries = Country.objects.all()

    pictures_filenames = []
    for country in countries:

        if country.picture:
            picture_filename = country.picture.url.split("/")[-1]
            pictures_filenames.append(picture_filename)

            folder_path = "/".join(country.picture.url.split("/")[:4])

    ruta_completa = os.path.join(parent_dir, *folder_path.split("/"))

    print(folder_path)
    print(pictures_filenames)

    if os.path.exists(ruta_completa):
        for filename in os.listdir(ruta_completa):
            print("filename1")
            print(filename)
            if not(filename in pictures_filenames):
                print("filename22")
                print(filename)
                file_path = os.path.join(ruta_completa, filename)
                if os.path.isfile(file_path):
                    send2trash.send2trash(file_path)

def limpiar_campo_fotos():
    profiles = Profile.objects.all().order_by("id")

    parent_dir = os.path.dirname(settings.BASE_DIR)

    for profile in profiles:
        if profile.picture:
            if profile.picture:
                folder_path = "/".join(profile.picture.url.split("/")[:5])

            ruta_completa = os.path.join(parent_dir, *folder_path.split("/"))

            if not(os.path.exists(ruta_completa)):
                profile.picture = None
        if profile.banner:
            if profile.banner:
                folder_path = "/".join(profile.banner.url.split("/")[:5])

            ruta_completa = os.path.join(parent_dir, *folder_path.split("/"))

            if not(os.path.exists(ruta_completa)):
                profile.banner = None
        validate = URLValidator()
        try:
            validate(profile.youtube_channel)
        except ValidationError as e:
            profile.youtube_channel = None
        validate = URLValidator()
        try:
            validate(profile.twitter)
        except ValidationError as e:
            profile.twitter = None
        validate = URLValidator()
        try:
            validate(profile.twitch)
        except ValidationError as e:
            profile.twitch = None
        validate = URLValidator()
        try:
            validate(profile.facebook)
        except ValidationError as e:
            profile.facebook = None
        profile.save()
                

def crear_grupos():

    grupo = Group.objects.get(name="List Leader")
    usuarios = grupo.user_set.all()
    list_leaders = [usuario.id for usuario in usuarios]

    grupo = Group.objects.get(name="List Helper")
    usuarios = grupo.user_set.all()
    list_helpers = [usuario.id for usuario in usuarios]

    grupo = Group.objects.get(name="Platformer List Leader")
    usuarios = grupo.user_set.all()
    platformer_list_leaders = [usuario.id for usuario in usuarios]

    grupos = Group.objects.filter(name__in=["List Helper", "List Leader", "Platformer List Leader"])
    grupos.delete()

    nombres_grupos = ["All DemonList Editor", "Classic Challenge List Helper", "Classic Challenge List Leader", "Classic Rated List Helper", "Classic Rated List Leader", 
        "Classic Shitty List Helper", "Classic Shitty List Leader", "Classic Unrated List Helper", "Classic Unrated List Leader", "General", "List Admin", 
        "Platformer Challenge List Helper", "Platformer Challenge List Leader", "Platformer Rated List Helper", "Platformer Rated List Leader", "Platformer Unrated List Helper", 
        "Platformer Unrated List Leader", "Easiest DemonList Leader", "Subscriber"]

    for nombre_grupo in nombres_grupos:
        Group.objects.get_or_create(name=nombre_grupo)

    group = Group.objects.get(name='List Admin')
    users = User.objects.filter(pk__in=list_leaders)
    for user in users:
        if user.id != 389:
            user.groups.add(group)
        else:
            group_ryexus_1 = Group.objects.get(name='Classic Rated List Helper')
            group_ryexus_2 = Group.objects.get(name='Classic Unrated List Helper')
            group_ryexus_3 = Group.objects.get(name='Classic Challenge List Helper')
            user.groups.add(group_ryexus_1, group_ryexus_2, group_ryexus_3)

    group_1 = Group.objects.get(name='Platformer Rated List Helper')
    group_2 = Group.objects.get(name='Platformer Unrated List Helper')
    group_3 = Group.objects.get(name='Platformer Challenge List Helper')
    users = User.objects.filter(pk__in=list_helpers)
    for user in users:
        user.groups.add(group_1, group_2, group_3)

    group_classic_rated = Group.objects.get(name='Classic Rated List Leader')
    users = User.objects.filter(pk__in=[389, 3988, 3763])
    for user in users:
        user.groups.add(group_classic_rated)

    group_classic_unrated = Group.objects.get(name='Classic Unrated List Leader')
    group_classic_challenge = Group.objects.get(name='Classic Challenge List Leader')
    group_platformer_unrated = Group.objects.get(name='Platformer Unrated List Leader')
    group_platformer_challenge = Group.objects.get(name='Platformer Challenge List Leader')
    users = User.objects.filter(pk__in=[4])
    for user in users:
        user.groups.add(group_classic_unrated, group_classic_challenge, group_platformer_unrated, group_platformer_challenge)

    group_classic_shitty = Group.objects.get(name='Classic Shitty List Leader')
    users = User.objects.filter(pk__in=[4730])
    for user in users:
        user.groups.add(group_classic_shitty)

    group_platformer_rated = Group.objects.get(name='Platformer Rated List Leader')
    users = User.objects.filter(pk__in=[4, 953, 2404, 414])
    for user in users:
        user.groups.add(group_platformer_rated)

    group_easiest = Group.objects.get(name='Easiest DemonList Leader')
    users = User.objects.filter(pk__in=[2864, 4517])
    for user in users:
        user.groups.add(group_easiest)

def easiest_demonlist_minis():
    demons = Demon.objects.filter(easiest_position__isnull=False)
    for demon in demons:
        with open(f"c:/Users/elias/OneDrive/Imágenes/Easiest/{demon.level_id}.png", "rb") as archivo:
            archivo_django = File(archivo)

            demon.photo.save(f"{demon.level_id}.png", archivo_django, save=True)

def crear_excel():

    data = {}

    demons = Demon.objects.filter(Q(all_position__isnull=False) | Q(challenge_position__isnull=False) | Q(easiest_position__isnull=False) | Q(shitty_position__isnull=False)).filter(Q(object_count=65535) | Q(object_count=0) | Q(object_count=None))
    demons_name = list(demons.values_list("level", flat=True))
    demons_level_id = list(demons.values_list("level_id", flat=True))

    data["Nombre"] = demons_name
    data["Level ID"] = demons_level_id

    df = pd.DataFrame(data)

    # Especificar el nombre del archivo Excel
    nombre_archivo = 'datos.xlsx'

    # Guardar el DataFrame en el archivo Excel
    df.to_excel(nombre_archivo, index=False)

    print(f'Se ha creado el archivo Excel "{nombre_archivo}"')

def notification_demons_to_parameter_demons():
    notifications = Notification.objects.filter(Q(action="record_accepted") | Q(action="record_rejected") | Q(action="record_under_consideration") | Q(action="demon_beaten"))
    notifications.update(demon_parameter=Subquery(Demon.objects.filter(level=OuterRef("parameter")).values("id")))

def eliminar_usuario_vacio():
    try:
        User.objects.get(id=1853).delete()
    except:
        pass

def quitar_demon_difficulty_unrated():
    Demon.objects.filter(demon_difficulty="Unrated").update(demon_difficulty=None)

def funcion_final_migracion_1_2():

    """PASO 1: USAR TUNEL SSH Y CONECTARME A LA BASE DE DATOS DE PRODUCCIÓN 
        PASO 2: BORRAR EL CAMPO REMOVED DE LA TABLA DEMON 
        PASO 3: BORRAR EL 0065_profile_claimable.py de la tabla django_migrations
        PASO 4: CORRER EL PYTHON MANAGE.PY MIGRATE
    """

    """AGREGAR Y ARREGLAR LA INFO DE LOS DEMONS DE LAS LISTAS"""
    #fix_demons_of_all_lists()

    """LIMPIAR FOTOS DE LA BASE DE DATOS (CORRER EN PRODUCCIÓN, PERO ANTES HAZ UN RESPALDO)"""
    #limpiar_fotos()

    """AGREGAR ESTAS LISTAS"""
    #shitty_list()
    #easiest_demon_list()
    #future_list()

    """DAR LIST POINTS A LA SHITTY LIST"""
    #order_list_points("classic", ["shitty"])

    """CREAR ROLES Y ASIGNARLOS"""
    #crear_grupos()

    """ASIGNAR DEMON_PARAMETER A CADA NOTIFICACIÓN QUE TENGA DEMON"""
    #notification_demons_to_parameter_demons()

    """ELIMINAR USUARIO VACÍO"""
    #eliminar_usuario_vacio()

    """QUITAR LA DEMON DIFFICULTY UNRATED"""
    #quitar_demon_difficulty_unrated()

    """PASOS PARA QUITAR EL COUNTDOWN TIMER
        PASO 1: QUITAR LÍNEA 46 Y 47 EN PLATFORMDEMONLIST/MIDDLEWARE.PY
        PASO 2: QUITAR LÍNEAS 12-16 EN DEMONLIST/URLS.PY
        PASO 3: QUITAR LÍNEAS 48-59 EN DEMONLIST/VIEWS.PY
        PASO 4: QUITAR LÍNEA 19 Y 327 EN NAV.HTML
        PASO 5: QUITAR LÍNEAS 407-439 EN EL MAIN.CSS
        PASO 6: BORRAR COUNTDOWN.HTML
    """

    """AGREGAR TODOS LOS DEMONS (FUNCIÓN DE 6 HORAS)"""
    #add_all_demons(0)

    # update_players_list_points_all("classic", ["rated"])
    # update_players_list_points_all("classic", ["unrated"])
    # update_players_list_points_all("classic", ["challenge"])
    # update_players_list_points_all("platformer", ["rated"])
    # update_players_list_points_all("platformer", ["unrated"])
    # update_players_list_points_all("platformer", ["challenge"])
    # update_countries_list_points_all("classic", ["rated"])
    # update_countries_list_points_all("classic", ["unrated"])
    # update_countries_list_points_all("classic", ["challenge"])
    # update_countries_list_points_all("platformer", ["rated"])
    # update_countries_list_points_all("platformer", ["unrated"])
    # update_countries_list_points_all("platformer", ["challenge"])
    # update_teams_list_points_all("classic", ["rated"])
    # update_teams_list_points_all("classic", ["unrated"])
    # update_teams_list_points_all("classic", ["challenge"])
    # update_teams_list_points_all("platformer", ["rated"])
    # update_teams_list_points_all("platformer", ["unrated"])
    # update_teams_list_points_all("platformer", ["challenge"])




def add_tiny_demonlist_levels():
    # Hacer la solicitud GET a la página
    with open('../Daniela.html', 'r', encoding='utf-8') as archivo:
        # Leer todo el contenido del archivo
        contenido = archivo.read()

    # Imprimir el contenido del archivo

    demons = []

    patron = r"https://i\.ytimg\.com/vi/[a-zA-Z0-9_-]+/mqdefault\.jpg"

    for i in range(100):
        position = contenido.split("<h2>")[i + 1].split(" ")[0][:-1]
        name_with_creator = contenido.split("<h2>")[i + 1].split("</h2>")[0].split(" ")[1:]
        name_parts = []
        creator_parts = []
        continue_name = True
        for part in name_with_creator:
            if part == "by":
                continue_name = False
            if continue_name:
                name_parts.append(part)
            elif part != "by":
                creator_parts.append(part)

        name = " ".join(name_parts)
        creator = " ".join(creator_parts)
        picture = re.findall(patron, contenido.split("data-property-value")[i + 1])[0]
        level_id = contenido.split("h6>ID: ")[i + 1].split("</h6>")[0]
        verifier = contenido.split("Verification")[i + 1].split("<h6>")[1][1:].split(" - ")[0]
        verification_video = contenido.split("Verification")[i + 1].split('href="')[1].split('" target')[0]

        demons.append({'name': name, 'position': position, 'picture': picture, 'level_id': level_id, 'creator': creator, 
                       'verifier': verifier, 'verification_video': verification_video})

    print(demons)

    for demon in demons:
        url = demon["picture"]
        if demon["verification_video"]:
            if demon["verification_video"][:16] == "https://youtu.be":
                verification_video_embed = 'https://www.youtube.com/embed/' + demon["verification_video"].split('/')[3]
            elif demon["verification_video"][:29] == "https://www.youtube.com/watch":
                verification_video_embed = 'https://www.youtube.com/embed/' + demon["verification_video"].split('=')[1]
            else:
                verification_video_embed = None
        else:
            verification_video_embed = None
        directory = r"C:\Users\IK\Pictures\Tiny Levels"
        filename = f"{demon['name']}.jpg"
        file_path = os.path.join(directory, filename)

        # Asegurarse de que el directorio existe
        os.makedirs(directory, exist_ok=True)

        # Descargar la imagen
        response = requests.get(url, stream=True)
        demon_instance = Demon.objects.create(
            level=demon["name"],
            mode="classic",
            category="tiny",
            tiny_position=demon["position"],
            creator=demon["creator"],
            verifier=demon["verifier"],
            verification_video=demon["verification_video"],
            verification_video_embed=verification_video_embed,
            level_id=demon["level_id"],
            update_created="2.2"
        )
        if response.status_code == 200:
            with open(file_path, 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)
            response.close()

            # Crear el objeto Demon
            with open(file_path, 'rb') as img_file:
                demon_instance.photo=File(img_file, name=os.path.basename(file_path))
                demon_instance.save()
            print(f"Objeto Demon creado: {demon_instance}")
        else:
            print(f"Error al descargar la imagen: {response.status_code}")


def add_pemonlist_levels():
    levels_ids = [
        105608796,
        105608980,
        106432861,
        108748094,
    ]

    for level_id in levels_ids:

        response = requests.get(f"https://pemonlist.com/level/{level_id}")
        soup = BeautifulSoup(response.content, 'html.parser')
        level_div = soup.find('div', class_='level')
        spans = level_div.find_all('span')

        rated_position = spans[0].text[1:]
        level = spans[1].text
        creator = spans[2].find_all('p')[0].text
        verifier = level_div.find_all('a')[0].find_all('p')[0].text

        print(f"rated_position: {rated_position}")
        print(f"level: {level}")
        print(f"creator: {creator}")
        print(f"verifier: {verifier}")
        print()

        try:
            demon = Demon.objects.get(level_id=level_id)
            demon.rated_position = rated_position
            demon.all_position = rated_position
            demon.save()
        except:
            demon = Demon.objects.create(
                level=level,
                rated_position=rated_position,
                all_position=rated_position,
                creator=creator,
                verifier=verifier,
                level_id=level_id,
            )


    demons = Demon.objects.filter(mode="platformer", category="rated")

    for demon in demons:
        print(f"demon: {demon}")
        print(f"level_id: {demon.level_id}")
        try:
            response = requests.get(f"https://pemonlist.com/level/{demon.level_id}")
            soup = BeautifulSoup(response.content, 'html.parser')
            level_div = soup.find('div', class_='level')
            spans = level_div.find_all('span')

            rated_position = spans[0].text[1:]

            demon.rated_position = rated_position
            demon.all_position = rated_position
            demon.save()
        except:
            pass


def edit_pemonlist_levels():
    demons = Demon.objects.filter(mode="platformer", category="rated", rated_position__isnull=False, photo=None)

        

def impossible_list():

    df = pd.read_excel(r'c:\Users\IK\Downloads\ipll (1).xlsx')

    data_dict = {}

    for columna in df.columns:
        data_dict[columna] = df[columna].tolist()

    for i in range(48):
        try:
            level_id = int(data_dict["Level id"][i])
        except:
            level_id = None
        print(f"Level id: {level_id}")
        try:
            impossible_list_points = values_list_points_platformer[int(data_dict["Posición"][i]) - 1]
        except:
            impossible_list_points = 0

        try:
            if data_dict["Video Verificacion"][i]:
                if data_dict["Video Verificacion"][i][:16] == "https://youtu.be":
                    verification_video = data_dict["Video Verificacion"][i]
                    verification_video_embed = 'https://www.youtube.com/embed/' + data_dict["Video Verificacion"][i].split('/')[3]
                else:
                    verification_video = None
                    verification_video_embed = None
            else:
                verification_video = None
                verification_video_embed = None
        except:
            verification_video = None
            verification_video_embed = None


        try:
            demon = Demon.objects.get(category="unrated", level_id=int(data_dict["Level id"][i]))
            demon.impossible_list_points = impossible_list_points
            demon.impossible_position = int(data_dict["Posición"][i])
            demon.save()
        except:

            """demon = Demon.objects.create(
                level=data_dict["Level"][i],
                list_points=impossible_list_points,
                level_id=level_id,
                update_created="2.2",
                mode="platformer",
                category="impossible",
                impossible_position=int(data_dict["Posición"][i]),
                length="platformer",
                verification_video=verification_video,
                verification_video_embed=verification_video_embed,
                creator=data_dict["Creator"][i],
            )"""
    order_list_points("platformer", "rated")



def spam_challenge_list():

    df = pd.read_excel(r'c:\Users\IK\Downloads\SCL Data (2).xlsx')

    data_dict = {}

    for columna in df.columns:
        data_dict[columna] = df[columna].tolist()

    for i in range(111):
        try:
            level_id = int(data_dict["ID"][i])
        except:
            level_id = None
        print(f"Level id: {level_id}")
        try:
            spam_list_points = values_list_points_spam[i]
        except:
            spam_list_points = 0

        if data_dict["Verifier"][i]:
            verifier = data_dict["Verifier"][i]
        else:
            verifier = None

        try:
            if data_dict["Verification Video"][i]:
                if data_dict["Verification Video"][i][:16] == "https://youtu.be":
                    verification_video = data_dict["Verification Video"][i]
                    verification_video_embed = 'https://www.youtube.com/embed/' + verification_video.split('/')[3]
                elif data_dict["Verification Video"][i][:29] == "https://www.youtube.com/watch":
                    verification_video = data_dict["Verification Video"][i]
                    verification_video_embed = 'https://www.youtube.com/embed/' + verification_video.split('=')[1]
                else:
                    verification_video = None
                    verification_video_embed = None
            else:
                verification_video = None
                verification_video_embed = None
        except:
            verification_video = None
            verification_video_embed = None

        try:
            demon = Demon.objects.get(category="spam", level_id=int(data_dict["ID"][i]))
            demon.list_points = spam_list_points
            demon.spam_position = int(i) + 1
            demon.save()
        except:

            demon = Demon.objects.create(
                level=data_dict["Level Name"][i],
                list_points=spam_list_points,
                level_id=level_id,
                update_created="2.2",
                mode="classic",
                category="spam",
                spam_position=int(i) + 1,
                verification_video=verification_video,
                verification_video_embed=verification_video_embed,
                creator=data_dict["Creator"][i],
                verifier=verifier,
            )

def impossible_tiny_list():

    levels = [
        {"position": 1, "level_name": "Helibump", "creator": "crmsnn", "level_id": "102654394"},
        {"position": 2, "level_name": "Ballistic despair", "creator": "sakupencheesegd", "level_id": "108997973"},
        {"position": 3, "level_name": "Endless pain", "creator": "ced.", "level_id": "109328333"},
        {"position": 4, "level_name": "Bloodlust", "creator": "ced", "level_id": "109051456"},
        {"position": 5, "level_name": "Prime Grandpa", "creator": "Silent Clubstep", "level_id": "109240992"},
        {"position": 6, "level_name": "Obama space", "creator": "dev", "level_id": "109014989"},
        {"position": 7, "level_name": "I Paid My Taxes", "creator": "SneedleGD", "level_id": "109267791"},
        {"position": 8, "level_name": "Despair", "creator": "sakupencheesegd", "level_id": "108962443"},
        {"position": 9, "level_name": "Heart attack", "creator": "sakupencheesegd", "level_id": "108973124"},
        {"position": 10, "level_name": "Red hot bargain", "creator": "dev", "level_id": "108976168"},
        {"position": 11, "level_name": "7 seconds of pain", "creator": "ced", "level_id": "109058517"},
        {"position": 12, "level_name": "Toxic tiny level", "creator": "sakupencheeesegd and fraternity", "level_id": "108961089"},
        {"position": 13, "level_name": "Scapesshards", "creator": "sakupencheesegd", "level_id": "109152897"},
        {"position": 14, "level_name": "Paranoia", "creator": "sakupencheesegd", "level_id": "109125297"},
        {"position": 15, "level_name": "shut yo 6itch ass up", "creator": "Deceptive", "level_id": "108937482"},
        {"position": 16, "level_name": "They Fear Us", "creator": "YourBarber", "level_id": "108760314"},
        {"position": 17, "level_name": "Dirediredocks", "creator": "fraternity", "level_id": "108936855"},
        {"position": 18, "level_name": "Safe2", "creator": "YourBarber", "level_id": "108914325"},
        {"position": 19, "level_name": "AUTISM CRIME", "creator": "YourBarber", "level_id": "107985891"},
        {"position": 20, "level_name": "sHist", "creator": "mewo", "level_id": "108359671"},
        {"position": 21, "level_name": "Terrible level", "creator": "ced", "level_id": "108432143"},
        {"position": 22, "level_name": "Silent Grandma", "creator": "YourBarber", "level_id": "108961610"},
        {"position": 23, "level_name": "back on track copy", "creator": "YourBarber", "level_id": "108998336"},
        {"position": 24, "level_name": "kendrick lamar", "creator": "YourBarber", "level_id": "107988076"},
        {"position": 25, "level_name": "Ballistic cheese", "creator": "sakupencheesegd", "level_id": "109002649"},
        {"position": 26, "level_name": "The List Is Dead", "creator": "Silent Clubstep", "level_id": "105746761"},
        {"position": 27, "level_name": "Wop Wop", "creator": "YourBarber", "level_id": "109034453"},
        {"position": 28, "level_name": "Slaughterspam", "creator": "YourBarber", "level_id": "108304948"},
        {"position": 29, "level_name": "Sakupening the Chee", "creator": "sakupencheesegd", "level_id": "108904905"},
        {"position": 30, "level_name": "Inviable", "creator": "fraqqer", "level_id": "108638604"},
        {"position": 31, "level_name": "cocmcoc", "creator": "notepicsadguy68", "level_id": "108520834"},
        {"position": 32, "level_name": "Epilepsy simulator", "creator": "fraqqer", "level_id": "108243474"},
        {"position": 33, "level_name": "Pedo Place", "creator": "YourBarber", "level_id": "108956400"},
        {"position": 34, "level_name": "Path", "creator": "Lustre", "level_id": "108186687"},
        {"position": 35, "level_name": "Zoink never clear v2", "creator": "Triangle :3", "level_id": "105490978"},
        {"position": 36, "level_name": "Slaughterer", "creator": "AspectLive", "level_id": "105568552"},
        {"position": 37, "level_name": "Barely 10 seconds", "creator": "Fiesty", "level_id": "107058103"},
        {"position": 38, "level_name": "Impossible for snee", "creator": "sakupencheesegd", "level_id": "109053333"},
        {"position": 39, "level_name": "worst impose le", "creator": "YourBarber", "level_id": "108311534"},
    ]

    for level in levels:
        print(level)

        try:
            level_id = int(level["level_id"])
        except:
            level_id = None
        print(f"Level id: {level_id}")
        try:
            impossible_tiny_list_points = values_list_points_platformer[level["position"] - 1]
        except:
            impossible_tiny_list_points = 0

        try:
            demon = Demon.objects.get(category="impossible_tiny", level_id=level_id)
            demon.list_points = impossible_tiny_list_points
            demon.impossible_tiny_position = level["position"]
            demon.save()
        except:

            demon = Demon.objects.create(
                level=level["level_name"],
                list_points=impossible_tiny_list_points,
                level_id=level_id,
                update_created="2.2",
                mode="classic",
                category="impossible_tiny",
                impossible_tiny_position=level["position"],
                creator=level["creator"],
            )




def pemonlist_level_packs():

    level_packs = [{'id': 2, 'name': 'Tech pack', 'color': 'beginner', 'mode': 'platformer', 'category': 'rated'}, {'id': 3, 'name': '"ling" pack', 'color': 'beginner', 'mode': 'platformer', 'category': 'rated'}, {'id': 4, 'name': 'Beginner pack I', 'color': 'beginner', 'mode': 'platformer', 'category': 'rated'}, {'id': 6, 'name': 'JSAB pack', 'color': 'bronze', 'mode': 'platformer', 'category': 'rated'}, {'id': 7, 'name': 'Beginner pack II', 'color': 'bronze', 'mode': 'platformer', 'category': 'rated'}, {'id': 5, 'name': 'Checkpointless pack I', 'color': 'bronze', 'mode': 'platformer', 'category': 'rated'}, {'id': 8, 'name': 'Jungle pack', 'color': 'silver', 
    'mode': 'platformer', 'category': 'rated'}, {'id': 9, 'name': 'Bossfight pack I', 'color': 'silver', 'mode': 'platformer', 'category': 'rated'}, {'id': 10, 'name': 'OWOSI pack', 'color': 'silver', 'mode': 'platformer', 'category': 'rated'}, {'id': 11, 'name': 'OG pack', 'color': 'gold', 'mode': 'platformer', 'category': 'rated'}, {'id': 12, 'name': 'Zejoant pack', 'color': 'gold', 'mode': 'platformer', 'category': 'rated'}, {'id': 13, 'name': 'Strawberry Jam pack', 'color': 'gold', 'mode': 'platformer', 'category': 'rated'}, {'id': 14, 'name': 'Minigame pack I', 'color': 'amber', 'mode': 'platformer', 'category': 'rated'}, {'id': 15, 'name': 'Puzzle Pack', 'color': 'amber', 'mode': 'platformer', 'category': 'rated'}, {'id': 16, 'name': 'Switch pack', 'color': 'amber', 'mode': 'platformer', 'category': 'rated'}, {'id': 17, 'name': 'Invisible pack', 'color': 'platinum', 'mode': 'platformer', 'category': 'rated'}, {'id': 18, 'name': 'Rain pack', 'color': 'platinum', 
    'mode': 'platformer', 'category': 'rated'}, {'id': 19, 'name': 'Tower pack I', 'color': 'platinum', 'mode': 'platformer', 'category': 'rated'}, {'id': 20, 'name': 'TEK pack', 'color': 'sapphire', 'mode': 'platformer', 'category': 'rated'}, {'id': 21, 'name': 'Mythic pack', 'color': 'sapphire', 'mode': 'platformer', 'category': 'rated'}, {'id': 22, 'name': 'Bossfight Pack II', 'color': 'sapphire', 'mode': 'platformer', 'category': 'rated'}, {'id': 23, 'name': 'Mountain pack', 'color': 
    'jade', 'mode': 'platformer', 'category': 'rated'}, {'id': 24, 'name': 'Bossfight pack III', 'color': 'jade', 'mode': 'platformer', 'category': 'rated'}, {'id': 25, 'name': 'KingEggplant987 pack', 'color': 'jade', 'mode': 'platformer', 'category': 'rated'}, {'id': 26, 'name': 'qalli pack', 'color': 'emerald', 'mode': 'platformer', 'category': 'rated'}, {'id': 27, 'name': 'Celeste pack', 'color': 'emerald', 'mode': 'platformer', 'category': 'rated'}, {'id': 28, 'name': 'XXXL pack I', 'color': 'emerald', 'mode': 'platformer', 'category': 'rated'}, {'id': 29, 'name': 'Black Hole pack', 'color': 'ruby', 'mode': 'platformer', 'category': 'rated'}, {'id': 30, 'name': 'Minigame Pack II', 'color': 'ruby', 'mode': 'platformer', 'category': 'rated'}, {'id': 31, 'name': 'Fish pack', 'color': 'ruby', 'mode': 'platformer', 'category': 'rated'}, {'id': 32, 'name': 'JSAB pack II', 'color': 'diamond', 'mode': 'platformer', 'category': 'rated'}, {'id': 33, 'name': 'Adventurer pack', 'color': 'diamond', 'mode': 'platformer', 'category': 'rated'}, {'id': 34, 'name': 'Troll pack', 'color': 'diamond', 'mode': 'platformer', 'category': 'rated'}, {'id': 35, 'name': 'I wanna be the pack', 'color': 'onyx', 'mode': 'platformer', 'category': 'rated'}, {'id': 36, 'name': 'XXXL pack II', 'color': 'onyx', 'mode': 'platformer', 'category': 'rated'}, {'id': 37, 'name': 'Wavedash pack', 'color': 'onyx', 'mode': 'platformer', 'category': 'rated'}, {'id': 38, 'name': 'Tower pack II', 'color': 'amethyst', 'mode': 'platformer', 'category': 'rated'}, {'id': 39, 'name': 'Beat pack', 'color': 'amethyst', 'mode': 'platformer', 'category': 'rated'}, {'id': 40, 'name': 'Custi pack', 'color': 'amethyst', 'mode': 'platformer', 'category': 'rated'}, {'id': 41, 'name': 'Jump King pack', 'color': 'azurite', 'mode': 'platformer', 'category': 'rated'}, {'id': 42, 'name': 'Rainbow pack', 'color': 'azurite', 'mode': 'platformer', 'category': 'rated'}, {'id': 43, 'name': '2-player solo pack', 'color': 'azurite', 'mode': 'platformer', 'category': 'rated'}, {'id': 44, 'name': 'Trials pack', 'color': 'obsidian', 'mode': 'platformer', 'category': 'rated'}, {'id': 45, 'name': "World's Hardest pack", 'color': 'obsidian', 'mode': 'platformer', 'category': 'rated'}, {'id': 46, 'name': 'Checkpointless pack III', 'color': 'obsidian', 'mode': 'platformer', 'category': 'rated'}, {'id': 47, 'name': 'Slope pack', 'color': 'obsidian', 'mode': 'platformer', 'category': 
    'rated'}, {'id': 48, 'name': 'Rage of Age pack I', 'color': 'obsidian', 'mode': 'platformer', 'category': 'rated'}, {'id': 49, 'name': 'Doppelganger pack', 'color': 'obsidian', 'mode': 'platformer', 'category': 'rated'}, {'id': 50, 'name': 'Checkpointless pack II', 'color': 'obsidian', 'mode': 'platformer', 'category': 'rated'}, {'id': 51, 'name': 'Halapeenyo Pack', 'color': 'obsidian', 'mode': 'platformer', 'category': 'rated'}, {'id': 52, 'name': 'Rage of Age pack II', 'color': 'obsidian', 'mode': 'platformer', 'category': 'rated'}, {'id': 53, 'name': 'OG Top 1 pack', 'color': 'obsidian', 'mode': 'platformer', 'category': 'rated'}, {'id': 54, 'name': 'bran pack', 'color': 'obsidian', 'mode': 'platformer', 'category': 'rated'}, {'id': 55, 'name': 'Gimmick pack', 'color': 'obsidian', 'mode': 'platformer', 'category': 'rated'}, {'id': 56, 'name': 'Chill pack', 'color': 'obsidian', 'mode': 'platformer', 'category': 'rated'}, {'id': 57, 'name': '2ItalianCats pack I', 'color': 'obsidian', 'mode': 'platformer', 'category': 'rated'}, {'id': 58, 'name': '2ItalianCats pack II', 'color': 'obsidian', 'mode': 'platformer', 'category': 'rated'}, {'id': 59, 'name': 'PulseN1nja pack', 'color': 'obsidian', 'mode': 'platformer', 'category': 'rated'}, {'id': 60, 'name': 'Archmage pack', 'color': 'obsidian', 'mode': 'platformer', 'category': 'rated'}]

    level_packs_demons = [{'id': 2, 'demons': 3696}, {'id': 2, 'demons': 25}, {'id': 2, 'demons': 20}, {'id': 3, 'demons': 8320}, {'id': 3, 'demons': 8292}, {'id': 3, 'demons': 53}, {'id': 4, 'demons': 11}, {'id': 4, 'demons': 20}, {'id': 4, 'demons': 7}, {'id': 5, 'demons': 3696}, {'id': 5, 'demons': 33}, {'id': 5, 'demons': 12}, {'id': 6, 'demons': 576}, {'id': 6, 'demons': 541}, {'id': 6, 'demons': 8271}, {'id': 7, 'demons': 1}, {'id': 7, 'demons': 322}, {'id': 7, 'demons': 45}, {'id': 8, 'demons': 11}, {'id': 8, 'demons': 619}, {'id': 8, 'demons': 7143}, {'id': 9, 'demons': 584}, {'id': 9, 'demons': 625}, {'id': 9, 'demons': 3617}, {'id': 10, 'demons': 857}, {'id': 10, 'demons': 598}, {'id': 10, 'demons': 542}, {'id': 11, 'demons': 1}, {'id': 11, 'demons': 11}, {'id': 11, 'demons': 15}, {'id': 12, 'demons': 18}, {'id': 12, 'demons': 8053}, {'id': 12, 'demons': 2239}, {'id': 13, 'demons': 8313}, {'id': 13, 'demons': 8307}, {'id': 13, 'demons': 8292}, {'id': 14, 'demons': 5784}, {'id': 
    14, 'demons': 657}, {'id': 14, 'demons': 51}, {'id': 15, 'demons': 857}, {'id': 15, 'demons': 909}, {'id': 15, 'demons': 598}, {'id': 16, 'demons': 48}, {'id': 16, 'demons': 570}, {'id': 16, 'demons': 4416}, {'id': 17, 'demons': 344}, {'id': 17, 'demons': 8295}, {'id': 17, 'demons': 583}, {'id': 18, 'demons': 574}, {'id': 18, 'demons': 6996}, {'id': 18, 'demons': 8270}, {'id': 19, 'demons': 5584}, {'id': 19, 'demons': 322}, {'id': 19, 'demons': 582}, {'id': 20, 'demons': 8}, {'id': 20, 'demons': 626}, {'id': 20, 'demons': 542}, {'id': 21, 'demons': 578}, {'id': 21, 'demons': 8053}, {'id': 21, 'demons': 8054}, {'id': 22, 'demons': 16}, {'id': 22, 'demons': 329}, {'id': 22, 'demons': 10}, {'id': 23, 'demons': 903}, {'id': 23, 'demons': 600}, {'id': 23, 'demons': 15}, {'id': 24, 'demons': 353}, {'id': 24, 'demons': 8074}, {'id': 24, 'demons': 910}, {'id': 25, 'demons': 544}, {'id': 25, 'demons': 8273}, {'id': 25, 'demons': 22}, {'id': 26, 'demons': 8270}, {'id': 26, 
    'demons': 8290}, {'id': 26, 'demons': 6}, {'id': 27, 'demons': 8066}, {'id': 27, 'demons': 13}, {'id': 27, 'demons': 7}, {'id': 28, 'demons': 578}, {'id': 28, 'demons': 8053}, {'id': 28, 'demons': 463}, {'id': 29, 'demons': 329}, {'id': 29, 'demons': 50}, {'id': 29, 'demons': 37}, {'id': 30, 'demons': 40}, {'id': 30, 'demons': 612}, {'id': 30, 'demons': 8023}, {'id': 31, 'demons': 360}, {'id': 31, 'demons': 57}, {'id': 31, 'demons': 618}, {'id': 32, 'demons': 8272}, {'id': 32, 'demons': 30}, {'id': 32, 'demons': 479}, {'id': 33, 'demons': 34}, {'id': 33, 'demons': 540}, {'id': 33, 'demons': 463}, {'id': 34, 'demons': 546}, {'id': 34, 'demons': 
    359}, {'id': 34, 'demons': 7975}, {'id': 35, 'demons': 2}, {'id': 35, 'demons': 8315}, {'id': 35, 'demons': 359}, {'id': 36, 'demons': 8016}, {'id': 36, 'demons': 
    34}, {'id': 36, 'demons': 662}, {'id': 37, 'demons': 904}, {'id': 37, 'demons': 368}, {'id': 37, 'demons': 6}, {'id': 38, 'demons': 3}, {'id': 38, 'demons': 661}, 
    {'id': 38, 'demons': 39}, {'id': 39, 'demons': 17}, {'id': 39, 'demons': 338}, {'id': 39, 'demons': 902}, {'id': 40, 'demons': 626}, {'id': 40, 'demons': 34}, {'id': 40, 'demons': 8031}, {'id': 41, 'demons': 41}, {'id': 41, 'demons': 58}, {'id': 41, 'demons': 21}, {'id': 42, 'demons': 464}, {'id': 42, 'demons': 6}, {'id': 42, 'demons': 39}, {'id': 43, 'demons': 654}, {'id': 43, 'demons': 566}, {'id': 43, 'demons': 31}, {'id': 44, 'demons': 31}, {'id': 44, 'demons': 38}, {'id': 44, 'demons': 455}, {'id': 45, 'demons': 42}, {'id': 45, 'demons': 14}, {'id': 45, 'demons': 455}, {'id': 46, 'demons': 659}, {'id': 46, 'demons': 660}, {'id': 46, 'demons': 38}, {'id': 47, 'demons': 32}, {'id': 47, 'demons': 8}, {'id': 47, 'demons': 611}, {'id': 48, 'demons': 616}, {'id': 48, 'demons': 8241}, {'id': 48, 'demons': 
    46}, {'id': 48, 'demons': 8023}, {'id': 49, 'demons': 616}, {'id': 49, 'demons': 42}, {'id': 49, 'demons': 59}, {'id': 49, 'demons': 14}, {'id': 50, 'demons': 360}, {'id': 50, 'demons': 620}, {'id': 50, 'demons': 374}, {'id': 50, 'demons': 47}, {'id': 51, 'demons': 480}, {'id': 51, 'demons': 41}, {'id': 51, 'demons': 619}, {'id': 51, 'demons': 21}, {'id': 52, 'demons': 562}, {'id': 52, 'demons': 19}, {'id': 52, 'demons': 8042}, {'id': 52, 'demons': 7975}, {'id': 53, 'demons': 24}, {'id': 53, 'demons': 1}, {'id': 53, 'demons': 2}, {'id': 53, 'demons': 3}, {'id': 54, 'demons': 32}, {'id': 54, 'demons': 658}, {'id': 54, 'demons': 638}, {'id': 54, 
    'demons': 655}, {'id': 55, 'demons': 480}, {'id': 55, 'demons': 619}, {'id': 55, 'demons': 8017}, {'id': 55, 'demons': 626}, {'id': 55, 'demons': 2239}, {'id': 56, 'demons': 34}, {'id': 56, 'demons': 611}, {'id': 56, 'demons': 18}, {'id': 56, 'demons': 568}, {'id': 56, 'demons': 542}, {'id': 57, 'demons': 3617}, {'id': 57, 'demons': 8292}, {'id': 57, 'demons': 8041}, {'id': 57, 'demons': 362}, {'id': 57, 'demons': 8017}, {'id': 58, 'demons': 362}, {'id': 58, 'demons': 46}, {'id': 58, 
    'demons': 48}, {'id': 58, 'demons': 20}, {'id': 58, 'demons': 540}, {'id': 59, 'demons': 577}, {'id': 59, 'demons': 901}, {'id': 59, 'demons': 616}, {'id': 59, 'demons': 368}, {'id': 59, 'demons': 464}, {'id': 60, 'demons': 546}, {'id': 60, 'demons': 37}, {'id': 60, 'demons': 902}, {'id': 60, 'demons': 16}, {'id': 60, 'demons': 30}]

    # for level_pack in level_packs:
    #     print(level_pack)

    #     id = int(level_pack["id"])
    #     name = level_pack["name"]
    #     color = level_pack["color"]
    #     mode = level_pack["mode"]
    #     category = level_pack["category"]

    #     demon = LevelPack.objects.create(
    #         id=id,
    #         name=name,
    #         color=color,
    #         mode=mode,
    #         category=category,
    #     )

    for level_pack_demon in level_packs_demons:
        level_pack = LevelPack.objects.get(id=level_pack_demon["id"])
        level_pack.demons.add(Demon.objects.get(id=level_pack_demon["demons"]))


def tiny_pemonlist():

    demons = [{'level': 'GRACELESS', 'creator': 'Oblivionwing', 'verifier': 'tFluffy', 'list_points': 250.0, 'verification_video': 'https://youtu.be/DVfss97tv8s', 'verification_video_embed': 'https://www.youtube.com/embed/DVfss97tv8s', 'level_id': 109011704, 'update_created': '2.2', 'tiny_position': 1}, {'level': 'overture', 'creator': 'Oblivionwing', 'verifier': 'tFluffy', 'list_points': 242.0, 'verification_video': 'https://youtu.be/yC2e_iBQ-6g', 'verification_video_embed': 'https://www.youtube.com/embed/yC2e_iBQ-6g', 'level_id': 108962236, 'update_created': '2.2', 'tiny_position': 2}, {'level': 'The Other Side', 'creator': 'Scratchman', 'verifier': 'ScratchMan', 'list_points': 234.26, 'verification_video': 'https://youtu.be/PinwQQ1l2Qc', 'verification_video_embed': 'https://www.youtube.com/embed/PinwQQ1l2Qc', 'level_id': 107956530, 'update_created': '2.2', 'tiny_position': 3}, {'level': 'the sfw needle', 'creator': 'aelz', 'verifier': 'aelz', 'list_points': 226.77, 'verification_video': 'https://youtu.be/thc87rpuaas', 'verification_video_embed': 'https://www.youtube.com/embed/thc87rpuaas', 'level_id': 107953600, 'update_created': '2.2', 'tiny_position': 4}, {'level': 'Clone', 'creator': 'Gdp', 'verifier': 'Gdp', 'list_points': 219.51, 'verification_video': 'https://youtu.be/Oq0wLQMR3uc', 'verification_video_embed': 'https://www.youtube.com/embed/Oq0wLQMR3uc', 'level_id': 108872883, 'update_created': '2.2', 'tiny_position': 5}, {'level': 'Finsternis', 'creator': 'Oblivionwing', 'verifier': 'Oblivionwing', 'list_points': 212.49, 'verification_video': 'https://youtu.be/27Hua3Gfe4Q', 'verification_video_embed': 'https://www.youtube.com/embed/27Hua3Gfe4Q', 'level_id': 107996611, 'update_created': '2.2', 'tiny_position': 6}, {'level': 'summit', 'creator': 'Natsumi', 'verifier': 
    'tFluffy', 'list_points': 205.69, 'verification_video': 'https://youtu.be/clCIov94qu0', 'verification_video_embed': 'https://www.youtube.com/embed/clCIov94qu0', 'level_id': 107984781, 'update_created': '2.2', 'tiny_position': 7}, {'level': 'The Farts Evil Needl', 'creator': 'aelz', 'verifier': 'aelz', 'list_points': 199.11, 
    'verification_video': 'https://youtu.be/-aTWTcGUOC0', 'verification_video_embed': 'https://www.youtube.com/embed/-aTWTcGUOC0', 'level_id': 107951253, 'update_created': '2.2', 'tiny_position': 8}, {'level': 'shat lava', 'creator': 'Dyln', 'verifier': 'tFluffy', 'list_points': 192.74, 'verification_video': 'https://youtu.be/s6dk9F0RCV0', 'verification_video_embed': 'https://www.youtube.com/embed/s6dk9F0RCV0', 'level_id': 108026267, 'update_created': '2.2', 'tiny_position': 9}, {'level': 'locked chamber', 'creator': 'Freakybob', 'verifier': 'Freakybob', 'list_points': 186.58, 'verification_video': 'https://youtu.be/69weBJM1J-w', 'verification_video_embed': 'https://www.youtube.com/embed/69weBJM1J-w', 'level_id': 108734004, 'update_created': '2.2', 'tiny_position': 10}, {'level': 'lobotomy bounce', 'creator': 'kowman10', 'verifier': 'kowman10', 'list_points': 180.61, 'verification_video': 'https://www.youtube.com/watch?v=zGq-nHtYQxE', 'verification_video_embed': 'https://www.youtube.com/embed/zGq-nHtYQxE', 'level_id': 108022044, 'update_created': '2.2', 'tiny_position': 11}, {'level': 'Cradles', 'creator': 'Epic GD', 'verifier': 'Epic GD', 'list_points': 174.83, 'verification_video': 'https://youtu.be/skg9dDKlBbo', 'verification_video_embed': 'https://www.youtube.com/embed/skg9dDKlBbo', 
    'level_id': 106909741, 'update_created': '2.2', 'tiny_position': 12}, {'level': 'My Cat To Death', 'creator': 'WcoolKid', 'verifier': 'WcoolKid', 'list_points': 169.24, 'verification_video': 'https://youtu.be/6VOtU3q7DuM', 'verification_video_embed': 'https://www.youtube.com/embed/6VOtU3q7DuM', 'level_id': 107974858, 'update_created': '2.2', 'tiny_position': 13}, {'level': 'Pick a Way', 'creator': 'Epic GD', 'verifier': 'Epic GD', 'list_points': 163.82, 'verification_video': 'https://youtu.be/LIswkudg0BM', 'verification_video_embed': 'https://www.youtube.com/embed/LIswkudg0BM', 'level_id': 106910788, 'update_created': '2.2', 'tiny_position': 14}, {'level': 'Blue', 'creator': 'Epic GD', 'verifier': 'Epic GD', 'list_points': 158.58, 'verification_video': 'https://youtu.be/Ce3sl5yrtd4', 'verification_video_embed': 'https://www.youtube.com/embed/Ce3sl5yrtd4', 'level_id': 108032982, 'update_created': '2.2', 'tiny_position': 15}, {'level': 'Bottom of the PDL', 'creator': 'MXGaming01', 'verifier': 'MXGaming01', 'list_points': 153.51, 'verification_video': 'https://youtu.be/qJFLIagfSrU', 'verification_video_embed': 'https://www.youtube.com/embed/qJFLIagfSrU', 'level_id': 108045456, 'update_created': '2.2', 'tiny_position': 16}]
    
    for demon in demons:
        print(demon)

        level = demon["level"]
        creator = demon["creator"]
        verifier = demon["verifier"]
        list_points = demon["list_points"]
        verification_video = demon["verification_video"]
        verification_video_embed = demon["verification_video_embed"]
        level_id = demon["level_id"]
        tiny_position = demon["tiny_position"]

        demon = Demon.objects.create(
            level=level,
            creator=creator,
            verifier=verifier,
            list_points=list_points,
            verification_video=verification_video,
            verification_video_embed=verification_video_embed,
            level_id=level_id,
            tiny_position=tiny_position,
            mode="platformer",
            category="tiny",
            length="platformer",
            update_created="2.2"
        )


def real_tiny_pemonlist():
    for i in range(1, 19):
        with open(rf'c:\Users\IK\Downloads\tpl-{i}.html', 'r', encoding='utf-8') as archivo:
            # Leer todo el contenido del archivo
            contenido = archivo.read()
        soup = BeautifulSoup(contenido, 'html.parser')

        level_info_div = soup.find('div', class_='level-container')
        h1 = level_info_div.find_all('h1')
        second_spans = level_info_div.find_all('span')
        ul = level_info_div.find_all('ul', class_='stats')
        second_p = ul[0].find_all('p')
        iframe = level_info_div.find_all('iframe')

        print(i)
        print(h1[0].text)
        print(second_spans[0].text)
        print(second_spans[1].text)
        print(second_p[1].text)
        print(iframe[0]["src"])
        print(f"https://youtu.be/{iframe[0]['src'].split('/')[-1]}")

        print()
        print()

        try:
            level_id = int(second_p[1].text)
        except:
            level_id = None

        Demon.objects.create(
            level=h1[0].text,
            creator=second_spans[0].text,
            verifier=second_spans[1].text,
            level_id=level_id,
            verification_video=f"https://youtu.be/{iframe[0]['src'].split('/')[-1]}",
            verification_video_embed=iframe[0]["src"],
            tiny_position=i,
            list_points=values_list_points_platformer[i - 1],
            update_created="2.2",
            mode="platformer",
            category="tiny",
            length="platformer",
        )



def update_level_packs():

    df = pd.read_excel(r'c:\Users\IK\Downloads\Pemonlist Level packs (19).xlsx')
    df_2 = pd.read_excel(r'c:\Users\IK\Downloads\Pemonlist Level packs (19).xlsx', sheet_name='Level IDs')

    level_packs = {}

    # Limpiar el DataFrame ignorando las primeras filas que no contienen packs y niveles
    df_clean = df.iloc[3:]  # Ajustar el índice según tu archivo

    # Inicializar variables
    pack_name = None
    levels = []

    # Recorrer cada columna
    for columna in df_clean.columns:
        for valor in df_clean[columna]:
            if pd.notna(valor):  # Si el valor no es NaN
                # Si el valor actual es un nombre de pack (basándonos en una suposición)
                if "Pack" in str(valor) and pack_name is None:
                    # Asignamos el valor como el nombre del pack
                    pack_name = valor
                elif "Pack" in str(valor) and pack_name:
                    # Si encontramos otro pack, guardamos el anterior y empezamos uno nuevo
                    level_packs[pack_name] = levels
                    pack_name = valor
                    levels = []
                else:
                    # Si no es un nuevo pack, agregamos el valor como nivel
                    levels.append(valor)

        # Después de recorrer la columna, guardar el último pack si no ha sido guardado
        if pack_name and levels:
            level_packs[pack_name] = levels

    # Crear un diccionario a partir de las columnas "Levels" y "ID"
    level_dict = dict(zip(df_2['Levels'], df_2['ID']))

    # Imprimir el resultado final
    for pack, levels in level_packs.items():
        print(f"{pack}: {levels}")

        try:
            level_pack = LevelPack.objects.get(
                name__iexact=pack
            )
        except:
            level_pack = LevelPack.objects.create(
                name=pack,
                color="diamond",
                mode="platformer",
                category="rated",
            )
        level_pack.demons.clear()
        for level in levels:
            print("level")
            print(level)
            level_pack.demons.add(Demon.objects.get(level_id=level_dict[level]))


def create_level_packs():
    level_packs_info = [
        {'name': 'Tech Pack', 'color': 'beginner', 'color_index': 0, 'mode': 'platformer', 'category': 'rated'}, {'name': '"ling" Pack', 'color': 'beginner', 'color_index': 0, 'mode': 'platformer', 'category': 'rated'}, {'name': 'Beginner Pack I', 'color': 'beginner', 'color_index': 0, 'mode': 'platformer', 'category': 'rated'}, {'name': 'Checkpointless Pack I', 'color': 'beginner', 'color_index': 0, 'mode': 'platformer', 'category': 'rated'}, {'name': 'Puzzle Pack', 'color': 'gold', 'color_index': 3, 'mode': 'platformer', 'category': 'rated'}, {'name': 'Zejoant Pack', 'color': 'silver', 'color_index': 2, 'mode': 'platformer', 'category': 'rated'}, {'name': 'Strawberry Jam Pack', 'color': 'silver', 'color_index': 2, 'mode': 'platformer', 'category': 'rated'}, {'name': 'Minigame Pack I', 'color': 'silver', 'color_index': 2, 'mode': 'platformer', 'category': 'rated'}, {'name': 'Bossfight Pack II', 'color': 'amber', 'color_index': 4, 'mode': 'platformer', 'category': 'rated'}, {'name': 'Gimmick Pack', 'color': 'amber', 'color_index': 4, 'mode': 'platformer', 'category': 'rated'}, {'name': 'Rage of Age Pack I', 'color': 'platinum', 'color_index': 5, 'mode': 'platformer', 'category': 'rated'}, {'name': 'Mountain Pack I', 'color': 'platinum', 'color_index': 5, 'mode': 'platformer', 'category': 'rated'}, {'name': 'KingEggplant Pack I', 'color': 'platinum', 'color_index': 5, 'mode': 'platformer', 'category': 'rated'}, {'name': 'Chill Pack', 'color': 'platinum', 'color_index': 5, 'mode': 'platformer', 'category': 'rated'}, {'name': 'Bossfight Pack III', 'color': 'platinum', 'color_index': 5, 'mode': 'platformer', 'category': 'rated'}, {'name': 'qalli Pack', 'color': 'platinum', 'color_index': 5, 'mode': 'platformer', 'category': 'rated'}, {'name': 'Escape Pack', 'color': 'amethyst', 'color_index': 12, 'mode': 'platformer', 'category': 'rated'}, {'name': 'Trials Pack', 'color': 'obsidian', 'color_index': 14, 'mode': 'platformer', 'category': 'rated'}, {'name': 'Worlds Hardest Pack', 'color': 'obsidian', 'color_index': 14, 'mode': 'platformer', 'category': 'rated'}, {'name': 'Checkpointless Pack III', 'color': 'obsidian', 'color_index': 14, 'mode': 'platformer', 'category': 'rated'}, {'name': 'Slope Pack', 'color': 'obsidian', 'color_index': 14, 'mode': 'platformer', 'category': 'rated'}, {'name': 'Spider Pack', 'color': 'ruby', 'color_index': 9, 'mode': 'platformer', 'category': 'rated'}, {'name': 'Super Meat Pack', 'color': 'ruby', 'color_index': 9, 'mode': 'platformer', 'category': 'rated'}, {'name': 'Doppelganger Pack', 'color': 'ruby', 'color_index': 9, 'mode': 'platformer', 'category': 'rated'}, {'name': '2ItalianCats Pack I', 'color': 'ruby', 'color_index': 9, 'mode': 'platformer', 'category': 'rated'}, {'name': 'Adventurer Pack', 'color': 'diamond', 'color_index': 10, 'mode': 'platformer', 'category': 'rated'}, {'name': 'Troll Pack', 'color': 'diamond', 'color_index': 10, 'mode': 'platformer', 'category': 'rated'}, {'name': 'I Wanna Be The Pack', 'color': 'diamond', 'color_index': 10, 'mode': 'platformer', 'category': 'rated'}, {'name': 'Mountain Pack II', 'color': 'diamond', 'color_index': 10, 'mode': 'platformer', 'category': 'rated'}, {'name': 'XXXL Pack II', 'color': 'diamond', 'color_index': 10, 'mode': 'platformer', 'category': 'rated'}, {'name': 'Jump King Pack', 'color': 'amethyst', 'color_index': 12, 'mode': 'platformer', 'category': 'rated'}, 
        {'name': 'Rainbow Pack', 'color': 'amethyst', 'color_index': 12, 'mode': 'platformer', 'category': 'rated'}, {'name': 'Tower Pack II', 'color': 'amethyst', 'color_index': 12, 'mode': 'platformer', 'category': 'rated'}, {'name': 'Checkpointless Pack II', 'color': 'ruby', 'color_index': 9, 'mode': 'platformer', 'category': 'rated'}, {'name': 'Black Hole Pack', 'color': 'ruby', 'color_index': 9, 'mode': 'platformer', 'category': 'rated'}, {'name': 'btwmag Pack', 'color': 'beginner', 'color_index': 0, 'mode': 'platformer', 'category': 'rated'}, {'name': 'Time Trial Pack', 'color': 'beginner', 'color_index': 0, 'mode': 'platformer', 'category': 'rated'}, {'name': 'JSAB Pack I', 'color': 'bronze', 'color_index': 1, 'mode': 'platformer', 'category': 'rated'}, {'name': 'Beginner Pack II', 'color': 'bronze', 'color_index': 1, 'mode': 'platformer', 'category': 'rated'}, {'name': 'Jungle Pack', 'color': 'bronze', 'color_index': 1, 'mode': 'platformer', 'category': 'rated'}, {'name': 'Bossfight Pack I', 'color': 'bronze', 'color_index': 1, 'mode': 'platformer', 'category': 'rated'}, {'name': 'Switch Pack', 'color': 'gold', 'color_index': 3, 'mode': 'platformer', 'category': 'rated'}, {'name': 'Invisible Pack', 'color': 'gold', 'color_index': 3, 'mode': 'platformer', 'category': 'rated'}, {'name': 'Black & White Pack', 'color': 'gold', 'color_index': 3, 'mode': 'platformer', 'category': 'rated'}, {'name': 'OWOSI Pack', 'color': 'silver', 'color_index': 2, 'mode': 'platformer', 'category': 'rated'}, {'name': 'OG Pack', 'color': 'silver', 'color_index': 2, 'mode': 'platformer', 'category': 'rated'}, {'name': 'Rain Pack', 'color': 'amber', 'color_index': 4, 'mode': 'platformer', 'category': 'rated'}, {'name': 'Lobotomy Pack', 'color': 'amber', 'color_index': 4, 'mode': 'platformer', 'category': 'rated'}, {'name': 'Tower Pack I', 'color': 'amber', 'color_index': 4, 'mode': 'platformer', 'category': 'rated'}, {'name': 'TEK Pack', 'color': 'amber', 'color_index': 4, 'mode': 'platformer', 'category': 'rated'}, {'name': 'Mythic Pack', 'color': 'amber', 'color_index': 4, 'mode': 'platformer', 'category': 'rated'}, {'name': 'Celeste Pack', 'color': 'platinum', 'color_index': 5, 'mode': 'platformer', 'category': 'rated'}, {'name': 'XXXL Pack I', 'color': 'platinum', 'color_index': 5, 'mode': 'platformer', 'category': 'rated'}, {'name': 'Factory Pack', 'color': 'platinum', 'color_index': 5, 'mode': 'platformer', 'category': 'rated'}, {'name': 'KingEggplant Pack II', 'color': 'platinum', 'color_index': 5, 'mode': 'platformer', 'category': 'rated'}, {'name': 'YoStarYeahya Pack', 'color': 'platinum', 'color_index': 5, 'mode': 'platformer', 'category': 'rated'}, {'name': 'Wavedash Pack', 'color': 'amethyst', 'color_index': 12, 'mode': 'platformer', 'category': 'rated'}, {'name': 'How to Pack', 'color': 'amethyst', 'color_index': 12, 'mode': 'platformer', 'category': 'rated'}, {'name': 'Beat Pack', 'color': 'amethyst', 'color_index': 12, 'mode': 'platformer', 'category': 'rated'}, {'name': 'PulseN1nja Pack', 'color': 'amethyst', 'color_index': 12, 'mode': 'platformer', 'category': 'rated'}, {'name': 'Custi Pack', 'color': 'amethyst', 'color_index': 12, 'mode': 'platformer', 'category': 'rated'}, {'name': 'Xyraphel Pack', 'color': 'amethyst', 'color_index': 12, 'mode': 'platformer', 'category': 'rated'}, {'name': 'Minigame Pack II', 'color': 'ruby', 'color_index': 9, 'mode': 'platformer', 'category': 'rated'}, {'name': 'Fish Pack', 'color': 'ruby', 'color_index': 9, 'mode': 'platformer', 'category': 'rated'}, {'name': 'JSAB Pack II', 'color': 'ruby', 'color_index': 9, 
        'mode': 'platformer', 'category': 'rated'}, {'name': 'thejshadow Pack', 'color': 'diamond', 'color_index': 10, 'mode': 'platformer', 'category': 'rated'}, {'name': '2ItalianCats Pack II', 'color': 'diamond', 'color_index': 10, 'mode': 'platformer', 'category': 'rated'}, {'name': 'Halapeenyo Pack', 'color': 'diamond', 'color_index': 10, 'mode': 'platformer', 'category': 'rated'}, {'name': 'Furret Pack', 'color': 'diamond', 'color_index': 10, 'mode': 'platformer', 'category': 'rated'}, 
        {'name': 'Rage of Age Pack II', 'color': 'diamond', 'color_index': 10, 'mode': 'platformer', 'category': 'rated'}, {'name': 'Orelu Pack', 'color': 'diamond', 'color_index': 10, 'mode': 'platformer', 'category': 'rated'}, {'name': 'dkitey Pack', 'color': 'obsidian', 'color_index': 14, 'mode': 'platformer', 'category': 'rated'}, {'name': 'zYuko Pack', 'color': 'obsidian', 'color_index': 14, 'mode': 'platformer', 'category': 'rated'}, {'name': 'bran Pack', 'color': 'obsidian', 'color_index': 14, 'mode': 'platformer', 'category': 'rated'}, {'name': 'OG Top 1 Pack', 'color': 'obsidian', 'color_index': 14, 'mode': 'platformer', 'category': 'rated'}, 
        {'name': '2-Player Solo Pack', 'color': 'obsidian', 'color_index': 14, 'mode': 'platformer', 'category': 'rated'}
    ]

    level_packs_levels_info = [{'name': 'Tech Pack', 'demons': 3696}, {'name': 'Tech Pack', 'demons': 25}, {'name': 'Tech Pack', 'demons': 20}, {'name': 'Zejoant Pack', 'demons': 2239}, {'name': 'Zejoant Pack', 'demons': 18}, {'name': 'Zejoant Pack', 'demons': 8053}, {'name': 'Bossfight Pack II', 'demons': 16}, {'name': 'Bossfight Pack II', 'demons': 10}, {'name': 'Bossfight Pack II', 'demons': 329}, {'name': 'Adventurer Pack', 'demons': 540}, {'name': 'Adventurer Pack', 'demons': 463}, {'name': 'Adventurer Pack', 'demons': 34}, {'name': 'Trials Pack', 'demons': 455}, {'name': 'Trials Pack', 'demons': 38}, {'name': 'Trials Pack', 'demons': 8353}, {'name': 'Spider Pack', 'demons': 542}, {'name': 'Spider Pack', 'demons': 8673}, {'name': 'Spider Pack', 'demons': 52}, {'name': 'Rage of Age Pack I', 'demons': 8241}, {'name': 'Rage of Age Pack I', 'demons': 59}, {'name': 'Rage of Age Pack I', 'demons': 46}, {'name': 'Rage of Age Pack I', 'demons': 8023}, {'name': 'Gimmick Pack', 'demons': 626}, {'name': 'Gimmick Pack', 'demons': 480}, {'name': 'Gimmick Pack', 'demons': 2239}, {'name': 'Gimmick Pack', 'demons': 619}, {'name': 'Gimmick Pack', 'demons': 8017}, {'name': '"ling" Pack', 'demons': 8320}, {'name': '"ling" Pack', 'demons': 53}, {'name': '"ling" Pack', 'demons': 8292}, {'name': 'Strawberry Jam Pack', 'demons': 8292}, {'name': 'Strawberry Jam Pack', 'demons': 8313}, {'name': 'Strawberry Jam Pack', 'demons': 8307}, {'name': 'Mountain Pack I', 'demons': 15}, {'name': 'Mountain Pack I', 'demons': 903}, {'name': 'Mountain Pack I', 'demons': 600}, {'name': 'Troll Pack', 'demons': 7975}, {'name': 'Troll Pack', 'demons': 546}, {'name': 'Troll Pack', 'demons': 359}, {'name': 'Worlds Hardest Pack', 'demons': 42}, {'name': 'Worlds Hardest Pack', 'demons': 14}, {'name': 'Worlds Hardest Pack', 'demons': 
        8280}, {'name': 'Super Meat Pack', 'demons': 46}, {'name': 'Super Meat Pack', 'demons': 655}, {'name': 'Super Meat Pack', 'demons': 8241}, {'name': 'KingEggplant Pack I', 'demons': 544}, {'name': 'KingEggplant Pack I', 'demons': 22}, {'name': 'KingEggplant Pack I', 'demons': 8273}, {'name': 'KingEggplant Pack I', 'demons': 8301}, {'name': 'Chill Pack', 'demons': 18}, {'name': 'Chill Pack', 'demons': 611}, {'name': 'Chill Pack', 'demons': 568}, {'name': 'Chill Pack', 'demons': 542}, {'name': 'Chill Pack', 'demons': 34}, {'name': 'Beginner Pack I', 'demons': 7}, {'name': 'Beginner Pack I', 'demons': 11}, {'name': 'Beginner Pack I', 'demons': 20}, {'name': 'Minigame Pack I', 'demons': 51}, {'name': 'Minigame Pack I', 'demons': 657}, {'name': 'Minigame Pack I', 'demons': 5784}, {'name': 'Bossfight Pack III', 'demons': 353}, {'name': 'Bossfight Pack III', 'demons': 910}, {'name': 'Bossfight Pack III', 'demons': 8074}, {'name': 'I Wanna Be The Pack', 'demons': 2}, {'name': 'I Wanna Be The Pack', 'demons': 359}, {'name': 'I Wanna Be The Pack', 'demons': 8315}, {'name': 'Checkpointless Pack III', 'demons': 660}, {'name': 'Checkpointless Pack III', 'demons': 38}, {'name': 'Checkpointless Pack III', 'demons': 659}, {'name': 'Mountain Pack II', 'demons': 611}, {'name': 'Mountain Pack II', 'demons': 658}, {'name': 'Mountain Pack II', 'demons': 8285}, {'name': 'Doppelganger Pack', 'demons': 616}, {'name': 'Doppelganger Pack', 'demons': 59}, {'name': 'Doppelganger Pack', 'demons': 14}, {'name': 'Doppelganger Pack', 'demons': 42}, {'name': '2ItalianCats Pack I', 'demons': 8041}, {'name': '2ItalianCats Pack I', 'demons': 362}, {'name': '2ItalianCats Pack I', 'demons': 8017}, {'name': '2ItalianCats Pack I', 'demons': 8292}, {'name': '2ItalianCats Pack I', 'demons': 3617}, {'name': 'Checkpointless Pack I', 'demons': 33}, {'name': 'Checkpointless Pack I', 'demons': 12}, {'name': 'Checkpointless Pack I', 'demons': 3696}, {'name': 'Puzzle Pack', 'demons': 598}, {'name': 'Puzzle Pack', 'demons': 857}, {'name': 'Puzzle Pack', 'demons': 909}, {'name': 'qalli Pack', 'demons': 6}, {'name': 'qalli Pack', 'demons': 8270}, {'name': 'qalli Pack', 'demons': 8290}, {'name': 'XXXL Pack II', 'demons': 34}, {'name': 'XXXL Pack II', 'demons': 8016}, {'name': 'XXXL Pack II', 'demons': 662}, {'name': 'Slope Pack', 'demons': 32}, {'name': 'Slope Pack', 'demons': 8}, {'name': 'Slope Pack', 'demons': 611}, {'name': 'Escape Pack', 'demons': 574}, {'name': 'Escape Pack', 'demons': 8260}, {'name': 'Escape Pack', 'demons': 8259}, {'name': 'Checkpointless Pack II', 'demons': 374}, {'name': 'Checkpointless Pack II', 'demons': 47}, {'name': 'Checkpointless Pack II', 'demons': 360}, {'name': 'Checkpointless Pack II', 'demons': 620}, {'name': '2ItalianCats Pack II', 'demons': 20}, {'name': '2ItalianCats Pack II', 'demons': 48}, {'name': '2ItalianCats Pack II', 'demons': 46}, {'name': '2ItalianCats Pack II', 'demons': 362}, {'name': '2ItalianCats Pack II', 'demons': 540}, {'name': 'JSAB Pack I', 'demons': 541}, {'name': 'JSAB Pack I', 'demons': 576}, {'name': 'JSAB Pack I', 'demons': 8271}, 
        {'name': 'Switch Pack', 'demons': 570}, {'name': 'Switch Pack', 'demons': 48}, {'name': 'Switch Pack', 'demons': 8306}, {'name': 'Celeste Pack', 'demons': 7}, {'name': 'Celeste Pack', 'demons': 13}, {'name': 'Celeste Pack', 'demons': 8066}, {'name': 'Wavedash Pack', 'demons': 904}, {'name': 'Wavedash Pack', 'demons': 6}, {'name': 'Wavedash Pack', 'demons': 368}, {'name': 'btwmag Pack', 'demons': 8319}, {'name': 'btwmag Pack', 'demons': 8316}, {'name': 'btwmag Pack', 'demons': 8294}, {'name': 'How to Pack', 'demons': 662}, {'name': 'How to Pack', 'demons': 8075}, {'name': 'How to Pack', 'demons': 1899}, {'name': 'Halapeenyo Pack', 'demons': 21}, {'name': 'Halapeenyo Pack', 'demons': 41}, {'name': 'Halapeenyo Pack', 'demons': 480}, {'name': 'Halapeenyo Pack', 'demons': 619}, {'name': 'Furret Pack', 'demons': 8303}, {'name': 'Furret Pack', 'demons': 18}, {'name': 'Furret Pack', 'demons': 10}, {'name': 'Furret Pack', 'demons': 8041}, {'name': 'Furret Pack', 'demons': 
        39}, {'name': 'Beginner Pack II', 'demons': 45}, {'name': 'Beginner Pack II', 'demons': 322}, {'name': 'Beginner Pack II', 'demons': 1}, {'name': 'Invisible Pack', 'demons': 344}, {'name': 'Invisible Pack', 'demons': 583}, {'name': 'Invisible Pack', 'demons': 8295}, {'name': 'XXXL Pack I', 'demons': 8053}, {'name': 'XXXL Pack I', 'demons': 578}, {'name': 'XXXL Pack I', 'demons': 463}, {'name': 'Beat Pack', 'demons': 902}, {'name': 'Beat Pack', 'demons': 338}, {'name': 'Beat Pack', 'demons': 17}, {'name': 'Time Trial Pack', 'demons': 53}, {'name': 'Time Trial Pack', 'demons': 5784}, {'name': 'Time Trial Pack', 'demons': 8317}, {'name': 'dkitey Pack', 'demons': 8293}, {'name': 'dkitey Pack', 'demons': 33}, {'name': 'dkitey Pack', 'demons': 8237}, {'name': 'Rage of Age Pack II', 'demons': 562}, {'name': 'Rage of Age Pack II', 'demons': 19}, {'name': 'Rage of Age Pack II', 'demons': 8042}, {'name': 'Rage of Age Pack II', 'demons': 7975}, {'name': 'PulseN1nja Pack', 'demons': 616}, {'name': 'PulseN1nja Pack', 'demons': 464}, {'name': 'PulseN1nja Pack', 'demons': 368}, {'name': 'PulseN1nja Pack', 'demons': 901}, {'name': 'PulseN1nja Pack', 'demons': 8285}, {'name': 'Jungle Pack', 'demons': 7143}, {'name': 'Jungle Pack', 'demons': 619}, {'name': 'Jungle Pack', 'demons': 11}, {'name': 'Rain Pack', 'demons': 8270}, {'name': 'Rain Pack', 'demons': 6996}, {'name': 'Rain Pack', 'demons': 574}, {'name': 'Black Hole Pack', 'demons': 37}, {'name': 'Black Hole Pack', 'demons': 50}, {'name': 'Black Hole Pack', 'demons': 329}, {'name': 'Custi Pack', 'demons': 8031}, {'name': 'Custi Pack', 'demons': 626}, {'name': 'Custi Pack', 'demons': 34}, {'name': 'Lobotomy Pack', 'demons': 8110}, {'name': 'Lobotomy Pack', 'demons': 16}, {'name': 'Lobotomy Pack', 'demons': 8676}, {'name': 'zYuko Pack', 'demons': 39}, {'name': 'zYuko Pack', 'demons': 24}, {'name': 'zYuko Pack', 'demons': 8281}, {'name': 'bran Pack', 'demons': 32}, {'name': 'bran Pack', 'demons': 638}, {'name': 'bran Pack', 'demons': 658}, {'name': 'bran Pack', 'demons': 655}, {'name': 'Xyraphel Pack', 'demons': 8286}, {'name': 'Xyraphel Pack', 'demons': 30}, {'name': 'Xyraphel Pack', 'demons': 37}, {'name': 'Xyraphel Pack', 'demons': 546}, {'name': 'Xyraphel Pack', 'demons': 902}, {'name': 'Bossfight Pack I', 'demons': 584}, {'name': 'Bossfight Pack I', 'demons': 625}, {'name': 'Bossfight Pack I', 'demons': 3617}, {'name': 'Tower Pack I', 'demons': 322}, {'name': 'Tower Pack I', 'demons': 5584}, {'name': 'Tower Pack I', 'demons': 582}, {'name': 'Minigame Pack II', 'demons': 40}, {'name': 'Minigame Pack II', 'demons': 612}, {'name': 'Minigame Pack II', 'demons': 8023}, {'name': 'Jump King Pack', 'demons': 58}, {'name': 'Jump King Pack', 'demons': 41}, {'name': 'Jump King Pack', 'demons': 
        21}, {'name': 'Factory Pack', 'demons': 566}, {'name': 'Factory Pack', 'demons': 17}, {'name': 'Factory Pack', 'demons': 18}, {'name': 'Orelu Pack', 'demons': 2}, 
        {'name': 'Orelu Pack', 'demons': 8309}, {'name': 'Orelu Pack', 'demons': 8283}, {'name': 'Orelu Pack', 'demons': 8352}, {'name': 'OG Top 1 Pack', 'demons': 659}, {'name': 'OG Top 1 Pack', 'demons': 24}, {'name': 'OG Top 1 Pack', 'demons': 2}, {'name': 'OG Top 1 Pack', 'demons': 3}, {'name': 'OG Top 1 Pack', 'demons': 1}, {'name': 'OWOSI Pack', 'demons': 857}, {'name': 'OWOSI Pack', 'demons': 598}, {'name': 'OWOSI Pack', 'demons': 542}, {'name': 'TEK Pack', 'demons': 542}, {'name': 'TEK Pack', 'demons': 8}, {'name': 'TEK Pack', 'demons': 626}, {'name': 'Fish Pack', 'demons': 360}, {'name': 'Fish Pack', 'demons': 618}, {'name': 'Fish Pack', 'demons': 57}, {'name': 'Rainbow Pack', 'demons': 464}, {'name': 'Rainbow Pack', 'demons': 6}, {'name': 'Rainbow Pack', 'demons': 39}, {'name': 'KingEggplant Pack II', 
        'demons': 8111}, {'name': 'KingEggplant Pack II', 'demons': 8666}, {'name': 'KingEggplant Pack II', 'demons': 8303}, {'name': 'Black & White Pack', 'demons': 29}, 
        {'name': 'Black & White Pack', 'demons': 542}, {'name': 'Black & White Pack', 'demons': 567}, {'name': 'Black & White Pack', 'demons': 8292}, {'name': 'OG Pack', 'demons': 1}, {'name': 'OG Pack', 'demons': 15}, {'name': 'OG Pack', 'demons': 11}, {'name': 'Mythic Pack', 'demons': 578}, {'name': 'Mythic Pack', 'demons': 8053}, {'name': 'Mythic Pack', 'demons': 8054}, {'name': 'JSAB Pack II', 'demons': 30}, {'name': 'JSAB Pack II', 'demons': 479}, {'name': 'JSAB Pack II', 'demons': 8272}, {'name': '2-Player Solo Pack', 'demons': 31}, {'name': '2-Player Solo Pack', 'demons': 566}, {'name': '2-Player Solo Pack', 'demons': 654}, {'name': 'YoStarYeahya Pack', 'demons': 8042}, {'name': 'YoStarYeahya Pack', 'demons': 8299}, {'name': 'YoStarYeahya Pack', 'demons': 8361}, {'name': 'thejshadow Pack', 'demons': 539}, {'name': 'thejshadow Pack', 'demons': 3696}, {'name': 'thejshadow Pack', 'demons': 901}, {'name': 'thejshadow Pack', 'demons': 8658}, {'name': 'Tower Pack II', 'demons': 661}, {'name': 'Tower Pack II', 'demons': 3}, {'name': 'Tower Pack II', 'demons': 39}, {'name': 'Tower Pack II', 'demons': 594}
    ]

    for pack_info in level_packs_info:
        name = pack_info["name"]
        color = pack_info["color"]
        color_index = pack_info["color_index"]
        mode = pack_info["mode"]
        category = pack_info["category"]

        level_pack = LevelPack.objects.create(
            name=name,
            color=color,
            color_index=color_index,
            mode=mode,
            category=category
        )

    for level in level_packs_levels_info:
        name = level["name"]
        demons = level["demons"]

        level_pack = LevelPack.objects.get(name=name)
        level_pack.demons.add(Demon.objects.get(id=demons))

def pddl_list():

    df = pd.read_excel(r'c:\Users\IK\Downloads\Platformer Demon Deathless List (2) (2).xlsx', header=2)

    data_dict = {}

    for columna in df.columns:
        data_dict[columna] = df[columna].tolist()

    for i in range(142):
        try:
            level_id = int(data_dict["ID:"][i])
        except:
            level_id = None
        print(f"Level id: {level_id}")
        try:
            deathless_list_points = values_list_points_platformer[i]
        except:
            deathless_list_points = 0

        try:
            if data_dict["Verification:"][i]:
                if data_dict["Verification:"][i][:16] == "https://youtu.be":
                    verification_video = data_dict["Verification:"][i]
                    verification_video_embed = 'https://www.youtube.com/embed/' + verification_video.split('/')[3]
                elif data_dict["Verification:"][i][:29] == "https://www.youtube.com/watch":
                    verification_video = data_dict["Verification:"][i]
                    verification_video_embed = 'https://www.youtube.com/embed/' + verification_video.split('=')[1]
                else:
                    verification_video = None
                    verification_video_embed = None
            else:
                verification_video = None
                verification_video_embed = None
        except:
            verification_video = None
            verification_video_embed = None

        try:
            demon = Demon.objects.get(deathless=True, level_id=level_id)
            if demon.deathless_position > int(i) + 1:
                change_type = "Up"
                change_number = demon.deathless_position - int(i) + 1
            elif demon.deathless_position < int(i) + 1:
                change_type = "Down"
                change_number = int(i) + 1 - demon.deathless_position 
            else:
                change_type = None
            if change_type:
                Changelog.objects.create(
                    demon=demon,
                    reason="Moved",
                    reason_option="moved",
                    reason_demon=demon,
                    change_type=change_type,
                    deathless_position=int(i) + 1,
                    change_number=change_number
                )
            demon.deathless_list_points = deathless_list_points
            demon.deathless_position = int(i) + 1
            demon.verification_video_deathless = verification_video
            demon.verification_video_embed_deathless = verification_video_embed
            demon.deathless=True
            demon.save()
        except:

            demon = Demon.objects.create(
                level=data_dict["Level"][i],
                deathless_list_points=deathless_list_points,
                level_id=level_id,
                update_created="2.2",
                mode="platformer",
                category="deathless",
                deathless=True,
                deathless_position=int(i) + 1,
                length="platformer",
                verification_video_deathless=verification_video,
                verification_video_embed_deathless=verification_video_embed,
            )

def tpl_list():
    # Configura el driver para tu navegador
    cService = webdriver.ChromeService(executable_path=r"C:\Users\IK\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe")
    driver = webdriver.Chrome(service=cService)

    try:
        # Abre la página
        driver.get("https://gdplatformerlist.com/#/")

        # Espera a que la página cargue completamente
        time.sleep(5)  # Ajusta el tiempo según tu conexión o usa WebDriverWait para mayor precisión

        # Encuentra la tabla con clase "list"
        table = driver.find_element(By.CSS_SELECTOR, "table.list")
        
        # Encuentra todos los botones dentro de la tabla
        buttons = table.find_elements(By.TAG_NAME, "button")

        print(f"Se encontraron {len(buttons)} botones en la tabla.")

        Demon.objects.filter(all_position__isnull=False).update(all_position=None)

        # Iterar sobre cada botón y hacer clic
        for i, button in enumerate(buttons):
            
            # Usa ActionChains para evitar problemas de visibilidad
            ActionChains(driver).move_to_element(button).click(button).perform()

            # Espera un momento después de cada clic
            time.sleep(1)  # Ajusta este tiempo según sea necesario


            try:
                # Encuentra el div con clase "level"
                level_div = driver.find_element(By.CSS_SELECTOR, "div.level")
                
                # Encuentra el primer h1 dentro del div
                h1_element = level_div.find_element(By.TAG_NAME, "h1")
                
                # Obtén el texto del h1
                level = h1_element.text
                print(f"TOP {i + 1}: {level}")

            except Exception as e:
                print(f"No se pudo obtener el texto del h1 después del clic en el botón {i + 1}: {e}")

            try:
                # Encuentra el div con clase "level-authors"
                level_authors_div = driver.find_element(By.CSS_SELECTOR, "div.level-authors")
                
                # Encuentra el primer p dentro del div.level-authors
                p_elements = level_authors_div.find_elements(By.TAG_NAME, "p")
                
                # Obtén el texto del p
                creator = p_elements[0].text
                print(f"Creador: {creator}")

                verifier = p_elements[1].text
                print(f"Verificador: {verifier}")

            except Exception as e:
                print(f"No se pudo obtener el texto del p después del clic en el botón {i + 1}: {e}")

            try:
                # Encuentra el div con clase "level-authors"
                stats_div = driver.find_element(By.CSS_SELECTOR, "ul.stats")
                
                # Encuentra el primer p dentro del div.level-authors
                p_elements = stats_div.find_elements(By.TAG_NAME, "p")
                
                # Obtén el texto del p
                level_id = int(p_elements[1].text)
                print(f"Level ID: {level_id}")

            except Exception as e:
                print(f"No se pudo obtener el texto del p después del clic en el botón {i + 1}: {e}")

            try:
                # Encuentra el iframe en la página
                iframe = driver.find_element(By.TAG_NAME, "iframe")
                
                # Obtén el atributo src del iframe
                verification_video_embed = iframe.get_attribute("src")
                verification_video = f"https://youtu.be/{verification_video_embed.split('/')[4]}"
                print(f"Youtube embed: {verification_video_embed}")
                print(f"Youtube: {verification_video}")

            except Exception as e:
                print(f"No se pudo encontrar el iframe o su atributo src después del clic en el botón {i + 1}: {e}")

            demon = Demon.objects.filter(
                level_id=level_id
            )

            if len(demon) >= 2:
                break

            try:
                demon = Demon.objects.get(
                    level_id=level_id
                )
                demon.all_position=i + 1
                demon.all_list_points=values_list_points_platformer[i]
                demon.removed=False
                demon.save()
            except:

                demon = Demon.objects.create(
                    level=level,
                    update_created="2.2",
                    mode="platformer",
                    category="all",
                    all_position=i + 1,
                    creator=creator,
                    verifier=verifier,
                    level_id=level_id,
                    length="platformer",
                    verification_video=verification_video,
                    verification_video_embed=verification_video_embed,
                    all_list_points=values_list_points_platformer[i]
                )

            print()


        print("Se hizo clic en todos los botones.")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Cierra el navegador
        driver.quit()

def add_aredl_levels():
    response = requests.get("https://api.aredl.net/api/aredl/levels")
    
    for level in response.json():
        response_2 = requests.get(f"https://api.aredl.net/api/aredl/levels/{level['id']}?verification=True")
        data = response_2.json()
        print(data["position"])
        print(data["verification"]["video_url"])

        if data["verification"]["video_url"][:16] == "https://youtu.be":
            verification_video_embed = 'https://www.youtube.com/embed/' + data["verification"]["video_url"].split('/')[3]
        elif data["verification"]["video_url"][:29] == "https://www.youtube.com/watch":
            verification_video_embed = 'https://www.youtube.com/embed/' + data["verification"]["video_url"].split('=')[1]
        print(verification_video_embed)

        try:
            list_points = values_list_points[data["position"] - 1]
        except:
            list_points = 0

        try:

            demon = Demon.objects.get(level_id=data["level_id"])
            demon.rated_position = data["position"]
            demon.list_points = list_points
            demon.save()

        except:
            demon = Demon.objects.create(
                level=data["name"],
                mode="classic",
                category="rated",
                rated_position=data["position"],
                creator=data["publisher"]["global_name"],
                verifier=data["verification"]["submitted_by"]["global_name"],
                level_id=data["level_id"],
                verification_video=data["verification"]["video_url"],
                verification_video_embed=verification_video_embed,
                list_points=list_points
            )
        print(demon)
        if data["level_id"] == 109730342:
            break