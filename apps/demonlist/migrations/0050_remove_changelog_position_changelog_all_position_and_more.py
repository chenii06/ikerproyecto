# Generated by Django 4.2.7 on 2024-01-15 18:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('demonlist', '0049_demon_all_position_demon_un_rated_position_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='changelog',
            old_name='position',
            new_name='rated_position',
        ),
        migrations.AddField(
            model_name='changelog',
            name='all_position',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='changelog',
            name='un_rated_position',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
