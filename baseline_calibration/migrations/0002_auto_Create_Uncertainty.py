# Generated by Django 3.1 on 2020-11-10 00:11

from __future__ import unicode_literals

from django.db import migrations, models
import os, re
from shutil import copyfile
from datetime import datetime, date
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.files import File

Default_budget = {
    'name' : 'Default',
    'Company': 'Landgate',
    'std_dev_of_zero':0.0002
    }

sources = [
    {'group' : '01', 'description': 'The EDM scale factor affected by temperature. (Type B)', 'units': 'x:1', 'ab_type': 'B', 'distribution': 'R', 'std_dev': 0.000000115, 'uc95': 0.0000002, 'k': 3**0.5, 'degrees_of_freedom': 30},
    {'group' : '04', 'description': 'Expected variation along measured dist', 'units':  '°C', 'ab_type':  'B', 'distribution':  'N', 'std_dev': 0.5, 'uc95': 1, 'k': 2, 'degrees_of_freedom': 10},
    {'group' : '05', 'description': 'Expected variation along measured dist.', 'units':  'hPa', 'ab_type':  'B', 'distribution':  'N', 'std_dev': 0.5, 'uc95': 1, 'k': 2, 'degrees_of_freedom': 10},
    {'group' : '09', 'description': 'Instrument Centring', 'units':  'm', 'ab_type':  'B', 'distribution':  'N', 'std_dev': 0.0002, 'uc95': 0.0004, 'k': 2, 'degrees_of_freedom': 30},
    {'group' : '09', 'description': 'Prism Centring', 'units':  'm', 'ab_type':  'B', 'distribution':  'N', 'std_dev': 0.0002, 'uc95': 0.0004, 'k': 2, 'degrees_of_freedom': 30},
    {'group' : '10', 'description': 'Measuring of Instrument Height', 'units':  'm', 'ab_type':  'B', 'distribution':  'N', 'std_dev': 0.0005, 'uc95': 0.001, 'k': 2, 'degrees_of_freedom': 30},
    {'group' : '10', 'description': 'Measuring of Reflector Height', 'units':  'm', 'ab_type':  'B', 'distribution':  'N', 'std_dev': 0.0005, 'uc95': 0.001, 'k': 2, 'degrees_of_freedom': 30},
]

lg_accreditation = [
    {'valid_from_date':'2021-06-14',
    'valid_to_date':'2024-06-13',
    'LUM_constant':0.5,
    'LUM_ppm':1.3,
    'statement':r'Accredited for compliance with ISO/IEC 17025 - Calibration.  The results of the tests, calibrations and/or measurements included in  this document are traceable to the international System of Units (SI) units and Australian/national standards. This document shall not be reproduced except in full.',
    'certificate_upload':os.path.join(settings.MEDIA_ROOT, 'InitialData/Accreditation/2021_LG_Accreditation.pdf')
     }]
    
#########################################################################
def load_initial_data(apps, schema_editor):
    Company = apps.get_model("accounts", "Company")
    Uncertainty_Budget = apps.get_model('baseline_calibration', 'Uncertainty_Budget')
    Uncertainty_Budget_Source = apps.get_model('baseline_calibration', 'Uncertainty_Budget_Source')
    medjil_accreditation = apps.get_model("baseline_calibration", "Accreditation")

    company_id = Company.objects.get(company_name = Default_budget['Company'])
    uc_budget_id, created = Uncertainty_Budget.objects.get_or_create(
        name = Default_budget['name'],
        company = company_id,
        std_dev_of_zero_adjustment = Default_budget['std_dev_of_zero']
        )
    
    for source in sources:
        obj, created = Uncertainty_Budget_Source.objects.get_or_create(
            uncertainty_budget=uc_budget_id,
            group  = source['group'],
            description = source['description'],
            units = source['units'],
            ab_type = source['ab_type'],
            distribution = source['distribution'],
            std_dev = source['std_dev'],
            uc95 = source['uc95'],
            k = source['k'],
            degrees_of_freedom = source['degrees_of_freedom']
            )
    
    for accred in lg_accreditation:
        obj, created = medjil_accreditation.objects.get_or_create(
            valid_from_date = accred['valid_from_date'],
            valid_to_date = accred['valid_to_date'],
            LUM_constant = accred['LUM_constant'],
            LUM_ppm = accred['LUM_ppm'],
            statement = accred['statement'],
            certificate_upload = accred['certificate_upload'],
            accredited_company = company_id,
            )

class Migration(migrations.Migration):

    dependencies = [
        ('baseline_calibration', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_initial_data),
    ]
