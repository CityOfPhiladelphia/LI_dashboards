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
        sql_bl = """select distinct j.ExternalFileNum "JobNumber", jt.Description "JobType", nvl(lt.Name, lt2.Name) "LicenseType", stat.Description "JobStatus", proc.ProcessId "ProcessID", pt.Description "ProcessType", extract(month from proc.DateCompleted) || '/'||extract(day from proc.DateCompleted)|| '/'|| extract(year from proc.DateCompleted) "JobAcceptedDate", proc.ProcessStatus,  proc.AssignedStaff,(CASE WHEN round(sysdate - proc.ScheduledStartDate) <= 1 then '0-1 Day' WHEN round(sysdate - proc.ScheduledStartDate) between 2 and 5 then '2-5 Days' WHEN round(sysdate - proc.ScheduledStartDate) between 6 and 10 then '6-10 Days' WHEN round(sysdate - proc.ScheduledStartDate) between 11 and 365 then '11 Days-1 Year' ELSE 'Over 1 Year' END) "Duration", (CASE when jt.Description like 'Business License Application' then
        'https://eclipseprod.phila.gov/phillylmsprod/int/lms/Default.aspx#presentationId=1239699&objectHandle='||j.JobId||'&processHandle=&paneId=1239699_151' when jt.Description like 'Amendment/Renewal' then 'https://eclipseprod.phila.gov/phillylmsprod/int/lms/Default.aspx#presentationId=1243107&objectHandle='||j.JobId||'&processHandle=&paneId=1243107_175'End) "JobLink" from api.jobs j, api.jobtypes jt, api.statuses stat, api.processes proc, api.processtypes pt, query.r_bl_amendrenew_license arl, query.r_bl_license_licensetype lrl, query.o_bl_licensetype lt, query.r_bl_application_license apl, query.r_bl_license_licensetype lrl2, query.o_bl_licensetype lt2 where j.JobId = proc.JobId and proc.ProcessTypeId = pt.ProcessTypeId and j.JobId = arl.AmendRenewId (+) and arl.LicenseId = lrl.LicenseId (+) and lrl.LicenseTypeId = lt.ObjectId (+) and j.JobId = apl.ApplicationObjectId (+) and apl.LicenseObjectId = lrl2.LicenseId (+) and lrl2.LicenseTypeId = lt2.ObjectId (+)and pt.ProcessTypeId like '1239327' and proc.DateCompleted is not null and j.JobTypeId = jt.JobTypeId and j.StatusId = stat.StatusId and j.CompletedDate is null and j.JobTypeId in ('1240320','1244773') and j.StatusId not in ('1014809', '978845','964970','967394') order by j.ExternalFileNum
        """
        sql_counts = """SELECT DISTINCT duration "Duration", jobtype "JobType", licensetype "LicenseType", Count(DISTINCT jobnumber) "JobCounts", Avg(TIME) AvgTime FROM(SELECT DISTINCT j.externalfilenum JobNumber, jt.description JobType, Nvl(lt.name, lt2.name) LicenseType, j.statusid, j.jobstatus, stat.description "JobStatus", pt.processtypeid, pt.description, Extract(month FROM proc.datecompleted) || '/' ||Extract(day FROM proc.datecompleted) || '/' || Extract(year FROM proc.datecompleted) "JobAcceptedDate", proc.processstatus, proc.assignedstaff, ( CASE WHEN Round(SYSDATE - proc.scheduledstartdate) <= 1 THEN '0-1 Day' WHEN Round(SYSDATE - proc.scheduledstartdate) BETWEEN 2 AND 5 THEN '2-5 Days' WHEN Round(SYSDATE - proc.scheduledstartdate) BETWEEN 6 AND 10 THEN '6-10 Days' WHEN Round(SYSDATE - proc.scheduledstartdate) BETWEEN 11 AND 365 THEN '11 Days-1 Year' ELSE 'Over 1 Year' END) Duration, j.jobid, ( SYSDATE - proc.scheduledstartdate ) TIME FROM api.jobs j, api.jobtypes jt, api.statuses stat, api.processes proc, api.processtypes pt, query.r_bl_amendrenew_license arl, query.r_bl_license_licensetype lrl, query.o_bl_licensetype lt, query.r_bl_application_license apl, query.r_bl_license_licensetype lrl2, query.o_bl_licensetype lt2 WHERE j.jobid = proc.jobid AND proc.processtypeid = pt.processtypeid AND j.jobid = arl.amendrenewid (+) AND arl.licenseid = lrl.licenseid (+) AND lrl.licensetypeid = lt.objectid (+) AND j.jobid = apl.applicationobjectid (+) AND apl.licenseobjectid = lrl2.licenseid (+) AND lrl2.licensetypeid = lt2.objectid (+) AND pt.processtypeid LIKE '1239327' AND proc.datecompleted IS NOT NULL AND j.jobtypeid = jt.jobtypeid AND j.statusid = stat.statusid AND j.completeddate IS NULL AND j.jobtypeid IN ( '1240320', '1244773' ) AND j.statusid NOT IN ( '1014809', '978845', '964970', '967394' ) ) GROUP BY duration, jobtype, licensetype ORDER BY avgtime DESC"""
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

