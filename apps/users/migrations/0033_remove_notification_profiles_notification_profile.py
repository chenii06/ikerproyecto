# Generated by Django 4.2.7 on 2024-01-09 13:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0032_remove_notification_profile_notification_profiles'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notification',
            name='profiles',
        ),
        migrations.AddField(
            model_name='notification',
            name='profile',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='profile', to='users.profile'),
        ),
    ]