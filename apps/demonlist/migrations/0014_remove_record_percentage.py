# Generated by Django 5.0 on 2023-12-24 10:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('demonlist', '0013_remove_demon_min_percentage_remove_demon_score_min'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='record',
            name='percentage',
        ),
    ]