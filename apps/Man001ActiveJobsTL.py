import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import plotly.graph_objs as go
import pandas as pd
from dash.dependencies import Input, Output
import urllib.parse

from app import app, con

testing_mode = False
print("Man001ActiveJobsTL.py")
print("Testing mode? " + str(testing_mode))

#Definitions: Job Type Tl Application and TL Amendment/Renewal
#Process Completed: Renewal Review Application, Issue License, Renew License, Amend License, Generate License, Completeness Check, Review Application, Amendment on Renewal
#Not in Status: Draft, More Information Required, Application Incomplete, Payment Pending
#time calculated as time between Scheduled Start Date to today

if testing_mode:
    df_table = pd.read_csv("test_data/Man001ActiveJobsTLIndividualRecords_test_data.csv")
    df_counts = pd.read_csv("test_data/Man001ActiveJobsTLCounts_test_data.csv")
else:
    with con() as con:
        sql_tl = """SELECT DISTINCT j.externalfilenum "JobNumber", jt.description "JobType", Nvl(lt.title, lt2.title) "LicenseType", stat.description "JobStatus", proc.processid "ProcessID", pt.description "ProcessType", Extract(month FROM proc.datecompleted) || '/' ||Extract(day FROM proc.datecompleted) || '/' || Extract(year FROM proc.datecompleted) "JobAcceptedDate", proc.processstatus "ProcessStatus", proc.assignedstaff "AssignedStaff",( CASE WHEN Round(SYSDATE - proc.scheduledstartdate) <= 1 THEN '0-1 Day' WHEN Round(SYSDATE - proc.scheduledstartdate) BETWEEN 2 AND 5 THEN '2-5 Days' WHEN Round(SYSDATE - proc.scheduledstartdate) BETWEEN 6 AND 10 THEN '6-10 Days' WHEN Round(SYSDATE - proc.scheduledstartdate) BETWEEN 11 AND 365 THEN '11 Days-1 Year' ELSE 'Over 1 Year' END) "TimeSinceScheduledStartDate", ( CASE WHEN jt.description LIKE 'Trade License Application' THEN 'https://eclipseprod.phila.gov/phillylmsprod/int/lms/Default.aspx#presentationId=2854033&objectHandle=' ||j.jobid ||'&processHandle=&paneId=2854033_116' WHEN jt.description LIKE 'Trade License Amend/Renew' THEN 'https://eclipseprod.phila.gov/phillylmsprod/int/lms/Default.aspx#presentationId=2857688&objectHandle=' ||j.jobid ||'&processHandle=&paneId=2857688_87' END ) "JobLink" FROM api.jobs j, api.jobtypes jt, api.statuses stat, api.processes proc, api.processtypes pt, query.j_tl_amendrenew ar, query.r_tl_amendrenew_license arl, query.r_tllicensetype lrl, query.o_tl_licensetype lt, query.j_tl_application apl, query.r_tllicensetype lrl2, query.o_tl_licensetype lt2 WHERE j.jobid = proc.jobid AND proc.processtypeid = pt.processtypeid AND j.externalfilenum = ar.externalfilenum (+) AND ar.objectid = arl.amendrenewid (+) AND arl.licenseid = lrl.licenseobjectid (+) AND lrl.licensetypeobjectid = lt.objectid (+) AND j.jobid = apl.objectid (+) AND apl.tradelicenseobjectid = lrl2.licenseobjectid (+) AND lrl2.licensetypeobjectid = lt2.objectid (+) AND j.externalfilenum LIKE 'T%' AND pt.processtypeid IN ( '2851903', '2854108', '2852692', '2852680', '2854639', '2853029', '2854845', '2855079' ) AND proc.datecompleted IS NOT NULL AND j.jobtypeid = jt.jobtypeid AND j.statusid = stat.statusid AND j.completeddate IS NULL AND j.jobtypeid IN ( '2853921', '2857525' ) AND j.statusid NOT IN ( '1014809', '978845', '964970', '967394' ) ORDER BY j.externalfilenum"""
        sql_counts = """SELECT DISTINCT timesincescheduledstartdate "TimeSinceScheduledStartDate", jobtype "JobType", licensetype "LicenseType", Count(DISTINCT jobnumber) "JobCounts", Avg(TIME) AvgTime FROM(SELECT DISTINCT j.externalfilenum JobNumber, Nvl(lt.title, lt2.title) LicenseType, jt.description JobType, j.statusid, j.jobstatus, stat.description "JobStatus", pt.processtypeid, pt.description, Extract(month FROM proc.datecompleted) || '/' ||Extract(day FROM proc.datecompleted) || '/' || Extract(year FROM proc.datecompleted) "JobAcceptedDate", proc.processstatus, proc.assignedstaff, ( CASE WHEN Round(SYSDATE - proc.scheduledstartdate) <= 1 THEN '0-1 Day' WHEN Round(SYSDATE - proc.scheduledstartdate) BETWEEN 2 AND 5 THEN '2-5 Days' WHEN Round(SYSDATE - proc.scheduledstartdate) BETWEEN 6 AND 10 THEN '6-10 Days' WHEN Round(SYSDATE - proc.scheduledstartdate) BETWEEN 11 AND 365 THEN '11 Days-1 Year' ELSE 'Over 1 Year' END) TimeSinceScheduledStartDate, j.jobid, ( SYSDATE - proc.scheduledstartdate ) TIME FROM api.jobs j, api.jobtypes jt, api.statuses stat, api.processes proc, api.processtypes pt, query.j_tl_amendrenew ar, query.r_tl_amendrenew_license arl, query.r_tllicensetype lrl, query.o_tl_licensetype lt, query.j_tl_application apl, query.r_tllicensetype lrl2, query.o_tl_licensetype lt2 WHERE j.jobid = proc.jobid AND proc.processtypeid = pt.processtypeid AND j.externalfilenum = ar.externalfilenum (+) AND ar.objectid = arl.amendrenewid (+) AND arl.licenseid = lrl.licenseobjectid (+) AND lrl.licensetypeobjectid = lt.objectid (+) AND j.jobid = apl.objectid (+) AND apl.tradelicenseobjectid = lrl2.licenseobjectid (+) AND lrl2.licensetypeobjectid = lt2.objectid (+) AND j.externalfilenum LIKE 'T%' AND pt.processtypeid IN( '2851903', '2854108', '2852692', '2852680', '2854639', '2853029', '2854845', '2855079' ) AND proc.datecompleted IS NOT NULL AND j.jobtypeid = jt.jobtypeid AND j.statusid = stat.statusid AND j.completeddate IS NULL AND j.jobtypeid IN ( '2853921', '2857525' ) AND j.statusid NOT IN ( '1014809', '978845', '964970', '967394' )) GROUP BY timesincescheduledstartdate, jobtype, licensetype ORDER BY avgtime DESC"""
        df_table = pd.read_sql(sql_tl, con)
        df_counts = pd.read_sql(sql_counts, con)

