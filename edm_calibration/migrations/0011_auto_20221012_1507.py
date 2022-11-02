# Generated by Django 3.2.12 on 2022-10-12 07:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edm_calibration', '0010_rename_std_dev_ucalibration_parameter_standard_deviation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ucalibration_parameter',
            name='k',
        ),
        migrations.AddField(
            model_name='upillar_survey',
            name='k',
            field=models.FloatField(default=2, verbose_name='coverage factor'),
            preserve_default=False,
        ),
    ]
