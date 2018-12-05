import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import plotly.graph_objs as go
import pandas as pd
from dash.dependencies import Input, Output
from datetime import datetime
import urllib.parse

from app import app, con


print("Man004TLJobVolumesBySubmissionType.py")

with con() as con:
    sql = 'SELECT * FROM li_dash_jobvolsbysubtype_tl'
    df_table = pd.read_sql_query(sql=sql, con=con)
    df_table['JOBCREATEDDATEFIELD'] = pd.to_datetime(df_table['JOBCREATEDDATEFIELD'])

username_options_unsorted = []
df_staff = df_table[df_table['CREATEDBYTYPE'] == 'Staff']
for username in df_staff['CREATEDBYUSERNAME'].unique():
    username_options_unsorted.append({'label': str(username), 'value': username})
username_options_sorted = sorted(username_options_unsorted, key=lambda k: k['label'])


def get_data_object(selected_start, selected_end, username):
    df_selected = df_table[(df_table['JOBCREATEDDATEFIELD'] >= selected_start)&(df_table['JOBCREATEDDATEFIELD'] <= selected_end)]
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
    df_count_selected = df_table[(df_table['JOBCREATEDDATEFIELD'] >= selected_start) & (df_table['JOBCREATEDDATEFIELD'] <= selected_end)]
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

layout = html.Div(
    children=[
        html.H1(
            'Job Volumes by Submission Type',
            style={'margin-top': '10px'}
        ),
        html.H1(
            '(Trade Licenses)',
            style={'margin-bottom': '50px'}
        ),
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
                        row_selectable=True,
                        sortable=True,
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
                        row_selectable=True,
                        filterable=True,
                        sortable=True,
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
        ], className='dashrow')
    ])

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
