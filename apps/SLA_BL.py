import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
from dash.dependencies import Input, Output
from datetime import datetime
import numpy as np

from app import app, con

print('SLA_BL.py')

with con() as con:
    sql = 'SELECT * FROM li_dash_sla_bl'
    df = pd.read_sql_query(sql=sql, con=con, parse_dates=['JOBCREATEDDATEFIELD', 'JOBCOMPLETEDDATEFIELD',
                                                          'PROCESSSCHEDULEDSTARTDATEFIELD', 'PROCESSDATECOMPLETEDFIELD'])
    sql_bd17 = 'SELECT * FROM business_days_since_2017'
    df_bd17 = pd.read_sql_query(sql=sql_bd17, con=con, parse_dates=['DATEOFYEAR'])
    sql = "SELECT from_tz(cast(last_ddl_time as timestamp), 'GMT') at TIME zone 'US/Eastern' as LAST_DDL_TIME FROM user_objects WHERE object_name = 'LI_DASH_SLA_BL'"
    last_ddl_time = pd.read_sql_query(sql=sql, con=con)

# Rename the columns to be more readable
df = (df.rename(columns={'JOBID': 'Job ID', 'PROCESSID': 'Process ID', 'JOBTYPE': 'Job Type',
                         'JOBCREATEDDATE': 'Job Created Date', 'PROCESSDATECOMPLETED': 'Process Completed Date'})
      .assign(YearText=lambda x: x['JOBCREATEDDATEFIELD'].dt.strftime('%Y'))
      .assign(MonthDateText=lambda x: x['JOBCREATEDDATEFIELD'].dt.strftime('%b %Y'))
      .assign(WeekText=lambda x: x['JOBCREATEDDATEFIELD'].dt.strftime('%W'))
      .assign(DayDateText=lambda x: x['JOBCREATEDDATEFIELD'].dt.strftime('%b %d %Y')))

df['Year'] = df['JOBCREATEDDATEFIELD'].dt.year
df['Month Year'] = df['JOBCREATEDDATEFIELD'].map(lambda dt: dt.date().replace(day=1))
df['Week'] = df['JOBCREATEDDATEFIELD'].map(lambda dt: dt.week)
df['Job Created Day'] = df['JOBCREATEDDATEFIELD'].dt.date
df['Process Completed Day'] = df['PROCESSDATECOMPLETEDFIELD'].dt.date

df_bd17['DATEOFYEARDATEONLY'] = df_bd17['DATEOFYEAR'].dt.date

#Get the number of business days since 1/1/2017 for all the Job Created Dates and Process Completed Dates
df_merged = df.merge(df_bd17, left_on='Job Created Day', right_on='DATEOFYEARDATEONLY', how='left')
df_merged2 = df_merged.merge(df_bd17, left_on='Process Completed Day', right_on='DATEOFYEARDATEONLY', how='left')
#Subtract the number of business days between 1/1/2017 and the Job Created Date from the number of business days between
#1/1/2017 and the Process Completed Date to get the number of business days that the job was open/in progress.
df_merged2['Bus. Days Open'] = df_merged2['BUSINESSDAYSSINCE_y'] - df_merged2['BUSINESSDAYSSINCE_x']
#Flag each job as either being within SLA or not based on whether the job was open for 2 days or fewer
df_merged2['W/in SLA'] = np.where(df_merged2['Bus. Days Open'] <= 2, 1, 0)

unique_job_types = df_merged2['Job Type'].unique()
unique_job_types = np.append(['All'], unique_job_types)


def update_jobs_created(selected_start, selected_end, selected_job_type):
    df_selected = df_merged2.copy(deep=True)

    if selected_job_type != "All":
        df_selected = df_selected[(df_selected['Job Type'] == selected_job_type)]

    df_selected = df_selected.loc[(df_selected['JOBCREATEDDATEFIELD'] >= selected_start)&(df_selected['JOBCREATEDDATEFIELD'] <= selected_end)]
    jobs_created = df_selected['JOBCREATEDDATEFIELD'].count()
    return '{:,.0f}'.format(jobs_created)


