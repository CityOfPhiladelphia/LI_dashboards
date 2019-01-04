import os
import urllib.parse

import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import plotly.graph_objs as go
import pandas as pd
from dash.dependencies import Input, Output
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

from app import app, cache, cache_timeout

APP_NAME = os.path.basename(__file__)

print(APP_NAME)

@cache_timeout
@cache.memoize()
def query_data(dataset):
    from app import con
    if dataset == 'df_ind':
        with con() as con:
            sql = 'SELECT * FROM li_dash_expirationdates_tl'
            df = pd.read_sql_query(sql=sql, con=con, parse_dates=['EXPIRATIONDATE'])
        df = (df.assign(YearText=lambda x: x['EXPIRATIONDATE'].dt.strftime('%Y'))
              .assign(MonthDateText=lambda x: x['EXPIRATIONDATE'].dt.strftime('%b %Y'))
              .assign(WeekText=lambda x: x['EXPIRATIONDATE'].dt.strftime('%W')))
        df['Year'] = df['EXPIRATIONDATE'].dt.year
        df['Month Year'] = df['EXPIRATIONDATE'].map(lambda dt: dt.date().replace(day=1))
        df['Week'] = df['EXPIRATIONDATE'].map(lambda dt: dt.week)
        df['YearWeekText'] = df['YearText'] + '-' + df['WeekText'] + '-0'
        df['Year Week'] = pd.to_datetime(df['YearWeekText'], format='%Y-%W-%w')
        df['Year Week'] = df['Year Week'].map(lambda t: t.date())
    elif dataset == 'last_ddl_time':
        with con() as con:
            sql = "SELECT from_tz(cast(last_ddl_time as timestamp), 'GMT') at TIME zone 'US/Eastern' as LAST_DDL_TIME FROM user_objects WHERE object_name = 'LI_DASH_EXPIRATIONDATES_TL'"
            df = pd.read_sql_query(sql=sql, con=con)
    return df.to_json(date_format='iso', orient='split')

@cache_timeout
@cache.memoize()
def dataframe(dataset):
    if dataset == 'df_ind':
        df = pd.read_json(query_data(dataset), orient='split', convert_dates=['EXPIRATIONDATE', 'Month Year', 'Year Week'])
        df['LICENSENUMBER'] = df['LICENSENUMBER'].astype(str)
        df['YearText'] = df['YearText'].astype(str)
        df['WeekText'] = df['WeekText'].astype(str)
        df['Year'] = pd.to_numeric(df['Year'])
        df['Week'] = pd.to_numeric(df['Week'])
        df['Month Year'] = df['Month Year'].dt.date
        df['Year Week'] = df['Year Week'].dt.date
    elif dataset == 'last_ddl_time':
        df = pd.read_json(query_data(dataset), orient='split')
    return df

