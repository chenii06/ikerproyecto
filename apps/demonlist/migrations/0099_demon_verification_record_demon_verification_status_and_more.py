# Generated by Django 4.2.5 on 2024-05-10 06:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('demonlist', '0098_alter_changelog_reason_option'),
    ]

    operations = [
        migrations.AddField(
            model_name='demon',
            name='verification_record',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='demon',
            name='verification_status',
            field=models.CharField(blank=True, choices=[('Not finished', 'Not finished'), ('Finished', 'Finished'), ('Verifying', 'Verifying')], max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='demon',
            name='category',
            field=models.CharField(choices=[('rated', 'rated'), ('unrated', 'unrated'), ('challenge', 'challenge'), ('easiest', 'easiest'), ('shitty', 'shitty'), ('future', 'future')], default='rated', max_length=100),
        ),
    ]