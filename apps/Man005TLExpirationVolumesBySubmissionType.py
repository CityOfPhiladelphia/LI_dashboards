import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output
from datetime import datetime
import dash_table_experiments as dt
import urllib.parse

from app import app, con

testing_mode = False
print("Man005TLExpirationVolumesBySubmissionType.py")
print("Testing mode? " + str(testing_mode))

if testing_mode:
    df = pd.read_csv("test_data/Man005TLExpirationVolumesBySubmissionType_test_data_short.csv")
else:
    with con() as con:
        with open(r'queries/Man005TLExpirationVolumesBySubmissionType.sql') as sql:
            df = pd.read_sql_query(sql=sql.read(), con=con)
    
#make sure ExpirationDate column is of type datetime so that filtering of dataframe based on date can happen later
df['ExpirationDate'] = pd.to_datetime(df['ExpirationDate'], errors = 'coerce')

def get_data_object(selected_start, selected_end):
    df_selected = df[(df['ExpirationDate']>=selected_start)&(df['ExpirationDate']<=selected_end)]
    df_selected['ExpirationDate'] = df_selected['ExpirationDate'].dt.strftime('%m/%d/%Y')  #change date format to make it consistent with other dates
    df_selected['JobType'] = df_selected['JobType'].map(lambda x: str(x)[5:]) #strip first five characters "j_BL_" just to make it easier for user to read
    return df_selected

def count_jobs(selected_start, selected_end):
    df_countselected = df[(df['ExpirationDate']>=selected_start)&(df['ExpirationDate']<=selected_end)]
    df_counter = df_countselected.groupby(by=['JobType', 'LicenseType'], as_index=False).size().reset_index()
    df_counter = df_counter.rename(index=str, columns={"JobType": "JobType", "LicenseType": "LicenseType", 0: "Count"})
    df_counter['JobType'] = df_counter['JobType'].map(lambda x: str(x)[5:]) #strip first five characters "j_BL_" just to make it easier for user to read
    df_counter['Count'] = df_counter.apply(lambda x: "{:,}".format(x['Count']), axis=1)
    return df_counter

layout = html.Div(
    children=[
        html.H1(
            'Trade License Expirations by Type',
            style={'margin-top': '10px', 'margin-bottom': '50px'}
        ),
        html.Div(
            children=[
                'Please Select Date Range (Job Created Date)'
            ],
            style={'margin-left': '5%', 'margin-top': '10px', 'margin-bottom': '5px'}
        ),
        html.Div([
            dcc.DatePickerRange(
                id='Man005TL-my-date-picker-range',
                start_date=datetime(2018, 1, 1),
                end_date=datetime.now()
            ),
        ], style={'margin-left': '5%', 'margin-bottom': '25px'}),
        html.Div([
            html.Div([
                html.Div([
                    dt.DataTable(
                        rows=[{}],
                        columns=["JobType", "LicenseType", "Count"],
                        row_selectable=True,
                        filterable=True,
                        sortable=True,
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
                ])
            ], style={'margin-left': 'auto', 'margin-right': 'auto', 'float': 'none'},
               className = 'nine columns')
        ], className='dashrow'),
        html.Div([
            html.Div([
                html.Div([
                    dt.DataTable(
                        rows=[{}],
                        row_selectable=True,
                        filterable=True,
                        sortable=True,
                        selected_row_indices=[],
                        id='Man005TL-table'
                    )
                ], style={'text-align': 'center'}),
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
        ], className='dashrow')
    ]
)


@app.callback(Output('Man005TL-count-table', 'rows'),
              [Input('Man005TL-my-date-picker-range', 'start_date'),
               Input('Man005TL-my-date-picker-range', 'end_date')])
def updatecount_table(start_date, end_date):
    df_counts = count_jobs(start_date, end_date)
    return df_counts.to_dict('records')


@app.callback(Output('Man005TL-count-table-download-link', 'href'),
              [Input('Man005TL-my-date-picker-range', 'start_date'),
               Input('Man005TL-my-date-picker-range', 'end_date')])
def update_count_table_download_link(start_date, end_date):
    df_results = count_jobs(start_date, end_date)
    csv_string = df_results.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string


@app.callback(Output('Man005TL-table', 'rows'),
              [Input('Man005TL-my-date-picker-range', 'start_date'),
               Input('Man005TL-my-date-picker-range', 'end_date')])
def update_table(start_date, end_date):
    df_inv = get_data_object(start_date, end_date)
    return df_inv.to_dict('records')

@app.callback(Output('Man005TL-table-download-link', 'href'),
              [Input('Man005TL-my-date-picker-range', 'start_date'),
               Input('Man005TL-my-date-picker-range', 'end_date')])
def update_table_download_link(start_date, end_date):
    df_results = get_data_object(start_date, end_date)
    csv_string = df_results.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string
