# Generated by Django 4.2.7 on 2024-11-21 18:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('demonlist', '0124_rename_verification_video_deathles_demon_verification_video_deathless_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='demon',
            name='all_list_points',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='demon',
            name='category',
            field=models.CharField(blank=True, choices=[('rated', 'rated'), ('unrated', 'unrated'), ('challenge', 'challenge'), ('easiest', 'easiest'), ('shitty', 'shitty'), ('future', 'future'), ('tiny', 'tiny'), ('deathless', 'deathless'), ('impossible', 'impossible'), ('spam', 'spam'), ('impossible_tiny', 'impossible_tiny')], default='rated', max_length=100, null=True),
        ),
    ]