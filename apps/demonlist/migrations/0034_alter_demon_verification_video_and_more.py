# Generated by Django 4.2.7 on 2024-01-02 21:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('demonlist', '0033_record_datetime_accepted'),
    ]

    operations = [
        migrations.AlterField(
            model_name='demon',
            name='verification_video',
            field=models.CharField(max_length=2000),
        ),
        migrations.AlterField(
            model_name='demon',
            name='verification_video_embed',
            field=models.CharField(max_length=2000),
        ),
        migrations.AlterField(
            model_name='record',
            name='raw_footage',
            field=models.CharField(blank=True, max_length=2000, null=True),
        ),
        migrations.AlterField(
            model_name='record',
            name='video',
            field=models.CharField(blank=True, max_length=2000, null=True),
        ),
    ]
