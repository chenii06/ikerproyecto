# Generated by Django 4.2.5 on 2024-04-18 23:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('demonlist', '0089_alter_roulettedemon_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='record',
            name='under_consideration',
            field=models.BooleanField(default=False),
        ),
    ]
