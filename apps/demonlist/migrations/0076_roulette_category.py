# Generated by Django 4.2.5 on 2024-04-07 17:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('demonlist', '0075_alter_roulette_mode'),
    ]

    operations = [
        migrations.AddField(
            model_name='roulette',
            name='category',
            field=models.CharField(choices=[('all', 'all'), ('rated', 'rated'), ('unrated', 'unrated'), ('challenge', 'challenge')], default='rated', max_length=100),
        ),
    ]
