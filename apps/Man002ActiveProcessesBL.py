import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from dash.dependencies import Input, Output
import urllib.parse

from app import app, con

testing_mode = True
print("Man002ActiveProcessesBL.py")
print("Testing mode? " + str(testing_mode))

#Definitions: BL Apps and Renewals
#excludes jobs in Statuses More Information Required, Denied, Draft, Withdrawn, Approved
#excludes processes of Pay Fees, Provide More Information for Renewal, Amend License
#No completion date on processes

if testing_mode:
    df_table = pd.read_csv("test_data/Man002ActiveProcessesBL_ind_records_test_data.csv")
    df_counts = pd.read_csv("test_data/Man002ActiveProcessesBL_counts_test_data.csv")
else:
    with con() as con:
        sql_tl = """select distinct j.ExternalFileNum "JobNumber", jt.Description "JobType", nvl(lt.Name, lt2.Name) "LicenseType", stat.Description "JobStatus", proc.ProcessId "ProcessID", pt.Description "ProcessType", extract(month from proc.CreatedDate) || '/'||extract(day from proc.CreatedDate)|| '/'|| extract(year from proc.CreatedDate) "CreatedDate", extract(month from proc.ScheduledStartDate) || '/'|| extract(day from proc.ScheduledStartDate)|| '/'||extract(year from proc.ScheduledStartDate) "ScheduledStartDate", proc.ProcessStatus "ProcessStatus",(CASE WHEN round(sysdate - proc.ScheduledStartDate) <= 1 then '0-1 Day' WHEN round(sysdate - proc.ScheduledStartDate) between 2 and 5 then '2-5 Days' WHEN round(sysdate - proc.ScheduledStartDate) between 6 and 10 then '6-10 Days' ELSE '11+ Days' END) "TimeSinceScheduledStartDate",(CASE when jt.Description like 'Business License Application' then 'https://eclipseprod.phila.gov/phillylmsprod/int/lms/Default.aspx#presentationId=1239699&objectHandle='||j.JobId||'&processHandle=&paneId=1239699_151'when jt.Description like 'Amendment/Renewal' then 'https://eclipseprod.phila.gov/phillylmsprod/int/lms/Default.aspx#presentationId=1243107&objectHandle='||j.JobId||'&processHandle=&paneId=1243107_175' End) "ProcessLink" from api.PROCESSES proc, api.jobs j, api.processtypes pt, api.jobtypes jt, api.statuses stat, query.r_bl_amendrenew_license arl, query.r_bl_license_licensetype lrl, query.o_bl_licensetype lt, query.r_bl_application_license apl, query.r_bl_license_licensetype lrl2, query.o_bl_licensetype lt2 where proc.JobId = j.JobId and proc.ProcessTypeId = pt.ProcessTypeId and proc.DateCompleted is null and j.JobTypeId = jt.JobTypeId and j.StatusId = stat.StatusId and pt.ProcessTypeId not in ('984507','2852606','2853029') and jt.JobTypeId in ('1240320', '1244773') and j.StatusId not in ('1030266','964970','1014809','1036493','1010379') and j.JobId = arl.AmendRenewId (+) and arl.LicenseId = lrl.LicenseId (+) and lrl.LicenseTypeId = lt.ObjectId (+) and j.JobId = apl.ApplicationObjectId (+) and apl.LicenseObjectId = lrl2.LicenseId (+) and lrl2.LicenseTypeId = lt2.ObjectId (+)"""
        sql_counts = """SELECT DISTINCT jobtype "JobType", processtype "ProcessType", licensetype "LicenseType", Count(DISTINCT processid) "ProcessCounts" FROM(SELECT DISTINCT j.externalfilenum JobExtNum, j.statusid, jt.description JobType, Nvl(ap.licensetypesdisplayformat, ar.licensetypesdisplayformat) LicenseType, stat.description JobStatus, pt.processtypeid, proc.processid ProcessID, pt.description ProcessType, Extract( month FROM proc.createddate) || '/' ||Extract(day FROM proc.createddate) || '/' || Extract(year FROM proc.createddate) CreatedDate, Extract( month FROM proc.scheduledstartdate) || '/' || Extract(day FROM proc.scheduledstartdate) || '/' ||Extract(year FROM proc.scheduledstartdate) ScheduledStartDate , ( CASE WHEN proc.datecompleted IS NOT NULL THEN Extract(month FROM proc.datecompleted) || '/' || Extract( day FROM proc.datecompleted) || '/' ||Extract(year FROM proc.datecompleted) ELSE NULL END) DateCompleted, proc.processstatus, ( CASE WHEN Round(SYSDATE - proc.scheduledstartdate) <= 1 THEN '0-1 Day' WHEN Round(SYSDATE - proc.scheduledstartdate) BETWEEN 2 AND 5 THEN '2-5 Days' WHEN Round(SYSDATE - proc.scheduledstartdate) BETWEEN 6 AND 10 THEN '6-10 Days' ELSE '11+ Days' END ) TimeSinceScheduledStartDate FROM api.processes proc, api.jobs j, api.processtypes pt, api.jobtypes jt, api.statuses stat, query.j_bl_amendrenew ar, query.j_bl_application ap WHERE proc.jobid = j.jobid AND proc.processtypeid = pt.processtypeid AND j.jobid = ar.jobid (+) AND j.jobid = ap.jobid (+) AND proc.datecompleted IS NULL AND j.jobtypeid = jt.jobtypeid AND j.statusid = stat.statusid AND pt.processtypeid NOT IN ( '984507', '2852606', '2853029' ) AND jt.jobtypeid IN ( '1240320', '1244773' ) AND j.statusid NOT IN ( '1030266', '964970', '1014809', '1036493', '1010379' )) GROUP BY jobtype, processtype, licensetype"""
        df_table = pd.read_sql(sql_tl, con)
        df_counts = pd.read_sql(sql_counts, con)

