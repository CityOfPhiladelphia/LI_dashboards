import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import plotly.graph_objs as go
import pandas as pd
from dash.dependencies import Input, Output
import urllib.parse

from app import app, con

testing_mode = False
print("Man001ActiveJobsBL.py")
print("Testing mode? " + str(testing_mode))

#Definitions: Job Type BL Application and BL Amendment/Renewal
#Completeness Check Completed, Job incomplete
#Not in Status: More Information Required, Payment Pending, Application Incomplete, Draft
#time calculated as time between completion of completeness check to today

if testing_mode:
    df_table = pd.read_csv("test_data/Man001ActiveJobsBLIndividualRecords_test_data.csv")
    df_counts = pd.read_csv("test_data/Man001ActiveJobsBLCounts_test_data.csv")
else:
    with con() as con:
        sql_bl = """SELECT DISTINCT j.externalfilenum "JobNumber", jt.description "JobType", Nvl(ap.licensetypesdisplayformat, ar.licensetypesdisplayformat) "LicenseType", stat.description "JobStatus", proc.processid "ProcessID", pt.description "ProcessType", Extract(month FROM proc.datecompleted) || '/' ||Extract(day FROM proc.datecompleted) || '/' || Extract(year FROM proc.datecompleted) "JobAcceptedDate", proc.processstatus, proc.assignedstaff,( CASE WHEN Round(SYSDATE - proc.scheduledstartdate) <= 1 THEN '0-1 Day' WHEN Round(SYSDATE - proc.scheduledstartdate) BETWEEN 2 AND 5 THEN '2-5 Days' WHEN Round(SYSDATE - proc.scheduledstartdate) BETWEEN 6 AND 10 THEN '6-10 Days' WHEN Round(SYSDATE - proc.scheduledstartdate) BETWEEN 11 AND 365 THEN '11 Days-1 Year' ELSE 'Over 1 Year' END) "Duration", ( CASE WHEN jt.description LIKE 'Business License Application' THEN 'https://eclipseprod.phila.gov/phillylmsprod/int/lms/Default.aspx#presentationId=1239699&objectHandle=' ||j.jobid ||'&processHandle=&paneId=1239699_151' WHEN jt.description LIKE 'Amendment/Renewal' THEN 'https://eclipseprod.phila.gov/phillylmsprod/int/lms/Default.aspx#presentationId=1243107&objectHandle=' ||j.jobid ||'&processHandle=&paneId=1243107_175' END ) "JobLink" FROM api.jobs j, api.jobtypes jt, api.statuses stat, api.processes proc, api.processtypes pt, query.j_bl_amendrenew ar, query.j_bl_application ap WHERE j.jobid = proc.jobid AND proc.processtypeid = pt.processtypeid AND j.jobid = ar.jobid (+) AND j.jobid = ap.jobid AND pt.processtypeid LIKE '1239327' AND proc.datecompleted IS NOT NULL AND j.jobtypeid = jt.jobtypeid AND j.statusid = stat.statusid AND j.completeddate IS NULL AND j.jobtypeid IN ( '1240320', '1244773' ) AND j.statusid NOT IN ( '1014809', '978845', '964970', '967394' ) ORDER BY j.externalfilenum"""
        sql_counts = """select distinct Duration "Duration", JobType "JobType", count(distinct JobNumber) "JobCounts", avg(Time) AvgTime from (select distinct j.ExternalFileNum JobNumber, jt.Description JobType, nvl(ap.LicenseTypesDisplayFormat, ar.LicenseTypesDisplayFormat) LicenseType, j.StatusId, j.JobStatus, stat.Description "JobStatus", pt.ProcessTypeId, pt.Description,extract(month from proc.DateCompleted) || '/'||extract(day from proc.DateCompleted)|| '/'|| extract(year from proc.DateCompleted) "JobAcceptedDate", proc.ProcessStatus,  proc.AssignedStaff,(CASE WHEN round(sysdate - proc.ScheduledStartDate) <= 1 then '0-1 Day' WHEN round(sysdate - proc.ScheduledStartDate) between 2 and 5 then '2-5 Days'WHEN round(sysdate - proc.ScheduledStartDate) between 6 and 10 then '6-10 Days' WHEN round(sysdate - proc.ScheduledStartDate) between 11 and 365 then '11 Days-1 Year' ELSE 'Over 1 Year' END) Duration, j.JobId, (sysdate - proc.ScheduledStartDate) Time from api.jobs j, api.jobtypes jt, api.statuses stat, api.processes proc, api.processtypes pt, query.j_bl_amendrenew ar, query.j_bl_application ap where j.JobId = proc.JobId and proc.ProcessTypeId = pt.ProcessTypeId and j.JobId = ar.JobId (+) and j.JobId = ap.JobId and pt.ProcessTypeId like '1239327' and proc.DateCompleted is not null and j.JobTypeId = jt.JobTypeId  and j.StatusId = stat.StatusId and j.CompletedDate is null and j.JobTypeId in ('1240320','1244773') and j.StatusId not in ('1014809', '978845', '964970','967394')) group by Duration, JobType order by AvgTime desc"""
        df_table = pd.read_sql(sql_bl, con)
        df_counts = pd.read_sql(sql_counts, con)

