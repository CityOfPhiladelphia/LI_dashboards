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

APP_NAME = os.path.basename(__file__)

print(APP_NAME)

@cache_timeout
@cache.memoize()
def query_data(dataset):
    from app import con
    with con() as con:
        if dataset == 'df_ind':
            sql = 'SELECT * FROM li_dash_overdueinsp_bl'
            df = pd.read_sql_query(sql=sql, con=con)
        elif dataset == 'last_ddl_time':
            sql = "SELECT from_tz(cast(last_ddl_time as timestamp), 'GMT') at TIME zone 'US/Eastern' as LAST_DDL_TIME FROM user_objects WHERE object_name = 'LI_DASH_OVERDUEINSP_BL'"
            df = pd.read_sql_query(sql=sql, con=con)
    return df.to_json(date_format='iso', orient='split')

@cache_timeout
@cache.memoize()
def dataframe(dataset):
    return pd.read_json(query_data(dataset), orient='split')

def get_df_time_since(df):
    df_time_since = df.groupby(['TIMEOVERDUE']).agg({'INSPECTIONOBJECTID': 'count'})
    return df_time_since

def update_layout():
    df = dataframe('df_ind')
    last_ddl_time = dataframe('last_ddl_time')

    df_time_since = get_df_time_since(df)

    licensetype_options_unsorted = []
    for licensetype in df['LICENSETYPE'].unique():
        if str(licensetype) != "nan":
            licensetype_options_unsorted.append({'label': str(licensetype), 'value': licensetype})
    licensetype_options_sorted = sorted(licensetype_options_unsorted, key=lambda k: k['label'])

    inspectionon_options_unsorted = []
    for inspectionon in df['INSPECTIONON'].unique():
        if str(inspectionon) != "nan":
            inspectionon_options_unsorted.append({'label': str(inspectionon), 'value': inspectionon})
    inspectionon_options_sorted = sorted(inspectionon_options_unsorted, key=lambda k: k['label'])

    inspector_options_unsorted = []
    for inspector in df['INSPECTOR'].unique():
        if str(inspector) != "nan":
            inspector_options_unsorted.append({'label': str(inspector), 'value': inspector})
    inspector_options_sorted = sorted(inspector_options_unsorted, key=lambda k: k['label'])

    return html.Div(
        children=[
            html.H1(
                'Overdue Inspections',
                style={'margin-top': '10px'}
            ),
            html.H1(
                '(Business Licenses)',
                style={'margin-bottom': '50px'}
            ),
            html.P(f"Data last updated {last_ddl_time['LAST_DDL_TIME'].iloc[0]}", style = {'text-align': 'center'}),
            html.Div([
                html.Div([
                    html.P('Please Select Date Range (Scheduled Inspection Date)'),
                    dcc.DatePickerRange(
                        id='Man006BL-my-date-picker-range',
                        start_date=datetime(2018, 1, 1),
                        end_date=datetime.now()
                    )
                ], className='five columns'),
                html.Div([
                    html.P('Inspector'),
                    dcc.Dropdown(
                        id='inspector-dropdown',
                        options=inspector_options_sorted,
                        multi=True
                    )
                ], className='five columns'),
            ], className='dashrow filters'),
            html.Div([
                html.Div([
                    html.P('License Type'),
                    dcc.Dropdown(
                        id='licensetype-dropdown',
                        options=licensetype_options_sorted,
                        multi=True
                    ),
                ], className='five columns'),
                html.Div([
                    html.P('Inspection On'),
                    dcc.Dropdown(
                        id='inspectionon-dropdown',
                        options=inspectionon_options_sorted,
                        multi=True
                    ),
                ], className='five columns'),
            ], className='dashrow filters'),
            html.Div([
                html.Div([
                    html.Div([
                        dt.DataTable(
                            rows=[{}],
                            sortable=True,
                            editable=False,
                            selected_row_indices=[],
                            id='Man006BL-count-table'
                        ),
                    ], id='Man006BL-count-table-div'),
                    html.Div([
                        html.A(
                            'Download Data',
                            id='Man006BL-count-table-download-link',
                            download='Man006BL-counts.csv',
                            href='',
                            target='_blank'
                        ),
                    ], style={'text-align': 'right'})
                ], style={'margin-top': '70px', 'margin-bottom': '50px',
                          'margin-left': 'auto', 'margin-right': 'auto', 'float': 'none'},
                   className='ten columns')
            ], className='dashrow'),
            html.Div([
                html.Div([
                    dcc.Graph(
                        id='time-since-piechart',
                        config={
                            'displayModeBar': False
                        },
                        figure=go.Figure(
                          data=[
                              go.Pie(
                                  labels=df_time_since.index,
                                  values=df_time_since['INSPECTIONOBJECTID'],
                                  hoverinfo='label+value+percent',
                                  hole=0.4,
                                  textfont=dict(color='#FFFFFF')
                              )
                          ],
                          layout=go.Layout(title=('Overdue Inspections by How Long They\'ve Been Overdue'))
                        )
                    )
                ], className='twelve columns'),
            ], className='dashrow'),
            html.Div([
                dt.DataTable(
                    rows=[{}],
                    filterable=True,
                    sortable=True,
                    editable=False,
                    selected_row_indices=[],
                    id='Man006BL-table'
                ),
            ], style={'width': '100%', 'margin-left': 'auto', 'margin-right': 'auto'},
                id='Man006BL-table-div'
            ),
            html.Div([
                html.A(
                    'Download Data',
                    id='Man006BL-download-link',
                    download='Man006BL.csv',
                    href='',
                    target='_blank'
                ),
            ], style={'text-align': 'right', 'margin-right': '5%'}),
            html.Details([
                html.Summary('Query Description'),
                html.Div([
                    html.P('Business licenses with inspections scheduled prior to today, but no completed inspection as of today.')
                ])
            ])
        ])