df_table['JobType'] = df_table['JobType'].map(lambda x: x.replace("Trade License", "TL"))  # Replace "Trade License " with TL just to make it easier for user to read

duration_options = [{'label': 'All', 'value': 'All'}]
for duration in df_counts['TimeSinceScheduledStartDate'].unique():
    duration_options.append({'label': str(duration), 'value': duration})

licensetype_options_unsorted = [{'label': 'All', 'value': 'All'}]
for licensetype in df_table['LicenseType'].unique():
    if str(licensetype) != "nan":
        licensetype_options_unsorted.append({'label': str(licensetype), 'value': licensetype})
licensetype_options_sorted = sorted(licensetype_options_unsorted, key=lambda k: k['label'])

def get_data_object(duration, license_type):
    df_selected = df_table
    if duration != "All":
        df_selected = df_selected[df_selected['TimeSinceScheduledStartDate'] == duration]
    if license_type != "All":
        df_selected = df_selected[df_selected['LicenseType'] == license_type]
    return df_selected

def update_counts_graph_data(license_type):
    df_counts_selected = df_counts
    if license_type != "All":
        df_counts_selected = df_counts_selected[df_counts_selected['LicenseType'] == license_type]
    return df_counts_selected

layout = html.Div([
    html.H1('Active Jobs With Completed Completeness Checks'),
    html.H1(
        '(Trade Licenses)',
        style={'margin-bottom': '10px'}
    ),
    html.Div('Filter by License Type', style={'margin-top': '25px'}),
    html.Div([
        dcc.Dropdown(
            id='licensetype-graph-dropdown',
            options=licensetype_options_sorted,
            value='All',
            searchable=True,
        ),
    ], style={'width': '40%', 'display': 'inline-block'}),
    dcc.Graph(id='my-graph',
    figure=go.Figure(
        data=[
            go.Bar(
                x=df_counts[df_counts['JobType'] == 'Trade License Application']['TimeSinceScheduledStartDate'],
                y=df_counts[df_counts['JobType'] == 'Trade License Application']['JobCounts'],
                name='Applications',
                marker=go.bar.Marker(
                    color='rgb(55, 83, 109)'
                )
            ),
            go.Bar(
                x=df_counts[df_counts['JobType'] == 'Trade License Amend/Renew']['TimeSinceScheduledStartDate'],
                y=df_counts[df_counts['JobType'] == 'Trade License Amend/Renew']['JobCounts'],
                name='Renewals/Amendments',
                marker=go.bar.Marker(
                    color='rgb(26, 118, 255)'
                )
            )
        ],
        layout=go.Layout(
            xaxis=dict(
                title='Time Since Scheduled Start Date of Process'
            ),
            yaxis=dict(
                title='Active Trade License Jobs'
            ),
            showlegend=True,
            legend=go.layout.Legend(
                x=.75,
                y=1
            )
        )
    ),
    style={'display': 'block', 'margin-bottom': '75px'}),
    html.Div(
        children=[
            'Time Since Scheduled Start Date of Process'
        ],
        style={'margin-left': '1%'}
    ),
    html.Div([
        dcc.Dropdown(
            id='duration-dropdown',
            options=duration_options,
            value='All',
            searchable=True
        ),
    ], style={'width': '30%', 'display': 'inline-block', 'margin-left': '2%'}),
    html.Div(
        children=[
            'License Type'
        ],
        style={'margin-left': '1%'}
    ),
    html.Div([
        dcc.Dropdown(id='licensetype-table-dropdown',
                     options=licensetype_options_sorted,
                     value='All',
                     searchable=True
                     ),
    ], style={'width': '40%', 'display': 'inline-block'}),
    html.Div([
        html.A(
            'Download Data',
            id='Man001ActiveJobsTL-download-link',
            download='Man001ActiveJobsTL.csv',
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
        editable=False,
        id='Man001ActiveJobsTL-table'
    )
])

@app.callback(
    Output('my-graph', 'figure'),
    [Input('licensetype-graph-dropdown', 'value')])
def update_graph(license_type):
    df_counts_updated = update_counts_graph_data(license_type)
    return {
        'data': [
             go.Bar(
                 x=df_counts_updated[df_counts_updated['JobType'] == 'Trade License Application']['Duration'],
                 y=df_counts_updated[df_counts_updated['JobType'] == 'Trade License Application']['JobCounts'],
                 name='TL Application Jobs Active',
                 marker=go.bar.Marker(
                     color='rgb(55, 83, 109)'
                 )
             ),
             go.Bar(
                 x=df_counts_updated[df_counts_updated['JobType'] == 'Trade License Amend/Renew']['Duration'],
                 y=df_counts_updated[df_counts_updated['JobType'] == 'Trade License Amend/Renew']['JobCounts'],
                 name='TL Renewal/Amendment Jobs Active',
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
    Output('Man001ActiveJobsTL-table', 'rows'),
    [Input('duration-dropdown', 'value'),
     Input('licensetype-table-dropdown', 'value')])
def update_table(duration, license_type):
    df = get_data_object(duration, license_type)
    return df.to_dict('records')


@app.callback(
    Output('Man001ActiveJobsTL-download-link', 'href'),
    [Input('duration-dropdown', 'value'),
     Input('licensetype-table-dropdown', 'value')])
def update_download_link(duration, license_type):
    df = get_data_object(duration, license_type)
    csv_string = df.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string