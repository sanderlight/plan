# Generated by Django 3.2.1 on 2024-09-19 19:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0034_remove_wgoal_goal_text'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wgoal',
            name='title',
            field=models.CharField(default='Default Title', max_length=255),
        ),
    ]
