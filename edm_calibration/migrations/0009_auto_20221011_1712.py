# Generated by Django 3.2.12 on 2022-10-11 09:12

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edm_calibration', '0008_auto_20221011_1709'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='uedm_observation',
            name='degrees_of_freedom',
        ),
        migrations.RemoveField(
            model_name='uedm_observation',
            name='modified_on',
        ),
        migrations.RemoveField(
            model_name='uedm_observation',
            name='uploaded_on',
        ),
        migrations.RemoveField(
            model_name='uedm_observation',
            name='variance',
        ),
        migrations.AddField(
            model_name='upillar_survey',
            name='degrees_of_freedom',
            field=models.IntegerField(blank=True, help_text='Degrees of freedom of calibration', null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(500)]),
        ),
        migrations.AddField(
            model_name='upillar_survey',
            name='variance',
            field=models.FloatField(blank=True, help_text='Variance of least squares adjustment of the calibration', null=True),
        ),
    ]
