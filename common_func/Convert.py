import numpy as np
from statistics import mean, pstdev
from django.db.models import Avg
from django.forms.models import model_to_dict
from django.db.models import Q

from instruments.models import (
    EDM_Inst,
    Prism_Inst,
    Staff,
    Mets_Inst,
    EDMI_certificate,
    Mets_certificate)
from staffcalibration.models import StaffCalibrationRecord
from accounts.models import Calibration_Report_Notes
from calibrationsites.models import (
    Pillar)
from baseline_calibration.models import (
    Uncertainty_Budget_Source,
    Certified_Distance,
    Pillar_Survey,
    Std_Deviation_Matrix)
from geodepy.geodesy import grid2geo, rho


def db_std_units(orig_val, orig_unit):
    # function converts all values to scalar, m, Hz, °C or hPa
    # if a distance is specified, scalar standard deviations are converted to m
    new_val = orig_val
    new_unit = orig_unit
    
    if orig_unit == 'ppm': new_val = round(orig_val / 1e6, 20)
    if orig_unit == '1:x': new_val = orig_val - 1
    if orig_unit == '%': new_val = orig_val / 100
    if orig_unit == 'nm': new_val = round(orig_val / 1e9, 20)
    if orig_unit == 'µm': new_val = round(orig_val / 1e6, 20)
    if orig_unit == 'mm': new_val = round(orig_val / 1000, 20)
    if orig_unit == 'mmHg': 
        new_val = round(float(orig_val) * 1.33322387415, 13)
    if orig_unit == 'inHg': 
        new_val = round(float(orig_val) * 33.8639, 13)
    if orig_unit == 'MHz': 
        new_val = orig_val * 1e6
        new_unit = 'Hz'
    if orig_unit == '°F': 
        new_val = (orig_val -32) * (5/9)
        new_unit = '°C'
        
    if any([orig_unit == 'nm', orig_unit == 'mm', orig_unit == 'µm']): 
        new_unit = 'm'
    if any([orig_unit == 'ppm', orig_unit == '1:x', orig_unit == '%']):
        new_unit = 'x:1'
    if any([orig_unit == 'inHg', orig_unit == 'mmHg']):
        new_unit = 'hPa'

    return new_val, new_unit


def convert_headings(raw_headings):
    converted_headings = []
    conversion_dict = {
        'height_of_instrument': 'inst_ht',
        'height_of_target': 'tgt_ht',
        'horizontal_direction(dd)': 'hz_direction',
        'slope_distance': 'raw_slope_dist',
        'temperature': 'raw_temperature',
        'pressure': 'raw_pressure',
        'humidity': 'raw_humidity',
        'pillar_rl': 'reduced_level',
        'pillar_name': 'pillar'
    }
    
    for raw_heading in raw_headings:
        if raw_heading.lower() in conversion_dict.keys():
            converted_headings.append(
                conversion_dict[raw_heading.lower()].replace(' ', '_'))
        else:
            converted_headings.append(raw_heading.lower().replace(' ', '_'))
    
    return converted_headings


def csv2dict(csv_file, clms=None, key_names=-1):
    dct={}
    rows = csv_file.read().decode("utf-8-sig").replace("\r","").split("\n")
    if not clms:
        clms = convert_headings(rows[0].split(','))

    clms.append('line')
    for lne, row in enumerate(rows[1:]):
        r = (row+','+str(lne+1)).replace('\r','').split(',')
        if key_names != -1: ky = str(r[key_names])            
        if key_names == -1: ky = str(lne + 1)
        number_of_clms = len(clms)
        try:
            if len(r) >= number_of_clms:
                dct[ky] = dict(zip(clms,r[:number_of_clms]))
        except Exception as e:
            raise ValueError (f'Invalid formating of csv file: {e}')              
    return dct


def list2dict(lst, clms, key_names=-1, filter_key=None, filter_value=None):
    dct={}
    for row in lst:
        if len(clms) == len(row):
            if key_names != -1: ky = str(row[clms.index(key_names)])
            if key_names == -1: ky = str(len(dct)+1)
            
            if not filter_key:
                dct[ky] = dict(zip(clms,row))
            elif row[clms.index(filter_key)] == filter_value:
                dct[ky] = dict(zip(clms,row))                
                
    return dct


def class2dict(clss,key_names=-1):
    dct={}
    for row in clss:
        if key_names != -1: ky = str(vars(row)[key_names])
        if key_names == -1: ky = str(len(dct)+1)
        dct[ky] = vars(row)
                
    return dct


