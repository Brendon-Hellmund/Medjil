from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.forms import modelformset_factory
from django.forms.models import model_to_dict
from django.http import QueryDict, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string

from collections import OrderedDict
from math import pi, sin, cos, sqrt
from datetime import date
from common_func.Convert import (
    baseline_qry,
    Calibrations_qry,
    csv2dict,
    dict_2_html_table,
    report_notes_qry,
    uncertainty_qry,
    group_list)
from common_func.SurveyReductions import (
    validate_survey,
    get_mets_params,
    apply_calib,
    edm_mets_correction,
    edm_std_function,
    offset_slope_correction,
    slope_certified_dist,
    add_certified_dist_uc,
    add_surveyed_uc,
    add_calib_uc,
    refline_std_dev,
    sum_uc_budget,
    add_typeA
    )
from .forms import (
    CalibrateEdmForm,
    UploadSurveyFiles,
    ChangeSurveyFiles,
    EDM_ObservationForm,
    PillarSurveyApprovals,
    EDMI_certificateForm
    )
from .models import (
    EDMI_certificate,
    uPillar_Survey,
    uEDM_Observation
    )
from common_func.LeastSquares import (
    LSA,
    ISO_test_a,
    ISO_test_b,
    ISO_test_c)
from baseline_calibration.models import (
    Uncertainty_Budget_Source)

    
@login_required(login_url="/accounts/login")
def edm_calibration_home(request):
    if request.user.is_superuser:
        pillar_surveys = uPillar_Survey.objects.all()
    else:        
        pillar_surveys = uPillar_Survey.objects.select_related('edm').filter(
            edm__edm_specs__edm_owner = request.user.company.id)
        
    context = {
        'pillar_surveys': pillar_surveys}
    
    return render(request, 'edm_calibration/edm_calibration_home.html', context)


def clear_cache(request):
    if 'calibrate_e' in request.session:
        del request.session['calibrate_e']
        
        return redirect('edm_calibration:edm_calibration_home')


@login_required(login_url="/accounts/login") 
def pillar_survey_del(request, id):
    try:
        delete_pillar_survey = uPillar_Survey.objects.get(id=id)
        if delete_pillar_survey.certificate:
            delete_pillar_survey.certificate.delete()
        delete_pillar_survey.delete()
    except:
        messages.error(
            request, 
            "This action cannot be performed! This record has a dependant record.")

    return redirect('edm_calibration:edm_calibration_home')


@login_required(login_url="/accounts/login") 
def calibrate1(request, id):
    if id == 'None':
        qs=''
        ini_data = {'computation_date':date.today().isoformat()}
        pillar_survey = CalibrateEdmForm(request.POST or None,
                                request.FILES or None,
                                user=request.user,
                                initial=ini_data)
        upload_survey_files = UploadSurveyFiles(request.POST or None,
                                                request.FILES or None)
    else:
        qs = get_object_or_404(uPillar_Survey, id=id)
        pillar_survey = CalibrateEdmForm(request.POST or None,
                                         request.FILES or None,
                                         instance = qs,
                                         user = request.user)
        upload_survey_files = ChangeSurveyFiles(request.POST or None,
                                                request.FILES or None)

    if pillar_survey.is_valid() and upload_survey_files.is_valid():
        frm = pillar_survey.cleaned_data
        survey_files = upload_survey_files.cleaned_data
        
        # Check the baseline has a valid calibration
        Check_Errors = validate_survey(pillar_survey = frm)
        if len(Check_Errors['Errors']) > 0:
            return render(request, 'baseline_calibration/errors_report.html', 
                          {'Check_Errors': Check_Errors})
    #----------------- Query related fields -----------------#
        calib = Calibrations_qry(frm)
        baseline = baseline_qry(frm)
        
        # read new edm file
        if survey_files['edm_file']:
            edm_clms=['from_pillar',
                      'to_pillar',
                      'inst_ht',
                      'tgt_ht',
                      'raw_slope_dist',
                      'raw_temperature',
                      'raw_pressure',
                      'raw_humidity']
            raw_edm_obs = csv2dict(survey_files['edm_file'],edm_clms)
            for v in raw_edm_obs.values():
                v['use_for_distance'] = True
                                   
            Check_Errors = validate_survey(pillar_survey=frm,
                                        baseline=baseline,
                                        calibrations=calib,
                                        raw_edm_obs=raw_edm_obs)
            
            if len(Check_Errors['Errors']) > 0:
                return render(request, 'baseline_calibration/errors_report.html', 
                              {'Check_Errors':Check_Errors})
        else:
            qs = uEDM_Observation.objects.filter(pillar_survey__pk=id)
            raw_edm_obs = {}
            for o in qs:
                dct = model_to_dict(o)
                dct['from_pillar'] = o.from_pillar.name
                dct['to_pillar'] = o.to_pillar.name
                raw_edm_obs[str(o.id)] = dct
            
        ps_instance = pillar_survey.save(commit=False)
        if frm['auto_base_calibration']:
            ps_instance.calibrated_baseline = baseline['calibrated_baseline']
        ps_instance.save()
        
        id = ps_instance.pk
        if survey_files['edm_file']:
            # Commit all the edm raw observations
            delete_edm_obs = uEDM_Observation.objects.filter(pillar_survey=id)
            delete_edm_obs.delete()
            for o in raw_edm_obs.values():
                uEDM_Observation.objects.create(
                    pillar_survey = ps_instance,
                    from_pillar = baseline['pillars'].get(name=o['from_pillar']),
                    to_pillar = baseline['pillars'].get(name=o['to_pillar']),
                    inst_ht = o['inst_ht'],
                    tgt_ht = o['tgt_ht'],
                    raw_slope_dist = o['raw_slope_dist'],
                    raw_temperature = o['raw_temperature'],
                    raw_pressure = o['raw_pressure'],
                    raw_humidity = o['raw_humidity'],
                    use_for_distance = o['use_for_distance'])         
                            
        return redirect('edm_calibration:calibrate2', id=id)

    else:
        for e in pillar_survey.errors:
            print(e)
        for e in upload_survey_files.errors:
            print(e)
            
    headers = {'page0':'EDMI Calibration Details',
                'page1': 'Instrumentation',
                'page2': 'Corrections / Calibrations Applied to Instruments',
                'page3': 'Error Budget and File Uploads',}
    
    return render(request, 'edm_calibration/calibrate.html', {
            'Headers': headers,
            'form': pillar_survey,
            'qs':qs,
            'survey_files':upload_survey_files})

