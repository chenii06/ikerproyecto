# Generated by Django 4.2.7 on 2024-08-08 17:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0090_country_platformer_deathless_list_points_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='default_stats_viewer',
            field=models.CharField(blank=True, choices=[('classic rated', 'classic rated'), ('classic unrated', 'classic unrated'), ('classic tiny', 'classic tiny'), ('classic shitty', 'classic shitty'), ('platformer rated', 'platformer rated'), ('platformer unrated', 'platformer unrated'), ('platformer challenge', 'platformer challenge'), ('platformer deathless', 'platformer deathless')], max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='default_submit_record',
            field=models.CharField(blank=True, choices=[('classic rated', 'classic rated'), ('classic unrated', 'classic unrated'), ('classic tiny', 'classic tiny'), ('classic shitty', 'classic shitty'), ('platformer rated', 'platformer rated'), ('platformer unrated', 'platformer unrated'), ('platformer challenge', 'platformer challenge'), ('platformer deathless', 'platformer deathless')], max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='preferences',
            field=models.CharField(blank=True, choices=[('classic rated', 'classic rated'), ('classic unrated', 'classic unrated'), ('classic tiny', 'classic tiny'), ('classic shitty', 'classic shitty'), ('platformer rated', 'platformer rated'), ('platformer unrated', 'platformer unrated'), ('platformer challenge', 'platformer challenge'), ('platformer deathless', 'platformer deathless')], max_length=100, null=True),
        ),
    ]