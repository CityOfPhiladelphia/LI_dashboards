import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import plotly.graph_objs as go
import pandas as pd
from dash.dependencies import Input, Output
from datetime import datetime
import urllib.parse

from app import app, con

with con() as con:
    sql="""SELECT biz.address "Business Address", lic.externalfilenum "License Number", lic.licensetype "License Type",( CASE WHEN jt.name LIKE 'j_BL_Inspection' THEN ins.externalfilenum END) "Job Number", jt.Description "Job Type", ( CASE WHEN jt.name LIKE 'j_BL_Inspection' THEN 'Inspection on License' WHEN jt.name LIKE 'j_BL_Application' THEN 'Inspection on Application' WHEN jt.name LIKE 'j_BL_AmendRenew' THEN 'Inspection on Renewal or Amend' END ) "Inspection On", ins.inspectiontype "Inspection Type", ins.objectid "Insp Object Id", Extract(month FROM ins.createddate) || '/' ||Extract(day FROM ins.createddate) || '/' || Extract(year FROM ins.createddate) "Inspection Created Date", ins.scheduledinspectiondate "Scheduled Inspection Date", ins.inspectorname "Inspector Name" FROM query.j_bl_inspection ins, query.r_bl_licenseinspection li, query.o_bl_license lic, query.o_bl_business biz, query.o_jobtypes jt WHERE ins.objectid = li.inspectionid AND ins.jobtypeid = jt.jobtypeid AND li.licenseid = lic.objectid AND lic.businessobjectid = biz.objectid AND ins.scheduledinspectiondate <= SYSDATE AND ins.completeddate IS NULL UNION SELECT biz.address "Business Address", lic.externalfilenum "License Number", lic.licensetype "License Type", ( CASE WHEN jt.name LIKE 'j_BL_Inspection' THEN ins.externalfilenum WHEN jt.name LIKE 'j_BL_Application' THEN ap.externalfilenum END ) "Job Number", jt.Description "Job Type", ( CASE WHEN jt.name LIKE 'j_BL_Inspection' THEN 'Inspection on License' WHEN jt.name LIKE 'j_BL_Application' THEN 'Inspection on Application' WHEN jt.name LIKE 'j_BL_AmendRenew' THEN 'Inspection on Renewal or Amend' END ) "Inspection On", ins.inspectiontype "Inspection Type", ins.objectid "Insp Object Id", Extract(month FROM ins.createddate) || '/' ||Extract(day FROM ins.createddate) || '/' || Extract(year FROM ins.createddate) "Created Date", ins.scheduledinspectiondate "Scheduled Inspection Date", ins.inspectorname "Inspector Name" FROM query.j_bl_inspection ins, query.r_bl_applicationinspection api, query.j_bl_application ap, query.o_jobtypes jt, query.r_bl_application_license apl, query.o_bl_license lic, query.o_bl_business biz WHERE ins.objectid = api.inspectionid AND api.applicationid = ap.objectid AND ap.jobtypeid = jt.jobtypeid AND ap.objectid = apl.applicationobjectid AND apl.licenseobjectid = lic.objectid AND lic.businessobjectid = biz.objectid AND ins.scheduledinspectiondate <= SYSDATE AND ins.completeddate IS NULL UNION SELECT biz.address "Business Address", lic.externalfilenum "License Number", lic.licensetype "License Type", ( CASE WHEN jt.name LIKE 'j_BL_Inspection' THEN ins.externalfilenum WHEN jt.name LIKE 'j_BL_AmendRenew' THEN ar.externalfilenum END ) "Job Number", jt.Description "Job Type", ( CASE WHEN jt.name LIKE 'j_BL_Inspection' THEN 'Inspection on License' WHEN jt.name LIKE 'j_BL_Application' THEN 'Inspection on Application' WHEN jt.name LIKE 'j_BL_AmendRenew' THEN 'Inspection on Renewal or Amend' END ) "Inspection On", ins.inspectiontype "Inspection Type", ins.objectid "Insp Object Id", Extract(month FROM ins.createddate) || '/' ||Extract(day FROM ins.createddate) || '/' || Extract(year FROM ins.createddate) "Created Date", ins.scheduledinspectiondate "Scheduled Inspection Date", ins.inspectorname "Inspector Name" FROM query.j_bl_inspection ins, query.r_bl_amendrenewinspection ari, query.j_bl_amendrenew ar, query.o_jobtypes jt, query.r_bl_amendrenew_license arl, query.o_bl_license lic, query.o_bl_business biz WHERE ins.objectid = ari.inspectionid AND ari.amendrenewid = ar.jobid AND ar.jobtypeid = jt.jobtypeid AND ar.objectid = arl.amendrenewid AND arl.licenseid = lic.objectid AND lic.businessobjectid = biz.objectid AND ins.scheduledinspectiondate <= SYSDATE AND ins.completeddate IS NULL"""
    df = pd.read_sql(sql,con)

def get_data_object(selected_start, selected_end):
    df_selected =df[(df['Scheduled Inspection Date']>=selected_start)&(df['Scheduled Inspection Date']<=selected_end)]
    return df_selected

def count_jobs(selected_start, selected_end):
    df_countselected =df[(df['Scheduled Inspection Date']>=selected_start)&(df['Scheduled Inspection Date']<=selected_end)]
    df_counter = df_countselected.groupby(by=['License Type','Inspection On'], as_index=False).agg({'Insp Object Id': pd.Series.nunique})
    df_counter = df_counter.rename(columns={'License Type': "License Type",'Inspection On': 'Inspection On', 'Insp Object Id': 'Count of Overdue Inspections'})
    return df_counter

#TODO why is this not including high date?

layout = html.Div(children=[
                html.H1(children='Inspections Past their Scheduled Completion Date on Business Licenses and BL Jobs'),
                html.Div(children='Please Select Date Range (Scheduled Inspection Date)'),
                dcc.DatePickerRange(
                id='my-date-picker-range',
                start_date=datetime(2018, 1, 1),
                end_date=datetime.now()
                ),
              dt.DataTable(
                    rows=[{}],
                    row_selectable=True,
                    sortable=True,
                    selected_row_indices=[],
                    id='Man006BL-count-table'),
                html.Div([
                    html.A(
                        'Download Data',
                        id='Man006BL-download-link',
                        download='Man006BL.csv',
                        href='',
                        target='_blank',
                    )
                ], style={'text-align': 'right'}),
                html.Div(children='Table of Overdue Business Licenses'),
                dt.DataTable(
                    rows=[{}],
                    row_selectable=True,
                    filterable=True,
                    sortable=True,
                    selected_row_indices=[],
                    id='Man006BL-table')
                ])
@app.callback(Output('Man006BL-table', 'rows'),
            [Input('my-date-picker-range', 'start_date'),
            Input('my-date-picker-range', 'end_date')])
def update_table(start_date, end_date):
    df_inv = get_data_object(start_date, end_date)
    return df_inv.to_dict('records')

@app.callback(Output('Man006BL-count-table', 'rows'),
            [Input('my-date-picker-range', 'start_date'),
            Input('my-date-picker-range', 'end_date')])
def updatecount_table(start_date, end_date):
    df_counts = count_jobs(start_date, end_date)
    return df_counts.to_dict('records')

@app.callback(
            Output('Man006BL-download-link', 'href'),
            [Input('my-date-picker-range', 'start_date'),
            Input('my-date-picker-range', 'end_date')])
def update_table_download_link(start_date, end_date):
    df = get_data_object(start_date, end_date)
    csv_string = df.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string