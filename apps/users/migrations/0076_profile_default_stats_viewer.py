# Generated by Django 4.2.5 on 2024-04-24 22:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0075_notification_demon_parameter'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='default_stats_viewer',
            field=models.CharField(blank=True, choices=[('classic rated', 'classic rated'), ('classic unrated', 'classic unrated'), ('classic challenge', 'classic challenge'), ('classic shitty', 'classic shitty'), ('platformer rated', 'platformer rated'), ('platformer unrated', 'platformer unrated'), ('platformer challenge', 'platformer challenge')], max_length=100, null=True),
        ),
    ]