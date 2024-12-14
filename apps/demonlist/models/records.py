"""Record model."""

# Django
from django.db import models

# Managers
from apps.demonlist.managers import ForeignKeyDemonManager

# Models
from apps.demonlist.models import Demon
from apps.users.models import Profile

# Utilities
import re


class Record(models.Model):
    """Record model."""

    objects = ForeignKeyDemonManager()

    demon = models.ForeignKey(Demon, on_delete=models.CASCADE)
    player = models.ForeignKey(Profile, on_delete=models.CASCADE, blank=True, null=True)
    tentative_player = models.CharField(max_length=1000, blank=True, null=True)
    best_time = models.TimeField(blank=True, null=True)
    percentage = models.IntegerField(blank=True, null=True)
    video = models.CharField(max_length=2000, blank=True, null=True)
    raw_footage = models.CharField(max_length=2000, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    mod = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='mod', blank=True, null=True)
    mod_notes = models.TextField(blank=True, null=True)
    admin = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='admin', blank=True, null=True)

    accepted = models.BooleanField(blank=True, null=True)
    under_consideration = models.BooleanField(default=False)

    top_order = models.IntegerField(blank=True, null=True)
    top_best_time = models.IntegerField(blank=True, null=True)

    enjoyment_stars = models.FloatField(blank=True, null=True)
    gameplay_stars = models.FloatField(blank=True, null=True)
    decoration_stars = models.FloatField(blank=True, null=True)
    balanced_stars = models.FloatField(blank=True, null=True)
    atmosphere_stars = models.FloatField(blank=True, null=True)

    mods = models.CharField(max_length=500, blank=True, null=True)

    deathless = models.BooleanField(default=False)

    datetime_submit = models.DateTimeField(auto_now_add=True)
    datetime_modified = models.DateTimeField(auto_now=True)
    datetime_checked = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        """Return record."""
        if self.best_time:
            # Formatear el tiempo para mostrar solo los primeros 3 dígitos de los milisegundos
            best_time_str = self.best_time.strftime('%H:%M:%S.%f')[:-3]
            return best_time_str
        return '{}'.format(self.id)

    @property
    def video_platform(self):
        youtube_pattern = re.compile(r'(https?://)?(www\.)?(m\.)?(youtube\.com|youtu\.be)/(watch\?v=)?([^&\n]+)')
        twitch_pattern = re.compile(r'(https?://)?(www\.)?twitch\.(tv|com)/.+')
        twitch_clips_pattern = re.compile(r'(https?://)?clips\.twitch\.tv/.+')
        facebook_pattern = re.compile(r'(https?://)?(www\.)?facebook\.(com)/.+')
        google_drive_pattern = re.compile(r'(https?://)?drive\.google\.com/.+')

        if youtube_pattern.match(self.video):
            return "YouTube"
        elif twitch_pattern.match(self.video):
            return "Twitch"
        elif twitch_clips_pattern.match(self.video):
            return "Twitch"
        elif facebook_pattern.match(self.video):
            return "Facebook"
        elif google_drive_pattern.match(self.video):
            return "Drive"
        else:
            return ""