@login_required(login_url="/accounts/login") 
def calibrate2(request,id):
    # If this is a get request:
    #     select or deselect the edm observations for the calibration
    # If this is a post request: and edm_obs_formset.is_valid
    #     calculate and generate the report. 
    # If this is a post request: cd_formset.is_valid() and sdev_mat_formset.is_valid() and pillar_survey_update.is_valid()
    #     comit the calibration and return to home page.
    
    #----------------- Query site, surveys, instruments and calibrations -----------------#
    # Get the pillar_survey in dict like cleaned form data
    ps_qs = uPillar_Survey.objects.get(id=id)
    query_dict = QueryDict('', mutable=True)
    query_dict.update(model_to_dict(ps_qs))
    pillar_survey_form = CalibrateEdmForm(query_dict, user=request.user)
    pillar_survey_form.is_valid()
    pillar_survey = pillar_survey_form.cleaned_data
    pillar_survey['pk'] = id
        
    # Get the raw_edm_obs in dict like cleaned form data
    formset = modelformset_factory(uEDM_Observation,
                            form=EDM_ObservationForm, extra=0)
    qs = uEDM_Observation.objects.filter(pillar_survey__pk=id)
    edm_obs_formset = formset(request.POST or None, queryset=qs)
    raw_edm_obs = {}
    for o in qs:
        dct = model_to_dict(o)
        dct['from_pillar'] = o.from_pillar.name
        dct['to_pillar'] = o.to_pillar.name
        raw_edm_obs[str(o.id)] = dct

    if request.method == 'GET':
        # Display page 5 of 5 edm raw data
        formset = zip(edm_obs_formset, raw_edm_obs.values())
        
        return render(request, 'edm_calibration/edm_rawdata.html', 
                      {'Page': 'Page 5 of 5',
                       'id': id,
                       'edm_obs_formset': edm_obs_formset,
                       'pillar_survey': pillar_survey,
                       'formset': formset})
    else:
        # This is a POST request
        # Update the 'use_for_distance' and recheck errors
        if edm_obs_formset.is_valid():
            edm_obs_formset.save()
            for form in edm_obs_formset:
                frm =form.cleaned_data
                raw_edm_obs[str(frm['id'].pk)]['use_for_distance']=frm['use_for_distance']
            
            context = edm_report_context(
                request, pillar_survey, raw_edm_obs, ps_qs)

            return render(request, 'edm_calibration/calibrate_report.html', context)

        #----------------------- code for commiting the calibration and returning to home page -----------------------------#        
        pillar_approvals_update = PillarSurveyApprovals(request.POST)
        EDMI_certificate = EDMI_certificateForm(request.POST)
        if ps_qs.certificate:
            EDMI_certificate = EDMI_certificateForm(request.POST, instance=ps_qs.certificate)
        else:
            EDMI_certificate = EDMI_certificateForm(request.POST)
        
        if (EDMI_certificate.is_valid() and pillar_approvals_update.is_valid()):
            # this is a POST command asking to commit the hidden calibration 
            # data held on the report page
            
            context = edm_report_context(
                request, pillar_survey, raw_edm_obs, ps_qs)            
            context['archive']=True
            html_content = render_to_string(
                'edm_calibration/calibrate_report.html', context)

            approvals = pillar_approvals_update.cleaned_data
            cert_instance = EDMI_certificate.save(commit=False)
            cert_instance.html_report = html_content
            cert_instance.save()
            
            pillar_survey = uPillar_Survey.objects.get(id=id)
            pillar_survey.data_entered_person = approvals['data_entered_person']
            pillar_survey.data_entered_position = approvals['data_entered_position']
            pillar_survey.data_entered_date = approvals['data_entered_date']
            pillar_survey.data_checked_person = approvals['data_checked_person']
            pillar_survey.data_checked_position = approvals['data_checked_position']
            pillar_survey.data_checked_date = approvals['data_checked_date']
            pillar_survey.certificate = cert_instance
            pillar_survey.save()
                
            return redirect('edm_calibration:edm_calibration_home')
        
