# Generated by Django 4.0.6 on 2022-08-19 03:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edm_calibration', '0004_upillar_survey_auto_base_calibration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uedm_observation',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='upillar_survey',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.DeleteModel(
            name='StepBySteGuideModel',
        ),
    ]