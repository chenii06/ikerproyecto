# Generated by Django 4.2.7 on 2024-01-28 13:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0053_profile_team'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='id_discord',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]