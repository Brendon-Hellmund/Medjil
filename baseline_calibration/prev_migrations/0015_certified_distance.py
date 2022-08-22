# Generated by Django 3.1 on 2022-03-23 08:48

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('calibrationsites', '0008_auto_20220323_1223'),
        ('baseline_calibration', '0014_delete_certified_distance'),
    ]

    operations = [
        migrations.CreateModel(
            name='Certified_Distance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('distance', models.DecimalField(decimal_places=5, max_digits=9, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1000)], verbose_name='certified distance')),
                ('a_uncertainty', models.DecimalField(decimal_places=5, max_digits=6, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1.0)], verbose_name='type A uncertainty of certified distance')),
                ('k_a_uncertainty', models.FloatField(default=2.0, validators=[django.core.validators.MinValueValidator(1.0), django.core.validators.MaxValueValidator(5.0)], verbose_name='Coverage factor for type A uncertainty of certified distance')),
                ('combined_uncertainty', models.DecimalField(decimal_places=5, max_digits=6, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1.0)], verbose_name='combined uncertainty of certified distance')),
                ('k_combined_uncertainty', models.FloatField(default=2.0, validators=[django.core.validators.MinValueValidator(1.0), django.core.validators.MaxValueValidator(5.0)], verbose_name='Coverage factor for combined uncertainty of certified distance')),
                ('offset', models.DecimalField(decimal_places=4, max_digits=5, validators=[django.core.validators.MinValueValidator(-0.3), django.core.validators.MaxValueValidator(0.3)], verbose_name='pillar offset')),
                ('os_uncertainty', models.DecimalField(decimal_places=5, max_digits=6, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1.0)], verbose_name='pillar offset uncertainty')),
                ('k_os_uncertainty', models.FloatField(default=2.0, validators=[django.core.validators.MinValueValidator(1.0), django.core.validators.MaxValueValidator(5.0)], verbose_name='Coverage factor for pillar offset uncertainty')),
                ('reduced_level', models.DecimalField(decimal_places=4, max_digits=7)),
                ('rl_uncertainty', models.DecimalField(decimal_places=5, max_digits=6, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(0.3)], verbose_name='Reduced level uncertainty')),
                ('k_rl_uncertainty', models.FloatField(default=2.0, validators=[django.core.validators.MinValueValidator(1.0), django.core.validators.MaxValueValidator(5.0)], verbose_name='Coverage factor for reduced level uncertainty')),
                ('uploaded_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified_on', models.DateTimeField(auto_now=True, null=True)),
                ('calibrated_baseline', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='baseline_calibration.calibrated_baseline')),
                ('from_pillar', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='certified_distance_from_pillar', to='calibrationsites.pillar')),
                ('to_pillar', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='certified_distance_to_pillar', to='calibrationsites.pillar')),
            ],
            options={
                'ordering': ['calibrated_baseline__pillar_survey', 'to_pillar__order'],
                'unique_together': {('calibrated_baseline', 'from_pillar', 'to_pillar')},
            },
        ),
    ]
