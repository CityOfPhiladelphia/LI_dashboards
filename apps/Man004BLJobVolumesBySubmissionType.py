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
    sql="""select lt.Name "LicenseType", (case when ap.CreatedBy like '%2%' then 'Online' when ap.CreatedBy like '%3%' then 'Online' when ap.CreatedBy like '%4%' then 'Online' when ap.CreatedBy like '%5%' then 'Online' when ap.CreatedBy like '%6%' then 'Online' when ap.CreatedBy like '%7%' then 'Online' when ap.CreatedBy like '%8%' then 'Online' when ap.CreatedBy like '%9%' then 'Online' when ap.CreatedBy = 'PPG User' then 'Online' when ap.CreatedBy = 'POSSE system power user' then 'Revenue' else 'Staff' end) as "CreatedByType", ap.CreatedByUserName "CreatedByUserName", ap.ObjectID "JobObjectID", ap.ExternalFileNum "JobNumber", (CASE WHEN jt.Name like 'j_BL_Application' then 'Application' when jt.Name like 'j_BL_AmendRenew' then 'Renewal or Amendment' END) "JobTypeName", extract(month from ap.CreatedDate) || '/'||extract(day from ap.CreatedDate)|| '/'|| extract(year from ap.CreatedDate) "JobCreatedDate", ap.CreatedDate "JobCreatedDateField",extract(month from ap.CompletedDate) || '/'||extract(day from ap.CompletedDate)|| '/'|| extract(year from ap.CompletedDate) "JobCompletedDate", ap.StatusDescription "StatusDescription" from lmscorral.bl_licensetype lt, lmscorral.bl_license lic, query.r_bl_application_license apl, query.j_bl_application ap, query.o_jobtypes jt where lt.ObjectId = lic.LicenseTypeObjectId (+) and lic.ObjectId = apl.LicenseObjectId (+) and apl.ApplicationObjectId = ap.ObjectId(+) and ap.JobTypeId = jt.JobTypeId (+) and ap.StatusId like '1036493' and ap.ExternalFileNum like 'BA%' union select lt.Name "LicenseType", (case when ar.CreatedBy like '%2%' then 'Online' when ar.CreatedBy like '%3%' then 'Online' when ar.CreatedBy like '%4%' then 'Online' when ar.CreatedBy like '%5%' then 'Online' when ar.CreatedBy like '%6%' then 'Online' when ar.CreatedBy like '%7%' then 'Online' when ar.CreatedBy like '%8%' then 'Online' when ar.CreatedBy like '%9%' then 'Online' when ar.CreatedBy = 'PPG User' then 'Online' when ar.CreatedBy = 'POSSE system power user' then 'Revenue' else 'Staff' end) as "CreatedByType", ar.CreatedByUserName "CreatedByUserName", ar.ObjectID "JobObjectID",  ar.ExternalFileNum "JobNumber", (CASE WHEN jt.Name like 'j_BL_Application' then 'Application' when jt.Name like 'j_BL_AmendRenew' then 'Renewal or Amendment' END) "JobTypeName", extract(month from ar.CreatedDate) || '/'||extract(day from ar.CreatedDate)|| '/'|| extract(year from ar.CreatedDate) "JobCreatedDate", ar.CreatedDate "JobCreatedDateField", extract(month from ar.CompletedDate) || '/'||extract(day from ar.CompletedDate)|| '/'|| extract(year from ar.CompletedDate) "JobCompletedDate", ar.StatusDescription "StatusDescription" from lmscorral.bl_licensetype lt, lmscorral.bl_license lic, query.r_bl_amendrenew_license arl, query.j_bl_amendrenew ar, query.o_jobtypes jt where lt.ObjectId = lic.LicenseTypeObjectId (+) and lic.ObjectId = arl.LicenseId (+) and arl.AmendRenewId = ar.ObjectId (+) and ar.JobTypeId = jt.JobTypeId (+) and ar.StatusId like '1036493' and ar.ExternalFileNum like 'BR%'"""
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
