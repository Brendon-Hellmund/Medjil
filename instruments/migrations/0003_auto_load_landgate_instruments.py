# Generated by Django 3.1 on 2020-11-12 02:23
import csv
from django.db import migrations, models
from datetime import datetime
from django.core.files.storage import FileSystemStorage
from django.core.files import File
# Start migration

def add_landgate_instruments(apps, schema_editor):
	Company = apps.get_model("accounts", "Company")	
	CalibrationSite = apps.get_model('calibrationsites', 'CalibrationSite')
	InstrumentModel = apps.get_model("instruments", "InstrumentModel")
	DigitalLevel = apps.get_model('instruments', 'DigitalLevel')
	Staff = apps.get_model('instruments', 'Staff')
	StaffCalibrationRecord = apps.get_model('staffcalibration', 'StaffCalibrationRecord')

	# Add digital levels
	with open("media/Landgate Instruments/Digital Levels/digital_levels.csv", "r") as f:
		reader = csv.reader(f); header = next(reader)
		k = 0
		inst_type = 'level'
		for row in reader:
				k +=1
				make = row[1].strip()
				level_model = row[2].strip().upper()
				level_number = row[0].strip()
				level_owner = 'Landgate'
				level_obj, created = DigitalLevel.objects.get_or_create(
						level_model = InstrumentModel.objects.get(model__exact=level_model), 
						level_owner = Company.objects.get(company_name__exact=level_owner),
						level_number = level_number,
						)
	# Add bar-coded staves
	with open("media/Landgate Instruments/Staves/staves.csv", "r") as f:
		reader = csv.reader(f); header = next(reader)
		k = 0
		inst_type = 'staff'
		for row in reader:
				k +=1
				staff_number = row[0].strip()
				staff_model = row[1].strip().upper()
				staff_type = row[2].strip()
				staff_owner = 'Landgate'
				staff_length = row[3].strip()
				thermal_coefficient = row[4].strip()
				standard_temperature = row[5].strip()
				observed_temperature = row[6].strip() 
				scale_factor = row[7].strip()
				graduation_uncertainty = row[8].strip()
				calibration_date = row[9].strip()
				observer = row[10].strip()
				site_name = row[11].strip()
				field_book = row[12].strip()
				calibration_report = row[13].strip()
				job_number = row[14].strip()
				level_model = row[15].strip()

				calibration_date = datetime.strptime(calibration_date, '%d/%m/%Y').date()
				staff_obj, created = Staff.objects.get_or_create(
						staff_model = InstrumentModel.objects.get(model__exact=staff_model), 
						staff_type = staff_type,
						staff_owner = Company.objects.get(company_name__exact=staff_owner),
						staff_number = staff_number,
						staff_length = staff_length,
						thermal_coefficient = thermal_coefficient,
						)
				# print(level_model)
				record_obj, created = StaffCalibrationRecord.objects.get_or_create(
					job_number = job_number,
					inst_staff = staff_obj,
					# inst_level = InstrumentModel.objects.get(model__exact = level_model),
					site_id = CalibrationSite.objects.get(site_name__exact = site_name),
					scale_factor = scale_factor,
					grad_uncertainty = graduation_uncertainty,
					standard_temperature = standard_temperature,
					# observed_temperature = observed_temperature,
					# observer = observer,
					calibration_date = calibration_date, 
					# field_book = File(open(field_book, 'rb'), name = field_book.split('/')[-1]),
					calibration_report = File(open(calibration_report, 'rb'), name = calibration_report.split('/')[-1]),
				)
				if level_model:
    					record_obj.inst_level = DigitalLevel.objects.get(level_model__model__exact = level_model)
				if observed_temperature:
    					record_obj.observed_temperature = observed_temperature
				if observer:
    					record_obj.observer = observer
				if field_book and (record_obj.field_book == '' or not record_obj.field_book):
    					record_obj.field_book = File(open(field_book, 'rb'), name = field_book.split('/')[-1])
				record_obj.save()
def reverse_func(apps, schema_editor):
	Company = apps.get_model("accounts", "Company")	
	InstrumentModel = apps.get_model("instruments", "InstrumentModel")
	
	DigitalLevel.objects.all().delete()
	Staff.objects.all().delete()



class Migration(migrations.Migration):

	dependencies = [
		('calibrationsites', '0001_initial'),
		('instruments', '0002_auto_load_default_instruments'),
		('staffcalibration', '0001_initial'),
	]

	operations = [
			migrations.RunPython(add_landgate_instruments, reverse_func),
	]
