# Generated by Django 4.2.5 on 2024-05-10 07:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('demonlist', '0100_demon_future_position'),
    ]

    operations = [
        migrations.AddField(
            model_name='changelog',
            name='future_position',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]