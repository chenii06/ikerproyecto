# Generated by Django 4.2.7 on 2024-01-09 11:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0028_notification_option_notification_profile_parameter'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='profile_parameter',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='profile_parameter', to='users.profile'),
        ),
    ]
