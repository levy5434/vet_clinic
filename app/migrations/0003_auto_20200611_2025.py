# Generated by Django 3.0.6 on 2020-06-11 18:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0002_auto_20200611_1823"),
    ]

    operations = [
        migrations.AlterField(
            model_name="disease",
            name="cure_data",
            field=models.DateField(
                blank=True, null=True, verbose_name="cure date"
            ),
        ),
    ]
