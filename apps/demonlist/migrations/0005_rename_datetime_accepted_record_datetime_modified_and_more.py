# Generated by Django 5.0 on 2023-12-23 01:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('demonlist', '0004_record'),
    ]

    operations = [
        migrations.RenameField(
            model_name='record',
            old_name='datetime_accepted',
            new_name='datetime_modified',
        ),
        migrations.AlterField(
            model_name='record',
            name='notes',
            field=models.TextField(blank=True, null=True),
        ),
    ]