# Generated by Django 4.2.7 on 2024-05-22 20:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0080_country_country_turkish'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='language',
            field=models.CharField(choices=[('English', 'English'), ('Spanish', 'Spanish'), ('Russian', 'Russian'), ('German', 'German'), ('Czech', 'Czech'), ('Turkish', 'Turkish')], default='English', max_length=12),
        ),
    ]
