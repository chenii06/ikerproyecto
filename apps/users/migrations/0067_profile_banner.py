# Generated by Django 4.2.5 on 2024-04-18 17:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0066_profile_roulette_animation'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='banner',
            field=models.ImageField(blank=True, max_length=500, null=True, upload_to='users/pictures'),
        ),
    ]
