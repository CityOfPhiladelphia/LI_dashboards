import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from dash.dependencies import Input, Output
import urllib.parse

from app import app, con


print("Man002ActiveProcessesBL.py")

#Definitions: BL Apps and Renewals
#excludes jobs in Statuses More Information Required, Denied, Draft, Withdrawn, Approved
#excludes processes of Pay Fees, Provide More Information for Renewal, Amend License
#No completion date on processes

with con() as con:
    sql = 'SELECT * FROM li_dash_activeproc_bl_ind'
    df_table = pd.read_sql_query(sql=sql, con=con)
    sql = 'SELECT * FROM li_dash_activeproc_bl_counts'
    df_counts = pd.read_sql_query(sql=sql, con=con)
    sql = "SELECT from_tz(cast(last_ddl_time as timestamp), 'GMT') at TIME zone 'US/Eastern' as LAST_DDL_TIME FROM user_objects WHERE object_name = 'LI_DASH_ACTIVEPROC_BL_IND'"
    ind_last_ddl_time = pd.read_sql_query(sql=sql, con=con)
    sql = "SELECT from_tz(cast(last_ddl_time as timestamp), 'GMT') at TIME zone 'US/Eastern' as LAST_DDL_TIME FROM user_objects WHERE object_name = 'LI_DASH_ACTIVEPROC_BL_COUNTS'"
    counts_last_ddl_time = pd.read_sql_query(sql=sql, con=con)

# Make TIMESINCESCHEDULEDSTARTDATE a Categorical Series and give it a sort order
time_categories = ["0-1 Day", "2-5 Days", "6-10 Days", "11 Days-1 Year", "Over 1 Year"]
df_counts['TIMESINCESCHEDULEDSTARTDATE'] = pd.Categorical(df_counts['TIMESINCESCHEDULEDSTARTDATE'], time_categories)
df_counts.sort_values(by='TIMESINCESCHEDULEDSTARTDATE')

duration_options = []
for duration in time_categories:
    duration_options.append({'label': str(duration), 'value': duration})

processtype_options_unsorted = []
for processtype in df_counts['PROCESSTYPE'].unique():
    processtype_options_unsorted.append({'label': str(processtype),'value': processtype})
processtype_options_sorted = sorted(processtype_options_unsorted, key=lambda k: k['label'])

licensetype_options_unsorted = [{'label': 'All', 'value': 'All'}]
for licensetype in df_table['LICENSETYPE'].unique():
    if str(licensetype) != "nan":
        licensetype_options_unsorted.append({'label': str(licensetype), 'value': licensetype})
licensetype_options_sorted = sorted(licensetype_options_unsorted, key=lambda k: k['label'])

def get_data_object(process_type, license_type):
    df_selected = df_table.copy(deep=True)
    if process_type is not None:
        if isinstance(process_type, str):
            df_selected = df_selected[df_selected['PROCESSTYPE'] == process_type]
        elif isinstance(process_type, list):
            if len(process_type) > 1:
                df_selected = df_selected[df_selected['PROCESSTYPE'].isin(process_type)]
            elif len(process_type) == 1:
                df_selected = df_selected[df_selected['PROCESSTYPE'] == process_type[0]]
    if license_type != "All":
        df_selected = df_selected[df_selected['LICENSETYPE'] == license_type]
    return df_selected

def update_counts_graph_data(process_type, license_type):
    df_counts_selected = df_counts.copy(deep=True)
    if process_type is not None:
        if isinstance(process_type, str):
            df_counts_selected = df_counts_selected[df_counts_selected['PROCESSTYPE'] == process_type]
        elif isinstance(process_type, list):
            if len(process_type) > 1:
                df_counts_selected = df_counts_selected[df_counts_selected['PROCESSTYPE'].isin(process_type)]
            elif len(process_type) == 1:
                df_counts_selected = df_counts_selected[df_counts_selected['PROCESSTYPE'] == process_type[0]]
    if license_type != "All":
        df_counts_selected = df_counts_selected[df_counts_selected['LICENSETYPE'] == license_type]
    df_grouped = (df_counts_selected.groupby(by=['JOBTYPE', 'TIMESINCESCHEDULEDSTARTDATE'])['PROCESSCOUNTS']
                  .sum()
                  .reset_index())
    df_grouped['JOBTYPE'] = df_grouped['JOBTYPE'].astype(str)
    df_grouped['TIMESINCESCHEDULEDSTARTDATE'] = pd.Categorical(df_grouped['TIMESINCESCHEDULEDSTARTDATE'], time_categories)
    for time_cat in time_categories:
        if time_cat not in df_grouped[df_grouped['JOBTYPE'] == 'Application']['TIMESINCESCHEDULEDSTARTDATE'].values:
            df_missing_time_cat = pd.DataFrame([['Application', time_cat, 0]], columns=['JOBTYPE', 'TIMESINCESCHEDULEDSTARTDATE', 'PROCESSCOUNTS'])
            df_grouped = df_grouped.append(df_missing_time_cat, ignore_index=True)
    df_grouped['TIMESINCESCHEDULEDSTARTDATE'] = pd.Categorical(df_grouped['TIMESINCESCHEDULEDSTARTDATE'], time_categories)
    return df_grouped.sort_values(by='TIMESINCESCHEDULEDSTARTDATE')

