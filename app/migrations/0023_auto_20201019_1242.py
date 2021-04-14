# Generated by Django 3.0.5 on 2020-10-19 10:42

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("app", "0022_remove_appointment_admin_only"),
    ]

    operations = [
        migrations.AlterField(
            model_name="appointment",
            name="client",
            field=models.ForeignKey(
                default=None,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
                verbose_name="client",
            ),
        ),
    ]
