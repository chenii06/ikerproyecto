# Generated by Django 4.2.7 on 2024-01-09 14:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0034_profile_language'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='language',
        ),
    ]
