#Author: Shannon Holm
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import plotly.graph_objs as go
import pandas as pd
from dash.dependencies import Input, Output
import urllib.parse

from app import app, con


#Definitions: TL Apps and Renewals
#excludes jobs in Statuses More Information Required, Denied, Draft, Withdrawn, Approved
#excludes processes of Pay Fees, Provide More Information for Renewal, Amend License
#No completion date on processes
with con() as con:
    sql_tl = """SELECT DISTINCT j.externalfilenum "JobNumber", jt.description "JobType", Nvl(lt.description, lt2.description) "LicenseType", stat.description "JobStatus", proc.processid "ProcessID", pt.description "ProcessType", Extract(month FROM proc.createddate) || '/' ||Extract(day FROM proc.createddate) || '/' || Extract(year FROM proc.createddate) CreatedDate, Extract(month FROM proc.scheduledstartdate) || '/' || Extract(day FROM proc.scheduledstartdate) || '/' ||Extract(year FROM proc.scheduledstartdate) "ScheduledStartDate", proc.processstatus "ProcessStatus",( CASE WHEN Round(SYSDATE - proc.scheduledstartdate) <= 1 THEN '0-1 Day' WHEN Round(SYSDATE - proc.scheduledstartdate) BETWEEN 2 AND 5 THEN '2-5 Days' WHEN Round(SYSDATE - proc.scheduledstartdate) BETWEEN 6 AND 10 THEN '6-10 Days' ELSE '11+ Days' END) "Duration", ( CASE WHEN jt.description LIKE 'Trade License Application' THEN 'https://eclipseprod.phila.gov/phillylmsprod/int/lms/Default.aspx#presentationId=2854033&objectHandle=' ||j.jobid ||'&processHandle=&paneId=2854033_116' WHEN jt.description LIKE 'Trade License Amend/Renew' THEN 'https://eclipseprod.phila.gov/phillylmsprod/int/lms/Default.aspx#presentationId=2857688&objectHandle=' ||j.jobid ||'&processHandle=&paneId=2857688_87' END ) "ProcessLink" FROM api.processes proc, api.jobs j, api.processtypes pt, api.jobtypes jt, api.statuses stat, query.r_tl_amendrenew_license arl, query.o_tl_license lic, query.o_tl_licensetype lt, query.r_tllicenselicense apl, query.o_tl_license lic2, query.o_tl_licensetype lt2 WHERE proc.jobid = j.jobid AND proc.processtypeid = pt.processtypeid AND proc.datecompleted IS NULL AND j.jobtypeid = jt.jobtypeid AND j.statusid = stat.statusid AND pt.processtypeid NOT IN ( '984507', '2852606', '2853029' ) AND jt.jobtypeid IN ( '2853921', '2857525' ) AND j.statusid NOT IN ( '1030266', '964970', '1014809', '1036493', '1010379' ) AND j.jobid = arl.amendrenewid (+) AND arl.licenseid = lic.objectid (+) AND lic.revenuecode = lt.revenuecode (+) AND j.jobid = apl.tlapp (+) AND apl.license = lic2.objectid (+) AND lic2.revenuecode = lt2.revenuecode (+)"""
    sql_counts = """select distinct JobType "JobType", ProcessType "ProcessType", count(distinct ProcessID) "ProcessCounts" from (select distinct j.ExternalFileNum JobExtNum, j.StatusId, jt.Description JobType,  stat.Description JobStatus, pt.ProcessTypeId, proc.ProcessId ProcessID, pt.Description ProcessType, extract(month from proc.CreatedDate) || '/'||extract(day from proc.CreatedDate)|| '/'|| extract(year from proc.CreatedDate) CreatedDate, extract(month from proc.ScheduledStartDate) || '/'|| extract(day from proc.ScheduledStartDate)|| '/'||extract(year from proc.ScheduledStartDate) ScheduledStartDate, (CASE WHEN  proc.DateCompleted is not null THEN extract(month from proc.DateCompleted) || '/'|| extract(day from proc.DateCompleted)|| '/'||extract(year from proc.DateCompleted) else null END) DateCompleted, proc.ProcessStatus,  (CASE WHEN round(sysdate - proc.ScheduledStartDate) <= 1 then '0-1 Day' WHEN round(sysdate - proc.ScheduledStartDate) between 2 and 5 then '2-5 Days' WHEN round(sysdate - proc.ScheduledStartDate) between 6 and 10 then '6-10 Days' ELSE '11+ Days' END) Duration from api.PROCESSES proc, api.jobs j, api.processtypes pt, api.jobtypes jt, api.statuses stat where proc.JobId = j.JobId and proc.ProcessTypeId = pt.ProcessTypeId and proc.DateCompleted is null and j.JobTypeId = jt.JobTypeId and j.StatusId = stat.StatusId and pt.ProcessTypeId not in ('984507','2852606','2853029') and jt.JobTypeId in ('2853921', '2857525') and j.StatusId not in ('1030266','964970','1014809','1036493','1010379'))group by JobType, ProcessType"""
    df_table = pd.read_sql(sql_tl, con)
    df_counts = pd.read_sql(sql_counts, con)

