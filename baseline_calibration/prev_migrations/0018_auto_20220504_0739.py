# Generated by Django 3.1 on 2022-05-03 23:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('baseline_calibration', '0017_auto_20220412_1122'),
    ]

    operations = [
        migrations.RenameField(
            model_name='edm_observation',
            old_name='humidity',
            new_name='raw_humidity',
        ),
        migrations.RenameField(
            model_name='edm_observation',
            old_name='pressure',
            new_name='raw_pressure',
        ),
        migrations.RenameField(
            model_name='edm_observation',
            old_name='slope_dist',
            new_name='raw_slope_dist',
        ),
        migrations.RenameField(
            model_name='edm_observation',
            old_name='temperature',
            new_name='raw_temperature',
        ),
        migrations.RemoveField(
            model_name='edm_observation',
            name='wet_temp',
        ),
        migrations.AddField(
            model_name='accreditation',
            name='statement',
            field=models.TextField(default='You have the authority from NATA to do this as accredited under ISO 17025:2012', help_text='eg. Accredited as a verifying authority for units of lenght according to ISO 17025:2012', verbose_name='Statement of accreditation'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='edm_observation',
            name='use_for_alignment',
            field=models.BooleanField(default=True, help_text='This observation (will) / (will not) be used for the alignment survey.', verbose_name='Use for alignment survey'),
        ),
        migrations.AddField(
            model_name='edm_observation',
            name='use_for_distance',
            field=models.BooleanField(default=True, help_text='This observation (will) / (will not) be used to determine certified distances for the range calibration survey.', verbose_name='Use for surveying the certified distances'),
        ),
    ]
