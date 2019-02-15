import os
import urllib.parse
from datetime import datetime

import dash_core_components as dcc
import dash_html_components as html
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
    if dataset == 'df_ind':
        with con() as con:
            sql = 'SELECT * FROM li_dash_sla_bl'
            df_ind = pd.read_sql_query(sql=sql, con=con, parse_dates=['JOBCREATEDDATEFIELD', 'PROCESSDATECOMPLETEDFIELD'])
            sql_bd17 = 'SELECT * FROM business_days_since_2017'
            df_bd17 = pd.read_sql_query(sql=sql_bd17, con=con, parse_dates=['DATEOFYEAR'])

        # Rename columns to be more readable
        df_ind = (df_ind.rename(columns={'JOBID': 'Job ID', 'PROCESSID': 'Process ID', 'JOBTYPE': 'Job Type'})
              .assign(MonthDateText=lambda x: x['JOBCREATEDDATEFIELD'].dt.strftime('%b %Y'))
              .assign(DayDateText=lambda x: x['JOBCREATEDDATEFIELD'].dt.strftime('%b %d %Y')))

        df_ind['Month Year'] = df_ind['JOBCREATEDDATEFIELD'].map(lambda dt: dt.date().replace(day=1))
        df_ind['Job Created Day'] = df_ind['JOBCREATEDDATEFIELD'].dt.date
        df_ind['Process Completed Day'] = df_ind['PROCESSDATECOMPLETEDFIELD'].dt.date
        df_bd17['DATEOFYEARDATEONLY'] = df_bd17['DATEOFYEAR'].dt.date

        # Get the number of business days since 1/1/2017 for all the Job Created Dates and Process Completed Dates
        df_merged = df_ind.merge(df_bd17, left_on='Job Created Day', right_on='DATEOFYEARDATEONLY', how='left')
        df = df_merged.merge(df_bd17, left_on='Process Completed Day', right_on='DATEOFYEARDATEONLY',
                                     how='left')
        # Subtract the number of business days between 1/1/2017 and the Job Created Date from the number of business days between
        # 1/1/2017 and the Process Completed Date to get the number of business days that the job was open/in progress.
        df['Bus. Days Open'] = df['BUSINESSDAYSSINCE_y'] - df['BUSINESSDAYSSINCE_x']
        # Flag each job as either being within SLA or not based on whether the job was open for 2 days or fewer
        df['W/in SLA'] = np.where(df['Bus. Days Open'] <= 2, 1, 0)
    elif dataset == 'last_ddl_time':
        with con() as con:
            sql = 'SELECT SCN_TO_TIMESTAMP(MAX(ora_rowscn)) last_ddl_time FROM LI_DASH_SLA_BL'
            df = pd.read_sql_query(sql=sql, con=con)
    return df.to_json(date_format='iso', orient='split')

@cache_timeout
@cache.memoize()
def dataframe(dataset):
    return pd.read_json(query_data(dataset), orient='split')

