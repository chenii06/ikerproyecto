# Generated by Django 4.2.7 on 2024-09-14 23:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('demonlist', '0123_demon_verification_video_deathles_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='demon',
            old_name='verification_video_deathles',
            new_name='verification_video_deathless',
        ),
        migrations.RenameField(
            model_name='demon',
            old_name='verification_video_embed_deathles',
            new_name='verification_video_embed_deathless',
        ),
    ]
