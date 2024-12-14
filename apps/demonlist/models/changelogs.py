"""Changelog model."""

# Django
from django.db import models


class Changelog(models.Model):
    """Changelog model."""

    demon = models.ForeignKey('Demon', on_delete=models.CASCADE, related_name="demon")
    reason = models.CharField(max_length=500)
    reason_option_choices = (("added_to_list", "added_to_list"),
                    ("added_above", "added_above"),
                    ("moved_up", "moved_up"),
                    ("moved_down", "moved_down"),
                    ("moved", "moved"),
                    ("rated", "rated"),
                    ("unrated", "unrated"),
                    ("challenge", "challenge"),
                    ("shitty", "shitty"),
                    ("tiny", "tiny"),
                    ("deathless", "deathless"),
                    ("impossible", "impossible"),
                    ("spam", "spam"),
                    ("impossible_tiny", "impossible_tiny"),
                    ("removed", "removed"),
                    )
    reason_option = models.CharField(max_length=500, blank=True, null=True, choices=reason_option_choices)
    reason_demon = models.ForeignKey('Demon', on_delete=models.CASCADE, blank=True, null=True, related_name="reason_demon")

    rated_position = models.IntegerField(blank=True, null=True)
    unrated_position = models.IntegerField(blank=True, null=True)
    challenge_position = models.IntegerField(blank=True, null=True)
    all_position = models.IntegerField(blank=True, null=True)

    easiest_position = models.IntegerField(blank=True, null=True)
    shitty_position = models.IntegerField(blank=True, null=True)
    future_position = models.IntegerField(blank=True, null=True)
    tiny_position = models.IntegerField(blank=True, null=True)
    deathless_position = models.IntegerField(blank=True, null=True)
    impossible_position = models.IntegerField(blank=True, null=True)
    spam_position = models.IntegerField(blank=True, null=True)
    impossible_tiny_position = models.IntegerField(blank=True, null=True)

    change_number = models.IntegerField(blank=True, null=True)
    change_type_options = (("Up", "Up"),
                           ("Down", "Down"))
    change_type = models.CharField(max_length=500, choices=change_type_options, blank=True, null=True)

    datetime = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Return changelog."""
        return '{}'.format(self.id)
 