def dict2np(dct):
    ilist=[]
    for d, v in dct.items():
        ilist.append(list(v.values()))

    return np.array(ilist, dtype=object), list(v.keys())


def dict_2_html_table(data):
    if not data:
        return "<p>No data to display.</p>"
    
    table_html = "<table>\n"
    
    # Assuming the keys of the first dictionary are the headers
    headers = data[0].keys()
    table_html += "<tr>"
    for header in headers:
        table_html += f"<th>{header}</th>"
    table_html += "</tr>\n"
    
    # Iterating over each dictionary to create rows
    for row in data:
        table_html += "<tr>"
        for key in headers:
            table_html += f"<td>{row.get(key, '')}</td>"
        table_html += "</tr>\n"
    table_html += "</table>"
    return table_html


def format_name(nme):
    num = ''.join([str(s) for s in nme if s.isdigit()])
    return nme.replace(num,num.zfill(3))


def group_list(raw_list, group_by, labels_list=[], avg_list=[], sum_list=[], std_list=[], mask_by=''):
    grouped = {}
    group_ky = 'grp_' + group_by

    for v in raw_list:
        if not v[group_by] in grouped.keys():
            grouped[v[group_by]] = {group_ky: [], group_by: v[group_by]}
            for ky in labels_list:
                grouped[v[group_by]][ky] = v.get(ky)

        if len(mask_by) == 0 or v.get(mask_by):
            grouped[v[group_by]][group_ky].append(v)

    pop_list = []
    if len(avg_list) != 0 or len(std_list) != 0 or len(sum_list) != 0:
        for i, group in grouped.items():
            if len(group[group_ky]) == 0:
                pop_list.append(i)
            else:
                for ky in avg_list:
                    values = [float(v.get(ky, 0)) for v in group[group_ky]]
                    group[ky] = mean(values)

                for ky in std_list:
                    values = [float(v.get(ky, 0)) for v in group[group_ky]]
                    group['std_' + ky] = pstdev(values)

                for ky in sum_list:
                    values = [float(v.get(ky, 0)) for v in group[group_ky]]
                    group['sum_' + ky] = sum(values)

    for i in pop_list:
        grouped.pop(i)

    return grouped


def Instruments_qry(cache_data):
    instruments={}
    instruments['edm'] = EDM_Inst.objects.select_related().get(pk=cache_data['edm'])
    instruments['prism'] = Prism_Inst.objects.select_related().get(pk=cache_data['prism'])
    if 'staff' in cache_data:
        instruments['staff'] = Staff.objects.select_related().get(pk=cache_data['staff'])
    instruments['thermometer'] = Mets_Inst.objects.select_related().get(pk=cache_data['thermometer'])
    instruments['barometer'] = Mets_Inst.objects.select_related().get(pk=cache_data['barometer'])
    if 'hygrometer' in cache_data:
        instruments['hygrometer'] = Mets_Inst.objects.select_related().get(pk=cache_data['hygrometer'])
            
    return instruments


def Calibrations_qry(frm_data):
    calib = {}
        
    #test if it is a baseline or EDMI calibration
    if 'staff' in frm_data:
        calib['edmi'] = EDMI_certificate.objects.filter(
            calibration_date__lte = frm_data['survey_date'],
            edm__pk = frm_data['edm'].pk, prism__pk = frm_data['prism'].pk
            ).order_by('-calibration_date')
        calib['staff'] = StaffCalibrationRecord.objects.filter(
            calibration_date__lte = frm_data['survey_date'] ,
            inst_staff__pk = frm_data['staff'].pk
            ).order_by('-calibration_date').first()
    else:
        calib['edmi'] = EDMI_certificate.objects.filter(
            calibration_date__lte = frm_data['survey_date'],
            edm__pk = frm_data['edm'].pk, 
            prism__pk = frm_data['prism'].pk
            ).order_by(
                '-calibration_date').select_related(
                    'certificate').values(                                
                        'calibration_date',
                        'scale_correction_factor',
                        'scf_uncertainty',
                        'zero_point_correction',
                        'zpc_uncertainty',
                        'cyclic_one',
                        'cyc_1_uncertainty',
                        'cyclic_two',
                        'cyc_2_uncertainty',
                        'cyclic_three',
                        'cyc_3_uncertainty',
                        'cyclic_four',
                        'cyc_4_uncertainty',
                        'standard_deviation',
                        'degrees_of_freedom')
                    
    calib['them'] = Mets_certificate.objects.filter(
                calibration_date__lte = frm_data['survey_date'] ,
                instrument__pk = frm_data['thermometer'].pk
                ).order_by('-calibration_date').first()
    calib['baro'] = Mets_certificate.objects.filter(
                calibration_date__lte = frm_data['survey_date'] ,
                instrument__pk = frm_data['barometer'].pk
                ).order_by('-calibration_date').first()
    if 'hygrometer' in frm_data:
        calib['hygro'] = Mets_certificate.objects.filter(
                    calibration_date__lte = frm_data['survey_date'] ,
                    instrument__pk = frm_data['hygrometer'].pk
                    ).order_by('-calibration_date').first()
    
    return calib