def update_layout():
    df = dataframe('df_ind')
    last_ddl_time = dataframe('last_ddl_time')

    jobtype_options_unsorted = [{'label': 'All', 'value': 'All'}]
    for jobtype in df['JOBTYPE'].unique():
        if str(jobtype) != "nan":
            jobtype_options_unsorted.append({'label': str(jobtype), 'value': jobtype})
    jobtype_options_sorted = sorted(jobtype_options_unsorted, key=lambda k: k['label'])

    licensetype_options_unsorted = [{'label': 'All', 'value': 'All'}]
    for licensetype in df['LICENSETYPE'].unique():
        if str(licensetype) != "nan":
            licensetype_options_unsorted.append({'label': str(licensetype), 'value': licensetype})
    licensetype_options_sorted = sorted(licensetype_options_unsorted, key=lambda k: k['label'])

    return html.Div(
        children=[
            html.H1(
                'Expiration Dates',
                style={'margin-top': '10px'}
            ),
            html.H1(
                '(Trade Licenses)',
                style={'margin-bottom': '20px'}
            ),
            html.P(f"Data last updated {last_ddl_time['LAST_DDL_TIME'].iloc[0]}", style = {'text-align': 'center'}),
        html.Div([
            html.Div([
                html.P('Expiration Date'),
                dcc.DatePickerRange(
                    id='Man005TL-my-date-picker-range',
                    start_date=date.today(),
                    end_date=date.today() + relativedelta(months=+12)
                ),
            ], className='four columns', style={'margin-left': '10%'}),
            html.Div([
                html.P('Aggregate Data by...'),
                dcc.Dropdown(
                    id='expiration-dates-tl-time-agg-dropdown',
                    options=[
                        {'label': 'Month', 'value': 'Month'},
                        {'label': 'Week', 'value': 'Week'}
                    ],
                    value='Month'
                ),
            ], className='four columns', style={'margin-left': '10%'}),
        ], className='dashrow filters'),
        html.Div([
            html.Div([
                html.P('Job Type'),
                dcc.Dropdown(
                    id='Man005TL-jobtype-dropdown',
                    options=jobtype_options_sorted,
                    value='All'
                ),
            ], className='four columns', style={'margin-left': '10%'}),
            html.Div([
                html.P('License Type'),
                dcc.Dropdown(
                    id='Man005TL-licensetype-dropdown',
                    options=licensetype_options_sorted,
                    value='All',
                    searchable=True
                ),
            ], className='four columns', style={'margin-left': '10%'}),
        ], className='dashrow filters'),
        html.Div([
            html.Div([
                dcc.Graph(
                    id='expiration-dates-tl-graph',
                    config={
                        'displayModeBar': False
                    },
                    figure=go.Figure(
                        data=[],
                        layout=go.Layout(
                            yaxis=dict(
                                title='Expiring Licenses'
                            )
                        )
                    )
                )
            ], className='twelve columns'),
        ], className='dashrow'),
        html.Div([
            html.Div([
                html.Div([
                    dt.DataTable(
                        rows=[{}],
                        columns=["Job Type", "License Type", "Expiring Licenses"],
                        filterable=True,
                        sortable=True,
                        editable=False,
                        selected_row_indices=[],
                        id='Man005TL-count-table'
                    )
                ], id='Man005TL-count-table-div'),
                html.Div([
                    html.A(
                        'Download Data',
                        id='Man005TL-count-table-download-link',
                        download='Man005TLExpirationVolumesBySubmissionType-counts.csv',
                        href='',
                        target='_blank',
                    )
                ], style={'text-align': 'right'})
            ], style={'margin-left': 'auto', 'margin-right': 'auto', 'float': 'none'},
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
                        id='Man005TL-table'
                    )
                ]),
                html.Div([
                    html.A(
                        'Download Data',
                        id='Man005TL-table-download-link',
                        download='Man005TLExpirationVolumesBySubmissionType-ind-records.csv',
                        href='',
                        target='_blank',
                    )
                ], style={'text-align': 'right'})
            ], style={'margin-top': '70px', 'margin-bottom': '50px',
                      'margin-left': 'auto', 'margin-right': 'auto', 'float': 'none'})
        ], className='dashrow'),
        html.Details([
            html.Summary('Query Description'),
            html.Div([
                html.P('Approved trade license amend/renew and application '
                       'jobs and when they expire.')
            ])
        ])
    ])

layout = update_layout

