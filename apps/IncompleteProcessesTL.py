import os
import urllib.parse
from datetime import datetime, date

import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as table
import plotly.graph_objs as go
import pandas as pd
from dash.dependencies import Input, Output
import numpy as np

from app import app, cache, cache_timeout

APP_NAME = os.path.basename(__file__)

print(APP_NAME)

@cache_timeout
@cache.memoize()
def query_data(dataset):
    from app import con
    with con() as con:
        if dataset == 'df_ind':
            sql = 'SELECT * FROM li_dash_incompleteprocesses_tl'
            df = pd.read_sql_query(sql=sql, con=con, parse_dates=['SCHEDULEDSTARTDATEFIELD'])
            # Rename the columns to be more readable
            df = (df.rename(columns={'PROCESSID': 'Process ID', 'PROCESSTYPE': 'Process Type', 'JOBNUMBER': 'Job Number',
                                     'JOBTYPE': 'Job Type', 'LICENSETYPE': 'License Type',
                                     'ASSIGNEDSTAFF': 'Assigned Staff',
                                     'NUMASSIGNEDSTAFF': 'Num of Assigned Staff',
                                     'SCHEDULEDSTARTDATE': 'Scheduled Start Date', 'JOBLINK': 'Job Link'})
                  .assign(DateText=lambda x: x['SCHEDULEDSTARTDATEFIELD'].dt.strftime('%b %Y')))
            df['Month Year'] = df['SCHEDULEDSTARTDATEFIELD'].map(lambda dt: dt.date().replace(day=1))
        elif dataset == 'last_ddl_time':
            sql = "SELECT from_tz(cast(last_ddl_time as timestamp), 'GMT') at TIME zone 'US/Eastern' as LAST_DDL_TIME FROM user_objects WHERE object_name = 'LI_DASH_INCOMPLETEPROCESSES_TL'"
            df = pd.read_sql_query(sql=sql, con=con)
    return df.to_json(date_format='iso', orient='split')

@cache_timeout
@cache.memoize()
def dataframe(dataset):
    if dataset == 'df_ind':
        df = pd.read_json(query_data(dataset), orient='split', convert_dates=['SCHEDULEDSTARTDATEFIELD', 'Month Year'])
        df['Month Year'] = df['Month Year'].dt.date
    elif dataset == 'last_ddl_time':
        df = pd.read_json(query_data(dataset), orient='split')
    return df

