# Generated by Django 4.2.7 on 2024-02-28 11:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('demonlist', '0064_alter_changelog_datetime'),
    ]

    operations = [
        migrations.AddField(
            model_name='demon',
            name='min_percentage',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]