# Generated by Django 4.2.7 on 2024-07-05 21:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0081_alter_profile_language'),
    ]

    operations = [
        migrations.AddField(
            model_name='country',
            name='country_danish',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]