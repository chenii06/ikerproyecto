# Generated by Django 4.2.5 on 2024-04-19 17:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0069_profile_device'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='fast_animation',
            field=models.BooleanField(default=False),
        ),
    ]