layout = html.Div([
    html.H1(
        'Active Processes',
        style={'margin-top': '10px'}
    ),
    html.H1(
        '(Business Licenses)',
        style={'margin-bottom': '50px'}
    ),
    html.Div([
        html.Div([
            html.P('Process Type'),
            dcc.Dropdown(
                id='processtype-dropdown',
                options=processtype_options_sorted,
                multi=True
            ),
        ], className='four columns'),
        html.Div([
            html.P('License Type'),
            dcc.Dropdown(
                id='licensetype-dropdown',
                options=licensetype_options_sorted,
                value='All',
                searchable=True
            ),
        ], className='six columns'),
    ], className='dashrow filters'),
    html.Div([
        dcc.Graph(
            id='002BL-graph',
            config={
                'displayModeBar': False
            },
            figure=go.Figure(
                data=[
                    go.Bar(
                        x=df_counts[df_counts['JOBTYPE'] == 'Application']['TIMESINCESCHEDULEDSTARTDATE'],
                        y=df_counts[df_counts['JOBTYPE'] == 'Application']['PROCESSCOUNTS'],
                        name='Applications',
                        marker=go.bar.Marker(
                            color='rgb(55, 83, 109)'
                        )
                    ),
                    go.Bar(
                        x=df_counts[df_counts['JOBTYPE'] == 'Amendment/Renewal']['TIMESINCESCHEDULEDSTARTDATE'],
                        y=df_counts[df_counts['JOBTYPE'] == 'Amendment/Renewal']['PROCESSCOUNTS'],
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
            )
        )
    ], style={'margin-left': 'auto', 'margin-right': 'auto', 'float': 'none'},
        className='nine columns'),
    html.P(f"Data last updated {counts_last_ddl_time['LAST_DDL_TIME'].iloc[0]}", className = 'timestamp', style = {
    'text-align': 'center'}),
    html.Div([
        html.Div([
            html.Div([
                dt.DataTable(
                    rows=[{}],
                    filterable=True,
                    sortable=True,
                    selected_row_indices=[],
                    editable=False,
                    id='Man002ActiveProcessesBL-table'
                )
            ], style={'text-align': 'center'}),
            html.Div([
                html.A(
                    'Download Data',
                    id='Man002ActiveProcessesBL-download-link',
                    download='Man002ActiveProcessesBL.csv',
                    href='',
                    target='_blank',
                )
            ], style={'text-align': 'right'}),
        ], style={'margin-top': '70px', 'margin-bottom': '50px'})
    ], className='dashrow'),
    html.P(f"Data last updated {ind_last_ddl_time['LAST_DDL_TIME'].iloc[0]}", className = 'timestamp', style = {
    'text-align': 'center'}),
    html.Details([
        html.Summary('Query Description'),
        html.Div(
            'Incomplete processes (excluding "Pay Fees", "Provide More Information for Renewal", and "Amend License" processes) '
            'associated with business license application or amend/renew jobs that have statuses of "Approved", "Draft", '
            '"Withdrawn", or "More Information Required" (i.e. not "Application Incomplete", "Distribute", '
            '"In Adjudication", "Payment Pending", "Rejected", or "Submitted")')
    ])
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
                x=df_counts_updated[df_counts_updated['JOBTYPE'] == 'Application']['TIMESINCESCHEDULEDSTARTDATE'],
                y=df_counts_updated[df_counts_updated['JOBTYPE'] == 'Application']['PROCESSCOUNTS'],
                name='Applications',
                marker=go.bar.Marker(
                    color='rgb(55, 83, 109)'
                )
            ),
            go.Bar(
                x=df_counts_updated[df_counts_updated['JOBTYPE'] == 'Amendment/Renewal']['TIMESINCESCHEDULEDSTARTDATE'],
                y=df_counts_updated[df_counts_updated['JOBTYPE'] == 'Amendment/Renewal']['PROCESSCOUNTS'],
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