def baseline_qry(frm_data):
    baseline={}
    if 'baseline' in frm_data:
        baseline['site'] = frm_data['baseline']
        baseline['history'] = (Certified_Distance.objects.select_related().filter(
                pillar_survey__baseline__pk = frm_data['baseline'].pk)
                .order_by('pillar_survey__survey_date','to_pillar__order'))
    
    if 'auto_base_calibration' in frm_data:
        if frm_data['auto_base_calibration']:
            baseline['site'] = frm_data['site']
            baseline['calibrated_baseline'] = (
                Pillar_Survey.objects.filter(
                    baseline = frm_data['site'].pk,
                    survey_date__lte = frm_data['survey_date'])
                .exclude(variance__isnull = True)
                .order_by('-survey_date'))[0]
        else:
            baseline['calibrated_baseline'] = frm_data['calibrated_baseline']
            baseline['site'] = baseline['calibrated_baseline'].baseline
    
        sd_m = (Std_Deviation_Matrix.objects
                .select_related('from_pillar', 'to_pillar')
                .filter(pillar_survey__pk = baseline['calibrated_baseline'].pk))
        baseline['std_dev_matrix'] = ({s.from_pillar.name + ' - ' + s.to_pillar.name:
                                        model_to_dict(s) for s in sd_m})

        cd = (Certified_Distance.objects
                .select_related('from_pillar', 'to_pillar')
                .filter(pillar_survey__pk = baseline['calibrated_baseline'].pk))
        baseline['certified_dist'] ={d.to_pillar.name:model_to_dict(d) for d in cd}
        
    baseline['pillars'] = Pillar.objects.filter(
                            site_id__pk = baseline['site'].pk
                            ).order_by('order')
    
    baseline_enz = Pillar.objects.filter(
                            site_id__pk = baseline['site'].pk).aggregate(
                                Avg('easting'), Avg('northing'), Avg('zone'))
    baseline_llh = grid2geo(float(baseline_enz['zone__avg']),
                            float(baseline_enz['easting__avg']),
                            float(baseline_enz['northing__avg']))
    baseline['d_radius'] = rho(baseline_llh[0])
    
    return baseline
        
    
def uncertainty_qry(frm_data):
    uc_budget={}
    uc_sources = (
        Uncertainty_Budget_Source.objects.filter(
            uncertainty_budget__pk = frm_data['uncertainty_budget'].pk)
        )

    uc_budget['sources'] = list(uc_sources.values())

    uc_budget['stddev_0_adj'] = float(frm_data['uncertainty_budget']
                                      .std_dev_of_zero_adjustment)
    return uc_budget


def report_notes_qry(company, report_type):
    rpt_notes = Calibration_Report_Notes.objects.filter(
                    Q(report_type = report_type, note_type = 'M') |
                    Q(report_type = report_type, note_type = 'C',company = company)
                    ).order_by('-note_type','pk')
    report_notes = []
    for n in rpt_notes:
        report_notes = report_notes + (n.note.split('\n'))

    return report_notes


def decrypt_file(file):
    NORMAL_CHARS =  r'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 abcdefghijklmnopqrstuvwxyz.|(),;"!@#$%^&*()_-+={}[]\<>?/:' +"'"
    ENCRYPT_CHARS = r'962XRLD7YJS1AHBQ5NCO3M08EKGIWUPTVZ4F qwertyuiopasdfghjklzxcvbnm|.(),;"!@#$%^&*()_-=+{}[]\<>?/:'+"'"
    
    dct=dict(zip(ENCRYPT_CHARS,NORMAL_CHARS))
    
    encrypted_rows = file.read().decode("utf-8").replace('\r','').split("\n")
    decrypted_rows = []
    for row in encrypted_rows[1:]:
        decrypted_str = ''
        for s in row:
            decrypted_str += dct[s]
        decrypted_rows.append(decrypted_str.split('|'))
    
    return decrypted_rows