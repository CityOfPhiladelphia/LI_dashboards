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
print("Man002ActiveProcessesTL.py")
print("Testing mode? " + str(testing_mode))

if testing_mode:
    df_table = pd.read_csv("test_data/Man002ActiveProcessesTL_ind_records_test_data.csv")
    df_counts = pd.read_csv("test_data/Man002ActiveProcessesTL_counts_test_data.csv")
else:
    # Definitions: TL Apps and Renewals
    # excludes jobs in Statuses More Information Required, Denied, Draft, Withdrawn, Approved
    # excludes processes of Pay Fees, Provide More Information for Renewal, Amend License
    # No completion date on processes
    with con() as con:
        sql_tl = """SELECT DISTINCT j.externalfilenum "JobNumber", jt.description "JobType", Nvl(lt.description, lt2.description) "LicenseType", stat.description "JobStatus", proc.processid "ProcessID", pt.description "ProcessType", Extract(month FROM proc.createddate) || '/' ||Extract(day FROM proc.createddate) || '/' || Extract(year FROM proc.createddate) CreatedDate, Extract(month FROM proc.scheduledstartdate) || '/' || Extract(day FROM proc.scheduledstartdate) || '/' ||Extract(year FROM proc.scheduledstartdate) "ScheduledStartDate", proc.processstatus "ProcessStatus",( CASE WHEN Round(SYSDATE - proc.scheduledstartdate) <= 1 THEN '0-1 Day' WHEN Round(SYSDATE - proc.scheduledstartdate) BETWEEN 2 AND 5 THEN '2-5 Days' WHEN Round(SYSDATE - proc.scheduledstartdate) BETWEEN 6 AND 10 THEN '6-10 Days' ELSE '11+ Days' END) "Duration", ( CASE WHEN jt.description LIKE 'Trade License Application' THEN 'https://eclipseprod.phila.gov/phillylmsprod/int/lms/Default.aspx#presentationId=2854033&objectHandle=' ||j.jobid ||'&processHandle=&paneId=2854033_116' WHEN jt.description LIKE 'Trade License Amend/Renew' THEN 'https://eclipseprod.phila.gov/phillylmsprod/int/lms/Default.aspx#presentationId=2857688&objectHandle=' ||j.jobid ||'&processHandle=&paneId=2857688_87' END ) "ProcessLink" FROM api.processes proc, api.jobs j, api.processtypes pt, api.jobtypes jt, api.statuses stat, query.r_tl_amendrenew_license arl, query.o_tl_license lic, query.o_tl_licensetype lt, query.r_tllicenselicense apl, query.o_tl_license lic2, query.o_tl_licensetype lt2 WHERE proc.jobid = j.jobid AND proc.processtypeid = pt.processtypeid AND proc.datecompleted IS NULL AND j.jobtypeid = jt.jobtypeid AND j.statusid = stat.statusid AND pt.processtypeid NOT IN ( '984507', '2852606', '2853029' ) AND jt.jobtypeid IN ( '2853921', '2857525' ) AND j.statusid NOT IN ( '1030266', '964970', '1014809', '1036493', '1010379' ) AND j.jobid = arl.amendrenewid (+) AND arl.licenseid = lic.objectid (+) AND lic.revenuecode = lt.revenuecode (+) AND j.jobid = apl.tlapp (+) AND apl.license = lic2.objectid (+) AND lic2.revenuecode = lt2.revenuecode (+)"""
        sql_counts = """SELECT DISTINCT JobType "JobType", ProcessType "ProcessType", LicenseType "LicenseType", COUNT(DISTINCT ProcessID) "ProcessCounts" FROM(SELECT DISTINCT j.ExternalFileNum JobExtNum, j.StatusId, jt.Description JobType, NVL(lt.description, lt2.description) LicenseType, stat.Description JobStatus, pt.ProcessTypeId, proc.ProcessId ProcessID, pt.Description ProcessType, extract(MONTH FROM proc.CreatedDate) || '/' ||extract(DAY FROM proc.CreatedDate) || '/' || extract(YEAR FROM proc.CreatedDate) CreatedDate, extract(MONTH FROM proc.ScheduledStartDate) || '/' || extract(DAY FROM proc.ScheduledStartDate) || '/' ||extract(YEAR FROM proc.ScheduledStartDate) ScheduledStartDate, ( CASE WHEN proc.DateCompleted IS NOT NULL THEN extract(MONTH FROM proc.DateCompleted) || '/' || extract(DAY FROM proc.DateCompleted) || '/' ||extract(YEAR FROM proc.DateCompleted) ELSE NULL END) DateCompleted, proc.ProcessStatus, ( CASE WHEN ROUND(sysdate - proc.ScheduledStartDate) <= 1 THEN '0-1 Day' WHEN ROUND(sysdate - proc.ScheduledStartDate) BETWEEN 2 AND 5 THEN '2-5 Days' WHEN ROUND(sysdate - proc.ScheduledStartDate) BETWEEN 6 AND 10 THEN '6-10 Days' ELSE '11+ Days' END) Duration FROM api.PROCESSES PROC, api.jobs j, api.processtypes pt, api.jobtypes jt, api.statuses stat, query.r_tl_amendrenew_license arl, query.o_tl_license lic, query.o_tl_licensetype lt, query.r_tllicenselicense apl, query.o_tl_license lic2, query.o_tl_licensetype lt2 WHERE proc.JobId = j.JobId AND proc.ProcessTypeId = pt.ProcessTypeId AND proc.DateCompleted IS NULL AND j.JobTypeId = jt.JobTypeId AND j.StatusId = stat.StatusId AND pt.ProcessTypeId NOT IN ('984507','2852606','2853029') AND jt.JobTypeId IN ('2853921', '2857525') AND j.StatusId NOT IN ('1030266','964970','1014809','1036493','1010379') AND j.jobid = arl.amendrenewid (+) AND arl.licenseid = lic.objectid (+) AND lic.revenuecode = lt.revenuecode (+) AND j.jobid = apl.tlapp (+) AND apl.license = lic2.objectid (+) AND lic2.revenuecode = lt2.revenuecode (+)) GROUP BY JobType, ProcessType, LicenseType"""
        df_table = pd.read_sql(sql_tl, con)
        df_counts = pd.read_sql(sql_counts, con)