def update_counts_graph_data(license_type):
    df_counts_selected = df_counts
    if license_type != "All":
        df_counts_selected = df_counts_selected[df_counts_selected['LicenseType'] == license_type]
    return df_counts_selected

layout = html.Div(
    children=[
        html.A('Test', href='#page-2'),
        html.H1('Business License Active Jobs With Completed Completeness Checks'),
        html.Div('Filter by License Type', style={'margin-bottom': '25px'}),
        html.Div([
            dcc.Dropdown(
                id='Man001ActiveJobsBL-licensetype-dropdown',
                options=licensetype_options_sorted,
                value='All',
                searchable=True,
            ),
        ], style={'width': '40%', 'display': 'inline-block'}),
        dcc.Graph(
            id='Man001ActiveJobsBL-my-graph',
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
            ), style={'height': 500, 'display': 'block', 'margin-top': '25px'}),
        html.Div(children='Filter by Duration'),
        html.Div([
            dcc.Dropdown(
                id='Man001ActiveJobsBL-duration-dropdown',
                options=duration_options,
                value='All',
                searchable=True
            ),
        ], style={'width': '30%', 'display': 'inline-block'}),
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
    ]
)

@app.callback(
    Output('Man001ActiveJobsBL-my-graph', 'figure'),
    [Input('Man001ActiveJobsBL-licensetype-dropdown', 'value')])
def update_graph(license_type):
    df_counts_updated = update_counts_graph_data(license_type)
    return {
        'data': [
             go.Bar(
                 x=df_counts_updated[df_counts_updated['JobType'] == 'Business License Application']['Duration'],
                 y=df_counts_updated[df_counts_updated['JobType'] == 'Business License Application']['JobCounts'],
                 name='BL Application Jobs Active',
                 marker=go.bar.Marker(
                     color='rgb(55, 83, 109)'
                 )
             ),
             go.Bar(
                 x=df_counts_updated[df_counts_updated['JobType'] == 'Amendment/Renewal']['Duration'],
                 y=df_counts_updated[df_counts_updated['JobType'] == 'Amendment/Renewal']['JobCounts'],
                 name='BL Renewal/Amendment Jobs Active',
                 marker=go.bar.Marker(
                     color='rgb(26, 118, 255)'
                 )
             )
        ],
        'layout': go.Layout(
            showlegend=True,
            legend=go.layout.Legend(
                x=.75,
                y=1
            ),
            margin=go.layout.Margin(l=40, r=0, t=40, b=30)
        )
    }

@app.callback(
    Output('Man001ActiveJobsBL-table', 'rows'), 
    [Input('Man001ActiveJobsBL-duration-dropdown', 'value'),
     Input('Man001ActiveJobsBL-licensetype-dropdown', 'value')])
def update_table(duration, license_type):
    df = get_data_object(duration, license_type)
    return df.to_dict('records')

@app.callback(
    Output('Man001ActiveJobsBL-download-link', 'href'),
    [Input('Man001ActiveJobsBL-duration-dropdown', 'value'),
     Input('Man001ActiveJobsBL-licensetype-dropdown', 'value')])
def update_download_link(duration, license_type):
    df = get_data_object(duration, license_type)
    csv_string = df.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string