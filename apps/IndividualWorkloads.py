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
            sql = 'SELECT * FROM li_dash_indworkloads'
            df = pd.read_sql_query(sql=sql, con=con, parse_dates=['DATECOMPLETEDFIELD'])
            # Rename the columns to be more readable
            df = (df.rename(columns={'PROCESSID': 'Process ID', 'PROCESSTYPE': 'Process Type', 'JOBNUMBER': 'Job Number',
                                     'JOBTYPE': 'Job Type', 'LICENSEKIND': 'Kind of License',
                                     'LICENSETYPE': 'License Type', 'PERSON': 'Person',
                                     'SCHEDULEDSTARTDATE': 'Scheduled Start Date', 'DATECOMPLETED': 'Date Completed',
                                     'DURATION': 'Duration (days)', 'JOBLINK': 'Job Link'})
                  .assign(DateText=lambda x: x['DATECOMPLETEDFIELD'].dt.strftime('%b %Y')))
            df['Month Year'] = df['DATECOMPLETEDFIELD'].map(lambda dt: dt.date().replace(day=1))
        elif dataset == 'last_ddl_time':
            sql = 'SELECT SCN_TO_TIMESTAMP(MAX(ora_rowscn)) last_ddl_time FROM LI_DASH_INDWORKLOADS'
            df = pd.read_sql_query(sql=sql, con=con)
    return df.to_json(date_format='iso', orient='split')

@cache_timeout
@cache.memoize()
def dataframe(dataset):
    if dataset == 'df_ind':
        df = pd.read_json(query_data(dataset), orient='split', convert_dates=['DATECOMPLETEDFIELD', 'Month Year'])
        df['Month Year'] = df['Month Year'].dt.date
    elif dataset == 'last_ddl_time':
        df = pd.read_json(query_data(dataset), orient='split')
    return df

