import os
import urllib.parse
from datetime import datetime

import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output
import dash_table_experiments as dt
import urllib.parse

from app import app, cache, cache_timeout

APP_NAME = os.path.basename(__file__)

print(APP_NAME)

@cache_timeout
@cache.memoize()
def query_data(dataset):
    from app import con
    with con() as con:
        if dataset == 'df_ind':
            sql = 'SELECT * FROM li_dash_uninsp_bl_comp_check'
            df = pd.read_sql_query(sql=sql, con=con, parse_dates=['MOSTRECENTCCFIELD'])
        elif dataset == 'last_ddl_time':
            sql = "SELECT from_tz(cast(last_ddl_time as timestamp), 'GMT') at TIME zone 'US/Eastern' as LAST_DDL_TIME FROM user_objects WHERE object_name = 'LI_DASH_UNINSP_BL_COMP_CHECK'"
            df = pd.read_sql_query(sql=sql, con=con)
    return df.to_json(date_format='iso', orient='split')

def dataframe(dataset):
    return pd.read_json(query_data(dataset), orient='split')

def update_layout():
    df = dataframe('df_ind')
    last_ddl_time = dataframe('last_ddl_time')

    licensetype_options_unsorted = [{'label': 'All', 'value': 'All'}]
    for licensetype in df['LICENSETYPE'].unique():
        if str(licensetype) != "nan":
            licensetype_options_unsorted.append({'label': str(licensetype), 'value': licensetype})
    licensetype_options_sorted = sorted(licensetype_options_unsorted, key=lambda k: k['label'])

    return html.Div(
        children=[
            html.H1(
                'Uninspected Business Licenses with Completed Completeness Checks',
                style={'margin-top': '10px', 'margin-bottom': '50px'}
            ),
            html.P(f"Data last updated {last_ddl_time['LAST_DDL_TIME'].iloc[0]}", style = {'text-align': 'center'}),
            html.Div([
                html.Div([
                    html.P('Most Recent Completeness Check Completed Date'),
                    dcc.DatePickerRange(
                        id='completeness-check-date-range',
                        start_date=datetime(2018, 1, 1),
                        end_date=datetime.now()
                    ),
                ], className='six columns'),
                html.Div([
                    html.P('License Type'),
                    dcc.Dropdown(
                        id='licensetype-dropdown',
                        options=licensetype_options_sorted,
                        value='All',
                        searchable=True
                    ),
                ], className='six columns'),
            ], className='dashrow filters'),
            html.Div([
                html.Div([
                    html.Div([
                        dt.DataTable(
                            rows=[{}],
                            filterable=True,
                            sortable=True,
                            id='summary-table'
                        )
                    ], id='summary-table-div'),
                    html.Div([
                        html.A(
                            'Download Data',
                            id='summary-table-download-link',
                            download='LicensesWithCompletenessChecksButNoCompletedInspections_summary.csv',
                            href='',
                            target='_blank',
                        )
                    ], style={'text-align': 'right'})
                ], style={'margin-left': 'auto', 'margin-right': 'auto', 'float': 'none'},
                    className='twelve columns')
            ], className='dashrow'),
            html.Div([
                html.Div([
                    html.Div([
                        dt.DataTable(
                            rows=[{}],
                            filterable=True,
                            sortable=True,
                            id='table'
                        )
                    ]),
                    html.Div([
                        html.A(
                            'Download Data',
                            id='table-download-link',
                            download='LicensesWithCompletenessChecksButNoCompletedInspections.csv',
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
                    html.P("Business licenses with completed completeness checks, but no completed inspections."),
                    html.P("Excluding license types that have never had an inspection created:"),
                    html.Ul(children=[
                        html.Li('Activity'),
                        html.Li('Amusement'),
                        html.Li('Annual Pole'),
                        html.Li('Bingo'),
                        html.Li('Carnival'),
                        html.Li('Dumpster License - Construction'),
                        html.Li('Food Caterer'),
                        html.Li('Food Estab Retail Non-Permanent Location (Event)'),
                        html.Li('Food Establishment Outdoor'),
                        html.Li('Food Establishment Retail Perm Location (Large)'),
                        html.Li('Food Manufacturer / Wholesaler'),
                        html.Li('Food Preparing and Serving'),
                        html.Li('Handbill Distribution'),
                        html.Li('Honor Box'),
                        html.Li('Limited Occasion'),
                        html.Li('Outdoor Advertising Sign'),
                        html.Li('Overhead Wire'),
                        html.Li('Pawn Shop'),
                        html.Li('Precious Metal Dealer'),
                        html.Li('Promoter Registration'),
                        html.Li('Public Garage / Parking Lot'),
                        html.Li('Rental'),
                        html.Li('Scales and Scanners'),
                        html.Li('Sidewalk Cafe'),
                        html.Li('Small Games Of Chance'),
                        html.Li('Special Permit'),
                        html.Li('Tow Company'),
                        html.Li('Vacant Commercial Property'),
                        html.Li('Vacant Residential Property / Lot'),
                        html.Li('Vendor - Center City Vendor'),
                        html.Li('Vendor - Motor Vehicle Sales'),
                        html.Li('Vendor - Neighborhood Vending District'),
                        html.Li('Vendor - On Foot'),
                        html.Li('Vendor - Pushcart'),
                        html.Li('Vendor - Sidewalk Sales'),
                        html.Li('Vendor - Special Vending')
                    ])
                ])
            ])
        ])

layout = update_layout

def get_summary_data(selected_start, selected_end, selected_license_type):
    df_selected = dataframe('df_ind')

    if selected_license_type != "All":
        df_selected = df_selected[(df_selected['LICENSETYPE'] == selected_license_type)]

    df_selected = (df_selected.loc[(df_selected['MOSTRECENTCCFIELD'] >= selected_start) & (df_selected['MOSTRECENTCCFIELD'] <= selected_end)]
                   .groupby(['LICENSETYPE']).count()
                   .reset_index()
                   .rename(columns={'LICENSETYPE': 'License Type', 'LICENSENUMBER': 'Licenses',
                                    'INSPECTIONCREATEDDATE': 'Inspections Created',
                                    'SCHEDULEDINSPECTIONDATE': 'Inspections Scheduled',
                                    'INSPECTIONCOMPLETEDDATE': 'Inspections Completed'})
                   .sort_values(by=['Licenses'], ascending=False))
    return df_selected.drop(['MOSTRECENTISSUEDATE', 'MOSTRECENTCOMPLETENESSCHECK', 'MOSTRECENTCCFIELD', 'EXPIRATIONDATE', 'JOBLINK'], axis=1)


def get_ind_records_data(selected_start, selected_end, selected_license_type):
    df_selected = dataframe('df_ind')

    if selected_license_type != "All":
        df_selected = df_selected[(df_selected['LICENSETYPE'] == selected_license_type)]
        
    df_selected = (df_selected.loc[(df_selected['MOSTRECENTCCFIELD'] >= selected_start) & (df_selected['MOSTRECENTCCFIELD'] <= selected_end)]
                   .rename(columns={'LICENSENUMBER': 'License Number', 'LICENSETYPE': 'License Type',
                                    'MOSTRECENTISSUEDATE': 'Most Recent Issue Date',
                                    'MOSTRECENTCOMPLETENESSCHECK': 'Most Recent Completeness Check',
                                    'EXPIRATIONDATE': 'Expiration Date',
                                    'INSPECTIONCREATEDDATE': 'Inspection Created Date',
                                    'SCHEDULEDINSPECTIONDATE': 'Inspection Scheduled Date',
                                    'INSPECTIONCOMPLETEDDATE': 'Inspection Completed Date',
                                    'JOBLINK': 'Job Link'})
                   .sort_values(by=['MOSTRECENTCCFIELD']))
    return df_selected.drop(['MOSTRECENTCCFIELD'], axis=1)



@app.callback(Output('summary-table', 'rows'),
            [Input('completeness-check-date-range', 'start_date'),
            Input('completeness-check-date-range', 'end_date'),
            Input('licensetype-dropdown', 'value')])
def update_summary_table(start_date, end_date, licensetype):
    df_summary = get_summary_data(start_date, end_date, licensetype)
    return df_summary.to_dict('records')

@app.callback(
            Output('summary-table-download-link', 'href'),
            [Input('completeness-check-date-range', 'start_date'),
            Input('completeness-check-date-range', 'end_date'),
            Input('licensetype-dropdown', 'value')])
def update_summary_table_download_link(start_date, end_date, licensetype):
    df_summary = get_summary_data(start_date, end_date, licensetype)
    csv_string = df_summary.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string

@app.callback(Output('table', 'rows'),
            [Input('completeness-check-date-range', 'start_date'),
            Input('completeness-check-date-range', 'end_date'),
            Input('licensetype-dropdown', 'value')])
def update_table(start_date, end_date, licensetype):
    df_ind = get_ind_records_data(start_date, end_date, licensetype)
    return df_ind.to_dict('records')

@app.callback(
            Output('table-download-link', 'href'),
            [Input('completeness-check-date-range', 'start_date'),
            Input('completeness-check-date-range', 'end_date'),
            Input('licensetype-dropdown', 'value')])
def update_table_download_link(start_date, end_date, licensetype):
    df_ind = get_ind_records_data(start_date, end_date, licensetype)
    csv_string = df_ind.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string