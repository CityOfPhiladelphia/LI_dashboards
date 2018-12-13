import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
from dash.dependencies import Input, Output
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import dash_table_experiments as dt
import urllib.parse

from app import app, con


print("Man005BLExpirationDates.py")

with con() as con:
    sql = 'SELECT * FROM li_dash_expirationdates_bl'
    df = pd.read_sql_query(sql=sql, con=con, parse_dates=['EXPIRATIONDATE'])

df = (df.assign(YearText=lambda x: x['EXPIRATIONDATE'].dt.strftime('%Y'))
      .assign(MonthDateText=lambda x: x['EXPIRATIONDATE'].dt.strftime('%b %Y'))
      .assign(WeekText=lambda x: x['EXPIRATIONDATE'].dt.strftime('%W'))
      .assign(DayDateText=lambda x: x['EXPIRATIONDATE'].dt.strftime('%b %d %Y')))

df['Year'] = df['EXPIRATIONDATE'].dt.year
df['Month Year'] = df['EXPIRATIONDATE'].map(lambda dt: dt.date().replace(day=1))
df['Week'] = df['EXPIRATIONDATE'].map(lambda dt: dt.week)
df['Job Created Day'] = df['EXPIRATIONDATE'].dt.date

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


def update_graph_data(selected_start, selected_end, selected_time_agg, selected_job_type, selected_license_type):
    df_selected = df.copy(deep=True)

    if selected_job_type != "All":
        df_selected = df_selected[df_selected['JOBTYPE'] == selected_job_type]
    if selected_license_type != "All":
        df_selected = df_selected[df_selected['LICENSETYPE'] == selected_license_type]

    if selected_time_agg == "Month":
        df_selected = (df_selected.loc[(df_selected['EXPIRATIONDATE'] >= selected_start) & (df_selected['EXPIRATIONDATE'] <= selected_end)]
                       .groupby(['Month Year', 'MonthDateText']).agg({'LICENSENUMBER': 'count'})
                       .reset_index()
                       .rename(index=str, columns={"Month Year": "Expiration Date", "MonthDateText": "DateText", "LICENSENUMBER": "Expiring Licenses"})
                       .sort_values(by='Expiration Date', ascending=False))
    if selected_time_agg == "Week":
        df_selected = (df_selected.loc[(df_selected['EXPIRATIONDATE'] >= selected_start) & (df_selected['EXPIRATIONDATE'] <= selected_end)]
                       .groupby(['Year', 'YearText', 'Week', 'WeekText']).agg({'LICENSENUMBER': 'count'})
                       .reset_index()
                       .rename(index=str, columns={"LICENSENUMBER": "Expiring Licenses"}))
        df_selected['DateText'] = df_selected['YearText'] + ' week ' + df_selected['WeekText']
        df_selected['YearWeekText'] = df_selected['YearText'] + '-' + df_selected['WeekText'] + '-0'
        df_selected['Expiration Date'] = pd.to_datetime(df_selected['YearWeekText'], format='%Y-%W-%w')
        df_selected.sort_values(by='Expiration Date', ascending=True, inplace=True)
    if selected_time_agg == "Day":
        df_selected = (df_selected.loc[(df_selected['EXPIRATIONDATE'] >= selected_start) & (df_selected['EXPIRATIONDATE'] <= selected_end)]
                       .groupby(['Job Created Day', 'DayDateText']).agg({'LICENSENUMBER': 'count'})
                       .reset_index()
                       .rename(index=str, columns={"Job Created Day": "Expiration Date", "DayDateText": "DateText", "LICENSENUMBER": "Expiring Licenses"})
                       .sort_values(by='Expiration Date', ascending=False))
    return df_selected


def count_jobs(selected_start, selected_end, selected_job_type, selected_license_type):
    df_selected = df.copy(deep=True)

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
    df_selected = df.copy(deep=True)

    if selected_job_type != "All":
        df_selected = df_selected[df_selected['JOBTYPE'] == selected_job_type]
    if selected_license_type != "All":
        df_selected = df_selected[df_selected['LICENSETYPE'] == selected_license_type]

    df_selected = df_selected.loc[(df_selected['EXPIRATIONDATE'] >= selected_start) & (df_selected['EXPIRATIONDATE'] <= selected_end)]
    df_selected['EXPIRATIONDATE'] = df_selected['EXPIRATIONDATE'].dt.strftime('%m/%d/%Y')  #change date format to make it consistent with other dates
    return df_selected.drop(['YearText', 'MonthDateText', 'WeekText', 'DayDateText', 'Year', 'Month Year', 'Week', 'Job Created Day'], axis=1)

