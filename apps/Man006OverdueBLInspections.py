import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import plotly.graph_objs as go
import pandas as pd
from dash.dependencies import Input, Output
from datetime import datetime
import urllib.parse

from app import app, con

testing_mode = False
print("Man006OverdueBLInspections.py")
print("Testing mode? " + str(testing_mode))

if testing_mode:
    df = pd.read_csv("test_data/Man006OverdueBLInspections_test_data_short.csv")
    df['ScheduledInspectionDateField'] = pd.to_datetime(df['ScheduledInspectionDateField'])
else:
    with con() as con:
        sql = """SELECT biz.address "Business Address", lic.externalfilenum "License Number", lic.licensetype "License Type",( CASE WHEN jt.name LIKE 'j_BL_Inspection' THEN ins.externalfilenum END) "Job Number", jt.Description "Job Type", ( CASE WHEN jt.name LIKE 'j_BL_Inspection' THEN 'License' WHEN jt.name LIKE 'j_BL_Application' THEN 'Application' WHEN jt.name LIKE 'j_BL_AmendRenew' THEN 'Renewal or Amend' END ) "Inspection On", ins.inspectiontype "Inspection Type", ins.objectid "Insp Object Id", Extract(month FROM ins.createddate) || '/' ||Extract(day FROM ins.createddate) || '/' || Extract(year FROM ins.createddate) "Inspection Created Date", round(SYSDATE - ins.createddate) "Days Since Insp Created", Extract(month FROM ins.scheduledinspectiondate) || '/' ||Extract(day FROM ins.scheduledinspectiondate) || '/' || Extract(year FROM ins.scheduledinspectiondate) "Scheduled Inspection Date", ins.scheduledinspectiondate "ScheduledInspectionDateField", ins.inspectorname "Inspector" FROM query.j_bl_inspection ins, query.r_bl_licenseinspection li, query.o_bl_license lic, query.o_bl_business biz, query.o_jobtypes jt WHERE ins.objectid = li.inspectionid AND ins.jobtypeid = jt.jobtypeid AND li.licenseid = lic.objectid AND lic.businessobjectid = biz.objectid AND ins.scheduledinspectiondate <= SYSDATE AND ins.completeddate IS NULL UNION SELECT biz.address "Business Address", lic.externalfilenum "License Number", lic.licensetype "License Type", ( CASE WHEN jt.name LIKE 'j_BL_Inspection' THEN ins.externalfilenum WHEN jt.name LIKE 'j_BL_Application' THEN ap.externalfilenum END ) "Job Number", jt.Description "Job Type", ( CASE WHEN jt.name LIKE 'j_BL_Inspection' THEN 'License' WHEN jt.name LIKE 'j_BL_Application' THEN 'Application' WHEN jt.name LIKE 'j_BL_AmendRenew' THEN 'Renewal or Amend' END ) "Inspection On", ins.inspectiontype "Inspection Type", ins.objectid "Insp Object Id", Extract(month FROM ins.createddate) || '/' ||Extract(day FROM ins.createddate) || '/' || Extract(year FROM ins.createddate) "Inspection Created Date", round(SYSDATE - ins.createddate) "Days Since Insp Created", Extract(month FROM ins.scheduledinspectiondate) || '/' ||Extract(day FROM ins.scheduledinspectiondate) || '/' || Extract(year FROM ins.scheduledinspectiondate) "Scheduled Inspection Date", ins.scheduledinspectiondate "ScheduledInspectionDateField", ins.inspectorname "Inspector" FROM query.j_bl_inspection ins, query.r_bl_applicationinspection api, query.j_bl_application ap, query.o_jobtypes jt, query.r_bl_application_license apl, query.o_bl_license lic, query.o_bl_business biz WHERE ins.objectid = api.inspectionid AND api.applicationid = ap.objectid AND ap.jobtypeid = jt.jobtypeid AND ap.objectid = apl.applicationobjectid AND apl.licenseobjectid = lic.objectid AND lic.businessobjectid = biz.objectid AND ins.scheduledinspectiondate <= SYSDATE AND ins.completeddate IS NULL UNION SELECT biz.address "Business Address", lic.externalfilenum "License Number", lic.licensetype "License Type", ( CASE WHEN jt.name LIKE 'j_BL_Inspection' THEN ins.externalfilenum WHEN jt.name LIKE 'j_BL_AmendRenew' THEN ar.externalfilenum END ) "Job Number", jt.Description "Job Type", ( CASE WHEN jt.name LIKE 'j_BL_Inspection' THEN 'License' WHEN jt.name LIKE 'j_BL_Application' THEN 'Application' WHEN jt.name LIKE 'j_BL_AmendRenew' THEN 'Renewal or Amend' END ) "Inspection On", ins.inspectiontype "Inspection Type", ins.objectid "Insp Object Id", Extract(month FROM ins.createddate) || '/' ||Extract(day FROM ins.createddate) || '/' || Extract(year FROM ins.createddate) "Inspection Created Date", round(SYSDATE - ins.createddate) "Days Since Insp Created", Extract(month FROM ins.scheduledinspectiondate) || '/' ||Extract(day FROM ins.scheduledinspectiondate) || '/' || Extract(year FROM ins.scheduledinspectiondate) "Scheduled Inspection Date", ins.scheduledinspectiondate "ScheduledInspectionDateField", ins.inspectorname "Inspector" FROM query.j_bl_inspection ins, query.r_bl_amendrenewinspection ari, query.j_bl_amendrenew ar, query.o_jobtypes jt, query.r_bl_amendrenew_license arl, query.o_bl_license lic, query.o_bl_business biz WHERE ins.objectid = ari.inspectionid AND ari.amendrenewid = ar.jobid AND ar.jobtypeid = jt.jobtypeid AND ar.objectid = arl.amendrenewid AND arl.licenseid = lic.objectid AND lic.businessobjectid = biz.objectid AND ins.scheduledinspectiondate <= SYSDATE AND ins.completeddate IS NULL"""
        df = pd.read_sql(sql, con)

