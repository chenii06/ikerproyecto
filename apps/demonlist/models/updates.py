"""Update model."""

# Django
from django.db import models


class Update(models.Model):
    """Update model."""
    version = models.CharField(max_length=5)
    changes = models.TextField(blank=True, null=True)

    date = models.DateField(auto_now_add=True)

    def __str__(self):
        # Return version
        return self.version
