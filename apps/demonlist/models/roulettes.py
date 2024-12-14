"""Roulette model."""

# Django
from django.db import models

# Models
from apps.demonlist.models import Demon
from apps.users.models import Profile


class Roulette(models.Model):
    """Roulette model."""

    name = models.CharField(max_length=500)

    mode_option_choices = (("classic", "classic"),
                    ("platformer", "platformer"),
                    ("platformer_best_time", "platformer_best_time"),
                    )
    mode = models.CharField(max_length=100, default="platformer", choices=mode_option_choices)

    category_option_choices = (("all", "all"),
                    ("rated", "rated"),
                    ("unrated", "unrated"),
                    ("challenge", "challenge"),
                    )
    category = models.CharField(max_length=100, default="rated", choices=category_option_choices)

    demon_difficulty = models.CharField(max_length=100, blank=True, null=True)
    extreme_filter = models.CharField(max_length=100, blank=True, null=True)

    player = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    players_to_share = models.ManyToManyField(Profile, related_name="players_to_share", blank=True, null=True)
    demons = models.ManyToManyField(Demon, blank=True, through='RouletteDemon')
    max_demons = models.IntegerField(blank=True, null=True)
    completed = models.BooleanField(default=False)

    active = models.BooleanField(default=True)

    ronda = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        """Return roulette id."""
        return '{}'.format(self.id)
    
