"""Record proxy models."""

# Managers
from apps.demonlist.managers import RecordManager

# Models
from apps.demonlist.models import Record

class ExtendedRecord(Record):
    """DetailRecord proxy model."""

    objects = RecordManager()

    class Meta:
        """Proxy model"""
        proxy = True