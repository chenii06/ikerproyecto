# Generated by Django 4.2.7 on 2024-01-05 18:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('demonlist', '0038_roulette_demon_level_id_ldm_roulettedemon_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='demon',
            name='level_id_ldm',
            field=models.BigIntegerField(blank=True, null=True),
        ),
    ]
