import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as table
import plotly.graph_objs as go
import pandas as pd
from dash.dependencies import Input, Output
from datetime import datetime
import numpy as np
import urllib.parse

from app import app, con

testing_mode = True
print('IndividualWorkloadsBL.py')
print('Testing mode: ' + str(testing_mode))

if testing_mode:
    df = pd.read_csv('test_data/individual_workloads_bl.csv', parse_dates=['SCHEDULEDSTARTDATE', 'DATECOMPLETED'])

else:
    with con() as con:
        with open(r'queries/permits/individual_workloads_bl.sql') as sql:
            df = pd.read_sql_query(sql=sql.read(), con=con, parse_dates=['SCHEDULEDSTARTDATE', 'DATECOMPLETED'])

# Rename the columns to be more readable
# Make a DateText Column to display on the graph
df = (df.rename(columns={'PROCESSID': 'Process ID', 'PROCESSTYPE': 'Process Type', 'JOBTYPE': 'Job Type', 'LICENSETYPE': 'License Type', 'NAME': 'Person',
                         'SCHEDULEDSTARTDATE': 'Scheduled Start Date', 'DATECOMPLETED': 'Date Completed', 'DURATION': 'Duration'}))

unique_persons = df['Person'].unique()
unique_persons = np.append(['All'], unique_persons)

unique_process_types = df['Process Type'].unique()
unique_process_types = np.append(['All'], unique_process_types)

unique_job_types = df['Job Type'].unique()
unique_job_types = np.append(['All'], unique_job_types)

unique_license_types = df['License Type'].unique()
unique_license_types = np.append(['All'], unique_license_types)

df_counts = (df.groupby(['Person', 'Process Type', 'Job Type', 'License Type', 'Date Completed'])
             .agg({'Process ID': 'count', 'Duration': 'sum'})
             .reset_index()
             .rename(columns={'Process ID': 'Processes Completed', 'Duration': 'Total Duration'})
             .sort_values(by='Date Completed', ascending=False))

df_counts['Month'] = df_counts['Date Completed'].map(lambda dt: dt.replace(day=1))

def update_graph_data(selected_start, selected_end, selected_person, selected_process_type, selected_job_type, selected_license_type):
    df_selected = df_counts.copy(deep=True)

    if selected_person != "All":
        df_selected = df_selected[(df_selected['Person'] == selected_person)]
    if selected_process_type != "All":
        df_selected = df_selected[(df_selected['Process Type'] == selected_process_type)]
    if selected_job_type != "All":
        df_selected = df_selected[(df_selected['Job Type'] == selected_job_type)]
    if selected_license_type != "All":
        df_selected = df_selected[(df_selected['License Type'] == selected_license_type)]

    df_selected = (df_selected.loc[(df_selected['Date Completed'] >= selected_start) & (df_selected['Date Completed'] <= selected_end)]
                   .groupby('Month').agg({'Processes Completed': 'sum'})
                   .reset_index()
                   .sort_values(by='Month', ascending=False))
    return df_selected

def update_counts_table_data(selected_start, selected_end, selected_person, selected_process_type, selected_job_type, selected_license_type):
    df_selected = df_counts.copy(deep=True)

    if selected_person != "All":
        df_selected = df_selected[(df_selected['Person'] == selected_person)]
    if selected_process_type != "All":
        df_selected = df_selected[(df_selected['Process Type'] == selected_process_type)]
    if selected_job_type != "All":
        df_selected = df_selected[(df_selected['Job Type'] == selected_job_type)]
    if selected_license_type != "All":
        df_selected = df_selected[(df_selected['License Type'] == selected_license_type)]

    df_selected = (df_selected.loc[(df_selected['Date Completed'] >= selected_start) & (df_selected['Date Completed'] <= selected_end)]
                   .groupby(['Person', 'Process Type']).agg({'Processes Completed': 'count', 'Total Duration': 'sum'})
                   .reset_index()
                   .sort_values(by=['Person', 'Process Type']))
    df_selected['Avg. Duration'] = (df_selected['Total Duration'] / df_selected['Processes Completed']).round(0)
    return df_selected[['Person', 'Process Type', 'Processes Completed', 'Avg. Duration']]

def update_ind_records_table_data(selected_start, selected_end, selected_person, selected_process_type, selected_job_type, selected_license_type):
    df_selected = df.copy(deep=True)

    if selected_person != "All":
        df_selected = df_selected[(df_selected['Person'] == selected_person)]
    if selected_process_type != "All":
        df_selected = df_selected[(df_selected['Process Type'] == selected_process_type)]
    if selected_job_type != "All":
        df_selected = df_selected[(df_selected['Job Type'] == selected_job_type)]
    if selected_license_type != "All":
        df_selected = df_selected[(df_selected['License Type'] == selected_license_type)]

    df_selected = (df_selected.loc[(df_selected['Date Completed'] >= selected_start) & (df_selected['Date Completed'] <= selected_end)]
                   .sort_values(by='Date Completed'))
    df_selected['Duration'] = df_selected['Duration'].round(2).map('{:,.2f}'.format)
    return df_selected