def update_layout():
    df = dataframe('df_ind')
    last_ddl_time = dataframe('last_ddl_time')

    unique_job_types = df['Job Type'].unique()
    unique_job_types = np.append(['All'], unique_job_types)

    return html.Div(children=[
                html.H1('SLA License Issuance (Business Licenses)', style={'text-align': 'center'}),
                html.P(f"Data last updated {last_ddl_time['LAST_DDL_TIME'].iloc[0]}", style = {'text-align': 'center'}),
                html.Div([
                    html.Div([
                        html.P('Filter by Job Created Date'),
                        dcc.DatePickerRange(
                            display_format='MMM Y',
                            id='sla-date-picker-range',
                            start_date=datetime(2018, 1, 1),
                            end_date=datetime.now()
                        ),
                    ], className='four columns'),
                    html.Div([
                        html.P('Filter by Job Type'),
                        dcc.Dropdown(
                            id='sla-job-type-dropdown',
                            options=[{'label': k, 'value': k} for k in unique_job_types],
                            value='All'
                        ),
                    ], className='four columns'),
                    html.Div([
                        html.P('Aggregate Data by...'),
                        dcc.Dropdown(
                            id='sla-time-agg-dropdown',
                            options=[
                                {'label': 'Month', 'value': 'Month'},
                                {'label': 'Day', 'value': 'Day'}
                            ],
                            value='Month'
                        ),
                    ], className='four columns'),
                ], className='dashrow filters'),
                html.Div([
                    html.Div([
                        html.H1('', id='sla-bl-jobs-created-indicator', style={'font-size': '35pt'}),
                        html.H2('Jobs Created', style={'font-size': '30pt'})
                    ], className='four columns', style={'text-align': 'center', 'margin': 'auto', 'padding': '50px 0'}),
                    html.Div([
                        html.H1('', id='sla-bl-percent-completed-indicator', style={'font-size': '35pt'}),
                        html.H2('Completed', style={'font-size': '30pt'})
                    ], className='four columns', style={'text-align': 'center', 'margin': 'auto', 'padding': '50px 0'}),
                    html.Div([
                        html.H1('', id='sla-bl-percent-completed-within-sla-indicator', style={'font-size': '35pt'}),
                        html.H2('Completed Within SLA', style={'font-size': '30pt'})
                    ], className='four columns', style={'text-align': 'center', 'margin': 'auto', 'padding': '50px 0'})
                ], className='dashrow'),
                html.Div([
                    html.Div([
                        dcc.Graph(
                            id='sla-bl-jobs-graph',
                            config={
                                'displayModeBar': False
                            },
                            figure=go.Figure(
                                data=[],
                                layout=go.Layout(
                                    yaxis=dict(
                                        title='Jobs'
                                    )
                                )
                            )
                        )
                    ], className='twelve columns'),
                ], className='dashrow'),
                html.Div([
                    html.Div([
                        dcc.Graph(
                            id='sla-bl-percent-graph',
                            config={
                                'displayModeBar': False
                            },
                            figure=go.Figure(
                                data=[],
                                layout=go.Layout(
                                    yaxis=dict(
                                        title='%'
                                    )
                                )
                            )
                        )
                    ], className='twelve columns'),
                ], className='dashrow'),
                html.Details([
                    html.Summary('Query Description'),
                    html.Div([
                        html.P(
                            'Business license jobs created since 1/1/2017, the % of them that were completed, and the '
                            '% of them that were completed within SLA.'),
                        html.P(
                            'Completed job: job having a completed completeness check.'),
                        html.P(
                            'Completed job within SLA: job having a completeness check that was completed 2 days or fewer after the job was '
                            'created. So if a job was created on Monday it would be considered within SLA if it was '
                            'completed on Monday, Tuesday, or Wednesday, but if it was completed on Thursday or later '
                            'it would be considered outside of SLA.')
                    ])
                ])
            ])

layout = update_layout

def update_jobs_created(selected_start, selected_end, selected_job_type):
    df_selected = dataframe('df_ind')

    if selected_job_type != "All":
        df_selected = df_selected[(df_selected['Job Type'] == selected_job_type)]

    df_selected = df_selected.loc[(df_selected['JOBCREATEDDATEFIELD'] >= selected_start)&(df_selected['JOBCREATEDDATEFIELD'] <= selected_end)]
    jobs_created = df_selected['JOBCREATEDDATEFIELD'].count()
    return '{:,.0f}'.format(jobs_created)


def update_percent_completed(selected_start, selected_end, selected_job_type):
    df_selected = dataframe('df_ind')

    if selected_job_type != "All":
        df_selected = df_selected[(df_selected['Job Type'] == selected_job_type)]

    df_selected = df_selected.loc[(df_selected['JOBCREATEDDATEFIELD'] >= selected_start)&(df_selected['JOBCREATEDDATEFIELD'] <= selected_end)]
    percent_completed = df_selected['PROCESSDATECOMPLETEDFIELD'].count() / df_selected['JOBCREATEDDATEFIELD'].count() * 100
    return '{:,.0f}%'.format(percent_completed)


