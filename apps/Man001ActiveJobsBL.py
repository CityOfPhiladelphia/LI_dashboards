import os
import urllib.parse
from datetime import datetime

import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import plotly.graph_objs as go
import pandas as pd
from dash.dependencies import Input, Output

from app import app, cache, cache_timeout

# Definitions: Job Type BL Application and BL Amendment/Renewal
# Completeness Check Completed, Job incomplete
# Not in Status: More Information Required, Payment Pending, Application Incomplete, Draft
# time calculated as time between completion of completeness check to today

APP_NAME = os.path.basename(__file__)

print(APP_NAME)

time_categories = ["0-1 Day", "2-5 Days", "6-10 Days", "11 Days-1 Year", "Over 1 Year"]

@cache_timeout
@cache.memoize()
def query_data(dataset):
    from app import con
    with con() as con:
        if dataset == 'df_ind':
            sql = 'SELECT * FROM li_dash_activejobs_bl_ind'
        elif dataset == 'df_counts':
            sql = 'SELECT * FROM li_dash_activejobs_bl_counts'
        elif dataset == 'ind_last_ddl_time':
            sql = "SELECT from_tz(cast(last_ddl_time as timestamp), 'GMT') at TIME zone 'US/Eastern' as LAST_DDL_TIME FROM user_objects WHERE object_name = 'LI_DASH_ACTIVEJOBS_BL_IND'"
        elif dataset == 'counts_last_ddl_time':
            sql = "SELECT from_tz(cast(last_ddl_time as timestamp), 'GMT') at TIME zone 'US/Eastern' as LAST_DDL_TIME FROM user_objects WHERE object_name = 'LI_DASH_ACTIVEJOBS_BL_COUNTS'"
        df = pd.read_sql_query(sql=sql, con=con)
        if dataset == 'df_counts':
            # Make TIMESINCESCHEDULEDSTARTDATE a Categorical Series and give it a sort order
            df['TIMESINCESCHEDULEDSTARTDATE'] = pd.Categorical(df['TIMESINCESCHEDULEDSTARTDATE'], time_categories)
            df.sort_values(by='TIMESINCESCHEDULEDSTARTDATE', inplace=True)
    return df.to_json(date_format='iso', orient='split')

def dataframe(dataset):
    return pd.read_json(query_data(dataset), orient='split')