layout = html.Div(children=[
                html.H1('Individual Workloads', style={'text-align': 'center'}),
                html.Div([
                    html.Div([
                        html.P('Filter by Date Range'),
                        dcc.DatePickerRange(
                            display_format='MMM Y',
                            id='ind-workloads-date-picker-range',
                            start_date=datetime(2016, 1, 1),
                            end_date=datetime.now()
                        ),
                    ], className='six columns'),
                    html.Div([
                        html.P('Filter by Person'),
                        dcc.Dropdown(
                                id='ind-workloads-person-dropdown',
                                options=[{'label': k, 'value': k} for k in unique_persons],
                                value='All'
                        ),
                    ], className='five columns'),
                ], className='dashrow filters'),
                html.Div([
                    html.Div([
                        html.P('Filter by Process Type'),
                        dcc.Dropdown(
                            id='ind-workloads-process-type-dropdown',
                            options=[{'label': k, 'value': k} for k in unique_process_types],
                            value='All'
                        ),
                    ], className='four columns'),
                    html.Div([
                        html.P('Filter by Job Type'),
                        dcc.Dropdown(
                            id='ind-workloads-job-type-dropdown',
                            options=[{'label': k, 'value': k} for k in unique_job_types],
                            value='All'
                        ),
                    ], className='four columns'),
                    html.Div([
                        html.P('Filter by License Type'),
                        dcc.Dropdown(
                            id='ind-workloads-license-type-dropdown',
                            options=[{'label': k, 'value': k} for k in unique_license_types],
                            value='All'
                        ),
                    ], className='four columns'),
                ], className='dashrow filters'),
                html.Div([
                    html.Div([
                        dcc.Graph(id='ind-workloads-graph',
                            figure=go.Figure(
                                data=[
                                    go.Scatter(
                                        x=df_counts['Month'],
                                        y=df_counts['Processes Completed'],
                                        mode='lines',
                                        text=df_counts['Month'],
                                        hoverinfo='text+y',
                                        line=dict(
                                            shape='spline',
                                            color='rgb(26, 118, 255)'
                                        ),
                                        name='Processes Completed'
                                    )
                                ],
                                layout=go.Layout(
                                    title='Processes Completed',
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
                        html.H3('Processes Completed by Person', style={'text-align': 'center'}),
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
                    ], style={'width': '50%', 'margin-left': 'auto', 'margin-right': 'auto','margin-top': '50px', 'margin-bottom': '50px'})
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
                    ], style={'width': '90%', 'margin-left': 'auto', 'margin-right': 'auto', 'margin-top': '50px',
                              'margin-bottom': '50px'})
                ], className='dashrow')
            ])

@app.callback(
    Output('ind-workloads-graph', 'figure'),
    [Input('ind-workloads-date-picker-range', 'start_date'),
     Input('ind-workloads-date-picker-range', 'end_date'),
     Input('ind-workloads-person-dropdown', 'value'),
     Input('ind-workloads-process-type-dropdown', 'value'),
     Input('ind-workloads-job-type-dropdown', 'value'),
     Input('ind-workloads-license-type-dropdown', 'value')])
def update_graph(start_date, end_date, person, process_type, job_type, license_type):
    df_results = update_graph_data(start_date, end_date, person, process_type, job_type, license_type)
    return {
        'data': [
            go.Scatter(
                x=df_results['Month'],
                y=df_results['Processes Completed'],
                mode='lines',
                text=df_results['Month'],
                hoverinfo='text+y',
                line=dict(
                    shape='spline',
                    color='rgb(26, 118, 255)'
                ),
                name='Processes Completed'
            )
        ],
        'layout': go.Layout(
                title='Processes Completed',
                yaxis=dict(
                    title='Processes Completed'
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
     Input('ind-workloads-license-type-dropdown', 'value')])
def update_count_table(start_date, end_date, person, process_type, job_type, license_type):
    df_results = update_counts_table_data(start_date, end_date, person, process_type, job_type, license_type)
    return df_results.to_dict('records')


@app.callback(
    Output('ind-workloads-count-table-download-link', 'href'),
    [Input('ind-workloads-date-picker-range', 'start_date'),
     Input('ind-workloads-date-picker-range', 'end_date'),
     Input('ind-workloads-person-dropdown', 'value'),
     Input('ind-workloads-process-type-dropdown', 'value'),
     Input('ind-workloads-job-type-dropdown', 'value'),
     Input('ind-workloads-license-type-dropdown', 'value')])
def update_count_table_download_link(start_date, end_date, person, process_type, job_type, license_type):
    df_results = update_counts_table_data(start_date, end_date, person, process_type, job_type, license_type)
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
     Input('ind-workloads-license-type-dropdown', 'value')])
def update_ind_records_table(start_date, end_date, person, process_type, job_type, license_type):
    df_results = update_ind_records_table_data(start_date, end_date, person, process_type, job_type, license_type)
    return df_results.to_dict('records')

@app.callback(
    Output('ind-workloads-ind-records-table-download-link', 'href'),
    [Input('ind-workloads-date-picker-range', 'start_date'),
     Input('ind-workloads-date-picker-range', 'end_date'),
     Input('ind-workloads-person-dropdown', 'value'),
     Input('ind-workloads-process-type-dropdown', 'value'),
     Input('ind-workloads-job-type-dropdown', 'value'),
     Input('ind-workloads-license-type-dropdown', 'value')])
def update_ind_records_table_download_link(start_date, end_date, person, process_type, job_type, license_type):
    df_results = update_ind_records_table_data(start_date, end_date, person, process_type, job_type, license_type)
    csv_string = df_results.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string