def update_layout():
    df = dataframe('df_ind')
    last_ddl_time = dataframe('last_ddl_time')

    person_options_unsorted = [{'label': 'All', 'value': 'All'}]
    for person in df['Person'].unique():
        person_options_unsorted.append({'label': str(person), 'value': person})
    person_options_sorted = sorted(person_options_unsorted, key=lambda k: k['label'])

    process_type_options_unsorted = [{'label': 'All', 'value': 'All'}]
    for pt in df['Process Type'].unique():
        process_type_options_unsorted.append({'label': str(pt), 'value': pt})
    process_type_options_sorted = sorted(process_type_options_unsorted, key=lambda k: k['label'])

    job_type_options_unsorted = [{'label': 'All', 'value': 'All'}]
    for jt in df['Job Type'].unique():
        job_type_options_unsorted.append({'label': str(jt), 'value': jt})
    job_type_options_sorted = sorted(job_type_options_unsorted, key=lambda k: k['label'])

    license_kind_options_unsorted = [{'label': 'All', 'value': 'All'}]
    for lt in df['Kind of License'].unique():
        license_kind_options_unsorted.append({'label': str(lt), 'value': lt})
    license_kind_options_sorted = sorted(license_kind_options_unsorted, key=lambda k: k['label'])

    license_type_options_unsorted = [{'label': 'All', 'value': 'All'}]
    for lt in df['License Type'].unique():
        license_type_options_unsorted.append({'label': str(lt), 'value': lt})
    license_type_options_sorted = sorted(license_type_options_unsorted, key=lambda k: k['label'])

    return html.Div(children=[
                html.H1('Individual Workloads', style={'text-align': 'center'}),
                html.P(f"Data last updated {last_ddl_time['LAST_DDL_TIME'].iloc[0]}", style = {'text-align': 'center'}),
                html.Div([
                    html.Div([
                        html.P('Process Completion Date'),
                        dcc.DatePickerRange(
                            display_format='MMM Y',
                            id='ind-workloads-date-picker-range',
                            start_date=datetime(2018, 1, 1),
                            end_date=date.today()
                        ),
                    ], className='four columns'),
                    html.Div([
                        html.P('Person'),
                        dcc.Dropdown(
                                id='ind-workloads-person-dropdown',
                                options=person_options_sorted,
                                value='All'
                        ),
                    ], className='four columns')
                ], className='dashrow filters'),
                html.Div([
                    html.Div([
                        html.P('Kind of License'),
                        dcc.Dropdown(
                            id='ind-workloads-license-kind-dropdown',
                            options=license_kind_options_sorted,
                            value='All'
                        ),
                    ], className='four columns'),
                    html.Div([
                        html.P('License Type'),
                        dcc.Dropdown(
                            id='ind-workloads-license-type-dropdown',
                            options=license_type_options_sorted,
                            value='All'
                        ),
                    ], className='eight columns')
                ], className='dashrow filters'),
                html.Div([
                    html.Div([
                        html.P('Job Type'),
                        dcc.Dropdown(
                            id='ind-workloads-job-type-dropdown',
                            options=job_type_options_sorted,
                            value='All'
                        ),
                    ], className='four columns'),
                    html.Div([
                        html.P('Process Type'),
                        dcc.Dropdown(
                            id='ind-workloads-process-type-dropdown',
                            options=process_type_options_sorted,
                            value='All'
                        ),
                    ], className='four columns')
                ], className='dashrow filters'),
                html.Div([
                    html.Div([
                        dcc.Graph(
                            id='ind-workloads-graph',
                            config={
                                'displayModeBar': False
                            },
                            figure=go.Figure(
                                data=[],
                                layout=go.Layout(
                                    title='Processes Completed by Month',
                                    yaxis=dict(
                                        title='Processes Completed'
                                    )
                                )
                            )
                        )
                    ], className='twelve columns'),
                ], className='dashrow'),
                html.Div([
                    html.Div([
                        html.H3('Processes Completed by Person and Process Type', style={'text-align': 'center'}),
                        html.Div([
                            table.DataTable(
                                rows=[{}],
                                editable=False,
                                sortable=True,
                                filterable=True,
                                id='ind-workloads-count-table'
                            ),
                        ], style={'text-align': 'center'},
                           id='ind-workloads-count-table-div'
                        ),
                        html.Div([
                            html.A(
                                'Download Data',
                                id='ind-workloads-count-table-download-link',
                                download='ind-workloads-counts.csv',
                                href='',
                                target='_blank',
                            )
                        ], style={'text-align': 'right'})
                    ], style={'margin-top': '50px', 'margin-bottom': '50px'})
                ], className='dashrow'),
                html.Div([
                    html.Div([
                        html.H3('Processes', style={'text-align': 'center'}),
                        html.Div([
                            table.DataTable(
                                rows=[{}],
                                editable=False,
                                sortable=True,
                                filterable=True,
                                id='ind-workloads-ind-records-table'
                            ),
                        ], style={'text-align': 'center'},
                            id='ind-workloads-ind-records-table-div'
                        ),
                        html.Div([
                            html.A(
                                'Download Data',
                                id='ind-workloads-ind-records-table-download-link',
                                download='ind-workloads-ind-records.csv',
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
                            'Processes completed by staff members in the last 13 months.')
                    ])
                ])
            ])

layout = update_layout

def update_graph_data(selected_start, selected_end, selected_person, selected_process_type, selected_job_type, selected_license_kind, selected_license_type):
    df_selected = dataframe('df_ind')

    months = df_selected['Month Year'].unique()
    months.sort()

    selected_months = months[(months >= datetime.strptime(selected_start, "%Y-%m-%d").date()) & (months <= datetime.strptime(selected_end, "%Y-%m-%d").date())]

    if selected_person != "All":
        df_selected = df_selected[(df_selected['Person'] == selected_person)]
    if selected_process_type != "All":
        df_selected = df_selected[(df_selected['Process Type'] == selected_process_type)]
    if selected_job_type != "All":
        df_selected = df_selected[(df_selected['Job Type'] == selected_job_type)]
    if selected_license_kind != "All":
        df_selected = df_selected[(df_selected['Kind of License'] == selected_license_kind)]
    if selected_license_type != "All":
        df_selected = df_selected[(df_selected['License Type'] == selected_license_type)]

    df_selected = (df_selected.loc[(df_selected['DATECOMPLETEDFIELD'] >= selected_start) & (df_selected['DATECOMPLETEDFIELD'] <= selected_end)]
                   .groupby(['Month Year', 'DateText']).agg({'Process ID': 'count'})
                   .reset_index()
                   .rename(columns={'Process ID': 'Processes Completed'}))
    for month in selected_months:
        if month not in df_selected['Month Year'].values:
            df_missing_month = pd.DataFrame([[month, month.strftime('%b %Y'), 0]], columns=['Month Year', 'DateText', 'Processes Completed'])
            df_selected = df_selected.append(df_missing_month, ignore_index=True)
    return df_selected.sort_values(by='Month Year', ascending=False)


def update_counts_table_data(selected_start, selected_end, selected_person, selected_process_type, selected_job_type, selected_license_kind, selected_license_type):
    df_selected = dataframe('df_ind')

    if selected_person != "All":
        df_selected = df_selected[(df_selected['Person'] == selected_person)]
    if selected_process_type != "All":
        df_selected = df_selected[(df_selected['Process Type'] == selected_process_type)]
    if selected_job_type != "All":
        df_selected = df_selected[(df_selected['Job Type'] == selected_job_type)]
    if selected_license_kind != "All":
        df_selected = df_selected[(df_selected['Kind of License'] == selected_license_kind)]
    if selected_license_type != "All":
        df_selected = df_selected[(df_selected['License Type'] == selected_license_type)]

    df_selected = (df_selected.loc[(df_selected['DATECOMPLETEDFIELD'] >= selected_start) & (df_selected['DATECOMPLETEDFIELD'] <= selected_end)]
                   .groupby(['Person', 'Process Type']).agg({'Process ID': 'count', 'Duration (days)': 'sum'})
                   .reset_index()
                   .rename(columns={'Process ID': 'Processes Completed'})
                   .sort_values(by=['Person', 'Process Type']))
    df_selected['Avg. Duration (days)'] = (df_selected['Duration (days)'] / df_selected['Processes Completed']).round(0)
    return df_selected[['Person', 'Process Type', 'Processes Completed', 'Avg. Duration (days)']]

def update_ind_records_table_data(selected_start, selected_end, selected_person, selected_process_type, selected_job_type, selected_license_kind, selected_license_type):
    df_selected = dataframe('df_ind')

    if selected_person != "All":
        df_selected = df_selected[(df_selected['Person'] == selected_person)]
    if selected_process_type != "All":
        df_selected = df_selected[(df_selected['Process Type'] == selected_process_type)]
    if selected_job_type != "All":
        df_selected = df_selected[(df_selected['Job Type'] == selected_job_type)]
    if selected_license_kind != "All":
        df_selected = df_selected[(df_selected['Kind of License'] == selected_license_kind)]
    if selected_license_type != "All":
        df_selected = df_selected[(df_selected['License Type'] == selected_license_type)]

    df_selected = (df_selected.loc[(df_selected['DATECOMPLETEDFIELD'] >= selected_start) & (df_selected['DATECOMPLETEDFIELD'] <= selected_end)]
                   .sort_values(by='DATECOMPLETEDFIELD'))
    df_selected['Duration (days)'] = df_selected['Duration (days)'].round(2).map('{:,.2f}'.format)
    return df_selected.drop(['Process ID', 'DATECOMPLETEDFIELD', 'Month Year', 'DateText'], axis=1)

def update_license_type_dropdown(selected_license_kind):
    df_selected = dataframe('df_ind')

    if selected_license_kind != "All":
        df_selected = df_selected[(df_selected['Kind of License'] == selected_license_kind)]
    license_type_options_unsorted = [{'label': 'All', 'value': 'All'}]
    for lt in df_selected['License Type'].unique():
        license_type_options_unsorted.append({'label': str(lt), 'value': lt})
    return sorted(license_type_options_unsorted, key=lambda k: k['label'])

def update_process_type_dropdown(selected_license_kind):
    df_selected = dataframe('df_ind')

    if selected_license_kind != "All":
        df_selected = df_selected[(df_selected['Kind of License'] == selected_license_kind)]
    process_type_options_unsorted = [{'label': 'All', 'value': 'All'}]
    for lt in df_selected['Process Type'].unique():
        process_type_options_unsorted.append({'label': str(lt), 'value': lt})
    return sorted(process_type_options_unsorted, key=lambda k: k['label'])



@app.callback(
    Output('ind-workloads-graph', 'figure'),
    [Input('ind-workloads-date-picker-range', 'start_date'),
     Input('ind-workloads-date-picker-range', 'end_date'),
     Input('ind-workloads-person-dropdown', 'value'),
     Input('ind-workloads-process-type-dropdown', 'value'),
     Input('ind-workloads-job-type-dropdown', 'value'),
     Input('ind-workloads-license-kind-dropdown', 'value'),
     Input('ind-workloads-license-type-dropdown', 'value')])
def update_graph(start_date, end_date, person, process_type, job_type, license_kind, license_type):
    df_results = update_graph_data(start_date, end_date, person, process_type, job_type, license_kind, license_type)
    return {
        'data': [
            go.Scatter(
                x=df_results['Month Year'],
                y=df_results['Processes Completed'],
                mode='lines',
                text=df_results['DateText'],
                hoverinfo='text+y',
                line=dict(
                    shape='spline',
                    color='rgb(26, 118, 255)'
                ),
                name='Processes Completed'
            )
        ],
        'layout': go.Layout(
                title='Processes Completed by Month',
                yaxis=dict(
                    title='Processes Completed',
                    range=[0, df_results['Processes Completed'].max() + (df_results['Processes Completed'].max() / 50)]
                )
        )
    }


@app.callback(
    Output('ind-workloads-count-table', 'rows'),
    [Input('ind-workloads-date-picker-range', 'start_date'),
     Input('ind-workloads-date-picker-range', 'end_date'),
     Input('ind-workloads-person-dropdown', 'value'),
     Input('ind-workloads-process-type-dropdown', 'value'),
     Input('ind-workloads-job-type-dropdown', 'value'),
     Input('ind-workloads-license-kind-dropdown', 'value'),
     Input('ind-workloads-license-type-dropdown', 'value')])
def update_count_table(start_date, end_date, person, process_type, job_type, license_kind, license_type):
    df_results = update_counts_table_data(start_date, end_date, person, process_type, job_type, license_kind, license_type)
    return df_results.to_dict('records')


@app.callback(
    Output('ind-workloads-count-table-download-link', 'href'),
    [Input('ind-workloads-date-picker-range', 'start_date'),
     Input('ind-workloads-date-picker-range', 'end_date'),
     Input('ind-workloads-person-dropdown', 'value'),
     Input('ind-workloads-process-type-dropdown', 'value'),
     Input('ind-workloads-job-type-dropdown', 'value'),
     Input('ind-workloads-license-kind-dropdown', 'value'),
     Input('ind-workloads-license-type-dropdown', 'value')])
def update_count_table_download_link(start_date, end_date, person, process_type, job_type, license_kind, license_type):
    df_results = update_counts_table_data(start_date, end_date, person, process_type, job_type, license_kind, license_type)
    csv_string = df_results.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string


@app.callback(
    Output('ind-workloads-ind-records-table', 'rows'),
    [Input('ind-workloads-date-picker-range', 'start_date'),
     Input('ind-workloads-date-picker-range', 'end_date'),
     Input('ind-workloads-person-dropdown', 'value'),
     Input('ind-workloads-process-type-dropdown', 'value'),
     Input('ind-workloads-job-type-dropdown', 'value'),
     Input('ind-workloads-license-kind-dropdown', 'value'),
     Input('ind-workloads-license-type-dropdown', 'value')])
def update_ind_records_table(start_date, end_date, person, process_type, job_type, license_kind, license_type):
    df_results = update_ind_records_table_data(start_date, end_date, person, process_type, job_type, license_kind, license_type)
    return df_results.to_dict('records')

@app.callback(
    Output('ind-workloads-ind-records-table-download-link', 'href'),
    [Input('ind-workloads-date-picker-range', 'start_date'),
     Input('ind-workloads-date-picker-range', 'end_date'),
     Input('ind-workloads-person-dropdown', 'value'),
     Input('ind-workloads-process-type-dropdown', 'value'),
     Input('ind-workloads-job-type-dropdown', 'value'),
     Input('ind-workloads-license-kind-dropdown', 'value'),
     Input('ind-workloads-license-type-dropdown', 'value')])
def update_ind_records_table_download_link(start_date, end_date, person, process_type, job_type, license_kind, license_type):
    df_results = update_ind_records_table_data(start_date, end_date, person, process_type, job_type, license_kind, license_type)
    csv_string = df_results.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string

@app.callback(
    Output('ind-workloads-license-type-dropdown', 'options'),
    [Input('ind-workloads-license-kind-dropdown', 'value')])
def update_licensetype_dropdown(license_kind):
    return update_license_type_dropdown(license_kind)

@app.callback(
    Output('ind-workloads-process-type-dropdown', 'options'),
    [Input('ind-workloads-license-kind-dropdown', 'value')])
def update_processtype_dropdown(license_kind):
    return update_process_type_dropdown(license_kind)