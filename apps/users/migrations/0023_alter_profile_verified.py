# Generated by Django 4.2.7 on 2023-12-30 03:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0022_profile_verified'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='verified',
            field=models.BooleanField(blank=True, null=True),
        ),
    ]
