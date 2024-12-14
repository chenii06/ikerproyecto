"""Roulette Demon model."""

# Django
from django.db import models

# Managers
from apps.demonlist.managers import ForeignKeyDemonManager

# Models
from apps.demonlist.models import Demon, Roulette


class RouletteDemon(models.Model):
    """Roulette Demon model."""

    objects = ForeignKeyDemonManager()

    roulette = models.ForeignKey(Roulette, on_delete=models.CASCADE)
    demon = models.ForeignKey(Demon, on_delete=models.CASCADE)
    stage = models.IntegerField(blank=True, null=True)
    num_level = models.IntegerField()
    demon_index = models.PositiveIntegerField()
    percentage = models.IntegerField(blank=True, null=True)
    best_time = models.TimeField(blank=True, null=True)