def update_percent_completed_within_sla(selected_start, selected_end, selected_job_type):
    df_selected = dataframe('df_ind')

    if selected_job_type != "All":
        df_selected = df_selected[(df_selected['Job Type'] == selected_job_type)]

    df_selected = df_selected.loc[(df_selected['JOBCREATEDDATEFIELD'] >= selected_start)&(df_selected['JOBCREATEDDATEFIELD'] <= selected_end)]
    percent_completed_within_sla = df_selected['W/in SLA'].sum() / df_selected['JOBCREATEDDATEFIELD'].count() * 100
    return '{:,.0f}%'.format(percent_completed_within_sla)


def update_jobs_graph_data(selected_start, selected_end, selected_job_type, selected_time_agg):
    df_selected = dataframe('df_ind')

    if selected_job_type != "All":
        df_selected = df_selected[(df_selected['Job Type'] == selected_job_type)]
    if selected_time_agg == "Month":
        df_selected = (df_selected.loc[(df_selected['JOBCREATEDDATEFIELD'] >= selected_start) & (df_selected['JOBCREATEDDATEFIELD'] <= selected_end)]
                       .groupby(['Month Year', 'MonthDateText']).agg(
                            {'Job ID': 'count', 'Process Completed Day': 'count'})
                       .reset_index()
                       .rename(
                            columns={'Month Year': 'Date Created', 'MonthDateText': 'DateText', 'Job ID': 'Jobs Created',
                                    'Process Completed Day': 'Jobs Completed'})
                       .sort_values(by='Date Created', ascending=False))
    if selected_time_agg == "Day":
        df_selected = (df_selected.loc[(df_selected['JOBCREATEDDATEFIELD'] >= selected_start) & (df_selected['JOBCREATEDDATEFIELD'] <= selected_end)]
                       .groupby(['Job Created Day', 'DayDateText']).agg(
                            {'Job ID': 'count', 'Process Completed Day': 'count'})
                       .reset_index()
                       .rename(
                            columns={'Job Created Day': 'Date Created', 'DayDateText': 'DateText', 'Job ID': 'Jobs Created',
                                    'Process Completed Day': 'Jobs Completed'})
                       .sort_values(by='Date Created', ascending=False))
    return df_selected

def update_percent_graph_data(selected_start, selected_end, selected_job_type, selected_time_agg):
    df_selected = dataframe('df_ind')

    if selected_job_type != "All":
        df_selected = df_selected[(df_selected['Job Type'] == selected_job_type)]
    if selected_time_agg == "Month":
        df_selected = (df_selected.loc[(df_selected['JOBCREATEDDATEFIELD'] >= selected_start) & (
        df_selected['JOBCREATEDDATEFIELD'] <= selected_end)]
                       .groupby(['Month Year', 'MonthDateText']).agg(
                            {'Job ID': 'count', 'Process Completed Day': 'count',
                            'W/in SLA': 'sum'})
                       .reset_index()
                       .rename(
                            columns={'Month Year': 'Date Created', 'MonthDateText': 'DateText', 'Job ID': 'Jobs Created',
                                    'Process Completed Day': 'Completeness Checks Completed', 'W/in SLA': '# w/in SLA'})
                       .sort_values(by='Date Created', ascending=False))
    if selected_time_agg == "Day":
        df_selected = (df_selected.loc[(df_selected['JOBCREATEDDATEFIELD'] >= selected_start) & (
        df_selected['JOBCREATEDDATEFIELD'] <= selected_end)]
                       .groupby(['Job Created Day', 'DayDateText']).agg(
                            {'Job ID': 'count', 'Process Completed Day': 'count',
                            'W/in SLA': 'sum'})
                       .reset_index()
                       .rename(
                            columns={'Job Created Day': 'Date Created', 'DayDateText': 'DateText', 'Job ID': 'Jobs Created',
                                    'Process Completed Day': 'Completeness Checks Completed', 'W/in SLA': '# w/in SLA'})
                       .sort_values(by='Date Created', ascending=False))
    df_selected['% Completed'] = df_selected['Completeness Checks Completed'] / df_selected['Jobs Created'] * 100
    df_selected['% Completed'] = df_selected['% Completed'].round(0)
    df_selected['% Completed w/in SLA'] = df_selected['# w/in SLA'] / df_selected['Jobs Created'] * 100
    df_selected['% Completed w/in SLA'] = df_selected['% Completed w/in SLA'].round(0)
    return df_selected

