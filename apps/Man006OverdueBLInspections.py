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
    sql="""select biz.Address "Business Address", biz.Location "Location", lic.ExternalFileNum "License Number", lic.LicenseType "LicenseType", (Case when jt.Name like 'j_BL_Inspection' then ins.ExternalFileNum END) "JobNumber", (Case when jt.Name like 'j_BL_Inspection' then 'Inspection on License' when jt.Name like 'j_BL_Application' then 'Inspection on Application' when jt.Name like 'j_BL_AmendRenew' then 'Inspection on Renewal or Amend' END) "InspectionOn", ins.ObjectId "InspObjectId",  extract(month from ins.CreatedDate) || '/'||extract(day from ins.CreatedDate)|| '/'|| extract(year from ins.CreatedDate) CreatedDate, ins.ScheduledInspectionDate "ScheduledInspectionDate" from QUERY.J_BL_INSPECTION ins, QUERY.R_BL_LICENSEINSPECTION li,query.o_bl_license lic,query.o_bl_business biz, query.o_jobtypes jt where ins.ObjectId = li.InspectionId and ins.JobTypeId = jt.JobTypeId and li.LicenseId = lic.ObjectId  and lic.BusinessObjectId = biz.ObjectId and ins.ScheduledInspectionDate <= sysdate and ins.CompletedDate is null union select biz.Address, biz.Location, lic.ExternalFileNum LicenseNumber, lic.LicenseType "LicenseType", (Case when jt.Name like 'j_BL_Inspection' then ins.ExternalFileNum when jt.Name like 'j_BL_Application' then ap.ExternalFileNum END) "JobNumber", (Case when jt.Name like 'j_BL_Inspection' then 'Inspection on License' when jt.Name like 'j_BL_Application' then 'Inspection on Application' when jt.Name like 'j_BL_AmendRenew' then 'Inspection on Renewal or Amend' END) "InspectionOn", ins.ObjectId "InspObjectId", extract(month from ins.CreatedDate) || '/'||extract(day from ins.CreatedDate)|| '/'|| extract(year from ins.CreatedDate) "CreatedDate", ins.ScheduledInspectionDate "ScheduledInspectionDate" from QUERY.J_BL_INSPECTION ins, query.r_bl_applicationinspection api, query.j_bl_application ap, query.o_jobtypes jt, query.r_bl_application_license apl, query.o_bl_license lic, query.o_bl_business biz where ins.ObjectId = api.InspectionId and api.ApplicationId = ap.ObjectId and ap.JobTypeId = jt.JobTypeId and ap.ObjectId = apl.ApplicationObjectId and apl.LicenseObjectId = lic.ObjectId and lic.BusinessObjectId = biz.ObjectId  and ins.ScheduledInspectionDate <= sysdate and ins.CompletedDate is null union select biz.Address "Business Address", biz.Location "Location", lic.ExternalFileNum "License Number", lic.LicenseType "LicenseType", (Case when jt.Name like 'j_BL_Inspection' then ins.ExternalFileNum when jt.Name like 'j_BL_AmendRenew' then ar.ExternalFileNum END) "JobNumber", (Case when jt.Name like 'j_BL_Inspection' then 'Inspection on License' when jt.Name like 'j_BL_Application' then 'Inspection on Application' when jt.Name like 'j_BL_AmendRenew' then 'Inspection on Renewal or Amend' END) "InspectionOn", ins.ObjectId "InspObjectId", extract(month from ins.CreatedDate) || '/'||extract(day from ins.CreatedDate)|| '/'|| extract(year from ins.CreatedDate) "CreatedDate", ins.ScheduledInspectionDate "ScheduledInspectionDate" from QUERY.J_BL_INSPECTION ins, query.r_bl_amendrenewinspection ari, query.j_bl_amendrenew ar, query.o_jobtypes jt, QUERY.R_BL_AMENDRENEW_LICENSE arl, query.o_bl_license lic, query.o_bl_business biz where ins.objectid = ari.InspectionId and ari.AmendRenewId = ar.JobId  and ar.JobTypeId = jt.JobTypeId and ar.ObjectId = arl.AmendRenewId and arl.LicenseId = lic.ObjectId and lic.BusinessObjectId = biz.ObjectId and ins.ScheduledInspectionDate <= sysdate and ins.CompletedDate is null"""
    df = pd.read_sql(sql,con)

def get_data_object(selected_start, selected_end):
    df_selected =df[(df['ScheduledInspectionDate']>=selected_start)&(df['ScheduledInspectionDate']<=selected_end)]
    return df_selected

def count_jobs(selected_start, selected_end):
    df_countselected =df[(df['ScheduledInspectionDate']>=selected_start)&(df['ScheduledInspectionDate']<=selected_end)]
    df_counter = df_countselected.groupby(by=['LicenseType','InspectionOn'], as_index=False).agg({'InspObjectId': pd.Series.nunique})
    df_counter = df_counter.rename(columns={'LicenseType': "License Type",'InspectionOn':'Inspection On', 'InspObjectId': 'Count of Overdue Inspections'})
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