# Generated by Django 3.0.5 on 2020-10-02 14:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0019_auto_20200928_2326"),
        ("user", "0024_auto_20200928_2334"),
    ]

    operations = [
        migrations.AlterField(
            model_name="slot",
            name="appointments",
            field=models.ManyToManyField(blank=True, to="app.Appointment"),
        ),
    ]