def update_layout():
    df = dataframe('df_ind')
    last_ddl_time = dataframe('last_ddl_time')

    staff_options_unsorted = [{'label': 'ALL', 'value': 'ALL'}]
    for staff in df['Assigned Staff'].unique():
        staff_options_unsorted.append({'label': str(staff), 'value': staff})
    staff_options_sorted = sorted(staff_options_unsorted, key=lambda k: k['label'])

    process_type_options_unsorted = [{'label': 'All', 'value': 'All'}]
    for pt in df['Process Type'].unique():
        process_type_options_unsorted.append({'label': str(pt), 'value': pt})
    process_type_options_sorted = sorted(process_type_options_unsorted, key=lambda k: k['label'])

    job_type_options_unsorted = [{'label': 'All', 'value': 'All'}]
    for jt in df['Job Type'].unique():
        job_type_options_unsorted.append({'label': str(jt), 'value': jt})
    job_type_options_sorted = sorted(job_type_options_unsorted, key=lambda k: k['label'])

    license_type_options_unsorted = [{'label': 'All', 'value': 'All'}]
    for lt in df['License Type'].unique():
        license_type_options_unsorted.append({'label': str(lt), 'value': lt})
    license_type_options_sorted = sorted(license_type_options_unsorted, key=lambda k: k['label'])

    return html.Div(children=[
                html.H1('Incomplete Processes (Trade Licenses)', style={'text-align': 'center'}),
                html.P(f"Data last updated {last_ddl_time['LAST_DDL_TIME'].iloc[0]}", style = {'text-align': 'center'}),
                html.Div([
                    html.Div([
                        html.P('Scheduled Start Date of Process'),
                        dcc.DatePickerRange(
                            display_format='MMM Y',
                            id='incomplete-processes-tl-date-picker-range',
                            start_date=datetime(2018, 1, 1),
                            end_date=date.today()
                        ),
                    ], className='four columns'),
                    html.Div([
                        html.P('Assigned Staff'),
                        dcc.Dropdown(
                                id='incomplete-processes-tl-staff-dropdown',
                                options=staff_options_sorted,
                                value='ALL'
                        ),
                    ], className='four columns')
                ], className='dashrow filters'),
                html.Div([
                    html.Div([
                        html.P('License Type'),
                        dcc.Dropdown(
                            id='incomplete-processes-tl-license-type-dropdown',
                            options=license_type_options_sorted,
                            value='All'
                        ),
                    ], className='twelve columns')
                ], className='dashrow filters'),
                html.Div([
                    html.Div([
                        html.P('Job Type'),
                        dcc.Dropdown(
                            id='incomplete-processes-tl-job-type-dropdown',
                            options=job_type_options_sorted,
                            value='All'
                        ),
                    ], className='four columns'),
                    html.Div([
                        html.P('Process Type'),
                        dcc.Dropdown(
                            id='incomplete-processes-tl-process-type-dropdown',
                            options=process_type_options_sorted,
                            value='All'
                        ),
                    ], className='four columns')
                ], className='dashrow filters'),
                html.Div([
                    html.Div([
                        dcc.Graph(
                            id='incomplete-processes-tl-graph',
                            config={
                                'displayModeBar': False
                            },
                            figure=go.Figure(
                                data=[],
                                layout=go.Layout(
                                    title='Incomplete Processes by Scheduled Start Month',
                                    yaxis=dict(
                                        title='Incomplete Processes'
                                    )
                                )
                            )
                        )
                    ], className='twelve columns'),
                ], className='dashrow'),
                html.Div([
                    html.Div([
                        html.H3('Incomplete Processes by Assigned Staff and Process Type', style={'text-align': 'center'}),
                        html.Div([
                            table.DataTable(
                                rows=[{}],
                                editable=False,
                                sortable=True,
                                filterable=True,
                                id='incomplete-processes-tl-count-table'
                            ),
                        ], style={'text-align': 'center'},
                           id='incomplete-processes-tl-count-table-div'
                        ),
                        html.Div([
                            html.A(
                                'Download Data',
                                id='incomplete-processes-tl-count-table-download-link',
                                download='incomplete-processes-tl-counts.csv',
                                href='',
                                target='_blank',
                            )
                        ], style={'text-align': 'right'})
                    ], style={'margin-top': '50px', 'margin-bottom': '50px'})
                ], className='dashrow'),
                html.Div([
                    html.Div([
                        html.H3('Incomplete Processes', style={'text-align': 'center'}),
                        html.Div([
                            table.DataTable(
                                rows=[{}],
                                editable=False,
                                sortable=True,
                                filterable=True,
                                id='incomplete-processes-tl-ind-records-table'
                            ),
                        ], style={'text-align': 'center'},
                            id='incomplete-processes-tl-ind-records-table-div'
                        ),
                        html.Div([
                            html.A(
                                'Download Data',
                                id='incomplete-processes-tl-ind-records-table-download-link',
                                download='incomplete-processes-tl-ind-records.csv',
                                href='',
                                target='_blank',
                            )
                        ], style={'text-align': 'right'})
                    ], style={'margin-top': '50px', 'margin-bottom': '50px'})
                ], className='dashrow'),
                html.Details([
                    html.Summary('Query Description'),
                    html.Div([
                        html.P(
                            'Incomplete trade license processes by assigned staff member.')
                    ])
                ])
            ])

layout = update_layout

