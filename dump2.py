import csv

import django
django.setup()

from apps.demonlist.models import Demon, Record, Changelog, Roulette, RouletteDemon
from apps.users.models import Profile, Country, Team, TeamInvitation, Notification


def import_from_csv(model):
    with open(f"{model.__name__}.csv", 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            instance = model()
            for field_name, value in row.items():
                if value != "":

                    if field_name in ["list_points", "enjoyment_stars", "gameplay_stars", "decoration_stars", "balanced_stars", "atmosphere_stars", "all_stars"]:
                        value = float(value)
                    if field_name in ["demon"]:
                        value = Demon.objects.get(level=value)
                    setattr(instance, field_name, value)
            instance.save()

# Importar datos de los archivos CSV a la nueva base de datos
import_from_csv(Profile)
import_from_csv(Demon)
import_from_csv(Record)
import_from_csv(Changelog)
import_from_csv(Roulette)
import_from_csv(RouletteDemon)
import_from_csv(Country)
import_from_csv(Team)
import_from_csv(TeamInvitation)
import_from_csv(Notification)