def update_percent_completed(selected_start, selected_end, selected_job_type):
    df_selected = df_merged2.copy(deep=True)

    if selected_job_type != "All":
        df_selected = df_selected[(df_selected['Job Type'] == selected_job_type)]

    df_selected = df_selected.loc[(df_selected['JOBCREATEDDATEFIELD'] >= selected_start)&(df_selected['JOBCREATEDDATEFIELD'] <= selected_end)]
    percent_completed = df_selected['PROCESSDATECOMPLETEDFIELD'].count() / df_selected['JOBCREATEDDATEFIELD'].count() * 100
    return '{:,.0f}%'.format(percent_completed)


def update_percent_completed_within_sla(selected_start, selected_end, selected_job_type):
    df_selected = df_merged2.copy(deep=True)

    if selected_job_type != "All":
        df_selected = df_selected[(df_selected['Job Type'] == selected_job_type)]

    df_selected = df_selected.loc[(df_selected['JOBCREATEDDATEFIELD'] >= selected_start)&(df_selected['JOBCREATEDDATEFIELD'] <= selected_end)]
    percent_completed_within_sla = df_selected['W/in SLA'].sum() / df_selected['JOBCREATEDDATEFIELD'].count() * 100
    return '{:,.0f}%'.format(percent_completed_within_sla)


def update_graph_data(selected_start, selected_end, selected_job_type, selected_time_agg):
    df_selected = df_merged2.copy(deep=True)

    if selected_job_type != "All":
        df_selected = df_selected[(df_selected['Job Type'] == selected_job_type)]
    if selected_time_agg == "Month":
        df_selected = (df_selected.loc[(df_selected['JOBCREATEDDATEFIELD'] >= selected_start) & (df_selected['JOBCREATEDDATEFIELD'] <= selected_end)]
                       .groupby(['Month Year', 'MonthDateText']).agg({'Job ID': 'count', 'Process Completed Date': 'count',
                                                                      'W/in SLA': 'sum'})
                       .reset_index()
                       .rename(columns={'Month Year': 'Date Created', 'MonthDateText': 'DateText', 'Job ID': 'Jobs Created',
                                        'Process Completed Date': 'Completeness Checks Completed', 'W/in SLA': '# w/in SLA'})
                       .sort_values(by='Date Created', ascending=False))
    if selected_time_agg == "Week":
        df_selected = (df_selected.loc[(df_selected['JOBCREATEDDATEFIELD'] >= selected_start) & (df_selected['JOBCREATEDDATEFIELD'] <= selected_end)]
                       .groupby(['Year', 'YearText', 'Week', 'WeekText']).agg({'Job ID': 'count', 'Process Completed Date': 'count',
                                                                        'W/in SLA': 'sum'})
                       .reset_index()
                       .rename(columns={'Job ID': 'Jobs Created',
                                        'Process Completed Date': 'Completeness Checks Completed', 'W/in SLA': '# w/in SLA'}))
        df_selected['DateText'] = df_selected['YearText'] + ' week ' + df_selected['WeekText']
        df_selected['YearWeekText'] = df_selected['YearText'] + '-' + df_selected['WeekText'] + '-0'
        df_selected['Date Created'] = pd.to_datetime(df_selected['YearWeekText'], format='%Y-%W-%w')
        df_selected.sort_values(by='Date Created', ascending=True, inplace=True)
    if selected_time_agg == "Day":
        df_selected = (df_selected.loc[(df_selected['JOBCREATEDDATEFIELD'] >= selected_start) & (df_selected['JOBCREATEDDATEFIELD'] <= selected_end)]
                       .groupby(['Job Created Day', 'DayDateText']).agg({'Job ID': 'count', 'Process Completed Date': 'count',
                                                                        'W/in SLA': 'sum'})
                       .reset_index()
                       .rename(columns={'Job Created Day': 'Date Created', 'DayDateText': 'DateText', 'Job ID': 'Jobs Created',
                                        'Process Completed Date': 'Completeness Checks Completed', 'W/in SLA': '# w/in SLA'})
                       .sort_values(by='Date Created', ascending=False))
    df_selected['% Completed'] = df_selected['Completeness Checks Completed'] / df_selected['Jobs Created'] * 100
    df_selected['% Completed'] = df_selected['% Completed'].round(0)
    df_selected['% Completed w/in SLA'] = df_selected['# w/in SLA'] / df_selected['Jobs Created'] * 100
    df_selected['% Completed w/in SLA'] = df_selected['% Completed w/in SLA'].round(0)
    return df_selected