def update_graph_data(selected_start, selected_end, selected_staff, selected_process_type, selected_job_type, selected_license_type):
    df_selected = dataframe('df_ind')

    months = df_selected['Month Year'].unique()
    months.sort()

    selected_months = months[(months >= datetime.strptime(selected_start, "%Y-%m-%d").date()) & (months <= datetime.strptime(selected_end, "%Y-%m-%d").date())]

    if selected_staff != "ALL":
        df_selected = df_selected[(df_selected['Assigned Staff'] == selected_staff)]
    if selected_process_type != "All":
        df_selected = df_selected[(df_selected['Process Type'] == selected_process_type)]
    if selected_job_type != "All":
        df_selected = df_selected[(df_selected['Job Type'] == selected_job_type)]
    if selected_license_type != "All":
        df_selected = df_selected[(df_selected['License Type'] == selected_license_type)]

    df_selected = (df_selected.loc[(df_selected['SCHEDULEDSTARTDATEFIELD'] >= selected_start) & (df_selected['SCHEDULEDSTARTDATEFIELD'] <= selected_end)]
                   .groupby(['Month Year', 'DateText']).agg({'Process ID': 'count'})
                   .reset_index()
                   .rename(columns={'Process ID': 'Incomplete Processes'}))
    for month in selected_months:
        if month not in df_selected['Month Year'].values:
            df_missing_month = pd.DataFrame([[month, month.strftime('%b %Y'), 0]], columns=['Month Year', 'DateText', 'Incomplete Processes'])
            df_selected = df_selected.append(df_missing_month, ignore_index=True)
    return df_selected.sort_values(by='Month Year', ascending=False)


def update_counts_table_data(selected_start, selected_end, selected_staff, selected_process_type, selected_job_type, selected_license_type):
    df_selected = dataframe('df_ind')

    if selected_staff != "ALL":
        df_selected = df_selected[(df_selected['Assigned Staff'] == selected_staff)]
    if selected_process_type != "All":
        df_selected = df_selected[(df_selected['Process Type'] == selected_process_type)]
    if selected_job_type != "All":
        df_selected = df_selected[(df_selected['Job Type'] == selected_job_type)]
    if selected_license_type != "All":
        df_selected = df_selected[(df_selected['License Type'] == selected_license_type)]

    df_selected = (df_selected.loc[(df_selected['SCHEDULEDSTARTDATEFIELD'] >= selected_start) & (df_selected['SCHEDULEDSTARTDATEFIELD'] <= selected_end)]
                   .groupby(['Assigned Staff', 'Process Type']).agg({'Process ID': 'count'})
                   .reset_index()
                   .rename(columns={'Process ID': 'Incomplete Processes'})
                   .sort_values(by=['Assigned Staff', 'Process Type']))
    return df_selected[['Assigned Staff', 'Process Type', 'Incomplete Processes']]

def update_ind_records_table_data(selected_start, selected_end, selected_staff, selected_process_type, selected_job_type, selected_license_type):
    df_selected = dataframe('df_ind')

    if selected_staff != "ALL":
        df_selected = df_selected[(df_selected['Assigned Staff'] == selected_staff)]
    if selected_process_type != "All":
        df_selected = df_selected[(df_selected['Process Type'] == selected_process_type)]
    if selected_job_type != "All":
        df_selected = df_selected[(df_selected['Job Type'] == selected_job_type)]
    if selected_license_type != "All":
        df_selected = df_selected[(df_selected['License Type'] == selected_license_type)]

    df_selected = (df_selected.loc[(df_selected['SCHEDULEDSTARTDATEFIELD'] >= selected_start) & (df_selected['SCHEDULEDSTARTDATEFIELD'] <= selected_end)]
                   .sort_values(by='SCHEDULEDSTARTDATEFIELD'))
    return df_selected.drop(['Process ID', 'SCHEDULEDSTARTDATEFIELD', 'Month Year', 'DateText'], axis=1)



@app.callback(
    Output('incomplete-processes-tl-graph', 'figure'),
    [Input('incomplete-processes-tl-date-picker-range', 'start_date'),
     Input('incomplete-processes-tl-date-picker-range', 'end_date'),
     Input('incomplete-processes-tl-staff-dropdown', 'value'),
     Input('incomplete-processes-tl-process-type-dropdown', 'value'),
     Input('incomplete-processes-tl-job-type-dropdown', 'value'),
     Input('incomplete-processes-tl-license-type-dropdown', 'value')])
