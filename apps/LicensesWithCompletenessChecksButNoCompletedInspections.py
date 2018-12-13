import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output
from datetime import datetime
import dash_table_experiments as dt
import urllib.parse

from app import app, con

print("LicensesWithCompletenessChecksButNoCompletedInspections.py")

with con() as con:
    sql = 'SELECT * FROM li_dash_licenseswcompleteness'
    df = pd.read_sql_query(sql=sql, con=con,
                            parse_dates=['MOSTRECENTCCFIELD'])

licensetype_options_unsorted = [{'label': 'All', 'value': 'All'}]
for licensetype in df['LICENSETYPE'].unique():
    if str(licensetype) != "nan":
        licensetype_options_unsorted.append({'label': str(licensetype), 'value': licensetype})
licensetype_options_sorted = sorted(licensetype_options_unsorted, key=lambda k: k['label'])

def get_summary_data(selected_start, selected_end, selected_license_type):
    df_selected = df.copy(deep=True)

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
    return df_selected.drop(['MOSTRECENTISSUEDATE', 'MOSTRECENTCOMPLETENESSCHECK', 'MOSTRECENTCCFIELD', 'EXPIRATIONDATE'], axis=1)


def get_ind_records_data(selected_start, selected_end, selected_license_type):
    df_selected = df.copy(deep=True)

    if selected_license_type != "All":
        df_selected = df_selected[(df_selected['LICENSETYPE'] == selected_license_type)]
        
    df_selected = (df_selected.loc[(df_selected['MOSTRECENTCCFIELD'] >= selected_start) & (df_selected['MOSTRECENTCCFIELD'] <= selected_end)]
                   .rename(columns={'LICENSENUMBER': 'License Number', 'LICENSETYPE': 'License Type',
                                    'MOSTRECENTISSUEDATE': 'Most Recent Issue Date',
                                    'MOSTRECENTCOMPLETENESSCHECK': 'Most Recent Completeness Check',
                                    'EXPIRATIONDATE': 'Expiration Date',
                                    'INSPECTIONCREATEDDATE': 'Inspection Created Date',
                                    'SCHEDULEDINSPECTIONDATE': 'Inspection Scheduled Date',
                                    'INSPECTIONCOMPLETEDDATE': 'Inspection Completed Date'})
                   .sort_values(by=['MOSTRECENTCCFIELD']))
    return df_selected.drop(['MOSTRECENTCCFIELD'], axis=1)



layout = html.Div(
    children=[
        html.H1(
            'Business Licenses with Completed Completeness Checks but No Completed Inspection',
            style={'margin-top': '10px', 'margin-bottom': '50px'}
        ),
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
                html.P(
                    'Business licenses with completed completeness checks, but no completed inspections.')
            ])
        ])
    ]
)

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