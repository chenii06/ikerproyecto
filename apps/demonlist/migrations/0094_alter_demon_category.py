# Generated by Django 4.2.5 on 2024-04-19 17:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('demonlist', '0093_changelog_shitty_position_demon_shitty_position'),
    ]

    operations = [
        migrations.AlterField(
            model_name='demon',
            name='category',
            field=models.CharField(choices=[('rated', 'rated'), ('unrated', 'unrated'), ('challenge', 'challenge'), ('easiest', 'easiest'), ('shitty', 'shitty')], default='rated', max_length=100),
        ),
    ]