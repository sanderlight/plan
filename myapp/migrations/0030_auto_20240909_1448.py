# Generated by Django 3.2.1 on 2024-09-09 18:48

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0029_auto_20240909_1446'),
    ]

    operations = [
        migrations.AddField(
            model_name='d',
            name='profile',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='myapp.profile'),
        ),
        migrations.AddField(
            model_name='d',
            name='start_date',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AddField(
            model_name='d1',
            name='start_date',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AddField(
            model_name='dgoal',
            name='profile',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='myapp.profile'),
        ),
        migrations.AddField(
            model_name='dgoal',
            name='start_date',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AddField(
            model_name='w',
            name='profile',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='myapp.profile'),
        ),
        migrations.AddField(
            model_name='w',
            name='start_date',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AddField(
            model_name='wgoal',
            name='profile',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='myapp.profile'),
        ),
        migrations.AddField(
            model_name='wgoal',
            name='start_date',
            field=models.DateField(default=datetime.date.today),
        ),
    ]
