# Generated by Django 3.2.1 on 2024-09-19 19:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0033_auto_20240919_1457'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='wgoal',
            name='goal_text',
        ),
    ]
