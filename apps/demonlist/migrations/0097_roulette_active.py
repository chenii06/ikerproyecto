# Generated by Django 4.2.5 on 2024-04-23 02:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('demonlist', '0096_demon_creator_profile_demon_verifier_profile'),
    ]

    operations = [
        migrations.AddField(
            model_name='roulette',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]