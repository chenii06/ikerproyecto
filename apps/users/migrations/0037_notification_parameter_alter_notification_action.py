# Generated by Django 4.2.7 on 2024-01-09 16:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0036_profile_language'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='parameter',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='notification',
            name='action',
            field=models.CharField(blank=True, choices=[('record_accepted', 'record_accepted'), ('record_rejected', 'record_rejected'), ('demon_beaten', 'demon_beaten'), ('roulette_shared', 'roulette_shared'), ('following', 'following')], max_length=500),
        ),
    ]