licensetype_options_unsorted = []
for licensetype in df['License Type'].unique():
    if str(licensetype) != "nan":
        licensetype_options_unsorted.append({'label': str(licensetype), 'value': licensetype})
licensetype_options_sorted = sorted(licensetype_options_unsorted, key=lambda k: k['label'])

jobtype_options_unsorted = []
for jobtype in df['Job Type'].unique():
    if str(jobtype) != "nan":
        jobtype_options_unsorted.append({'label': str(jobtype), 'value': jobtype})
jobtype_options_sorted = sorted(jobtype_options_unsorted, key=lambda k: k['label'])

inspector_options_unsorted = []
for inspector in df['Inspector'].unique():
    if str(inspector) != "nan":
        inspector_options_unsorted.append({'label': str(inspector), 'value': inspector})
inspector_options_sorted = sorted(inspector_options_unsorted, key=lambda k: k['label'])

def get_data_object(selected_start, selected_end, license_type, job_type, inspector):
    df_selected = df[(df['ScheduledInspectionDateField'] >= selected_start) & (df['ScheduledInspectionDateField'] <= selected_end)]
    if license_type is not None:
        if isinstance(license_type, str):
            df_selected = df_selected[df_selected['License Type'] == license_type]
        elif isinstance(license_type, list):
            if len(license_type) > 1:
                df_selected = df_selected[df_selected['License Type'].isin(license_type)]
            elif len(license_type) == 1:
                df_selected = df_selected[df_selected['License Type'] == license_type[0]]
    if job_type is not None:
        if isinstance(job_type, str):
            df_selected = df_selected[df_selected['Job Type'] == job_type]
        elif isinstance(job_type, list):
            if len(job_type) > 1:
                df_selected = df_selected[df_selected['Job Type'].isin(job_type)]
            elif len(job_type) == 1:
                df_selected = df_selected[df_selected['Job Type'] == job_type[0]]
    if inspector is not None:
        if isinstance(inspector, str):
            df_selected = df_selected[df_selected['Inspector'] == inspector]
        elif isinstance(inspector, list):
            if len(inspector) > 1:
                df_selected = df_selected[df_selected['Inspector'].isin(inspector)]
            elif len(inspector) == 1:
                df_selected = df_selected[df_selected['Inspector'] == inspector[0]]
    if len(df_selected['Days Since Insp Created']) > 0:
        df_selected['Days Since Insp Created'] = df_selected.apply(lambda x: "{:,}".format(x['Days Since Insp Created']), axis=1)
    return df_selected.drop('ScheduledInspectionDateField', axis=1)

