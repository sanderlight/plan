# Generated by Django 3.2.1 on 2024-09-08 23:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0026_auto_20240908_1458'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='goal',
            name='timeframe_unit',
        ),
        migrations.RemoveField(
            model_name='goal',
            name='timeframe_value',
        ),
        migrations.AlterField(
            model_name='goal',
            name='profile',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='myapp.profile'),
        ),
    ]
