# Generated by Django 4.2.5 on 2024-04-16 02:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('demonlist', '0085_demon_artist_name_demon_number_of_coins_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='demon',
            name='all_demonlist',
        ),
    ]