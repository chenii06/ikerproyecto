# Generated by Django 4.2.5 on 2024-04-14 00:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('demonlist', '0079_demon_all_demonlist'),
    ]

    operations = [
        migrations.AddField(
            model_name='demon',
            name='downloaded',
            field=models.BigIntegerField(blank=True, null=True),
        ),
    ]
