# Generated by Django 4.2.5 on 2024-04-19 19:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0070_profile_fast_animation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='device',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]