# Generated by Django 3.2.1 on 2024-08-13 23:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0013_auto_20240813_1940'),
    ]

    operations = [
        migrations.AlterField(
            model_name='weeklygoal',
            name='description',
            field=models.TextField(),
        ),
    ]
