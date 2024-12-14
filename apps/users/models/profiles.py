# Django
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django_cte import CTEManager
from django.db import models

# Utils
from utils.constants import list_choices

class Profile(models.Model):

    objects = CTEManager()
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    youtube_channel = models.URLField(max_length=200, blank=True, null=True)
    twitter = models.URLField(max_length=200, blank=True, null=True)
    twitch = models.URLField(max_length=200, blank=True, null=True)
    facebook = models.URLField(max_length=200, blank=True, null=True)
    id_discord = models.CharField(max_length=500, blank=True, null=True)
    discord = models.CharField(max_length=200, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=12, blank=True, null=True)
    picture = models.ImageField(upload_to="users/pictures", blank=True, null=True, max_length=500)
    banner = models.ImageField(upload_to="users/pictures", blank=True, null=True, max_length=500)
    country = models.ForeignKey("Country", on_delete=models.CASCADE, blank=True, null=True)
    team = models.ForeignKey("Team", on_delete=models.CASCADE, blank=True, null=True)
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

    followers = models.ManyToManyField('self', related_name='followings', blank=True, symmetrical=False)
    
    dark_mode = models.BooleanField(default=True)

    verified = models.BooleanField(blank=True, null=True)

    ranking = models.IntegerField(blank=True, null=True)

    language_choices = (("English", "English"),
                           ("Spanish", "Spanish"),
                           ("Russian", "Russian"),
                           ("German", "German"),
                           ("Czech", "Czech"),
                           ("Turkish", "Turkish"),
                           ("Danish", "Danish"),
                           ("Portuguese", "Portuguese"),
                           ("French", "French"),
                           )
    language = models.CharField(max_length=12, choices=language_choices, default="English")

    claimable = models.BooleanField(default=False)
    roulette_animation = models.BooleanField(default=True)
    fast_animation = models.BooleanField(default=False)

    device = models.CharField(max_length=100, blank=True, null=True)
    
    preferences = models.CharField(max_length=100, choices=list_choices, blank=True, null=True)

    default_submit_record = models.CharField(max_length=100, choices=list_choices, blank=True, null=True)
    default_stats_viewer = models.CharField(max_length=100, choices=list_choices, blank=True, null=True)

    tier = models.IntegerField(blank=True, null=True)
    
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        # Return username
        return self.user.username
    def clean(self):
        # Validar que el valor de preferences coincida con una de las opciones
        if self.preferences:
            valid_choices = [choice[0] for choice in list_choices]
            if self.preferences not in valid_choices:
                raise ValidationError({'preferences': 'The selected value is not valid.'})
        if self.default_submit_record:
            valid_choices = [choice[0] for choice in list_choices]
            if self.default_submit_record not in valid_choices:
                raise ValidationError({'default_submit_record': 'The selected value is not valid.'})
        if self.default_stats_viewer:
            valid_choices = [choice[0] for choice in list_choices]
            if self.default_stats_viewer not in valid_choices:
                raise ValidationError({'default_stats_viewer': 'The selected value is not valid.'})
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
        if self.youtube_channel and not self.youtube_channel.startswith(('http://', 'https://')):
            self.youtube_channel = 'https://' + self.youtube_channel
        if self.twitter and not self.twitter.startswith(('http://', 'https://')):
            self.twitter = 'https://' + self.twitter
        if self.twitch and not self.twitch.startswith(('http://', 'https://')):
            self.twitch = 'https://' + self.twitch
        if self.facebook and not self.facebook.startswith(('http://', 'https://')):
            self.facebook = 'https://' + self.facebook
        self.full_clean()
        super(Profile, self).save(*args, **kwargs)