def update_graph_data(selected_start, selected_end, selected_time_agg, selected_job_type, selected_license_type):
    df_selected = dataframe('df_ind')
    months = df_selected['Month Year'].unique()
    months.sort()
    weeks = df_selected[df_selected['Year Week'].notnull()]['Year Week'].unique()
    weeks.sort()

    if selected_time_agg == "Month":
        selected_months = months[(months >= datetime.strptime(selected_start, "%Y-%m-%d").date()) &
                                 (months <= datetime.strptime(selected_end, "%Y-%m-%d").date())]
    elif selected_time_agg == "Week":
        selected_weeks = weeks[(weeks >= datetime.strptime(selected_start, "%Y-%m-%d").date()) &
                                 (weeks <= datetime.strptime(selected_end, "%Y-%m-%d").date())]

    if selected_job_type != "All":
        df_selected = df_selected[df_selected['JOBTYPE'] == selected_job_type]
    if selected_license_type != "All":
        df_selected = df_selected[df_selected['LICENSETYPE'] == selected_license_type]

    if selected_time_agg == "Month":
        df_selected = (df_selected.loc[(df_selected['EXPIRATIONDATE'] >= selected_start) & (df_selected['EXPIRATIONDATE'] <= selected_end)]
                       .groupby(['Month Year', 'MonthDateText']).agg({'LICENSENUMBER': 'count'})
                       .reset_index()
                       .rename(index=str, columns={"Month Year": "Expiration Date", "MonthDateText": "DateText", "LICENSENUMBER": "Expiring Licenses"}))
        for month in selected_months:
            if month not in df_selected['Expiration Date'].values:
                df_missing_month = pd.DataFrame([[month, month.strftime('%b %Y'), 0]],
                                                columns=['Expiration Date', 'DateText', 'Expiring Licenses'])
                df_selected = df_selected.append(df_missing_month, ignore_index=True)
        return df_selected.sort_values(by='Expiration Date', ascending=False)
    elif selected_time_agg == "Week":
        df_selected = (df_selected.loc[(df_selected['EXPIRATIONDATE'] >= selected_start) & (df_selected['EXPIRATIONDATE'] <= selected_end)]
                       .groupby(['Year', 'YearText', 'Week', 'WeekText']).agg({'LICENSENUMBER': 'count'})
                       .reset_index()
                       .rename(index=str, columns={"LICENSENUMBER": "Expiring Licenses"}))
        df_selected['DateText'] = df_selected['YearText'] + ' week ' + df_selected['WeekText']
        df_selected['YearWeekText'] = df_selected['YearText'] + '-' + df_selected['WeekText'] + '-0'
        df_selected['Expiration Date'] = pd.to_datetime(df_selected['YearWeekText'], format='%Y-%W-%w')
        df_selected['Expiration Date'] = df_selected['Expiration Date'].map(lambda t: t.date())
        for week in selected_weeks:
            if week not in df_selected['Expiration Date'].values:
                df_missing_week = pd.DataFrame([[week, week.strftime('%Y %W'), 0]],
                                                columns=['Expiration Date', 'DateText', 'Expiring Licenses'])
                df_selected = df_selected.append(df_missing_week, ignore_index=True)
        return df_selected.sort_values(by='Expiration Date', ascending=False)


def count_jobs(selected_start, selected_end, selected_job_type, selected_license_type):
    df_selected = dataframe('df_ind')

    if selected_job_type != "All":
        df_selected = df_selected[df_selected['JOBTYPE'] == selected_job_type]
    if selected_license_type != "All":
        df_selected = df_selected[df_selected['LICENSETYPE'] == selected_license_type]

    df_selected = (df_selected.loc[(df_selected['EXPIRATIONDATE'] >= selected_start) & (df_selected['EXPIRATIONDATE'] <= selected_end)]
                   .groupby(['JOBTYPE', 'LICENSETYPE']).agg({'LICENSENUMBER': 'count'})
                   .reset_index()
                   .rename(index=str, columns={"JOBTYPE": "Job Type", "LICENSETYPE": "License Type", "LICENSENUMBER": "Expiring Licenses"}))
    df_selected['Expiring Licenses'] = df_selected.apply(lambda x: "{:,}".format(x['Expiring Licenses']), axis=1)
    return df_selected


