# Generated by Django 4.2.7 on 2024-01-09 23:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0039_remove_country_country_spanish'),
    ]

    operations = [
        migrations.AddField(
            model_name='country',
            name='country_spanish',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
