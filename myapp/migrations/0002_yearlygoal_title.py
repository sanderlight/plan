# Generated by Django 4.2.4 on 2024-06-04 04:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="yearlygoal",
            name="title",
            field=models.CharField(default="Default Title", max_length=100),
        ),
    ]
