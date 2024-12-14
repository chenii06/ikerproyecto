import csv

import django
django.setup()

from apps.demonlist.models import Demon, Record, Changelog, Roulette, RouletteDemon
from apps.users.models import Profile, Country, Team, TeamInvitation, Notification


def export_models_to_csv():
    export_model_to_csv(Demon, 'Demon.csv')
    export_model_to_csv(Record, 'Record.csv')
    export_model_to_csv(Changelog, 'Changelog.csv')
    export_model_to_csv(Roulette, 'Roulette.csv')
    export_model_to_csv(RouletteDemon, 'RouletteDemon.csv')
    export_model_to_csv(Profile, 'Profile.csv')
    export_model_to_csv(Country, 'Country.csv')
    export_model_to_csv(Team, 'Team.csv')
    export_model_to_csv(TeamInvitation, 'TeamInvitation.csv')
    export_model_to_csv(Notification, 'Notification.csv')

def export_model_to_csv(model, filename):
    queryset = model.objects.all()
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [field.name for field in model._meta.fields]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for obj in queryset:
            writer.writerow({field.name: getattr(obj, field.name) for field in model._meta.fields})

export_models_to_csv()