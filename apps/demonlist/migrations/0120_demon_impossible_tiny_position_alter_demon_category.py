# Generated by Django 4.2.7 on 2024-09-03 04:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('demonlist', '0119_changelog_spam_position_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='demon',
            name='impossible_tiny_position',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='demon',
            name='category',
            field=models.CharField(blank=True, choices=[('rated', 'rated'), ('unrated', 'unrated'), ('challenge', 'challenge'), ('easiest', 'easiest'), ('shitty', 'shitty'), ('future', 'future'), ('tiny', 'tiny'), ('impossible', 'impossible'), ('spam', 'spam'), ('impossible_tiny', 'impossible_tiny')], default='rated', max_length=100, null=True),
        ),
    ]