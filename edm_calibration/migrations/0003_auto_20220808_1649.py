# Generated by Django 3.2.12 on 2022-08-08 08:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('edm_calibration', '0002_auto_20220808_1547'),
    ]

    operations = [
        migrations.RenameField(
            model_name='uedm_observation',
            old_name='humidity',
            new_name='raw_humidity',
        ),
        migrations.RenameField(
            model_name='uedm_observation',
            old_name='pressure',
            new_name='raw_pressure',
        ),
        migrations.RenameField(
            model_name='uedm_observation',
            old_name='slope_dist',
            new_name='raw_slope_dist',
        ),
        migrations.RenameField(
            model_name='uedm_observation',
            old_name='temperature',
            new_name='raw_temperature',
        ),
    ]