def count_jobs(selected_start, selected_end, license_type, job_type, inspector):
    df_count_selected = df[(df['ScheduledInspectionDateField'] >= selected_start) & (df['ScheduledInspectionDateField'] <=selected_end)]
    if license_type is not None:
        if isinstance(license_type, str):
            df_count_selected = df_count_selected[df_count_selected['License Type'] == license_type]
        elif isinstance(license_type, list):
            if len(license_type) > 1:
                df_count_selected = df_count_selected[df_count_selected['License Type'].isin(license_type)]
            elif len(license_type) == 1:
                df_count_selected = df_count_selected[df_count_selected['License Type'] == license_type[0]]
    if job_type is not None:
        if isinstance(job_type, str):
            df_count_selected = df_count_selected[df_count_selected['Job Type'] == job_type]
        elif isinstance(job_type, list):
            if len(job_type) > 1:
                df_count_selected = df_count_selected[df_count_selected['Job Type'].isin(job_type)]
            elif len(job_type) == 1:
                df_count_selected = df_count_selected[df_count_selected['Job Type'] == job_type[0]]
    if inspector is not None:
        if isinstance(inspector, str):
            df_count_selected = df_count_selected[df_count_selected['Inspector'] == inspector]
        elif isinstance(inspector, list):
            if len(inspector) > 1:
                df_count_selected = df_count_selected[df_count_selected['Inspector'].isin(inspector)]
            elif len(inspector) == 1:
                df_count_selected = df_count_selected[df_count_selected['Inspector'] == inspector[0]]
    df_counter = df_count_selected.groupby(by=['License Type', 'Inspection On'], as_index=False).agg({'Insp Object Id': pd.Series.nunique})
    df_counter = df_counter.rename(columns={'License Type': "License Type", 'Inspection On': 'Inspection On', 'Insp Object Id': 'Count of Overdue Inspections'})
    if len(df_counter['Count of Overdue Inspections']) > 0:
        df_counter['Count of Overdue Inspections'] = df_counter.apply(lambda x: "{:,}".format(x['Count of Overdue Inspections']), axis=1)
    return df_counter

#TODO why is this not including high date?

