# Generated by Django 3.2.12 on 2022-10-13 01:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edm_calibration', '0011_auto_20221012_1507'),
    ]

    operations = [
        migrations.AlterField(
            model_name='upillar_survey',
            name='k',
            field=models.FloatField(blank=True, null=True, verbose_name='coverage factor'),
        ),
    ]
