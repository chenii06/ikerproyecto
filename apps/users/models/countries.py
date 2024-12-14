# Django
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django_cte import CTEManager
from django.db import models


class Country(models.Model):
    
    objects = CTEManager()
    
    country = models.CharField(max_length=200, blank=True)
    platformer_list_points = models.FloatField(default=0)
    platformer_unrated_list_points = models.FloatField(default=0)
    platformer_challenge_list_points = models.FloatField(default=0)
    platformer_deathless_list_points = models.FloatField(default=0)
    platformer_impossible_list_points = models.FloatField(default=0)
    platformer_tiny_list_points = models.FloatField(default=0)
    platformer_all_list_points = models.FloatField(default=0)
    classic_list_points = models.FloatField(default=0)
    classic_unrated_list_points = models.FloatField(default=0)
    classic_tiny_list_points = models.FloatField(default=0)
    classic_shitty_list_points = models.FloatField(default=0)
    classic_spam_list_points = models.FloatField(default=0)
    classic_impossible_tiny_list_points = models.FloatField(default=0)

    classic_list_points_with_mods = models.FloatField(default=0)
    classic_unrated_list_points_with_mods = models.FloatField(default=0)
    classic_tiny_list_points_with_mods = models.FloatField(default=0)
    classic_shitty_list_points_with_mods = models.FloatField(default=0)
    classic_spam_list_points_with_mods = models.FloatField(default=0)
    classic_impossible_tiny_list_points_with_mods = models.FloatField(default=0)

    picture = models.FileField(upload_to="countries/pictures", blank=True, null=True)

    country_spanish = models.CharField(max_length=200, blank=True)
    country_russian = models.CharField(max_length=200, blank=True)
    country_german = models.CharField(max_length=200, blank=True)
    country_czech = models.CharField(max_length=200, blank=True)
    country_turkish = models.CharField(max_length=200, blank=True)
    country_danish = models.CharField(max_length=200, blank=True)
    country_portuguese = models.CharField(max_length=200, blank=True)
    country_french = models.CharField(max_length=200, blank=True)

    abbreviation = models.CharField(max_length=3, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        # Return country
        return self.country
    def save(self, *args, **kwargs):
        self.platformer_list_points = round(self.platformer_list_points, 2)
        self.platformer_unrated_list_points = round(self.platformer_unrated_list_points, 2)
        self.platformer_challenge_list_points = round(self.platformer_challenge_list_points, 2)
        self.platformer_deathless_list_points = round(self.platformer_deathless_list_points, 2)
        self.platformer_impossible_list_points = round(self.platformer_impossible_list_points, 2)
        self.platformer_tiny_list_points = round(self.platformer_tiny_list_points, 2)
        self.platformer_all_list_points = round(self.platformer_all_list_points, 2)
        self.classic_list_points = round(self.classic_list_points, 2)
        self.classic_unrated_list_points = round(self.classic_unrated_list_points, 2)
        self.classic_tiny_list_points = round(self.classic_tiny_list_points, 2)
        self.classic_shitty_list_points = round(self.classic_shitty_list_points, 2)
        self.classic_spam_list_points = round(self.classic_spam_list_points, 2)
        self.classic_impossible_tiny_list_points = round(self.classic_impossible_tiny_list_points, 2)
        self.classic_list_points_with_mods = round(self.classic_list_points_with_mods, 2)
        self.classic_unrated_list_points_with_mods = round(self.classic_unrated_list_points_with_mods, 2)
        self.classic_tiny_list_points_with_mods = round(self.classic_tiny_list_points_with_mods, 2)
        self.classic_shitty_list_points_with_mods = round(self.classic_shitty_list_points_with_mods, 2)
        self.classic_spam_list_points_with_mods = round(self.classic_spam_list_points_with_mods, 2)
        self.classic_impossible_tiny_list_points_with_mods = round(self.classic_impossible_tiny_list_points_with_mods, 2)
        super(Country, self).save(*args, **kwargs)
    
    class Meta:
        verbose_name_plural = "Countries"