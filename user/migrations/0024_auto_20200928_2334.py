# Generated by Django 3.0.5 on 2020-09-28 21:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0019_auto_20200928_2326'),
        ('user', '0023_auto_20200928_2333'),
    ]

    operations = [
        migrations.AlterField(
            model_name='slot',
            name='appointments',
            field=models.ManyToManyField(blank=True, null=True, to='app.Appointment'),
        ),
    ]