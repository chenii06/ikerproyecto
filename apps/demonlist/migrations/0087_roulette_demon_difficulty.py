# Generated by Django 4.2.5 on 2024-04-16 19:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('demonlist', '0086_remove_demon_all_demonlist'),
    ]

    operations = [
        migrations.AddField(
            model_name='roulette',
            name='demon_difficulty',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
