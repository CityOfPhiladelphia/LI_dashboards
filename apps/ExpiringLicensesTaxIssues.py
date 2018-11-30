import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as table
import plotly.graph_objs as go
import pandas as pd
from dash.dependencies import Input, Output
from datetime import datetime
import numpy as np
import urllib.parse

from app import app, con_CLOUD

testing_mode = False
print('ExpiringLicensesTaxIssues.py')
print('Testing mode: ' + str(testing_mode))

if testing_mode:
    df = pd.read_csv('test_data/expiring_licenses.csv', parse_dates=['EXPIRATIONDATE'])

else:
    with con_CLOUD() as con:
        sql = 'SELECT DISTINCT * FROM expiring_licenses'
        df = pd.read_sql_query(sql=sql, con=con, parse_dates=['EXPIRATIONDATE'])

# Rename the columns to be more readable
df = (df.rename(columns={'LEGALNAME': 'Legal Name', 
                         'BUSINESS_NAME': 'Business Name',
                         'LICENSETYPE': 'License Type',
                         'EXPIRATIONDATE': 'Expiration Date',
                         'OWNEROCCUPIED': 'Owner Occupied',
                         'MESSAGE': 'Message',
                         'BUSINESSID': 'Business ID',
                         'LICENSENUMBER': 'License Number',
                         'LINK': 'Link'}))

message_values_with_issues = ['ACCOUNT AND ENTITY NOT RELATED', 
                              'EIN, SSN OR ACCOUNT ID MUST BE FILLED IN',
                              'ENTITY/ACCOUNT NOT FOUND']

summary_table = (df.copy(deep=True)
                   .groupby(['Message'])['License Number'].count()
                   .reset_index()
                   .rename(columns={'Message': 'Message Category',
                                    'License Number': 'Count'}))

total_with_issues = summary_table[summary_table['Message Category'].isin(message_values_with_issues)]['Count'].sum()
total = summary_table['Count'].sum()
                                                                    
summary_table = (summary_table.append({'Message Category': 'Total With Issues',
                                      'Count': total_with_issues}, ignore_index=True)
                              .append({'Message Category': 'Total',
                                       'Count': total}, ignore_index=True))

summary_table['Count'] = summary_table.apply(lambda x: "{:,}".format(x['Count']), axis=1)

unique_messages = message_values_with_issues
unique_messages = np.append(['All'], unique_messages)

unique_license_types = df['License Type'].unique()
unique_license_types = np.append(['All'], unique_license_types)

def update_data(selected_start, selected_end, selected_message, selected_license_type):
    df_selected = df.copy(deep=True)

    if selected_message != "All":
        df_selected = df_selected[(df_selected['Message'] == selected_message)]
    if selected_license_type != "All":
        df_selected = df_selected[(df_selected['License Type'] == selected_license_type)]

    df_selected = (df_selected.loc[(df_selected['Expiration Date'] >= selected_start) & (df_selected['Expiration Date'] <= selected_end)]
                              .sort_values(by='Expiration Date'))

    return df_selected


def update_table_data(selected_start, selected_end, selected_message, selected_license_type):
    df_selected = update_data(selected_start, selected_end, selected_message, selected_license_type)
    return df_selected[df_selected['Message'].isin(message_values_with_issues)]

layout = html.Div(children=[
                html.H1('Expiring Licenses with Tax Issues', style={'text-align': 'center'}),
                html.P('This dashboard is used for data clean up only.', style={'text-align': 'center'}),
                html.P(f'Data last updated {df["Expiration Date"].min().date()}.', style={'text-align': 'center'}),
                html.Div([
                    html.Div([
                        html.P('Filter by Date Range'),
                        dcc.DatePickerRange(
                            id='expiring-licenses-date-picker-range',
                            start_date=df['Expiration Date'].min(),
                            end_date=df['Expiration Date'].max()
                        ),
                    ], className='four columns'),
                    html.Div([
                        html.P('Filter by Message'),
                        dcc.Dropdown(
                                id='expiring-licenses-message-dropdown',
                                options=[{'label': k, 'value': k} for k in unique_messages],
                                value='All'
                        ),
                    ], className='four columns'),
                    html.Div([
                        html.P('Filter by License Type'),
                        dcc.Dropdown(
                            id='expiring-licenses-license-type-dropdown',
                            options=[{'label': k, 'value': k} for k in unique_license_types],
                            value='All'
                        ),
                    ], className='four columns'),
                ], className='dashrow filters',
                   style={'width': '100%', 'margin-left': 'auto', 'margin-right': 'auto'}
                ),
                html.Div([
                    html.Div([
                        html.Div([
                            table.DataTable(
                                rows=[{}],
                                editable=False,
                                sortable=True,
                                filterable=True,
                                id='expiring-licenses-table'
                            ),
                        ], id='expiring-licenses-table-div'),
                        html.Div([
                            html.A(
                                'Download Data',
                                id='expiring-licenses-table-download-link',
                                download='expiring-licenses.csv',
                                href='',
                                target='_blank',
                            )
                        ], style={'text-align': 'right'})
                    ], style={'width': '100%', 'margin-left': 'auto', 'margin-right': 'auto','margin-top': '50px', 'margin-bottom': '50px'})
                ], className='dashrow'),
                html.Div([
                    html.Div([
                        html.H2('Summary Table', style={'text-align': 'center'}),
                        html.Div([
                            table.DataTable(
                                rows=summary_table.to_dict('records'),
                                columns=summary_table.columns,
                                editable=False,
                                id='expiring-licenses-summary-table'
                            ),
                        ], id='expiring-licenses-summary-table-div'),
                        html.Div([
                            html.A(
                                'Download Data',
                                id='expiring-licenses-summary-table-download-link',
                                download='expiring-licenses-summary.csv',
                                href='',
                                target='_blank',
                            )
                        ], style={'text-align': 'right'})
                    ], style={'width': '55%', 'margin-left': 'auto', 'margin-right': 'auto','margin-top': '50px', 'margin-bottom': '50px'})
                ], className='dashrow'),
            ])

@app.callback(
    Output('expiring-licenses-table', 'rows'),
    [Input('expiring-licenses-date-picker-range', 'start_date'),
     Input('expiring-licenses-date-picker-range', 'end_date'),
     Input('expiring-licenses-message-dropdown', 'value'),
     Input('expiring-licenses-license-type-dropdown', 'value'),])
def update_table(start_date, end_date, message, license_type):
    df_results = update_table_data(start_date, end_date, message, license_type)
    return df_results.to_dict('records')


@app.callback(
    Output('expiring-licenses-table-download-link', 'href'),
    [Input('expiring-licenses-date-picker-range', 'start_date'),
     Input('expiring-licenses-date-picker-range', 'end_date'),
     Input('expiring-licenses-message-dropdown', 'value'),
     Input('expiring-licenses-license-type-dropdown', 'value')])
def update_table_download_link(start_date, end_date, message, license_type):
    df_results = update_table_data(start_date, end_date, message, license_type)
    csv_string = df_results.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string