layout = update_layout


def get_data_object(selected_start, selected_end, license_type, inspection_on, inspector):
    df_selected = dataframe('df_ind')
    df_selected = df_selected[(df_selected['SCHEDULEDINSPECTIONDATEFIELD'] >= selected_start) & (df_selected['SCHEDULEDINSPECTIONDATEFIELD'] <= selected_end)]
    if license_type is not None:
        if isinstance(license_type, str):
            df_selected = df_selected[df_selected['LICENSETYPE'] == license_type]
        elif isinstance(license_type, list):
            if len(license_type) > 1:
                df_selected = df_selected[df_selected['LICENSETYPE'].isin(license_type)]
            elif len(license_type) == 1:
                df_selected = df_selected[df_selected['LICENSETYPE'] == license_type[0]]
    if inspection_on is not None:
        if isinstance(inspection_on, str):
            df_selected = df_selected[df_selected['INSPECTIONON'] == inspection_on]
        elif isinstance(inspection_on, list):
            if len(inspection_on) > 1:
                df_selected = df_selected[df_selected['INSPECTIONON'].isin(inspection_on)]
            elif len(inspection_on) == 1:
                df_selected = df_selected[df_selected['INSPECTIONON'] == inspection_on[0]]
    if inspector is not None:
        if isinstance(inspector, str):
            df_selected = df_selected[df_selected['INSPECTOR'] == inspector]
        elif isinstance(inspector, list):
            if len(inspector) > 1:
                df_selected = df_selected[df_selected['INSPECTOR'].isin(inspector)]
            elif len(inspector) == 1:
                df_selected = df_selected[df_selected['INSPECTOR'] == inspector[0]]
    if len(df_selected['DAYSOVERDUE']) > 0:
        df_selected['DAYSOVERDUE'] = df_selected.apply(lambda x: "{:,}".format(x['DAYSOVERDUE']), axis=1)
    return df_selected.drop('SCHEDULEDINSPECTIONDATEFIELD', axis=1)