# Remove the words "Business License" just to make it easier for user to read
df_table['JobType'] = df_table['JobType'].map(lambda x: x.replace("Business License ", ""))
df_counts['JobType'] = df_counts['JobType'].map(lambda x: x.replace("Business License ", ""))

processtype_options_unsorted = []
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
    if process_type is not None:
        if isinstance(process_type, str):
            df_selected = df_selected[df_selected['ProcessType'] == process_type]
        elif isinstance(process_type, list):
            if len(process_type) > 1:
                df_selected = df_selected[df_selected['ProcessType'].isin(process_type)]
            elif len(process_type) == 1:
                df_selected = df_selected[df_selected['ProcessType'] == process_type[0]]
    if license_type != "All":
        df_selected = df_selected[df_selected['LicenseType'] == license_type]
    return df_selected

def update_counts_graph_data(process_type, license_type):
    df_counts_selected = df_counts
    if process_type is not None:
        if isinstance(process_type, str):
            df_counts_selected = df_counts_selected[df_counts_selected['ProcessType'] == process_type]
        elif isinstance(process_type, list):
            if len(process_type) > 1:
                df_counts_selected = df_counts_selected[df_counts_selected['ProcessType'].isin(process_type)]
            elif len(process_type) == 1:
                df_counts_selected = df_counts_selected[df_counts_selected['ProcessType'] == process_type[0]]
    if license_type != "All":
        df_counts_selected = df_counts_selected[df_counts_selected['LicenseType'] == license_type]
    return df_counts_selected

