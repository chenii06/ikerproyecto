# Generated by Django 4.2.7 on 2023-12-26 09:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('demonlist', '0019_alter_changelog_datetime'),
    ]

    operations = [
        migrations.AlterField(
            model_name='changelog',
            name='datetime',
            field=models.DateTimeField(auto_now=True),
        ),
    ]