processtype_options_unsorted = [{'label': 'All', 'value': 'All'}]
for processtype in df_counts['ProcessType'].unique():
    processtype_options_unsorted.append({'label': str(processtype),'value': processtype})
processtype_options_sorted = sorted(processtype_options_unsorted, key=lambda k: k['label'])

licensetype_options_unsorted = [{'label': 'All', 'value': 'All'}]
for licensetype in df_table['LicenseType'].unique():
    if str(licensetype) != "nan":
        licensetype_options_unsorted.append({'label': str(licensetype), 'value': licensetype})
licensetype_options_sorted = sorted(licensetype_options_unsorted, key=lambda k: k['label'])

def get_data_object(process_type, license_type):
    df_selected = df_table
    if process_type != "All":
        df_selected = df_selected[df_selected['ProcessType'] == process_type]
    if license_type != "All":
        df_selected = df_selected[df_selected['LicenseType'] == license_type]
    return df_selected

layout = html.Div([
    html.H1('Trade License Active Processes'),
    dcc.Graph(id='my-graph',
        figure=go.Figure(
            data=[
                go.Bar(
                    x=df_counts[df_counts['JobType']=='Trade License Application']['ProcessType'],
                    y=df_counts[df_counts['JobType']=='Trade License Application']['ProcessCounts'],
                    name='TL Application Jobs Active',
                    marker=go.bar.Marker(
                        color='rgb(55, 83, 109)'
                    )
                ),
                go.Bar(
                    x=df_counts[df_counts['JobType']=='Trade License Amend/Renew']['ProcessType'],
                    y=df_counts[df_counts['JobType']=='Trade License Amend/Renew']['ProcessCounts'],
                    name='TL Renewal/Amendment Jobs Active',
                    marker=go.bar.Marker(
                        color='rgb(26, 118, 255)'
                    )
                )
            ],
            layout=go.Layout(
                showlegend=True,
                legend=go.layout.Legend(
                    x=.75,
                    y=1
                ),
                xaxis=dict(
                    autorange=True,
                    tickangle=0,
                    tickfont=dict(
                        size=11
                    )
                ),
                margin=go.layout.Margin(l=40, r=0, t=40, b=30)
            )
        ),
        style={'height': 500, 'diplay':'inline-block'}
    ),
    html.Div(children='Filter by Process Type'),
    html.Div([
        dcc.Dropdown(id='processtype-dropdown',
                     options=processtype_options_sorted,
                     value='All'
        ),
    ], style={'width': '30%', 'display': 'inline-block'}),
    html.Div(children='Filter by License Type'),
    html.Div([
        dcc.Dropdown(id='licensetype-dropdown',
                     options=licensetype_options_sorted,
                     value='All',
                     ),
    ], style={'width': '40%', 'display': 'inline-block'}),
    html.Div([
        html.A(
            'Download Data',
            id='Man002ActiveProcessesTL-download-link',
            download='Man002ActiveProcessesTL.csv',
            href='',
            target='_blank',
        )
    ], style={'text-align': 'right'}),
    dt.DataTable(
        rows=[{}],
        row_selectable=True,
        filterable=True,
        sortable=True,
        id='Man002ActiveProcessesTL-table'
    )
    ]
)

@app.callback(
    Output('Man002ActiveProcessesTL-table', 'rows'), 
    [Input('processtype-dropdown', 'value'),
     Input('licensetype-dropdown', 'value')])
def update_table(process_type, license_type):
    df = get_data_object(process_type, license_type)
    return df.to_dict('records')

@app.callback(
    Output('Man002ActiveProcessesTL-download-link', 'href'),
    [Input('processtype-dropdown', 'value'),
     Input('licensetype-dropdown', 'value')])
def update_download_link(process_type, license_type):
    df = get_data_object(process_type, license_type)
    csv_string = df.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string
