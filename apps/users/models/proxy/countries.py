"""Country proxy models."""

# Managers
from apps.users.managers import CountryManager

# Models
from apps.users.models import Country

class ExtendedCountry(Country):
    """ListCountry proxy model."""

    objects = CountryManager()

    class Meta:
        """Proxy model"""
        proxy = True
