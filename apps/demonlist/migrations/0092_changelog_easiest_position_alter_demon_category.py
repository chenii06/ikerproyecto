# Generated by Django 4.2.5 on 2024-04-19 05:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('demonlist', '0091_demon_easiest_position'),
    ]

    operations = [
        migrations.AddField(
            model_name='changelog',
            name='easiest_position',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='demon',
            name='category',
            field=models.CharField(choices=[('rated', 'rated'), ('unrated', 'unrated'), ('challenge', 'challenge'), ('easiest', 'easiest')], default='rated', max_length=100),
        ),
    ]
