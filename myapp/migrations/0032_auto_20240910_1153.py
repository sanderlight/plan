# Generated by Django 3.2.1 on 2024-09-10 15:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0031_remove_m_goal'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='d',
            name='goal',
        ),
        migrations.RemoveField(
            model_name='useranalyticsdata',
            name='goal',
        ),
        migrations.RemoveField(
            model_name='w',
            name='goal',
        ),
    ]