layout = html.Div(
    children=[
        html.H1(
            'Expiration Dates',
            style={'margin-top': '10px'}
        ),
        html.H1(
            '(Business Licenses)',
            style={'margin-bottom': '20px'}
        ),
        html.Div([
            html.Div([
                html.P('Expiration Date'),
                dcc.DatePickerRange(
                    id='Man005BL-my-date-picker-range',
                    start_date=date.today(),
                    end_date=date.today() + relativedelta(months=+12)
                ),
            ], className='four columns', style={'margin-left': '10%'}),
            html.Div([
                html.P('Aggregate Data by...'),
                dcc.Dropdown(
                    id='expiration-dates-bl-time-agg-dropdown',
                    options=[
                        {'label': 'Month', 'value': 'Month'},
                        {'label': 'Week', 'value': 'Week'},
                        {'label': 'Day', 'value': 'Day'}
                    ],
                    value='Month'
                ),
            ], className='four columns', style={'margin-left': '10%'}),
        ], className='dashrow filters'),
        html.Div([
            html.Div([
                html.P('Job Type'),
                dcc.Dropdown(
                    id='Man005BL-jobtype-dropdown',
                    options=jobtype_options_sorted,
                    value='All'
                ),
            ], className='four columns', style={'margin-left': '10%'}),
            html.Div([
                html.P('License Type'),
                dcc.Dropdown(
                    id='Man005BL-licensetype-dropdown',
                    options=licensetype_options_sorted,
                    value='All',
                    searchable=True
                ),
            ], className='four columns', style={'margin-left': '10%'}),
        ], className='dashrow filters'),
        html.Div([
            html.Div([
                dcc.Graph(id='expiration-dates-bl-graph',
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
                        id='Man005BL-count-table'
                    )
                ], id='Man005BL-count-table-div'),
                html.Div([
                    html.A(
                        'Download Data',
                        id='Man005BL-count-table-download-link',
                        download='Man005BLExpirationVolumesBySubmissionType-counts.csv',
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
                        id='Man005BL-table'
                    )
                ]),
                html.Div([
                    html.A(
                        'Download Data',
                        id='Man005BL-table-download-link',
                        download='Man005BLExpirationVolumesBySubmissionType-ind-records.csv',
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
                html.P('Approved business license amend/renew and application '
                       'jobs and when they expire. (Doesn\'t include commercial activity licenses)')
            ])
        ])
    ]
)


@app.callback(
    Output('expiration-dates-bl-graph', 'figure'),
    [Input('Man005BL-my-date-picker-range', 'start_date'),
     Input('Man005BL-my-date-picker-range', 'end_date'),
     Input('expiration-dates-bl-time-agg-dropdown', 'value'),
     Input('Man005BL-jobtype-dropdown', 'value'),
     Input('Man005BL-licensetype-dropdown', 'value')])
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

@app.callback(Output('Man005BL-count-table', 'rows'),
            [Input('Man005BL-my-date-picker-range', 'start_date'),
             Input('Man005BL-my-date-picker-range', 'end_date'),
             Input('Man005BL-jobtype-dropdown', 'value'),
             Input('Man005BL-licensetype-dropdown', 'value')])
def updatecount_table(start_date, end_date, jobtype, licensetype):
    df_counts = count_jobs(start_date, end_date, jobtype, licensetype)
    return df_counts.to_dict('records')

@app.callback(
            Output('Man005BL-count-table-download-link', 'href'),
            [Input('Man005BL-my-date-picker-range', 'start_date'),
             Input('Man005BL-my-date-picker-range', 'end_date'),
             Input('Man005BL-jobtype-dropdown', 'value'),
             Input('Man005BL-licensetype-dropdown', 'value')])
def update_count_table_download_link(start_date, end_date, jobtype, licensetype):
    df_counts = count_jobs(start_date, end_date, jobtype, licensetype)
    csv_string = df_counts.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string

@app.callback(Output('Man005BL-table', 'rows'),
            [Input('Man005BL-my-date-picker-range', 'start_date'),
             Input('Man005BL-my-date-picker-range', 'end_date'),
             Input('Man005BL-jobtype-dropdown', 'value'),
             Input('Man005BL-licensetype-dropdown', 'value')])
def update_table(start_date, end_date, jobtype, licensetype):
    df_inv = get_data_object(start_date, end_date, jobtype, licensetype)
    return df_inv.to_dict('records')

@app.callback(
            Output('Man005BL-table-download-link', 'href'),
            [Input('Man005BL-my-date-picker-range', 'start_date'),
             Input('Man005BL-my-date-picker-range', 'end_date'),
             Input('Man005BL-jobtype-dropdown', 'value'),
             Input('Man005BL-licensetype-dropdown', 'value')])
def update_table_download_link(start_date, end_date, jobtype, licensetype):
    df_inv = get_data_object(start_date, end_date, jobtype, licensetype)
    csv_string = df_inv.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string