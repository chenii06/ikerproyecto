# Generated by Django 4.2.7 on 2023-12-27 05:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0017_alter_profile_country'),
    ]

    operations = [
        migrations.AlterField(
            model_name='country',
            name='list_points',
            field=models.FloatField(blank=True, default=0, max_length=200),
        ),
    ]