# Remove the words "Trade License" just to make it easier for user to read
df_table['JobType'] = df_table['JobType'].map(lambda x: x.replace("Trade License ", ""))
df_counts['JobType'] = df_counts['JobType'].map(lambda x: x.replace("Trade License ", ""))

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
        '(Trade Licenses)',
        style={'margin-bottom': '50px'}
    ),
    html.Div(
        children=[
            'Process Type'
        ],
        style={'margin-left': '15%', 'margin-bottom': '5px'}
    ),
    html.Div([
        dcc.Dropdown(
            id='processtype-dropdown',
            options=processtype_options_sorted,
            multi=True
        ),
    ], style={'width': '25%', 'display': 'inline-block', 'margin-left': '15%'}),

    html.Div(
        children=[
            'License Type'
        ],
        style={'margin-left': '15%', 'margin-bottom': '5px'}
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
        id='002TL-graph',
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
                    x=df_counts[df_counts['JobType'] == 'Amend/Renew'].groupby(['ProcessType'])['ProcessCounts'].agg(np.sum).index,
                    y=df_counts[df_counts['JobType'] == 'Amend/Renew'].groupby(['ProcessType'])['ProcessCounts'].agg(np.sum),
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
                    y=1
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
            id='Man002ActiveProcessesTL-table'
        )
    ], style={'width': '90%', 'margin-left': 'auto', 'margin-right': 'auto'}),
    html.Div([
        html.A(
            'Download Data',
            id='Man002ActiveProcessesTL-download-link',
            download='Man002ActiveProcessesTL.csv',
            href='',
            target='_blank',
        )
    ], style={'text-align': 'right', 'margin-right': '5%'}),
])

@app.callback(
    Output('002TL-graph', 'figure'),
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
                x=df_counts_updated[df_counts_updated['JobType'] == 'Amend/Renew'].groupby(['ProcessType'])['ProcessCounts'].agg(np.sum).index,
                y=df_counts_updated[df_counts_updated['JobType'] == 'Amend/Renew'].groupby(['ProcessType'])['ProcessCounts'].agg(np.sum),
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
