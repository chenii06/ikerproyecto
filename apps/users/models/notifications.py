# Django
from django.db import models


class Notification(models.Model):
    profile = models.ForeignKey("Profile", on_delete=models.CASCADE, null=True, related_name="profile")

    action_choices = (("record_accepted", "record_accepted"),
                    ("record_rejected", "record_rejected"),
                    ("record_under_consideration", "record_under_consideration"),
                    ("demon_beaten", "demon_beaten"),
                    ("roulette_shared", "roulette_shared"),
                    ("following", "following"),
                    ("team_invitation", "team_invitation"),
                    )
    action = models.CharField(max_length=500, blank=True, choices=action_choices)
    parameter = models.CharField(max_length=500, blank=True, null=True)
    
    read = models.BooleanField(default=False)

    option_choices = (("Profile", "Profile"),
                           ("Warning", "Warning"))
    option = models.CharField(max_length=500, blank=True, choices=option_choices)
    id_roulette_parameter = models.IntegerField(null=True, blank=True)
    id_team_parameter = models.IntegerField(null=True, blank=True)
    record_parameter = models.CharField(max_length=500, blank=True, null=True)
    profile_parameter = models.ForeignKey("Profile", on_delete=models.CASCADE, null=True, blank=True, related_name="profile_parameter")
    demon_parameter = models.ForeignKey("demonlist.Demon", on_delete=models.CASCADE, null=True, blank=True, related_name="demon_parameter")
    
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Return action
        return self.action