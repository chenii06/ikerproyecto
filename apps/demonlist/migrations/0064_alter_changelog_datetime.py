# Generated by Django 4.2.7 on 2024-02-25 23:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('demonlist', '0063_alter_changelog_datetime'),
    ]

    operations = [
        migrations.AlterField(
            model_name='changelog',
            name='datetime',
            field=models.DateTimeField(auto_now=True),
        ),
    ]