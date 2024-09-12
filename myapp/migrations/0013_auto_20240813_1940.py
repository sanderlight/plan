# Generated by Django 3.2.1 on 2024-08-13 23:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0012_alter_weeklygoal_week_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='weeklygoal',
            name='yearly_goal',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='myapp.yearlygoal'),
        ),
        migrations.AlterField(
            model_name='weeklygoal',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
