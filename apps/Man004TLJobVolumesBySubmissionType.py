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
print("Man004TLJobVolumesBySubmissionType.py")
print("Testing mode? " + str(testing_mode))

if testing_mode:
    df_table = pd.read_csv("man004TL_test_data.csv")
else:
    with con() as con:
        sql = """select lt.LicenseCodeDescription "LicenseType", (case when ap.CreatedByUserName like '%2%' then 'Online' when ap.CreatedByUserName like '%3%' then 'Online' when ap.CreatedByUserName like '%4%' then 'Online' when ap.CreatedByUserName like '%5%' then 'Online' when ap.CreatedByUserName like '%6%' then 'Online' when ap.CreatedByUserName like '%7%' then 'Online' when ap.CreatedByUserName like '%8%' then 'Online' when ap.CreatedByUserName like '%9%' then 'Online' when ap.CreatedBy = 'PPG User' then 'Online' when ap.CreatedBy = 'POSSE system power user' then 'Revenue' else 'Staff' end) as "CreatedByType", ap.CreatedByUserName "CreatedByUserName", ap.ObjectID "JobObjectID", ap.ExternalFileNum "JobNumber", (CASE WHEN jt.Name like 'j_TL_Application' then 'Application' when jt.Name like 'j_TL_AmendRenew' then 'Renewal or Amendment' END) "JobTypeName", extract(month from ap.CreatedDate) || '/'||extract(day from ap.CreatedDate)|| '/'|| extract(year from ap.CreatedDate) "JobCreatedDate", ap.CreatedDate "JobCreatedDateField",extract(month from ap.CompletedDate) || '/'||extract(day from ap.CompletedDate)|| '/'|| extract(year from ap.CompletedDate) "JobCompletedDate", ap.StatusDescription "StatusDescription" from lmscorral.tl_tradelicensetypes lt, lmscorral.tl_tradelicenses lic, query.j_tl_application ap, query.o_jobtypes jt where lt.LicenseCode = lic.LicenseCode (+) and lic.ObjectId =  ap.TradeLicenseObjectId (+) and ap.JobTypeId = jt.JobTypeId (+) and ap.StatusId like '1036493' and ap.ExternalFileNum like 'TL%' union select lt.LicenseCodeDescription "LicenseType", (case when ar.CreatedByUserName like '%2%' then 'Online' when ar.CreatedByUserName like '%3%' then 'Online' when ar.CreatedByUserName like '%4%' then 'Online' when ar.CreatedByUserName like '%5%' then 'Online' when ar.CreatedByUserName like '%6%' then 'Online' when ar.CreatedByUserName like '%7%' then 'Online' when ar.CreatedByUserName like '%8%' then 'Online' when ar.CreatedByUserName like '%9%' then 'Online' when ar.CreatedBy = 'PPG User' then 'Online' when ar.CreatedBy = 'POSSE system power user' then 'Revenue' else 'Staff' end) as "CreatedByType", ar.CreatedByUserName "CreatedByUserName", ar.ObjectId "JobObjectID",  ar.ExternalFileNum "JobNumber", (CASE WHEN jt.Name like 'j_TL_Application' then 'Application' when jt.Name like 'j_TL_AmendRenew' then 'Renewal or Amendment' END) "JobTypeName", extract(month from ar.CreatedDate) || '/'||extract(day from ar.CreatedDate)|| '/'|| extract(year from ar.CreatedDate) "JobCreatedDate", ar.CreatedDate "JobCreatedDateField", extract(month from ar.CompletedDate) || '/'||extract(day from ar.CompletedDate)|| '/'|| extract(year from ar.CompletedDate) "JobCompletedDate", ar.StatusDescription "StatusDescription" from lmscorral.tl_tradelicensetypes lt, lmscorral.tl_tradelicenses lic, query.r_tl_amendrenew_license arl, query.j_tl_amendrenew ar, query.o_jobtypes jt where lt.LicenseCode = lic.LicenseCode (+) and lic.ObjectId = arl.LicenseId (+) and arl.AmendRenewId = ar.ObjectId (+) and ar.JobTypeId = jt.JobTypeId (+) and ar.StatusId like '1036493' and ar.ExternalFileNum like 'TR%'"""
        df_table = pd.read_sql(sql,con)

username_options_unsorted = []
df_staff = df_table[df_table['CreatedByType'] == 'Staff']
for username in df_staff['CreatedByUserName'].unique():
    username_options_unsorted.append({'label': str(username), 'value': username})
username_options_sorted = sorted(username_options_unsorted, key=lambda k: k['label'])

def get_data_object(selected_start, selected_end, username):
    df_table['JobCreatedDateField'] = pd.to_datetime(df_table['JobCreatedDateField'])
    df_selected = df_table[(df_table['JobCreatedDateField']>=selected_start)&(df_table['JobCreatedDateField']<=selected_end)]
    if username is not None:
        if isinstance(username, str):
            df_selected = df_selected[df_selected['CreatedByUserName'] == username]
        elif isinstance(username, list):
            if len(username) > 0:
                df_selected = df_selected[df_selected['CreatedByUserName'].isin(username)]
    return df_selected

def count_jobs(selected_start, selected_end):
    df_countselected =df_table[(df_table['JobCreatedDateField']>=selected_start)&(df_table['JobCreatedDateField']<=selected_end)]
    df_counter = df_countselected.groupby(by=['CreatedByType','JobTypeName'], as_index=False).agg({'JobObjectID': pd.Series.nunique})
    df_counter = df_counter.rename(columns={'CreatedByType': "Job Submission Type",'JobTypeName':'Job Type', 'JobObjectID': 'Count of Jobs Submitted'})
    return df_counter

#TODO why is this not including high date?

layout = html.Div(children=[
                html.H1(children='Trade Application and Renewal Volumes by Submission Method'),
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
                    id='Man004TL-counttable'),
            html.Div([
                html.A(
                    'Download Data',
                    id='Man004TL-download-link',
                    download='Man004TL.csv',
                    href='',
                    target='_blank',
                )
            ], style={'text-align': 'right'}),
            html.P(id='page-break'),
            html.Div(children='Filter by Username (Staff only)'),
            html.Div([
                dcc.Dropdown(id='username-dropdown',
                             options=username_options_sorted,
                             multi=True
                             ),
            ], style={'width': '30%', 'display': 'inline-block'}),
            dt.DataTable(
                rows=[{}],
                row_selectable=True,
                filterable=True,
                sortable=True,
                selected_row_indices=[],
                id='Man004TL-table')
        ])
@app.callback(Output('Man004TL-table', 'rows'),
            [Input('my-date-picker-range', 'start_date'),
             Input('my-date-picker-range', 'end_date'),
             Input('username-dropdown', 'value')])
def update_table(start_date, end_date, username_val):
    df_inv = get_data_object(start_date, end_date, username_val)
    return df_inv.to_dict('records')

@app.callback(Output('Man004TL-counttable', 'rows'),
            [Input('my-date-picker-range', 'start_date'),
            Input('my-date-picker-range', 'end_date')])
def updatecount_table(start_date, end_date):
    df_counts = count_jobs(start_date, end_date)
    return df_counts.to_dict('records')

@app.callback(
    Output('Man004TL-download-link', 'href'),
    [Input('my-date-picker-range', 'start_date'),
     Input('my-date-picker-range', 'end_date'),
     Input('username-dropdown', 'value')])
def update_download_link(start_date, end_date, username_val):
    df = get_data_object(start_date, end_date, username_val)
    csv_string = df.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string