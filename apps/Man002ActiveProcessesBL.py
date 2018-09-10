import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import plotly.graph_objs as go
import pandas as pd
from dash.dependencies import Input, Output
import urllib.parse

from app import app, con

testing_mode = False
print("Man002ActiveProcessesBL.py")
print("Testing mode? " + str(testing_mode))

#Definitions: BL Apps and Renewals
#excludes jobs in Statuses More Information Required, Denied, Draft, Withdrawn, Approved
#excludes processes of Pay Fees, Provide More Information for Renewal, Amend License
#No completion date on processes

if testing_mode:
    df_table = pd.read_csv("test_data/Man002ActiveProcessesBLIndividualRecords_test_data.csv")
    df_counts = pd.read_csv("test_data/Man002ActiveProcessesBLCounts_test_data.csv")
else:
    with con() as con:
        sql_tl = """select distinct j.ExternalFileNum "JobNumber", jt.Description "JobType", nvl(lt.Name, lt2.Name) "LicenseType", stat.Description "JobStatus", proc.ProcessId "ProcessID", pt.Description "ProcessType", extract(month from proc.CreatedDate) || '/'||extract(day from proc.CreatedDate)|| '/'|| extract(year from proc.CreatedDate) "CreatedDate", extract(month from proc.ScheduledStartDate) || '/'|| extract(day from proc.ScheduledStartDate)|| '/'||extract(year from proc.ScheduledStartDate) "ScheduledStartDate", proc.ProcessStatus "ProcessStatus",(CASE WHEN round(sysdate - proc.ScheduledStartDate) <= 1 then '0-1 Day' WHEN round(sysdate - proc.ScheduledStartDate) between 2 and 5 then '2-5 Days' WHEN round(sysdate - proc.ScheduledStartDate) between 6 and 10 then '6-10 Days' ELSE '11+ Days' END) "Duration",(CASE when jt.Description like 'Business License Application' then 'https://eclipseprod.phila.gov/phillylmsprod/int/lms/Default.aspx#presentationId=1239699&objectHandle='||j.JobId||'&processHandle=&paneId=1239699_151'when jt.Description like 'Amendment/Renewal' then 'https://eclipseprod.phila.gov/phillylmsprod/int/lms/Default.aspx#presentationId=1243107&objectHandle='||j.JobId||'&processHandle=&paneId=1243107_175' End) "ProcessLink" from api.PROCESSES proc, api.jobs j, api.processtypes pt, api.jobtypes jt, api.statuses stat, query.r_bl_amendrenew_license arl, query.r_bl_license_licensetype lrl, query.o_bl_licensetype lt, query.r_bl_application_license apl, query.r_bl_license_licensetype lrl2, query.o_bl_licensetype lt2 where proc.JobId = j.JobId and proc.ProcessTypeId = pt.ProcessTypeId and proc.DateCompleted is null and j.JobTypeId = jt.JobTypeId and j.StatusId = stat.StatusId and pt.ProcessTypeId not in ('984507','2852606','2853029') and jt.JobTypeId in ('1240320', '1244773') and j.StatusId not in ('1030266','964970','1014809','1036493','1010379') and j.JobId = arl.AmendRenewId (+) and arl.LicenseId = lrl.LicenseId (+) and lrl.LicenseTypeId = lt.ObjectId (+) and j.JobId = apl.ApplicationObjectId (+) and apl.LicenseObjectId = lrl2.LicenseId (+) and lrl2.LicenseTypeId = lt2.ObjectId (+)"""
        sql_counts = """select distinct JobType "JobType", ProcessType "ProcessType", count(distinct ProcessID) "ProcessCounts" from (select distinct j.ExternalFileNum JobExtNum, j.StatusId, jt.Description JobType,  stat.Description JobStatus, pt.ProcessTypeId, proc.ProcessId ProcessID, pt.Description ProcessType, extract(month from proc.CreatedDate) || '/'||extract(day from proc.CreatedDate)|| '/'|| extract(year from proc.CreatedDate) CreatedDate, extract(month from proc.ScheduledStartDate) || '/'|| extract(day from proc.ScheduledStartDate)|| '/'||extract(year from proc.ScheduledStartDate) ScheduledStartDate, (CASE WHEN  proc.DateCompleted is not null THEN extract(month from proc.DateCompleted) || '/'|| extract(day from proc.DateCompleted)|| '/'||extract(year from proc.DateCompleted) else null END) DateCompleted, proc.ProcessStatus,  (CASE WHEN round(sysdate - proc.ScheduledStartDate) <= 1 then '0-1 Day' WHEN round(sysdate - proc.ScheduledStartDate) between 2 and 5 then '2-5 Days' WHEN round(sysdate - proc.ScheduledStartDate) between 6 and 10 then '6-10 Days' ELSE '11+ Days' END) Duration from api.PROCESSES proc, api.jobs j, api.processtypes pt, api.jobtypes jt, api.statuses stat where proc.JobId = j.JobId and proc.ProcessTypeId = pt.ProcessTypeId and proc.DateCompleted is null and j.JobTypeId = jt.JobTypeId and j.StatusId = stat.StatusId and pt.ProcessTypeId not in ('984507','2852606','2853029') and jt.JobTypeId in ('1240320', '1244773') and j.StatusId not in ('1030266','964970','1014809','1036493','1010379')) group by JobType, ProcessType"""
        df_table = pd.read_sql(sql_tl, con)
        df_counts = pd.read_sql(sql_counts, con)