layout = html.Div(children=[
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
                                {'label': 'Week', 'value': 'Week'},
                                {'label': 'Day', 'value': 'Day'}
                            ],
                            value='Month'
                        ),
                    ], className='four columns'),
                ], className='dashrow filters'),
                html.Div([
                    html.Div([
                        dcc.Graph(id='sla-graph',
                            figure=go.Figure(
                                data=[],
                                layout=go.Layout(
                                    yaxis=dict(
                                        title='Jobs Created'
                                    )
                                )
                            )
                        )
                    ], className='twelve columns'),
                ], className='dashrow'),
                html.Div([
                    html.Div([
                        html.H1('', id='sla-jobs-created-indicator', style={'font-size': '35pt'}),
                        html.H2('Jobs Created', style={'font-size': '30pt'})
                    ], className='four columns', style={'text-align': 'center', 'margin': 'auto', 'padding': '50px 0'}),
                    html.Div([
                        html.H1('', id='sla-percent-completed-indicator', style={'font-size': '35pt'}),
                        html.H2('Completed', style={'font-size': '30pt'})
                    ], className='four columns', style={'text-align': 'center', 'margin': 'auto', 'padding': '50px 0'}),
                    html.Div([
                        html.H1('', id='sla-percent-completed-within-sla-indicator', style={'font-size': '35pt'}),
                        html.H2('Completed Within SLA', style={'font-size': '30pt'})
                    ], className='four columns', style={'text-align': 'center', 'margin': 'auto', 'padding': '50px 0'})
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

@app.callback(
    Output('sla-graph', 'figure'),
    [Input('sla-date-picker-range', 'start_date'),
     Input('sla-date-picker-range', 'end_date'),
     Input('sla-job-type-dropdown', 'value'),
     Input('sla-time-agg-dropdown', 'value')])
def update_graph(start_date, end_date, job_type, time_agg):
    df_results = update_graph_data(start_date, end_date, job_type, time_agg)
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
                y=df_results['% Completed'].map('{:,.0f}%'.format),
                mode='lines',
                text=df_results['DateText'],
                hoverinfo='text+y',
                line=dict(
                    shape='spline',
                    color='#ff7f0e'
                ),
                name='% Completed',
                yaxis='y2'
            ),
            go.Scatter(
                x=df_results['Date Created'],
                y=df_results['% Completed w/in SLA'].map('{:,.0f}%'.format),
                mode='lines',
                text=df_results['DateText'],
                hoverinfo='text+y',
                line=dict(
                    shape='spline',
                    color='#8B0000'
                ),
                name='% Completed w/in SLA',
                yaxis='y2'
            )
        ],
        'layout': go.Layout(
                yaxis=dict(
                    title='Jobs Created',
                    range=[0, df_results['Jobs Created'].max() + (df_results['Jobs Created'].max()/25)]
                ),
                xaxis=dict(
                    title='Job Creation Date'
                ),
                yaxis2=dict(
                    title='% of Jobs',
                    titlefont=dict(
                        color='#ff7f0e'
                    ),
                    tickfont=dict(
                        color='#ff7f0e'
                    ),
                    overlaying='y',
                    side='right',
                    range=[0, 100]
                )
        )
    }

@app.callback(
    Output('sla-jobs-created-indicator', 'children'),
    [Input('sla-date-picker-range', 'start_date'),
     Input('sla-date-picker-range', 'end_date'),
     Input('sla-job-type-dropdown', 'value')])
def update_jobs_created_indicator(start_date, end_date, job_type):
    jobs_created = update_jobs_created(start_date, end_date, job_type)
    return str(jobs_created)


@app.callback(
    Output('sla-percent-completed-indicator', 'children'),
    [Input('sla-date-picker-range', 'start_date'),
     Input('sla-date-picker-range', 'end_date'),
     Input('sla-job-type-dropdown', 'value')])
def update_percent_completed_indicator(start_date, end_date, job_type):
    percent_completed = update_percent_completed(start_date, end_date, job_type)
    return str(percent_completed)


@app.callback(
    Output('sla-percent-completed-within-sla-indicator', 'children'),
    [Input('sla-date-picker-range', 'start_date'),
     Input('sla-date-picker-range', 'end_date'),
     Input('sla-job-type-dropdown', 'value')])
def update_percent_completed_within_sla_indicator(start_date, end_date, job_type):
    percent_completed_within_sla = update_percent_completed_within_sla(start_date, end_date, job_type)
    return str(percent_completed_within_sla)