def certificate(request, id):
    
    certificate_qs = get_object_or_404(EDMI_certificate, id=id)
    html_content = certificate_qs.html_report
    return HttpResponse(html_content, content_type='text/html')


def edm_report_context(request, pillar_survey, raw_edm_obs, ps_qs):
    calib = Calibrations_qry(pillar_survey)
    baseline = baseline_qry(pillar_survey)
                           
    Check_Errors = validate_survey(pillar_survey=pillar_survey,
                                baseline=baseline,
                                calibrations=calib,
                                raw_edm_obs=raw_edm_obs)
    
    if len(Check_Errors['Errors']) > 0:
        return render(request, 'baseline_calibration/errors_report.html', 
                      {'Check_Errors':Check_Errors})
                      
    #----------------- Query notes and Uncertainty -----------------#
    report_notes = report_notes_qry(company=request.user.company, report_type='E')
    uc_budget = uncertainty_qry(pillar_survey)
    uc_budget['sources'] = add_calib_uc(uc_budget['sources'], 
                                        calib,
                                        pillar_survey)
    get_mets_params(
        pillar_survey['edm'], 
        pillar_survey['mets_applied'])
    for o in raw_edm_obs.values():
        #----------------- Instrument Corrections -----------------#
        o['Temp'],c = apply_calib(o['raw_temperature'],
                                    pillar_survey['thermo_calib_applied'], 
                                    calib['them'])
        o['Pres'],c = apply_calib(o['raw_pressure'],
                                    pillar_survey['baro_calib_applied'],
                                    calib['baro'])
        o['Humid'],c = apply_calib(o['raw_humidity'],
                                    pillar_survey['hygro_calib_applied'],
                                    calib['hygro'])
        o = edm_mets_correction(o, 
                                pillar_survey['edm'],
                                pillar_survey['mets_applied'])
        
        o['slope_dist'] = (float(o['raw_slope_dist'] )
                           + o['Mets_Correction'])
        o['Bay'] = o['from_pillar'] + ' - ' + o['to_pillar']
    
    edm_observations = group_list(raw_edm_obs.values(),
                                    group_by='Bay',
                                    labels_list=['from_pillar',
                                                 'to_pillar'],
                                    avg_list=['inst_ht',
                                              'tgt_ht',
                                              'Temp',
                                              'Pres',
                                              'Humid',
                                              'Mets_Correction',
                                              'raw_slope_dist',
                                              'slope_dist',],
                                    std_list=['slope_dist'])
    
    edm_trend = edm_std_function(edm_observations, 
                                 uc_budget['stddev_0_adj'])           #y = Ax + B
                   
    matrix_A = []
    matrix_x = []
    matrix_P = []
    for i, o in enumerate(edm_observations.values()):
        o['id']=str(i+1)
        o = (offset_slope_correction(o,
                                  baseline['certified_dist'],
                                  baseline['certified_dist'],
                                  baseline['d_radius']))
        
        o['certified_slope_dist'] = (slope_certified_dist(o, 
                                      baseline['certified_dist'],
                                      baseline['d_radius']))
        o['diff_to_certified_sd'] = (o['slope_dist']
                                     - o['certified_slope_dist'])
        
        o['Reduced_distance'] = (o['slope_dist'] 
                                + o['Offset_Correction']
                                + o['Slope_Correction'])

        #----------------- Calculate Uncertainties -----------------#
        o['uc_sources'] = add_certified_dist_uc(o, 
                                          uc_budget['sources'],
                                          baseline['std_dev_matrix'],
                                          baseline['calibrated_baseline'].degrees_of_freedom)
        
        o['uc_sources'] = add_surveyed_uc(o, edm_trend, 
                                          o['uc_sources'],
                                          baseline['certified_dist'])
              
        o['uc_budget'] = refline_std_dev(o, 
                                        baseline['certified_dist'], 
                                        pillar_survey['edm'])
          
        o['uc_combined'] = sum_uc_budget(o['uc_budget'])
        
        #----------------- Least Squares -----------------#
        #----------------- compile Design matrix, weight Matrix -----------------#
        d_term = ((2*pi*o['Reduced_distance'])
                  / pillar_survey['edm'].edm_specs.unit_length)
        o['d_term'] = d_term
        a_row = [1,
                 o['Reduced_distance'],
                 sin(d_term),
                 cos(d_term),
                 sin(2*d_term),
                 cos(2*d_term)]
        matrix_A.append(a_row)
      
        frm = baseline['certified_dist'][o['from_pillar']]['distance']
        to = baseline['certified_dist'][o['to_pillar']]['distance']
        matrix_x.append(abs(float(to) - float(frm))
                             -o['Reduced_distance'])
          
        P_row = [0]*len(edm_observations)
        P_row[len(matrix_x)-1] = (1/
                (o['uc_combined']['std_dev']*float(pillar_survey['scalar']))**2)
        matrix_P.append(P_row)
    
    if not pillar_survey['test_cyclic']:
        matrix_A = [a[:2] for a in matrix_A]
        order_cmt = ['zero']
        report_notes.append('User input for this calibration requested that no test for cyclic errors be performed.')
    
    # run LSA with 6, 4 then 2 parameters
    # Check t-student test results after each LSA to determine if the end 2 cyclic errors are significant
    testing_terms = [True, True]
    while False not in testing_terms and len(matrix_A[0])!=0:
        matrix_y, vcv_matrix, chi_test, residuals = LSA(matrix_A, 
                                                        matrix_x,
                                                        matrix_P)
        
        matrix_y[0]['term']='zpc'
        matrix_y[1]['term']='scf'
        for i, p in enumerate(matrix_y[2:]):
            p['term'] = f'{i+1}C'

        if pillar_survey['test_cyclic']:
            testing_terms = [t['t_test'] for t in matrix_y[-2:]]
            if len(matrix_A[0])==6: order_cmt = 'second'
            if len(matrix_A[0])==4: order_cmt = 'first'
            if len(matrix_A[0])!= 2:
                if False in testing_terms:
                    report_notes.append(
                        f'The t-student test has been used to test and determine that the {order_cmt} ' \
                        f'order cyclic errors are statistically significant in this calibration data.')
                else:
                    notes_tbl = []
                    for y in matrix_y:
                        notes_tbl.append(
                            {'Term':y['term'],
                             'Value': round(y['value'],5),
                             'Uncertainty': "{:.2g}".format(y['uncertainty']),
                             'Null Hypothesis': y['hypothesis'],
                             'Insignificant':y['t_test']})
                    notes_tbl = dict_2_html_table(notes_tbl)
                    report_notes.append(
                        f'The t-student test has been used to test the significance of the {order_cmt} order cyclic errors.' \
                        f' This has determined that these cyclic errors are statistically insignificant in this calibration data.' \
                        f'{notes_tbl}')
                        
        # remove 2 parameters to maybe run again
        matrix_A = [a[:-2] for a in matrix_A]
    
    pillar_survey['parameters'] = matrix_y
    ini_edmi_certificate = {
        'edm':pillar_survey['edm'],
        'prism':pillar_survey['prism'],
        'calibration_date': pillar_survey['survey_date'],
        'zero_point_correction': matrix_y[0]['value'],
        'zpc_uncertainty': matrix_y[0]['uncertainty'],
        'zpc_coverage_factor': chi_test['k'],
        'standard_deviation': sqrt(chi_test['Variance']),
        'degrees_of_freedom': chi_test['dof'],
        'scale_correction_factor': matrix_y[1]['value'] + 1,
        'scf_uncertainty': matrix_y[1]['uncertainty'],
        'scf_coverage_factor': chi_test['k']
        }
    if len(matrix_y)>2:
        ini_edmi_certificate.update({
            'has_cyclic_corrections': True,
            'cyclic_one': matrix_y[2]['value'],
            'cyc_1_uncertainty': matrix_y[2]['uncertainty'],
            'cyc_1_coverage_factor': chi_test['k'],
            'cyclic_two': matrix_y[3]['value'],
            'cyc_2_uncertainty': matrix_y[3]['uncertainty'],
            'cyc_2_coverage_factor': chi_test['k']
            })
    if len(matrix_y)>4:
        ini_edmi_certificate.update({
            'cyclic_three': matrix_y[4]['value'],
            'cyc_3_uncertainty': matrix_y[4]['uncertainty'],
            'cyc_3_coverage_factor': chi_test['k'],
            'cyclic_four': matrix_y[4]['value'],
            'cyc_4_uncertainty': matrix_y[4]['uncertainty'],
            'cyc_4_coverage_factor': chi_test['k']
            })
    edmi_certificate = EDMI_certificateForm(initial=ini_edmi_certificate)
            
    for o in edm_observations.values():
        o['residual'] = residuals[o['id']]['residual']
        o['std_residual'] = residuals[o['id']]['std_residual']
        o['uc_sources'] = add_typeA(o, matrix_y, chi_test['dof'])      
        o['uc_budget'] = refline_std_dev(
            o, 
            baseline['certified_dist'], 
            pillar_survey['edm'])
          
        o['uc_combined'] = sum_uc_budget(o['uc_budget'])
    
    # Perform ISO statistical tests
    ISO_test=[]
    ISO_test.append(
        ISO_test_a(
            pillar_survey,
            chi_test,
            [{'distance':50},
             {'distance':100},
             {'distance':200},
             {'distance':400}, 
             {'distance':600}])
        )
    
    if len(calib['edmi']) > 1:
        ISO_test.append(
            ISO_test_b(
                {'Variance':(calib['edmi'][1]['standard_deviation'])**2,
                 'dof': calib['edmi'][1]['degrees_of_freedom']},
                chi_test)
            )
        
    ISO_test.append(
        ISO_test_c(
            matrix_y[0]['value'],
            matrix_y[0]['std_dev'],
            chi_test))

    #Prepare the context for the template    
    back_colours = ['#FF0000', '#800000', '#FFFF00', '#808000', 
                    '#00FF00', '#008000', '#00FFFF', '#008080', 
                    '#0000FF', '#000080', '#FF00FF', '#800080',]
    
    edm_observations = list(edm_observations.values())
    first_to_last = {'Reduced_distance':0}
    residual_chart = []
    n_rpt_shots = max([len(e['grp_Bay']) for e in edm_observations])
    i=0
    for o in edm_observations:
        if i == len(back_colours): i=0
        while len(o['grp_Bay'])<n_rpt_shots:
            o['grp_Bay'].append('')
            
        for uc in o['uc_budget'].values():
            uc['chart_colour'] = back_colours[i]
            if uc['group'] in dict(Uncertainty_Budget_Source.group_types).keys():
                uc['group_verbose'] = dict(Uncertainty_Budget_Source.group_types)[uc['group']]
        i+=1
        for uc in o['uc_sources']:
            if uc['group'] in dict(Uncertainty_Budget_Source.group_types).keys():
                uc['group_verbose'] = dict(Uncertainty_Budget_Source.group_types)[uc['group']]
        o['uc_sources']=sorted(o['uc_sources'], key=lambda x: x['group_verbose'])
        o['uc_budget'] = OrderedDict(sorted(o['uc_budget'].items()))
        
        residual_chart.append({'from_pillar': o['from_pillar'], 
                           'to_pillar':o['to_pillar'],
                           'Reduced_distance': o['Reduced_distance'],
                           'residual': o['residual'],
                           'std_residual': o['std_residual']})
        if o['Reduced_distance'] > first_to_last['Reduced_distance']:
            first_to_last = o
    
    #Add current pillar survey to history table
    # calib['edmi'][0]['k'] = chi_test['k']
    # calib['edmi'][0]['parameters'] = matrix_y
    
    #create signiture block
    pillar_approvals_update = PillarSurveyApprovals(instance=ps_qs)
    
    context = {'pillar_survey':pillar_survey,
               'pillar_approvals_update':pillar_approvals_update,
               'calib':calib,
               'baseline': baseline,
               'chi_test': chi_test,
               'ISO_test': ISO_test,
               'edm_observations': edm_observations,
               'residual_chart': residual_chart,
               'report_notes': report_notes,
               'Check_Errors': Check_Errors,
               'first_to_last': first_to_last,
               'hidden':[edmi_certificate]}
    return context
