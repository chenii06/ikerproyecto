# Generated by Django 4.2.7 on 2024-01-11 03:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0040_country_country_spanish'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='picture',
            field=models.ImageField(blank=True, max_length=500, null=True, upload_to='users/pictures'),
        ),
    ]