def update_layout():
    df_counts = dataframe('df_counts')
    counts_last_ddl_time = dataframe('counts_last_ddl_time')
    ind_last_ddl_time = dataframe('ind_last_ddl_time')

    licensetype_options_unsorted = [{'label': 'All', 'value': 'All'}]
    for licensetype in df_counts['LICENSETYPE'].unique():
        if str(licensetype) != "nan":
            licensetype_options_unsorted.append({'label': str(licensetype), 'value': licensetype})
    licensetype_options_sorted = sorted(licensetype_options_unsorted, key=lambda k: k['label'])

    duration_options = []
    for duration in df_counts['TIMESINCESCHEDULEDSTARTDATE'].unique():
        duration_options.append({'label': str(duration), 'value': duration})

    return html.Div(
        children=[
            html.H1(
                'Active Jobs With Completed Completeness Checks',
                style={'margin-top': '10px'}
            ),
            html.H1(
                '(Business Licenses)',
                style={'margin-bottom': '50px'}
            ),
            html.Div([
                html.Div([
                    html.P('Time Since Scheduled Start Date of Process'),
                    dcc.Dropdown(
                        id='Man001ActiveJobsBL-duration-dropdown',
                        options=duration_options,
                        multi=True
                    ),
                ], className='four columns'),
                html.Div([
                    html.P('License Type'),
                    dcc.Dropdown(
                        id='Man001ActiveJobsBL-licensetype-dropdown',
                        options=licensetype_options_sorted,
                        value='All',
                        searchable=True
                    ),
                ], className='six columns'),
            ], className='dashrow filters'),
            html.Div([
                dcc.Graph(
                    id='Man001ActiveJobsBL-my-graph',
                    config={
                        'displayModeBar': False
                    },
                    figure=go.Figure(
                        data=[
                            go.Bar(
                                x=df_counts[df_counts['JOBTYPE'] == 'Application']['TIMESINCESCHEDULEDSTARTDATE'],
                                y=df_counts[df_counts['JOBTYPE'] == 'Application']['JOBCOUNTS'],
                                name='Application',
                                marker=go.bar.Marker(
                                    color='rgb(55, 83, 109)'
                                )
                            ),
                            go.Bar(
                                x=df_counts[df_counts['JOBTYPE'] == 'Amendment/Renewal']['TIMESINCESCHEDULEDSTARTDATE'],
                                y=df_counts[df_counts['JOBTYPE'] == 'Amendment/Renewal']['JOBCOUNTS'],
                                name='Amendment/Renewal',
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
                    )
                )
            ], style={'margin-left': 'auto', 'margin-right': 'auto', 'float': 'none'},
                className='nine columns'),
            html.P("Data last updated {}".format(counts_last_ddl_time['LAST_DDL_TIME'].iloc[0]), className = 'timestamp', style = {'text-align': 'center'}),
            html.Div([
                html.Div([
                    html.Div([
                        dt.DataTable(
                            rows=[{}],
                            filterable=True,
                            sortable=True,
                            selected_row_indices=[],
                            editable=False,
                            id='Man001ActiveJobsBL-table'
                        )
                    ], style={'text-align': 'center'}),
                    html.Div([
                        html.A(
                            'Download Data',
                            id='Man001ActiveJobsBL-download-link',
                            download='Man001ActiveJobsBL.csv',
                            href='',
                            target='_blank',
                        )
                    ], style={'text-align': 'right'})
                ], style={'margin-top': '70px', 'margin-bottom': '50px'})
            ], className='dashrow'),
            html.P("Data last updated {}".format(ind_last_ddl_time['LAST_DDL_TIME'].iloc[0]), className = 'timestamp', style = {
                'text-align': 'center'}),
            html.Details([
                html.Summary('Query Description'),
                html.Div(
                    'All business license application or amend/renew jobs that have a completed completeness check process,'
                    ' but haven\'t been completed and don\'t have a status of "More Information Required", '
                    '"Payment Pending", "Application Incomplete", or "Draft" (i.e. have a status of "Distribute", '
                    '"In Adjudication", or "Submitted").')
            ])
        ])

layout = update_layout

def get_data_object(duration, license_type):
    df_selected = dataframe('df_ind')
    if duration is not None:
        if isinstance(duration, str):
            df_selected = df_selected[df_selected['TIMESINCESCHEDULEDSTARTDATE'] == duration]
        elif isinstance(duration, list):
            if len(duration) > 1:
                df_selected = df_selected[df_selected['TIMESINCESCHEDULEDSTARTDATE'].isin(duration)]
            elif len(duration) == 1:
                df_selected = df_selected[df_selected['TIMESINCESCHEDULEDSTARTDATE'] == duration[0]]
    if license_type != "All":
        df_selected = df_selected[df_selected['LICENSETYPE'] == license_type]
    return df_selected.drop(['PROCESSID'], axis=1)

def update_counts_graph_data(duration, license_type):
    df_counts_selected = dataframe('df_counts')
    if duration is not None:
        if isinstance(duration, str):
            df_counts_selected = df_counts_selected[df_counts_selected['TIMESINCESCHEDULEDSTARTDATE'] == duration]
        elif isinstance(duration, list):
            if len(duration) > 1:
                df_counts_selected = df_counts_selected[df_counts_selected['TIMESINCESCHEDULEDSTARTDATE'].isin(duration)]
            elif len(duration) == 1:
                df_counts_selected = df_counts_selected[df_counts_selected['TIMESINCESCHEDULEDSTARTDATE'] == duration[0]]
    if license_type != "All":
        df_counts_selected = df_counts_selected[df_counts_selected['LICENSETYPE'] == license_type]
    df_grouped = (df_counts_selected.groupby(by=['JOBTYPE', 'TIMESINCESCHEDULEDSTARTDATE'])['JOBCOUNTS']
                  .sum()
                  .reset_index())
    df_grouped['JOBTYPE'] = df_grouped['JOBTYPE'].astype(str)
    df_grouped['TIMESINCESCHEDULEDSTARTDATE'] = pd.Categorical(df_grouped['TIMESINCESCHEDULEDSTARTDATE'], time_categories)
    for time_cat in time_categories:
        if time_cat not in df_grouped[df_grouped['JOBTYPE'] == 'Application']['TIMESINCESCHEDULEDSTARTDATE'].values:
            df_missing_time_cat = pd.DataFrame([['Application', time_cat, 0]], columns=['JOBTYPE', 'TIMESINCESCHEDULEDSTARTDATE', 'JOBCOUNTS'])
            df_grouped = df_grouped.append(df_missing_time_cat, ignore_index=True)
    df_grouped['TIMESINCESCHEDULEDSTARTDATE'] = pd.Categorical(df_grouped['TIMESINCESCHEDULEDSTARTDATE'], time_categories)
    return df_grouped.sort_values(by='TIMESINCESCHEDULEDSTARTDATE')


@app.callback(
    Output('Man001ActiveJobsBL-my-graph', 'figure'),
    [Input('Man001ActiveJobsBL-duration-dropdown', 'value'),
     Input('Man001ActiveJobsBL-licensetype-dropdown', 'value')])
def update_graph(duration, license_type):
    df_counts_updated = update_counts_graph_data(duration, license_type)
    return {
        'data': [
             go.Bar(
                 x=df_counts_updated[df_counts_updated['JOBTYPE'] == 'Application']['TIMESINCESCHEDULEDSTARTDATE'],
                 y=df_counts_updated[df_counts_updated['JOBTYPE'] == 'Application']['JOBCOUNTS'],
                 name='Application',
                 marker=go.bar.Marker(
                     color='rgb(55, 83, 109)'
                 )
             ),
             go.Bar(
                 x=df_counts_updated[df_counts_updated['JOBTYPE'] == 'Amendment/Renewal']['TIMESINCESCHEDULEDSTARTDATE'],
                 y=df_counts_updated[df_counts_updated['JOBTYPE'] == 'Amendment/Renewal']['JOBCOUNTS'],
                 name='Amendment/Renewal',
                 marker=go.bar.Marker(
                     color='rgb(26, 118, 255)'
                 )
             )
        ],
        'layout': go.Layout(
            xaxis=dict(
                title='Time Since Scheduled Start Date of Process'
            ),
            yaxis=dict(
                title='Active Business License Jobs'
            ),
            showlegend=True,
            legend=go.layout.Legend(
                x=.75,
                y=1
            )
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