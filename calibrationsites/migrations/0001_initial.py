# Generated by Django 4.0.6 on 2022-08-22 04:56

import calibrationsites.models
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0003_create_suser'),
    ]

    operations = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Enter the full name of Country, e.g, Australia', max_length=40, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Enter the full name of State/Region, e.g., Western Australia', max_length=40, verbose_name='State')),
                ('statecode', models.CharField(help_text='Enter State Code with a max. of three letters, e.g., WA', max_length=3, null=True, validators=[django.core.validators.RegexValidator('^[A-Z]*$', 'Only capital letters are allowed')], verbose_name='State Code')),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='calibrationsites.country')),
            ],
            options={
                'unique_together': {('country', 'name')},
            },
        ),
        migrations.CreateModel(
            name='Locality',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Enter locality or suburb name, e.g., Boya', max_length=40, verbose_name='Locality/Suburb')),
                ('postcode', models.IntegerField(help_text='Enter Postal Code, e.g., 6056', null=True, verbose_name='Post Code')),
                ('country', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='calibrationsites.country')),
                ('state', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='calibrationsites.state')),
            ],
            options={
                'unique_together': {('state', 'name')},
            },
        ),
        migrations.CreateModel(
            name='CalibrationSite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('site_type', models.CharField(blank=True, choices=[(None, '--- Select Type ---'), ('baseline', 'EDM Calibration Baseline'), ('staff_lab', 'Staff Calibration Laboratory'), ('staff_range', 'Staff Calibration Range')], max_length=20, null=True, verbose_name='Site Type')),
                ('site_name', models.CharField(help_text='Name for the Calibration Site', max_length=100, unique=True, verbose_name='Site Name')),
                ('site_address', models.CharField(help_text='Address for the Calibration Site, e.g., Kent Street, Curtin University', max_length=100, null=True, verbose_name='Site Address')),
                ('no_of_pillars', models.IntegerField(blank=True, help_text='Enter the number of pins or baseline pillars, if applicable', null=True, verbose_name='Number of Pillars/Pins')),
                ('description', models.TextField(blank=True, null=True)),
                ('site_access', models.FileField(help_text='Upload a pdf diagram showing an access to the location', null=True, upload_to=calibrationsites.models.get_upload_to_location, verbose_name='Access Summary')),
                ('site_config', models.FileField(help_text='Upload a pdf diagram showing the location of pins or pillars', null=True, upload_to=calibrationsites.models.get_upload_to_location, verbose_name='Site Configuration')),
                ('uploaded_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified_on', models.DateTimeField(auto_now=True, null=True)),
                ('country', models.ForeignKey(help_text='Add/select a Country', null=True, on_delete=django.db.models.deletion.SET_NULL, to='calibrationsites.country', verbose_name='Country')),
                ('locality', models.ForeignKey(help_text='Add/select the location of Site', null=True, on_delete=django.db.models.deletion.SET_NULL, to='calibrationsites.locality', verbose_name='Locality/Suburb')),
                ('operator', models.ForeignKey(blank=True, help_text='Select the site operator', null=True, on_delete=django.db.models.deletion.RESTRICT, to='accounts.company', verbose_name='Authority')),
                ('state', models.ForeignKey(help_text='Add/select a State/Region', null=True, on_delete=django.db.models.deletion.SET_NULL, to='calibrationsites.state', verbose_name='State/Region')),
            ],
        ),
        migrations.CreateModel(
            name='Pillar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='e.g., 1', max_length=25, verbose_name='Pillar/Pin No')),
                ('order', models.CharField(blank=True, max_length=25, verbose_name='formatted name')),
                ('easting', models.DecimalField(blank=True, decimal_places=3, help_text='MGA2020 Easting (m). eg., 395006.085', max_digits=9, null=True, validators=[django.core.validators.MinValueValidator(300000), django.core.validators.MaxValueValidator(900000)])),
                ('northing', models.DecimalField(blank=True, decimal_places=3, help_text='MGA2020 Northing (m). eg., 6458541.334', max_digits=10, null=True, validators=[django.core.validators.MinValueValidator(3000000), django.core.validators.MaxValueValidator(10000000)])),
                ('height', models.FloatField(blank=True, help_text='Enter the orthometic height, if known', null=True, validators=[django.core.validators.MinValueValidator(-30), django.core.validators.MaxValueValidator(10000)])),
                ('zone', models.PositiveSmallIntegerField(blank=True, help_text='Grid Zone, if applicable', null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(60)])),
                ('site_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='calibrationsites.calibrationsite', verbose_name='Site Name')),
            ],
            options={
                'ordering': ['site_id', 'order'],
                'unique_together': {('site_id', 'name')},
            },
        ),
    ]
