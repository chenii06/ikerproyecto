# Generated by Django 4.2.7 on 2024-01-15 19:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('demonlist', '0050_remove_changelog_position_changelog_all_position_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='changelog',
            old_name='un_rated_position',
            new_name='unrated_position',
        ),
    ]