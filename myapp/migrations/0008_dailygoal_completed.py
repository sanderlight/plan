# Generated by Django 3.2.1 on 2024-07-02 18:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0007_alter_monthlygoal_unique_together_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='dailygoal',
            name='completed',
            field=models.BooleanField(default=False),
        ),
    ]
