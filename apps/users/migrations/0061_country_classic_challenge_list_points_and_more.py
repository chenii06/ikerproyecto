# Generated by Django 4.2.7 on 2024-02-28 11:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0060_country_platformer_challenge_list_points_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='country',
            name='classic_challenge_list_points',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='country',
            name='classic_unrated_list_points',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='profile',
            name='classic_challenge_list_points',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='profile',
            name='classic_unrated_list_points',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='team',
            name='classic_challenge_list_points',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='team',
            name='classic_unrated_list_points',
            field=models.FloatField(default=0),
        ),
    ]