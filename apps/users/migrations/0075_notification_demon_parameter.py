# Generated by Django 4.2.5 on 2024-04-24 10:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('demonlist', '0098_alter_changelog_reason_option'),
        ('users', '0074_alter_profile_default_submit_record'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='demon_parameter',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='demon_parameter', to='demonlist.demon'),
        ),
    ]