import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import plotly.graph_objs as go
import pandas as pd
from dash.dependencies import Input, Output
from datetime import datetime
import urllib.parse

from app import app, con

#TODO add in job type

with con() as con:
    sql="""SELECT lt.name "LicenseType",( CASE WHEN ap.createdbyusername LIKE '%2%' THEN 'Online' WHEN ap.createdbyusername LIKE '%3%' THEN 'Online' WHEN ap.createdbyusername LIKE '%4%' THEN 'Online' WHEN ap.createdbyusername LIKE '%5%' THEN 'Online' WHEN ap.createdbyusername LIKE '%6%' THEN 'Online' WHEN ap.createdbyusername LIKE '%7%' THEN 'Online' WHEN ap.createdbyusername LIKE '%8%' THEN 'Online' WHEN ap.createdbyusername LIKE '%9%' THEN 'Online' WHEN ap.createdbyusername = 'PPG User' THEN 'Online' WHEN ap.createdbyusername = 'POSSE system power user' THEN 'Revenue' ELSE 'Staff' END) AS "CreatedByType", ap.createdbyusername "CreatedByUserName", ap.objectid "JobObjectID", ap.externalfilenum "JobNumber", ( CASE WHEN jt.name LIKE 'j_BL_Application' THEN 'Application' WHEN jt.name LIKE 'j_BL_AmendRenew' THEN 'Renewal or Amendment' END ) "JobTypeName", Extract(month FROM ap.createddate) || '/' ||Extract(day FROM ap.createddate) || '/' || Extract(year FROM ap.createddate) "JobCreatedDate", ap.createddate "JobCreatedDateField", Extract(month FROM ap.completeddate) || '/' ||Extract(day FROM ap.completeddate) || '/' || Extract(year FROM ap.completeddate) "JobCompletedDate", ap.statusdescription "StatusDescription" FROM lmscorral.bl_licensetype lt, lmscorral.bl_license lic, query.r_bl_application_license apl, query.j_bl_application ap, query.o_jobtypes jt WHERE lt.objectid = lic.licensetypeobjectid (+) AND lic.objectid = apl.licenseobjectid (+) AND apl.applicationobjectid = ap.objectid(+) AND ap.jobtypeid = jt.jobtypeid (+) AND ap.statusid LIKE '1036493' AND ap.externalfilenum LIKE 'BA%' UNION SELECT lt.name "LicenseType", ( CASE WHEN ar.createdbyusername LIKE '%2%' THEN 'Online' WHEN ar.createdbyusername LIKE '%3%' THEN 'Online' WHEN ar.createdbyusername LIKE '%4%' THEN 'Online' WHEN ar.createdbyusername LIKE '%5%' THEN 'Online' WHEN ar.createdbyusername LIKE '%6%' THEN 'Online' WHEN ar.createdbyusername LIKE '%7%' THEN 'Online' WHEN ar.createdbyusername LIKE '%8%' THEN 'Online' WHEN ar.createdbyusername LIKE '%9%' THEN 'Online' WHEN ar.createdbyusername = 'PPG User' THEN 'Online' WHEN ar.createdbyusername = 'POSSE system power user' THEN 'Revenue' ELSE 'Staff' END ) AS "CreatedByType", ar.createdbyusername "CreatedByUserName", ar.objectid "JobObjectID", ar.externalfilenum "JobNumber", ( CASE WHEN jt.name LIKE 'j_BL_Application' THEN 'Application' WHEN jt.name LIKE 'j_BL_AmendRenew' THEN 'Renewal or Amendment' END ) "JobTypeName", Extract(month FROM ar.createddate) || '/' ||Extract(day FROM ar.createddate) || '/' || Extract(year FROM ar.createddate) "JobCreatedDate", ar.createddate "JobCreatedDateField", Extract(month FROM ar.completeddate) || '/' ||Extract(day FROM ar.completeddate) || '/' || Extract(year FROM ar.completeddate) "JobCompletedDate", ar.statusdescription "StatusDescription" FROM lmscorral.bl_licensetype lt, lmscorral.bl_license lic, query.r_bl_amendrenew_license arl, query.j_bl_amendrenew ar, query.o_jobtypes jt WHERE lt.objectid = lic.licensetypeobjectid (+) AND lic.objectid = arl.licenseid (+) AND arl.amendrenewid = ar.objectid (+) AND ar.jobtypeid = jt.jobtypeid (+) AND ar.statusid LIKE '1036493' AND ar.externalfilenum LIKE 'BR%'"""
    df = pd.read_sql(sql,con)

def get_data_object(selected_start, selected_end):
    df_selected = df[(df['JobCreatedDateField']>=selected_start)&(df['JobCreatedDateField']<=selected_end)]
    return df_selected

def count_jobs(selected_start, selected_end):
    df_countselected =df[(df['JobCreatedDateField']>=selected_start)&(df['JobCreatedDateField']<=selected_end)]
    df_counter = df_countselected.groupby(by=['CreatedByType','JobTypeName'], as_index=False).agg({'JobObjectID': pd.Series.nunique})
    df_counter = df_counter.rename(columns={'CreatedByType': "Job Submission Type", 'JobTypeName':'Job Type','JobObjectID': 'Count of Jobs Submitted'})
    return df_counter

#TODO why is this not including high date?

layout = html.Div(children=[
                html.H1(children='Business Application and Renewal Volumes by Submission Method'),
                html.Div(children='Please Select Date Range (Job Created Date)'),
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
                    id='Man004BL-counttable'),
            html.Div([
                html.A(
                    'Download Data',
                    id='Man004BL-download-link',
                    download='Man004BL.csv',
                    href='',
                    target='_blank',
                )
            ], style={'text-align': 'right'}),
            html.Div(children='Table of Approved Jobs'),
                dt.DataTable(
                    rows=[{}],
                    row_selectable=True,
                    filterable=True,
                    sortable=True,
                    selected_row_indices=[],
                    id='Man004BL-table')
                ])

@app.callback(Output('Man004BL-table', 'rows'),
            [Input('my-date-picker-range', 'start_date'),
            Input('my-date-picker-range', 'end_date')])
def update_table(start_date, end_date):
    df_inv = get_data_object(start_date, end_date)
    return df_inv.to_dict('records')

@app.callback(Output('Man004BL-counttable', 'rows'),
            [Input('my-date-picker-range', 'start_date'),
            Input('my-date-picker-range', 'end_date')])
def updatecount_table(start_date, end_date):
    df_counts = count_jobs(start_date, end_date)
    return df_counts.to_dict('records')

@app.callback(
    Output('Man004BL-download-link', 'href'),
    [Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')])
def update_download_link(start_date, end_date):
    df = get_data_object(start_date, end_date)
    csv_string = df.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string
