# Generated by Django 4.2.7 on 2024-01-11 23:36

from django.db import migrations
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0041_alter_profile_picture'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='country',
            managers=[
                ('objects_cte', django.db.models.manager.Manager()),
            ],
        ),
    ]