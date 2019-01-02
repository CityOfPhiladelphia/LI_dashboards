import os
import urllib.parse
from datetime import datetime

import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import plotly.graph_objs as go
import pandas as pd
from dash.dependencies import Input, Output
from datetime import datetime

from app import app, cache, cache_timeout

APP_NAME = os.path.basename(__file__)

print(APP_NAME)

@cache_timeout
@cache.memoize()
def query_data(dataset):
    from app import con
    with con() as con:
        if dataset == 'df_ind':
            sql = 'SELECT * FROM li_dash_jobvolsbysubtype_tl'
            df = pd.read_sql_query(sql=sql, con=con, parse_dates=['JOBCREATEDDATEFIELD'])
        elif dataset == 'last_ddl_time':
            sql = "SELECT from_tz(cast(last_ddl_time as timestamp), 'GMT') at TIME zone 'US/Eastern' as LAST_DDL_TIME FROM user_objects WHERE object_name = 'LI_DASH_JOBVOLSBYSUBTYPE_TL'"
            df = pd.read_sql_query(sql=sql, con=con)
    return df.to_json(date_format='iso', orient='split')


def dataframe(dataset):
    return pd.read_json(query_data(dataset), orient='split')

def update_layout():
    df = dataframe('df_ind')
    last_ddl_time = dataframe('last_ddl_time')

    username_options_unsorted = []
    df_staff = df[df['CREATEDBYTYPE'] == 'Staff']
    for username in df_staff['CREATEDBYUSERNAME'].unique():
        username_options_unsorted.append({'label': str(username), 'value': username})
    username_options_sorted = sorted(username_options_unsorted, key=lambda k: k['label'])

    return html.Div(
        children=[
            html.H1(
                'Job Volumes by Submission Type',
                style={'margin-top': '10px'}
            ),
            html.H1(
                '(Trade Licenses)',
                style={'margin-bottom': '50px'}
            ),
            html.P(f"Data last updated {last_ddl_time['LAST_DDL_TIME'].iloc[0]}", style = {'text-align': 'center'}),
            html.Div([
                html.Div([
                    html.P('Please Select Date Range (Job Created Date)'),
                    dcc.DatePickerRange(
                        id='my-date-picker-range',
                        start_date=datetime(2018, 1, 1),
                        end_date=datetime.now()
                    ),
                ], className='four columns'),
                html.Div([
                    html.P('Filter by Username (Staff only)'),
                    dcc.Dropdown(
                        id='username-dropdown',
                        options=username_options_sorted,
                        multi=True
                    ),
                ], className='five columns')
            ], className='dashrow filters'),
            html.Div([
                html.Div([
                    html.Div([
                        dt.DataTable(
                            rows=[{}],
                            sortable=True,
                            editable=False,
                            selected_row_indices=[],
                            id='Man004TL-counttable'
                        ),
                    ], id='Man004TL-counttable-div')
                ], style={'margin-top': '70px', 'margin-bottom': '50px',
                          'margin-left': 'auto', 'margin-right': 'auto', 'float': 'none'},
                    className='nine columns')
            ], className='dashrow'),
            html.Div([
                html.Div([
                    html.Div([
                        dt.DataTable(
                            rows=[{}],
                            filterable=True,
                            sortable=True,
                            editable=False,
                            selected_row_indices=[],
                            id='Man004TL-table'
                        )
                    ]),
                    html.Div([
                        html.A(
                            'Download Data',
                            id='Man004TL-download-link',
                            download='Man004BL.csv',
                            href='',
                            target='_blank',
                        )
                    ], style={'text-align': 'right'})
                ], style={'margin-top': '70px', 'margin-bottom': '50px'})
            ], className='dashrow'),
            html.Details([
                html.Summary('Query Description'),
                html.Div([
                    html.P('All approved trade license amend/renew and application jobs, how they were submitted (online, '
                           'revenue, or staff), and who they were submitted by.'),
                    html.P('We determine how a job was submitted (online, revenue, or staff) based on the username who created it:'),
                    html.Ul(children=[
                        html.Li('Online: If the username contains a number or equals "PPG User"'),
                        html.Li('Revenue: If the username equals "POSSE system power user"'),
                        html.Li('Staff: If the username doesn\'t meet one of the other two conditions')
                    ])
                ])
            ])
        ])

layout = update_layout

def get_data_object(selected_start, selected_end, username):
    df_selected = dataframe('df_ind')

    df_selected = df_selected[(df_selected['JOBCREATEDDATEFIELD'] >= selected_start) & (df_selected['JOBCREATEDDATEFIELD'] <= selected_end)]
    if username is not None:
        if isinstance(username, str):
            df_selected = df_selected[df_selected['CREATEDBYUSERNAME'] == username]
        elif isinstance(username, list):
            if len(username) > 1:
                df_selected = df_selected[df_selected['CREATEDBYUSERNAME'].isin(username)]
            elif len(username) == 1:
                df_selected = df_selected[df_selected['CREATEDBYUSERNAME'] == username[0]]
    return df_selected.drop('JOBCREATEDDATEFIELD', axis=1)


def count_jobs(selected_start, selected_end, username):
    df_selected = dataframe('df_ind')

    df_count_selected = df_selected[(df_selected['JOBCREATEDDATEFIELD'] >= selected_start) & (df_selected['JOBCREATEDDATEFIELD'] <= selected_end)]
    if username is not None:
        if isinstance(username, str):
            df_count_selected = df_count_selected[df_count_selected['CREATEDBYUSERNAME'] == username]
        elif isinstance(username, list):
            if len(username) > 1:
                df_count_selected = df_count_selected[df_count_selected['CREATEDBYUSERNAME'].isin(username)]
            elif len(username) == 1:
                df_count_selected = df_count_selected[df_count_selected['CREATEDBYUSERNAME'] == username[0]]
    df_counter = df_count_selected.groupby(by=['CREATEDBYTYPE', 'JOBTYPE'], as_index=False).agg({'JOBOBJECTID': pd.Series.nunique})
    df_counter = df_counter.rename(columns={'CREATEDBYTYPE': "Job Submission Type", 'JOBTYPE': 'Job Type', 'JOBOBJECTID': 'Count of Jobs Submitted'})
    if len(df_counter['Count of Jobs Submitted']) > 0:
        df_counter['Count of Jobs Submitted'] = df_counter.apply(lambda x: "{:,}".format(x['Count of Jobs Submitted']), axis=1)
    return df_counter

#TODO why is this not including high date?

@app.callback(
    Output('Man004TL-counttable', 'rows'),
    [Input('my-date-picker-range', 'start_date'),
     Input('my-date-picker-range', 'end_date'),
     Input('username-dropdown', 'value')])
def updatecount_table(start_date, end_date, username_val):
    df_counts = count_jobs(start_date, end_date, username_val)
    return df_counts.to_dict('records')


@app.callback(
    Output('Man004TL-download-link', 'href'),
    [Input('my-date-picker-range', 'start_date'),
     Input('my-date-picker-range', 'end_date'),
     Input('username-dropdown', 'value')])
def update_download_link(start_date, end_date, username_val):
    df_inv = get_data_object(start_date, end_date, username_val)
    csv_string = df_inv.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string

@app.callback(
    Output('Man004TL-table', 'rows'),
    [Input('my-date-picker-range', 'start_date'),
     Input('my-date-picker-range', 'end_date'),
     Input('username-dropdown', 'value')])
def update_table(start_date, end_date, username_val):
    df_inv = get_data_object(start_date, end_date, username_val)
    return df_inv.to_dict('records')