def update_graph(start_date, end_date, staff, process_type, job_type, license_type):
    df_results = update_graph_data(start_date, end_date, staff, process_type, job_type, license_type)
    return {
        'data': [
            go.Scatter(
                x=df_results['Month Year'],
                y=df_results['Incomplete Processes'],
                mode='lines',
                text=df_results['DateText'],
                hoverinfo='text+y',
                line=dict(
                    shape='spline',
                    color='rgb(26, 118, 255)'
                ),
                name='Incomplete Processes'
            )
        ],
        'layout': go.Layout(
                title='Incomplete Processes by Scheduled Start Month',
                yaxis=dict(
                    title='Incomplete Processes',
                    range=[0, df_results['Incomplete Processes'].max() + (df_results['Incomplete Processes'].max() / 50)]
                )
        )
    }


@app.callback(
    Output('incomplete-processes-tl-count-table', 'rows'),
    [Input('incomplete-processes-tl-date-picker-range', 'start_date'),
     Input('incomplete-processes-tl-date-picker-range', 'end_date'),
     Input('incomplete-processes-tl-staff-dropdown', 'value'),
     Input('incomplete-processes-tl-process-type-dropdown', 'value'),
     Input('incomplete-processes-tl-job-type-dropdown', 'value'),
     Input('incomplete-processes-tl-license-type-dropdown', 'value')])
def update_count_table(start_date, end_date, staff, process_type, job_type, license_type):
    df_results = update_counts_table_data(start_date, end_date, staff, process_type, job_type, license_type)
    return df_results.to_dict('records')


@app.callback(
    Output('incomplete-processes-tl-count-table-download-link', 'href'),
    [Input('incomplete-processes-tl-date-picker-range', 'start_date'),
     Input('incomplete-processes-tl-date-picker-range', 'end_date'),
     Input('incomplete-processes-tl-staff-dropdown', 'value'),
     Input('incomplete-processes-tl-process-type-dropdown', 'value'),
     Input('incomplete-processes-tl-job-type-dropdown', 'value'),
     Input('incomplete-processes-tl-license-type-dropdown', 'value')])
def update_count_table_download_link(start_date, end_date, staff, process_type, job_type, license_type):
    df_results = update_counts_table_data(start_date, end_date, staff, process_type, job_type, license_type)
    csv_string = df_results.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string


@app.callback(
    Output('incomplete-processes-tl-ind-records-table', 'rows'),
    [Input('incomplete-processes-tl-date-picker-range', 'start_date'),
     Input('incomplete-processes-tl-date-picker-range', 'end_date'),
     Input('incomplete-processes-tl-staff-dropdown', 'value'),
     Input('incomplete-processes-tl-process-type-dropdown', 'value'),
     Input('incomplete-processes-tl-job-type-dropdown', 'value'),
     Input('incomplete-processes-tl-license-type-dropdown', 'value')])
def update_ind_records_table(start_date, end_date, staff, process_type, job_type, license_type):
    df_results = update_ind_records_table_data(start_date, end_date, staff, process_type, job_type, license_type)
    return df_results.to_dict('records')

@app.callback(
    Output('incomplete-processes-tl-ind-records-table-download-link', 'href'),
    [Input('incomplete-processes-tl-date-picker-range', 'start_date'),
     Input('incomplete-processes-tl-date-picker-range', 'end_date'),
     Input('incomplete-processes-tl-staff-dropdown', 'value'),
     Input('incomplete-processes-tl-process-type-dropdown', 'value'),
     Input('incomplete-processes-tl-job-type-dropdown', 'value'),
     Input('incomplete-processes-tl-license-type-dropdown', 'value')])
def update_ind_records_table_download_link(start_date, end_date, staff, process_type, job_type, license_type):
    df_results = update_ind_records_table_data(start_date, end_date, staff, process_type, job_type, license_type)
    csv_string = df_results.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string