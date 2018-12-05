import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output
from datetime import datetime
import dash_table_experiments as dt
import urllib.parse

from app import app, con


print("Man005BLExpirationVolumesBySubmissionType.py")

with con() as con:
    sql = 'SELECT * FROM li_dash_expvolsbysubtype_bl'
    df = pd.read_sql_query(sql=sql, con=con)
    
#make sure EXPIRATIONDATE column is of type datetime so that filtering of dataframe based on date can happen later
df['EXPIRATIONDATE'] = pd.to_datetime(df['EXPIRATIONDATE'], errors = 'coerce')

def get_data_object(selected_start, selected_end):
    df_selected = df[(df['EXPIRATIONDATE']>=selected_start)&(df['EXPIRATIONDATE']<=selected_end)]
    df_selected['EXPIRATIONDATE'] = df_selected['EXPIRATIONDATE'].dt.strftime('%m/%d/%Y')  #change date format to make it consistent with other dates
    df_selected['JOBTYPE'] = df_selected['JOBTYPE'].map(lambda x: str(x)[5:]) #strip first five characters "j_BL_" just to make it easier for user to read
    return df_selected

def count_jobs(selected_start, selected_end):
    df_countselected = df[(df['EXPIRATIONDATE']>=selected_start)&(df['EXPIRATIONDATE']<=selected_end)]
    df_counter = df_countselected.groupby(by=['JOBTYPE', 'LICENSETYPE'], as_index=False).size().reset_index()
    df_counter = df_counter.rename(index=str, columns={"JOBTYPE": "JobType", "LICENSETYPE": "LicenseType", 0: "Count"})
    df_counter['JobType'] = df_counter['JobType'].map(lambda x: str(x)[5:]) #strip first five characters "j_BL_" just to make it easier for user to read
    df_counter['Count'] = df_counter.apply(lambda x: "{:,}".format(x['Count']), axis=1)
    return df_counter

layout = html.Div(
    children=[
        html.H1(
            'Business License Expirations by Type',
            style = {'margin-top': '10px', 'margin-bottom': '50px'}
        ),
        html.Div(
            children=[
                'Please Select Date Range (Job Created Date)'
            ],
            style={'margin-left': '5%', 'margin-top': '10px', 'margin-bottom': '5px'}
        ),
        html.Div([
            dcc.DatePickerRange(
                id='Man005BL-my-date-picker-range',
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
                        row_selectable=True,
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
    df = count_jobs(start_date, end_date)
    csv_string = df.to_csv(index=False, encoding='utf-8')
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
    df = get_data_object(start_date, end_date)
    csv_string = df.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string