def get_data_object(selected_start, selected_end, selected_job_type, selected_license_type):
    df_selected = dataframe('df_ind')

    if selected_job_type != "All":
        df_selected = df_selected[df_selected['JOBTYPE'] == selected_job_type]
    if selected_license_type != "All":
        df_selected = df_selected[df_selected['LICENSETYPE'] == selected_license_type]

    df_selected = df_selected.loc[(df_selected['EXPIRATIONDATE'] >= selected_start) & (df_selected['EXPIRATIONDATE'] <= selected_end)]
    df_selected['EXPIRATIONDATE'] = df_selected['EXPIRATIONDATE'].dt.strftime('%m/%d/%Y')  #change date format to make it consistent with other dates
    return df_selected.drop(['YearText', 'MonthDateText', 'WeekText', 'Year', 'Month Year', 'Week', 'YearWeekText', 'Year Week'], axis=1)


@app.callback(
    Output('expiration-dates-tl-graph', 'figure'),
    [Input('Man005TL-my-date-picker-range', 'start_date'),
     Input('Man005TL-my-date-picker-range', 'end_date'),
     Input('expiration-dates-tl-time-agg-dropdown', 'value'),
     Input('Man005TL-jobtype-dropdown', 'value'),
     Input('Man005TL-licensetype-dropdown', 'value')])
def update_graph(start_date, end_date, time_agg, jobtype, licensetype):
    df_results = update_graph_data(start_date, end_date, time_agg, jobtype, licensetype)
    return {
        'data': [
            go.Scatter(
                x=df_results['Expiration Date'],
                y=df_results['Expiring Licenses'],
                mode='lines',
                text=df_results['DateText'],
                hoverinfo='text+y',
                line=dict(
                    shape='spline',
                    color='rgb(26, 118, 255)'
                ),
                name='Expiring Licenses'
            )
        ],
        'layout': go.Layout(
                title='Expiring Licenses',
                yaxis=dict(
                    title='Expiring Licenses',
                    range=[0, df_results['Expiring Licenses'].max() + (df_results['Expiring Licenses'].max() / 25)]
                )
        )
    }

@app.callback(Output('Man005TL-count-table', 'rows'),
            [Input('Man005TL-my-date-picker-range', 'start_date'),
             Input('Man005TL-my-date-picker-range', 'end_date'),
             Input('Man005TL-jobtype-dropdown', 'value'),
             Input('Man005TL-licensetype-dropdown', 'value')])
def updatecount_table(start_date, end_date, jobtype, licensetype):
    df_counts = count_jobs(start_date, end_date, jobtype, licensetype)
    return df_counts.to_dict('records')

@app.callback(
            Output('Man005TL-count-table-download-link', 'href'),
            [Input('Man005TL-my-date-picker-range', 'start_date'),
             Input('Man005TL-my-date-picker-range', 'end_date'),
             Input('Man005TL-jobtype-dropdown', 'value'),
             Input('Man005TL-licensetype-dropdown', 'value')])
def update_count_table_download_link(start_date, end_date, jobtype, licensetype):
    df_counts = count_jobs(start_date, end_date, jobtype, licensetype)
    csv_string = df_counts.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string

@app.callback(Output('Man005TL-table', 'rows'),
            [Input('Man005TL-my-date-picker-range', 'start_date'),
             Input('Man005TL-my-date-picker-range', 'end_date'),
             Input('Man005TL-jobtype-dropdown', 'value'),
             Input('Man005TL-licensetype-dropdown', 'value')])
def update_table(start_date, end_date, jobtype, licensetype):
    df_ind = get_data_object(start_date, end_date, jobtype, licensetype)
    return df_ind.to_dict('records')

@app.callback(
            Output('Man005TL-table-download-link', 'href'),
            [Input('Man005TL-my-date-picker-range', 'start_date'),
             Input('Man005TL-my-date-picker-range', 'end_date'),
             Input('Man005TL-jobtype-dropdown', 'value'),
             Input('Man005TL-licensetype-dropdown', 'value')])
def update_table_download_link(start_date, end_date, jobtype, licensetype):
    df_ind = get_data_object(start_date, end_date, jobtype, licensetype)
    csv_string = df_ind.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string