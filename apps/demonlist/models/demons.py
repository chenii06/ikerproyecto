"""Demon model."""

# Django
from django.db import models

# Managers
from apps.demonlist.managers import DemonManager

# Models
from apps.users.models import Profile


class Demon(models.Model):
    """Demon model."""

    objects = DemonManager()

    level = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    creator = models.CharField(max_length=255, blank=True, null=True)
    verifier = models.CharField(max_length=255, blank=True, null=True)
    creator_profile = models.ForeignKey(Profile, on_delete=models.CASCADE, blank=True, null=True, related_name="creator_profile")
    verifier_profile = models.ForeignKey(Profile, on_delete=models.CASCADE, blank=True, null=True, related_name="verifier_profile")
    list_points = models.FloatField(default=0)
    all_list_points = models.FloatField(default=0)
    deathless_list_points = models.FloatField(default=0)
    impossible_list_points = models.FloatField(default=0)

    photo = models.ImageField(upload_to='demons/photos', blank=True, null=True)
    verification_video_embed = models.CharField(max_length=2000, blank=True, null=True)
    verification_video = models.CharField(max_length=2000, blank=True, null=True)
    verification_video_embed_deathless = models.CharField(max_length=2000, blank=True, null=True)
    verification_video_deathless = models.CharField(max_length=2000, blank=True, null=True)

    level_id = models.BigIntegerField(blank=True, null=True)
    level_id_ldm = models.BigIntegerField(blank=True, null=True)
    object_count = models.BigIntegerField(blank=True, null=True)
    demon_difficulty = models.CharField(max_length=50, blank=True, null=True)
    update_created = models.CharField(max_length=5, blank=True, null=True)
    level_password = models.BigIntegerField(blank=True, null=True)

    enjoyment_stars = models.FloatField(blank=True, null=True, default=0)
    gameplay_stars = models.FloatField(blank=True, null=True, default=0)
    decoration_stars = models.FloatField(blank=True, null=True, default=0)
    balanced_stars = models.FloatField(blank=True, null=True, default=0)
    atmosphere_stars = models.FloatField(blank=True, null=True, default=0)

    all_stars = models.FloatField(blank=True, null=True, default=0)

    category_option_choices = (
        ("rated", "rated"),
        ("unrated", "unrated"),
        ("challenge", "challenge"),
        ("easiest", "easiest"),
        ("shitty", "shitty"),
        ("future", "future"),
        ("tiny", "tiny"),
        ("deathless", "deathless"),
        ("impossible", "impossible"),
        ("spam", "spam"),
        ("impossible_tiny", "impossible_tiny"),
        ("all", "all"),
    )

    category = models.CharField(max_length=100, default="rated", choices=category_option_choices, blank=True, null=True)
    deathless = models.BooleanField(default=False)
    mode_option_choices = (("classic", "classic"),
                    ("platformer", "platformer"),
                    )

    mode = models.CharField(max_length=100, default="platformer", choices=mode_option_choices)
    
    min_percentage = models.IntegerField(blank=True, null=True)

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

    downloads = models.BigIntegerField(blank=True, null=True)
    likes = models.BigIntegerField(blank=True, null=True)
    type_option_choices = (("featured", "featured"),
                    ("epic", "epic"),
                    ("legendary", "legendary"),
                    ("mythic", "mythic"),
                    )
    type = models.CharField(max_length=100, choices=type_option_choices, blank=True, null=True)
    length_option_choices = (("tiny", "tiny"),
                    ("short", "short"),
                    ("medium", "medium"),
                    ("long", "long"),
                    ("xl", "xl"),
                    ("platformer", "platformer"),
                    )
    length = models.CharField(max_length=100, choices=length_option_choices, blank=True, null=True)
    two_players = models.BooleanField(default=False)
    number_of_coins = models.IntegerField(blank=True, null=True)

    song_id = models.BigIntegerField(blank=True, null=True)
    song_name = models.CharField(max_length=1000, blank=True, null=True)
    artist_name = models.CharField(max_length=1000, blank=True, null=True)
    song_size = models.FloatField(blank=True, null=True)
    song_link = models.CharField(max_length=2000, blank=True, null=True)

    verification_status_option_choices = (("Not finished", "Not finished"),
                ("Finished", "Finished"),
                ("Verifying", "Verifying"),
                )
    verification_status = models.CharField(max_length=100, choices=verification_status_option_choices, blank=True, null=True)
    verification_record = models.IntegerField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    removed = models.BooleanField(default=False)

    def __str__(self):
        """Return level."""
        return '{}'.format(self.level)
    def save(self, *args, **kwargs):
        if self.list_points:
            self.list_points = round(self.list_points, 2)
        if self.enjoyment_stars:
            self.enjoyment_stars = round(self.enjoyment_stars, 1)
        if self.gameplay_stars:
            self.gameplay_stars = round(self.gameplay_stars, 1)
        if self.decoration_stars:
            self.decoration_stars = round(self.decoration_stars, 1)
        if self.balanced_stars:
            self.balanced_stars = round(self.balanced_stars, 1)
        if self.atmosphere_stars:
            self.atmosphere_stars = round(self.atmosphere_stars, 1)
        if self.all_stars:
            self.all_stars = round(self.all_stars, 1)

        super(Demon, self).save(*args, **kwargs)
