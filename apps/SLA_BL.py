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
print('SLA_BL.py')
print('Testing mode: ' + str(testing_mode))

if testing_mode:
    df = pd.read_csv('test_data/bl_sla_completeness_checks_only.csv', parse_dates=['JOBCREATEDDATEFIELD', 'JOBCOMPLETEDDATEFIELD',
                                                                                   'PROCESSSCHEDULEDSTARTDATEFIELD', 'PROCESSDATECOMPLETEDFIELD'])

else:
    with con() as con:
        with open(r'queries/SLA_BL.sql') as sql:
            df = pd.read_sql_query(sql=sql.read(), con=con, parse_dates=['JOBCREATEDDATEFIELD', 'JOBCOMPLETEDDATEFIELD',
                                                                         'PROCESSSCHEDULEDSTARTDATEFIELD', 'PROCESSDATECOMPLETEDFIELD'])

# Rename the columns to be more readable
df = (df.rename(columns={'JOBID': 'Job ID', 'PROCESSID': 'Process ID', 'JOBTYPE': 'Job Type',
                         'JOBCREATEDDATE': 'Job Created Date', 'PROCESSDATECOMPLETED': 'Process Completed Date'})
      .assign(MonthDateText=lambda x: x['JOBCREATEDDATEFIELD'].dt.strftime('%b %Y'))
      .assign(DayDateText=lambda x: x['JOBCREATEDDATEFIELD'].dt.strftime('%b %d')))

df['Month Year'] = df['JOBCREATEDDATEFIELD'].map(lambda dt: dt.date().replace(day=1))

unique_job_types = df['Job Type'].unique()
unique_job_types = np.append(['All'], unique_job_types)


def update_graph_data(selected_start, selected_end, selected_job_type, selected_time_agg):
    df_selected = df.copy(deep=True)

    if selected_job_type != "All":
        df_selected = df_selected[(df_selected['Job Type'] == selected_job_type)]
    if selected_time_agg == "Month":
        df_selected = (df_selected.loc[(df_selected['JOBCREATEDDATEFIELD'] >= selected_start) & (df_selected['JOBCREATEDDATEFIELD'] <= selected_end)]
                       .groupby(['Month Year', 'MonthDateText']).agg({'Job ID': 'count', 'Process Completed Date': 'count'})
                       .reset_index()
                       .rename(columns={'Month Year': 'Date Created', 'MonthDateText': 'DateText', 'Job ID': 'Jobs Created',
                                        'Process Completed Date': 'Completeness Checks Completed'})
                       .sort_values(by='Date Created', ascending=False))
    if selected_time_agg == "Day":
        df_selected = (df_selected.loc[(df_selected['JOBCREATEDDATEFIELD'] >= selected_start) & (df_selected['JOBCREATEDDATEFIELD'] <= selected_end)]
                       .groupby(['Job Created Date', 'DayDateText']).agg({'Job ID': 'count', 'Process Completed Date': 'count'})
                       .reset_index()
                       .rename(columns={'Job Created Date': 'Date Created', 'DayDateText': 'DateText', 'Job ID': 'Jobs Created',
                                        'Process Completed Date': 'Completeness Checks Completed'})
                       .sort_values(by='Date Created', ascending=False))
    df_selected['% Completed w/in 2 Bus. Days'] = df_selected['Completeness Checks Completed'] / df_selected['Jobs Created'] * 100
    df_selected['% Completed w/in 2 Bus. Days'] = df_selected['% Completed w/in 2 Bus. Days'].round(0)
    return df_selected


layout = html.Div(children=[
                html.H1('SLA', style={'text-align': 'center'}),
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
                ], className='dashrow filters',
                   style={'width': '90%', 'margin-left': 'auto', 'margin-right': 'auto'}
                ),
                html.Div([
                    html.Div([
                        dcc.Graph(id='sla-graph',
                            figure=go.Figure(
                                data=[],
                                layout=go.Layout(
                                    title='Jobs Created',
                                    yaxis=dict(
                                        title='Jobs Created'
                                    )
                                )
                            )
                        )
                    ], className='ten columns'),
                ], className='dashrow',
                    style={'margin-left': 'auto', 'margin-right': 'auto'}
                )
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
                y=df_results['% Completed w/in 2 Bus. Days'].map('{:,.0f}%'.format),
                mode='lines',
                text=df_results['DateText'],
                hoverinfo='text+y',
                line=dict(
                    shape='spline',
                    color='#ff7f0e'
                ),
                name='% Completed w/in 2 Bus. Days',
                yaxis='y2'
            )
        ],
        'layout': go.Layout(
                title='Jobs Created',
                yaxis=dict(
                    title='Jobs Created'
                ),
                xaxis=dict(
                    title='Job Creation Date'
                ),
                yaxis2=dict(
                    title='% Completed w/in 2 Bus. Days',
                    titlefont=dict(
                        color='#ff7f0e'
                    ),
                    tickfont=dict(
                        color='#ff7f0e'
                    ),
                    overlaying='y',
                    side='right'
                )
        )
    }