@app.callback(
    Output('sla-bl-jobs-created-indicator', 'children'),
    [Input('sla-date-picker-range', 'start_date'),
     Input('sla-date-picker-range', 'end_date'),
     Input('sla-job-type-dropdown', 'value')])
def update_jobs_created_indicator(start_date, end_date, job_type):
    jobs_created = update_jobs_created(start_date, end_date, job_type)
    return str(jobs_created)

@app.callback(
    Output('sla-bl-percent-completed-indicator', 'children'),
    [Input('sla-date-picker-range', 'start_date'),
     Input('sla-date-picker-range', 'end_date'),
     Input('sla-job-type-dropdown', 'value')])
def update_percent_completed_indicator(start_date, end_date, job_type):
    percent_completed = update_percent_completed(start_date, end_date, job_type)
    return str(percent_completed)

@app.callback(
    Output('sla-bl-percent-completed-within-sla-indicator', 'children'),
    [Input('sla-date-picker-range', 'start_date'),
     Input('sla-date-picker-range', 'end_date'),
     Input('sla-job-type-dropdown', 'value')])
def update_percent_completed_within_sla_indicator(start_date, end_date, job_type):
    percent_completed_within_sla = update_percent_completed_within_sla(start_date, end_date, job_type)
    return str(percent_completed_within_sla)


@app.callback(
    Output('sla-bl-jobs-graph', 'figure'),
    [Input('sla-date-picker-range', 'start_date'),
     Input('sla-date-picker-range', 'end_date'),
     Input('sla-job-type-dropdown', 'value'),
     Input('sla-time-agg-dropdown', 'value')])
def update_jobs_graph(start_date, end_date, job_type, time_agg):
    df_results = update_jobs_graph_data(start_date, end_date, job_type, time_agg)
    return {
        'data': [
            go.Scatter(
                x=df_results['Date Created'],
                y=df_results['Jobs Created'],
                mode='lines',
                text=df_results['DateText'],
                hoverinfo='text+y',
                line=dict(
                    shape='spline',
                    color='rgb(26, 118, 255)'
                ),
                name='Jobs Created'
            ),
            go.Scatter(
                x=df_results['Date Created'],
                y=df_results['Jobs Completed'],
                mode='lines',
                text=df_results['DateText'],
                hoverinfo='text+y',
                line=dict(
                    shape='spline',
                    color='#ff7f0e'
                ),
                name='Jobs Completed'
            )
        ],
        'layout': go.Layout(
                xaxis=dict(
                    title='Job Creation Date'
                ),
                yaxis=dict(
                    title='Jobs',
                    range=[0, df_results['Jobs Created'].max() + (df_results['Jobs Created'].max() / 25)]
                )
        )
    }

@app.callback(
    Output('sla-bl-percent-graph', 'figure'),
    [Input('sla-date-picker-range', 'start_date'),
     Input('sla-date-picker-range', 'end_date'),
     Input('sla-job-type-dropdown', 'value'),
     Input('sla-time-agg-dropdown', 'value')])
def update_percent_graph(start_date, end_date, job_type, time_agg):
    df_results = update_percent_graph_data(start_date, end_date, job_type, time_agg)
    return {
        'data': [
            go.Scatter(
                x=df_results['Date Created'],
                y=df_results['% Completed'].map('{:,.0f}%'.format),
                mode='lines',
                text=df_results['DateText'],
                hoverinfo='text+y',
                line=dict(
                    shape='spline',
                    color='#ff7f0e'
                ),
                name='% of Jobs Completed',
                yaxis='y'
            ),
            go.Scatter(
                x=df_results['Date Created'],
                y=df_results['% Completed w/in SLA'].map('{:,.0f}%'.format),
                mode='lines',
                text=df_results['DateText'],
                hoverinfo='text+y',
                line=dict(
                    shape='spline',
                    color='#008000'
                ),
                name='% of Jobs Completed w/in SLA',
                yaxis='y'
            )
        ],
        'layout': go.Layout(
                xaxis=dict(
                    title='Job Creation Date'
                ),
                yaxis=dict(
                    title='% of Jobs',
                    range=[0, 100]
                )
        )
    }