duration_options = [{'label': 'All', 'value': 'All'}]
for duration in df_counts['Duration'].unique():
    duration_options.append({'label': str(duration), 'value': duration})

licensetype_options_unsorted = [{'label': 'All', 'value': 'All'}]
for licensetype in df_table['LicenseType'].unique():
    if str(licensetype) != "nan":
        licensetype_options_unsorted.append({'label': str(licensetype), 'value': licensetype})
licensetype_options_sorted = sorted(licensetype_options_unsorted, key=lambda k: k['label'])

def get_data_object(duration, license_type):
    df_selected = df_table
    if duration != "All":
        df_selected = df_selected[df_selected['Duration'] == duration]
    if license_type != "All":
        df_selected = df_selected[df_selected['LicenseType'] == license_type]
    return df_selected

layout = html.Div(children=[
    html.H1('Business License Active Jobs With Completed Completeness Checks'),
    dcc.Graph(id='my-graph',
    figure=go.Figure(
        data=[
            go.Bar(
                x=df_counts[df_counts['JobType'] == 'Business License Application']['Duration'],
                y=df_counts[df_counts['JobType'] == 'Business License Application']['JobCounts'],
                name='BL Application Jobs Active',
                marker=go.bar.Marker(
                    color='rgb(55, 83, 109)'
                )
            ),
            go.Bar(
                x=df_counts[df_counts['JobType'] == 'Amendment/Renewal']['Duration'],
                y=df_counts[df_counts['JobType'] == 'Amendment/Renewal']['JobCounts'],
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
                y=1
            ),
            margin=go.layout.Margin(l=40, r=0, t=40, b=30)
        )
    ), style={'height': 500, 'display': 'block', 'margin-bottom': '25px'}),
    html.Div(children='Filter by Duration'),
    html.Div([
        dcc.Dropdown(id='duration-dropdown',
                    options=duration_options,
                    value='All',
                    searchable=True
                    ),
    ], style={'width': '30%', 'display': 'inline-block'}),
    html.Div(children='Filter by License Type'),
    html.Div([
        dcc.Dropdown(id='licensetype-dropdown',
                     options=licensetype_options_sorted,
                     value='All',
                     searchable=True
                     ),
    ], style={'width': '40%', 'display': 'inline-block'}),
    html.Div([
        html.A(
            'Download Data',
            id='Man001ActiveJobsBL-download-link',
            download='Man001ActiveJobsBL.csv',
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
        id='Man001ActiveJobsBL-table'
    )
])

@app.callback(
    Output('Man001ActiveJobsBL-table', 'rows'), 
    [Input('duration-dropdown', 'value'),
     Input('licensetype-dropdown', 'value')])
def update_table(duration, license_type):
    df = get_data_object(duration, license_type)
    return df.to_dict('records')

@app.callback(
    Output('Man001ActiveJobsBL-download-link', 'href'),
    [Input('duration-dropdown', 'value'),
     Input('licensetype-dropdown', 'value')])
def update_download_link(duration, license_type):
    df = get_data_object(duration, license_type)
    csv_string = df.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string