def count_jobs(selected_start, selected_end, license_type, inspection_on, inspector):
    df_selected = dataframe('df_ind')
    df_selected = df_selected[(df_selected['SCHEDULEDINSPECTIONDATEFIELD'] >= selected_start) & (df_selected['SCHEDULEDINSPECTIONDATEFIELD'] <= selected_end)]
    if license_type is not None:
        if isinstance(license_type, str):
            df_selected = df_selected[df_selected['LICENSETYPE'] == license_type]
        elif isinstance(license_type, list):
            if len(license_type) > 1:
                df_selected = df_selected[df_selected['LICENSETYPE'].isin(license_type)]
            elif len(license_type) == 1:
                df_selected = df_selected[df_selected['LICENSETYPE'] == license_type[0]]
    if inspection_on is not None:
        if isinstance(inspection_on, str):
            df_selected = df_selected[df_selected['INSPECTIONON'] == inspection_on]
        elif isinstance(inspection_on, list):
            if len(inspection_on) > 1:
                df_selected = df_selected[df_selected['INSPECTIONON'].isin(inspection_on)]
            elif len(inspection_on) == 1:
                df_selected = df_selected[df_selected['INSPECTIONON'] == inspection_on[0]]
    if inspector is not None:
        if isinstance(inspector, str):
            df_selected = df_selected[df_selected['INSPECTOR'] == inspector]
        elif isinstance(inspector, list):
            if len(inspector) > 1:
                df_selected = df_selected[df_selected['INSPECTOR'].isin(inspector)]
            elif len(inspector) == 1:
                df_selected = df_selected[df_selected['INSPECTOR'] == inspector[0]]
    df_counts = df_selected.groupby(by=['LICENSETYPE', 'INSPECTIONON'], as_index=False).agg({'INSPECTIONOBJECTID': pd.Series.nunique})
    df_counts = df_counts.rename(columns={'LICENSETYPE': "License Type", 'INSPECTIONON': 'Inspection On', 'INSPECTIONOBJECTID': 'Overdue Inspections'})
    if len(df_counts['Overdue Inspections']) > 0:
        df_counts['Overdue Inspections'] = df_counts.apply(lambda x: "{:,}".format(x['Overdue Inspections']), axis=1)
    return df_counts

#TODO why is this not including high date?


@app.callback(Output('Man006BL-count-table', 'rows'),
              [Input('Man006BL-my-date-picker-range', 'start_date'),
               Input('Man006BL-my-date-picker-range', 'end_date'),
               Input('licensetype-dropdown', 'value'),
               Input('inspectionon-dropdown', 'value'),
               Input('inspector-dropdown', 'value')])
def updatecount_table(start_date, end_date, license_type_val, inspection_on_val, inspector_val):
    df_counts = count_jobs(start_date, end_date, license_type_val, inspection_on_val, inspector_val)
    return df_counts.to_dict('records')

@app.callback(
            Output('Man006BL-count-table-download-link', 'href'),
            [Input('Man006BL-my-date-picker-range', 'start_date'),
             Input('Man006BL-my-date-picker-range', 'end_date'),
             Input('licensetype-dropdown', 'lt_value'),
             Input('inspectionon-dropdown', 'jt_value'),
             Input('inspector-dropdown', 'inspector_value')])
def update_count_table_download_link(start_date, end_date, license_type_val, inspection_on_val, inspector_val):
    df_for_csv = count_jobs(start_date, end_date, license_type_val, inspection_on_val, inspector_val)
    csv_string = df_for_csv.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string

@app.callback(Output('Man006BL-table', 'rows'),
            [Input('Man006BL-my-date-picker-range', 'start_date'),
             Input('Man006BL-my-date-picker-range', 'end_date'),
             Input('licensetype-dropdown', 'value'),
             Input('inspectionon-dropdown', 'value'),
             Input('inspector-dropdown', 'value')])
def update_table(start_date, end_date, license_type_val, inspection_on_val, inspector_val):
    df_ind = get_data_object(start_date, end_date, license_type_val, inspection_on_val, inspector_val)
    return df_ind.to_dict('records')

@app.callback(
            Output('Man006BL-download-link', 'href'),
            [Input('Man006BL-my-date-picker-range', 'start_date'),
             Input('Man006BL-my-date-picker-range', 'end_date'),
             Input('licensetype-dropdown', 'value'),
             Input('inspectionon-dropdown', 'value'),
             Input('inspector-dropdown', 'value')])
def update_table_download_link(start_date, end_date, license_type_val, inspection_on_val, inspector_val):
    df_for_csv = get_data_object(start_date, end_date, license_type_val, inspection_on_val, inspector_val)
    csv_string = df_for_csv.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string