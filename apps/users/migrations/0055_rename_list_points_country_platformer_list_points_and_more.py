# Generated by Django 4.2.7 on 2024-02-11 08:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0054_profile_id_discord'),
    ]

    operations = [
        migrations.RenameField(
            model_name='country',
            old_name='list_points',
            new_name='platformer_list_points',
        ),
        migrations.RenameField(
            model_name='profile',
            old_name='list_points',
            new_name='platformer_list_points',
        ),
        migrations.RenameField(
            model_name='team',
            old_name='list_points',
            new_name='platformer_list_points',
        ),
    ]