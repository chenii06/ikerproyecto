# Generated by Django 4.2.7 on 2024-02-07 23:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('demonlist', '0055_alter_changelog_datetime'),
    ]

    operations = [
        migrations.AddField(
            model_name='demon',
            name='mode',
            field=models.CharField(choices=[('classic', 'classic'), ('platformer', 'platformer')], default='platformer', max_length=100),
        ),
    ]