# Generated by Django 4.2.7 on 2024-04-04 01:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('demonlist', '0072_demon_removed_alter_changelog_reason_option'),
    ]

    operations = [
        migrations.AlterField(
            model_name='demon',
            name='removed',
            field=models.BooleanField(default=False),
        ),
    ]
