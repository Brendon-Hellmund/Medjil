# Generated by Django 4.0.6 on 2023-04-14 07:29

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import staffcalibration.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('calibrationsites', '0001_initial'),
        ('instruments', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='StaffCalibrationRecord',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, help_text='Unique ID for this calibration record', primary_key=True, serialize=False)),
                ('job_number', models.CharField(help_text='Enter a job number, e.g., JN20222511', max_length=15, verbose_name='Job Number')),
                ('scale_factor', models.FloatField(help_text='Enter the correction factor provided in the Certificate.', null=True, validators=[django.core.validators.MinValueValidator(0.99), django.core.validators.MaxValueValidator(1.003)], verbose_name='Scale Factor')),
                ('grad_uncertainty', models.FloatField(blank=True, help_text='Enter the graduation uncertainty, if provided in the certificate.', null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(0.1)], verbose_name='Graduation Uncertainty')),
                ('standard_temperature', models.FloatField(default=25.0, help_text='Temperature at which the Scale Factor is valid.', null=True)),
                ('observed_temperature', models.FloatField(blank=True, help_text='Average temperature observed during the observation.', null=True)),
                ('field_file', models.FileField(blank=True, help_text='Upload the ASCII file generated by the level instrument', null=True, upload_to=staffcalibration.models.get_upload_to_fieldfile, verbose_name='Field Data')),
                ('field_book', models.FileField(blank=True, help_text='Upload the field book in pdf/jpg/tif format', null=True, upload_to=staffcalibration.models.get_upload_to_fieldbook, verbose_name='Field Book')),
                ('observer_isme', models.BooleanField(default=False, verbose_name='I am the Observer')),
                ('observer', models.CharField(blank=True, max_length=50, null=True)),
                ('calibration_date', models.DateField(help_text='Date of observation/measurement taken.', null=True)),
                ('calibration_report', models.FileField(blank=True, help_text='Calibration report/certificate in pdf/jpg/tif format.', null=True, upload_to=staffcalibration.models.get_upload_to_calibreport, verbose_name='Calibration certificate')),
                ('created_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified_on', models.DateTimeField(auto_now=True, null=True)),
                ('inst_level', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='instruments.digitallevel', verbose_name='Level Number')),
                ('inst_staff', models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, to='instruments.staff', verbose_name='Staff Number')),
                ('site_id', models.ForeignKey(blank=True, limit_choices_to=models.Q(('site_type', 'staff_range'), ('site_type', 'staff_lab'), _connector='OR'), null=True, on_delete=django.db.models.deletion.RESTRICT, to='calibrationsites.calibrationsite', verbose_name='Calibration Site')),
            ],
            options={
                'ordering': ['inst_staff', 'calibration_date'],
                'unique_together': {('job_number', 'inst_staff', 'calibration_date')},
            },
        ),
        migrations.CreateModel(
            name='AdjustedDataModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uscale_factor', models.FloatField(help_text='Enter the correction factor provided in the Certificate.', null=True, validators=[django.core.validators.MinValueValidator(0.99), django.core.validators.MaxValueValidator(1.003)], verbose_name='Uncorrected Scale Factor')),
                ('temp_at_sf1', models.FloatField(help_text='Temperature at which Scale Factor is 1.', null=True)),
                ('staff_reading', models.JSONField(null=True, verbose_name='Staff Reading')),
                ('calibration_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='staffcalibration.staffcalibrationrecord', verbose_name='Calibration Id')),
            ],
        ),
    ]
