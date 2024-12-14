"""Level Pack model."""

# Django
from django.db import models

# Managers
from apps.demonlist.managers import DemonManager

# Models
from apps.demonlist.models import Demon


class LevelPack(models.Model):
    """Level Pack model."""

    name = models.CharField(max_length=500)

    color_option_choices = (
        ("beginner", "beginner"),
        ("bronze", "bronze"),
        ("silver", "silver"),
        ("gold", "gold"),
        ("amber", "amber"),
        ("platinum", "platinum"),
        ("sapphire", "sapphire"),
        ("jade", "jade"),
        ("emerald", "emerald"),
        ("ruby", "ruby"),
        ("diamond", "diamond"),
        ("onyx", "onyx"),
        ("amethyst", "amethyst"),
        ("azurite", "azurite"),
        ("obsidian", "obsidian"),
    )
    color = models.CharField(max_length=100, choices=color_option_choices)

    color_index = models.PositiveIntegerField(default=0)

    mode_option_choices = (("platformer", "platformer"),)
    mode = models.CharField(max_length=100, default="platformer", choices=mode_option_choices)
    category_option_choices = (("rated", "rated"),)
    category = models.CharField(max_length=100, default="rated", choices=category_option_choices)

    demons = models.ManyToManyField(Demon, related_name='level_packs')

    def __str__(self):
        """Return level pack id."""
        return '{}'.format(self.id)

    def save(self, *args, **kwargs):
        """Override save method to set color_index based on color."""
        color_map = dict(self.color_option_choices)
        self.color_index = list(color_map.keys()).index(self.color)
        super().save(*args, **kwargs)
