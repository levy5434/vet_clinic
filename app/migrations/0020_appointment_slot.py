# Generated by Django 3.0.5 on 2020-10-05 16:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0026_remove_slot_appointments"),
        ("app", "0019_auto_20200928_2326"),
    ]

    operations = [
        migrations.AddField(
            model_name="appointment",
            name="slot",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="user.Slot",
                verbose_name="slot",
            ),
        ),
    ]
