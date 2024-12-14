# Django
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django_cte import CTEManager
from django.db import models


class Team(models.Model):
    
    objects = CTEManager()
    
    name = models.CharField(max_length=400, blank=True)
    owner = models.ForeignKey("Profile", blank=True, null=True, on_delete=models.CASCADE, related_name="owner")
    members = models.ManyToManyField("Profile", blank=True, null=True, related_name="members")
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

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        # Return name
        return self.name
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
        super(Team, self).save(*args, **kwargs)