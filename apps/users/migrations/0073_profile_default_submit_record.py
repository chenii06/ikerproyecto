# Generated by Django 4.2.5 on 2024-04-24 03:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0072_country_classic_shitty_list_points_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='default_submit_record',
            field=models.CharField(blank=True, choices=[('classic rated', 'classic rated'), ('classic unrated', 'classic unrated'), ('classic challenge', 'classic challenge'), ('platformer rated', 'platformer rated'), ('platformer unrated', 'platformer unrated'), ('platformer challenge', 'platformer challenge')], max_length=100, null=True),
        ),
    ]
