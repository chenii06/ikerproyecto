# Generated by Django 4.2.7 on 2024-01-13 12:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0048_team_members_alter_team_owner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='owner',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='owner', to='users.profile'),
            preserve_default=False,
        ),
    ]
