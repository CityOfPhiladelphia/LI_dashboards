import dash_core_components as dcc
import dash_html_components as html
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

def get_data_object(selected_start, selected_end):
    df_selected = df.copy(deep=True)
    df_selected = df_selected.loc[(df_selected['EXPIRATIONDATE'] >= selected_start) & (df_selected['EXPIRATIONDATE'] <= selected_end)]
    df_selected['EXPIRATIONDATE'] = df_selected['EXPIRATIONDATE'].dt.strftime('%m/%d/%Y')  #change date format to make it consistent with other dates
    return df_selected

def count_jobs(selected_start, selected_end):
    df_selected = df.copy(deep=True)
    df_selected = (df_selected.loc[(df_selected['EXPIRATIONDATE'] >= selected_start) & (df_selected['EXPIRATIONDATE'] <= selected_end)]
                   .groupby(['JOBTYPE', 'LICENSETYPE']).agg({'LICENSENUMBER': 'count'})
                   .reset_index()
                   .rename(index=str, columns={"JOBTYPE": "Job Type", "LICENSETYPE": "License Type", "LICENSENUMBER": "Expiring Licenses"}))
    df_selected['Count'] = df_selected.apply(lambda x: "{:,}".format(x['Expiring Licenses']), axis=1)
    return df_selected

layout = html.Div(
    children=[
        html.H1(
            'Expiration Dates',
            style={'margin-top': '10px'}
        ),
        html.H1(
            '(Business Licenses)',
            style={'margin-bottom': '50px'}
        ),
        html.Div(
            children=[
                'Expiration Date'
            ],
            style={'margin-left': '5%', 'margin-top': '10px', 'margin-bottom': '5px'}
        ),
        html.Div([
            dcc.DatePickerRange(
                id='Man005BL-my-date-picker-range',
                start_date=date.today(),
                end_date=date.today() + relativedelta(months=+3)
            ),
        ], style={'margin-left': '5%', 'margin-bottom': '25px'}),
        html.Div([
            html.Div([
                html.Div([
                    dt.DataTable(
                        rows=[{}],
                        columns=["Job Type", "License Type", "Expiring Licenses"],
                        filterable=True,
                        sortable=True,
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
        ], className='dashrow')
    ]
)

@app.callback(Output('Man005BL-count-table', 'rows'),
            [Input('Man005BL-my-date-picker-range', 'start_date'),
            Input('Man005BL-my-date-picker-range', 'end_date')])
def updatecount_table(start_date, end_date):
    df_counts = count_jobs(start_date, end_date)
    return df_counts.to_dict('records')

@app.callback(
            Output('Man005BL-count-table-download-link', 'href'),
            [Input('Man005BL-my-date-picker-range', 'start_date'),
            Input('Man005BL-my-date-picker-range', 'end_date')])
def update_count_table_download_link(start_date, end_date):
    df_counts = count_jobs(start_date, end_date)
    csv_string = df_counts.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string

@app.callback(Output('Man005BL-table', 'rows'),
            [Input('Man005BL-my-date-picker-range', 'start_date'),
            Input('Man005BL-my-date-picker-range', 'end_date')])
def update_table(start_date, end_date):
    df_inv = get_data_object(start_date, end_date)
    return df_inv.to_dict('records')

@app.callback(
            Output('Man005BL-table-download-link', 'href'),
            [Input('Man005BL-my-date-picker-range', 'start_date'),
            Input('Man005BL-my-date-picker-range', 'end_date')])
def update_table_download_link(start_date, end_date):
    df_inv = get_data_object(start_date, end_date)
    csv_string = df_inv.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string