# Django
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django_cte import CTEManager
from django.db import models

class TeamInvitation(models.Model):
    
    objects = CTEManager()
    
    team = models.ForeignKey("Team", on_delete=models.CASCADE)
    player = models.ForeignKey("Profile", on_delete=models.CASCADE)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        # Return team
        return self.team.name