processtype_options = [{'label': 'All', 'value': 'All'}]
for processtype in df_counts['ProcessType'].unique():
    processtype_options.append({'label': str(processtype),'value': processtype})

licensetype_options = [{'label': 'All', 'value': 'All'}]
for licensetype in df_table['LicenseType'].unique():
    if str(licensetype) != "nan":
        licensetype_options.append({'label': str(licensetype), 'value': licensetype})

def get_data_object(process_type, license_type):
    df_selected = df_table
    if process_type != "All":
        df_selected = df_selected[df_selected['ProcessType'] == process_type]
    if license_type != "All":
        df_selected = df_selected[df_selected['LicenseType'] == license_type]
    return df_selected

layout = html.Div([
    html.H1('Business License Active Processes'),
    dcc.Graph(id='my-graph',
    figure=go.Figure(
        data=[
            go.Bar(
                x=df_counts[df_counts['JobType']=='Business License Application']['ProcessType'],
                y=df_counts[df_counts['JobType']=='Business License Application']['ProcessCounts'],
                name='BL Application Jobs Active',
                marker=go.bar.Marker(
                    color='rgb(55, 83, 109)'
                )
            ),
            go.Bar(
                x=df_counts[df_counts['JobType']=='Amendment/Renewal']['ProcessType'],
                y=df_counts[df_counts['JobType']=='Amendment/Renewal']['ProcessCounts'],
                name='BL Renewal/Amendment Jobs Active',
                marker=go.bar.Marker(
                    color='rgb(26, 118, 255)'
                )
            )
        ],
        layout=go.Layout(
            showlegend=True,
            legend=go.layout.Legend(
                x=.75,
                y=1,
            ),
            xaxis=dict(
                    autorange=True,
                    tickangle=30,
                    tickfont=dict(
                        size=11
                )
            ),
            margin=go.layout.Margin(l=40, r=0, t=40, b=100)
        )
    ),
    style={'height': 600, 'diplay':'inline-block'}),
    html.P(id='page-break'),
    html.Div(children='Filter by Process Type'),
    html.Div([
        dcc.Dropdown(id='processtype-dropdown',
                     options=processtype_options,
                     value='All'
        ),
    ], style={'width': '30%', 'display': 'inline-block'}),
    html.Div(children='Filter by LicenseType'),
    html.Div([
        dcc.Dropdown(id='licensetype-dropdown',
                     options=licensetype_options,
                     value='All',
                     ),
    ], style={'width': '40%', 'display': 'inline-block'}),
    html.Div([
        html.A(
            'Download Data',
            id='Man002ActiveProcessesBL-download-link',
            download='Man002ActiveProcessesBL.csv',
            href='',
            target='_blank',
        )
    ], style={'text-align': 'right'}),
    dt.DataTable(
        # Initialise the rows
        rows=[{}],
        row_selectable=True,
        filterable=True,
        sortable=True,
        selected_row_indices=[],
        id='Man002ActiveProcessesBL-table'
    )
])

@app.callback(
    Output('Man002ActiveProcessesBL-table', 'rows'),
    [Input('processtype-dropdown', 'value'),
     Input('licensetype-dropdown', 'value')])
def update_table(process_type, license_type):
    df = get_data_object(process_type, license_type)
    return df.to_dict('records')

@app.callback(
    Output('Man002ActiveProcessesBL-download-link', 'href'),
    [Input('processtype-dropdown', 'value'),
     Input('licensetype-dropdown', 'value')])
def update_download_link(process_type, license_type):
    df = get_data_object(process_type, license_type)
    csv_string = df.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string
