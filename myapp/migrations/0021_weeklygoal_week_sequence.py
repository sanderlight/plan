# Generated by Django 3.2.1 on 2024-08-17 11:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0020_alter_goal_profile'),
    ]

    operations = [
        migrations.AddField(
            model_name='weeklygoal',
            name='week_sequence',
            field=models.IntegerField(default=None),
        ),
    ]