layout = html.Div(
    children=[
        html.H1(
            'Inspections Past their Scheduled Completion Date',
            style={'margin-top': '10px'}
        ),
        html.H1(
            '(Business Licenses and BL Jobs)',
            style={'margin-bottom': '50px'}
        ),
        html.Div([
            html.Div([
                html.P('Please Select Date Range (Scheduled Inspection Date)'),
                dcc.DatePickerRange(
                    id='Man006BL-my-date-picker-range',
                    start_date=datetime(2018, 1, 1),
                    end_date=datetime.now()
                )
            ], className='five columns'),
            html.Div([
                html.P('Inspector'),
                dcc.Dropdown(
                    id='inspector-dropdown',
                    options=inspector_options_sorted,
                    multi=True
                )
            ], className='five columns'),
        ], className='dashrow filters'),
        html.Div([
            html.Div([
                html.P('License Type'),
                dcc.Dropdown(
                    id='licensetype-dropdown',
                    options=licensetype_options_sorted,
                    multi=True
                ),
            ], className='five columns'),
            html.Div([
                html.P('Job Type'),
                dcc.Dropdown(
                    id='jobtype-dropdown',
                    options=jobtype_options_sorted,
                    multi=True
                ),
            ], className='five columns'),
        ], className='dashrow filters'),
        html.Div([
            html.Div([
                html.Div([
                    dt.DataTable(
                        rows=[{}],
                        row_selectable=True,
                        sortable=True,
                        selected_row_indices=[],
                        id='Man006BL-count-table'
                    ),
                ]),
                html.Div([
                    html.A(
                        'Download Data',
                        id='Man006BL-count-table-download-link',
                        download='Man006BL-counts.csv',
                        href='',
                        target='_blank'
                    ),
                ], style={'text-align': 'right'})
            ], style={'margin-top': '70px', 'margin-bottom': '50px',
                      'margin-left': 'auto', 'margin-right': 'auto', 'float': 'none'},
               className='ten columns')
        ], className='dashrow'),
        html.Div([
            dt.DataTable(
                rows=[{}],
                row_selectable=True,
                filterable=True,
                sortable=True,
                selected_row_indices=[],
                id='Man006BL-table'
            ),
        ], style={'width': '100%', 'margin-left': 'auto', 'margin-right': 'auto'},
            id='Man006BL-table-div'
        ),
        html.Div([
            html.A(
                'Download Data',
                id='Man006BL-download-link',
                download='Man006BL.csv',
                href='',
                target='_blank'
            ),
        ], style={'text-align': 'right', 'margin-right': '5%'}),
    ]
)


@app.callback(Output('Man006BL-count-table', 'rows'),
              [Input('Man006BL-my-date-picker-range', 'start_date'),
               Input('Man006BL-my-date-picker-range', 'end_date'),
               Input('licensetype-dropdown', 'value'),
               Input('jobtype-dropdown', 'value'),
               Input('inspector-dropdown', 'value')])
def updatecount_table(start_date, end_date, license_type_val, job_type_val, inspector_val):
    df_counts = count_jobs(start_date, end_date, license_type_val, job_type_val, inspector_val)
    return df_counts.to_dict('records')

@app.callback(
            Output('Man006BL-count-table-download-link', 'href'),
            [Input('Man006BL-my-date-picker-range', 'start_date'),
             Input('Man006BL-my-date-picker-range', 'end_date'),
             Input('licensetype-dropdown', 'lt_value'),
             Input('jobtype-dropdown', 'jt_value'),
             Input('inspector-dropdown', 'inspector_value')])
def update_count_table_download_link(start_date, end_date, license_type_val, job_type_val, inspector_val):
    df_for_csv = count_jobs(start_date, end_date, license_type_val, job_type_val, inspector_val)
    csv_string = df_for_csv.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string

@app.callback(Output('Man006BL-table', 'rows'),
            [Input('Man006BL-my-date-picker-range', 'start_date'),
             Input('Man006BL-my-date-picker-range', 'end_date'),
             Input('licensetype-dropdown', 'value'),
             Input('jobtype-dropdown', 'value'),
             Input('inspector-dropdown', 'value')])
def update_table(start_date, end_date, license_type_val, job_type_val, inspector_val):
    df_inv = get_data_object(start_date, end_date, license_type_val, job_type_val, inspector_val)
    return df_inv.to_dict('records')

@app.callback(
            Output('Man006BL-download-link', 'href'),
            [Input('Man006BL-my-date-picker-range', 'start_date'),
             Input('Man006BL-my-date-picker-range', 'end_date'),
             Input('licensetype-dropdown', 'value'),
             Input('jobtype-dropdown', 'value'),
             Input('inspector-dropdown', 'value')])
def update_table_download_link(start_date, end_date, license_type_val, job_type_val, inspector_val):
    df_for_csv = get_data_object(start_date, end_date, license_type_val, job_type_val, inspector_val)
    csv_string = df_for_csv.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string