layout = html.Div([
    html.H1(
        'Active Processes',
        style={'margin-top': '10px'}
    ),
    html.H1(
        '(Business Licenses)',
        style={'margin-bottom': '50px'}
    ),
    html.Div(
        children=[
            'Process Type'
        ],
        style={'margin-left': '15%', 'margin-top': '10px', 'margin-bottom': '5px'}
    ),
    html.Div([
        dcc.Dropdown(
            id='processtype-dropdown',
            options=processtype_options_sorted,
            multi=True
        ),
    ], style={'width': '33%', 'display': 'inline-block', 'margin-left': '15%'}),
    html.Div(
        children=[
            'License Type'
        ],
        style={'margin-left': '15%', 'margin-top': '10px', 'margin-bottom': '5px'}
    ),
    html.Div([
        dcc.Dropdown(
            id='licensetype-dropdown',
            options=licensetype_options_sorted,
            value='All',
            searchable=True
        ),
    ], style={'width': '33%', 'display': 'inline-block', 'margin-left': '15%'}),
    dcc.Graph(
        id='002BL-graph',
        figure=go.Figure(
            data=[
                go.Bar(
                    x=df_counts[df_counts['JobType'] == 'Application'].groupby(['ProcessType'])['ProcessCounts'].agg(np.sum).index,
                    y=df_counts[df_counts['JobType'] == 'Application'].groupby(['ProcessType'])['ProcessCounts'].agg(np.sum),
                    name='Applications',
                    marker=go.bar.Marker(
                        color='rgb(55, 83, 109)'
                    )
                ),
                go.Bar(
                    x=df_counts[df_counts['JobType'] == 'Amendment/Renewal'].groupby(['ProcessType'])['ProcessCounts'].agg(np.sum).index,
                    y=df_counts[df_counts['JobType'] == 'Amendment/Renewal'].groupby(['ProcessType'])['ProcessCounts'].agg(np.sum),
                    name='Renewals/Amendments',
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
                yaxis=dict(
                    title='Active Processes'
                ),
                margin=go.layout.Margin(l=40, r=0, t=40, b=100)
            )
        ), style={'height': '500px', 'display': 'block', 'margin-bottom': '75px', 'width': '70%', 'margin-left': 'auto', 'margin-right': 'auto'}
    ),
    html.Div([
        dt.DataTable(
            # Initialise the rows
            rows=[{}],
            row_selectable=True,
            filterable=True,
            sortable=True,
            selected_row_indices=[],
            editable=False,
            id='Man002ActiveProcessesBL-table'
        )
    ], style={'width': '90%', 'margin-left': 'auto', 'margin-right': 'auto'}),
    html.Div([
        html.A(
            'Download Data',
            id='Man002ActiveProcessesBL-download-link',
            download='Man002ActiveProcessesBL.csv',
            href='',
            target='_blank',
        )
    ], style={'text-align': 'right', 'margin-right': '5%'}),
])

@app.callback(
    Output('002BL-graph', 'figure'),
    [Input('processtype-dropdown', 'value'),
     Input('licensetype-dropdown', 'value')])
def update_graph(process_type, license_type):
    df_counts_updated = update_counts_graph_data(process_type, license_type)
    return {
        'data': [
            go.Bar(
                x=df_counts_updated[df_counts_updated['JobType'] == 'Application'].groupby(['ProcessType'])['ProcessCounts'].agg(np.sum).index,
                y=df_counts_updated[df_counts_updated['JobType'] == 'Application'].groupby(['ProcessType'])['ProcessCounts'].agg(np.sum),
                name='Applications',
                marker=go.bar.Marker(
                    color='rgb(55, 83, 109)'
                )
            ),
            go.Bar(
                x=df_counts_updated[df_counts_updated['JobType'] == 'Amendment/Renewal'].groupby(['ProcessType'])['ProcessCounts'].agg(np.sum).index,
                y=df_counts_updated[df_counts_updated['JobType'] == 'Amendment/Renewal'].groupby(['ProcessType'])['ProcessCounts'].agg(np.sum),
                name='Renewals/Amendments',
                marker=go.bar.Marker(
                    color='rgb(26, 118, 255)'
                )
            )
        ],
        'layout': go.Layout(
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
            yaxis=dict(
                title='Active Processes'
            ),
            margin=go.layout.Margin(l=40, r=0, t=40, b=100)
        )
    }

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
