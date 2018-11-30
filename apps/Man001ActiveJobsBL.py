import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from dash.dependencies import Input, Output
import urllib.parse

from app import app, con

testing_mode = False
print("Man001ActiveJobsBL.py")
print("Testing mode? " + str(testing_mode))

#Definitions: Job Type BL Application and BL Amendment/Renewal
#Completeness Check Completed, Job incomplete
#Not in Status: More Information Required, Payment Pending, Application Incomplete, Draft
#time calculated as time between completion of completeness check to today

if testing_mode:
    df_table = pd.read_csv("test_data/Man001ActiveJobsBLIndividualRecords_test_data.csv")
    df_counts = pd.read_csv("test_data/Man001ActiveJobsBLCounts_test_data.csv")
else:
    with con() as con:
        with open(r'queries/Man001ActiveJobsBL_ind_records.sql') as sql:
            df_table = pd.read_sql_query(sql=sql.read(), con=con)
        with open(r'queries/Man001ActiveJobsBL_counts.sql') as sql:
            df_counts = pd.read_sql_query(sql=sql.read(), con=con)

# Remove the words "Business License" just to make it easier for user to read
df_table['JobType'] = df_table['JobType'].map(lambda x: x.replace("Business License ", ""))
df_counts['JobType'] = df_counts['JobType'].map(lambda x: x.replace("Business License ", ""))

duration_options = []
for duration in df_counts['TimeSinceScheduledStartDate'].unique():
    duration_options.append({'label': str(duration), 'value': duration})

licensetype_options_unsorted = [{'label': 'All', 'value': 'All'}]
for licensetype in df_table['LicenseType'].unique():
    if str(licensetype) != "nan":
        licensetype_options_unsorted.append({'label': str(licensetype), 'value': licensetype})
licensetype_options_sorted = sorted(licensetype_options_unsorted, key=lambda k: k['label'])

def get_data_object(duration, license_type):
    df_selected = df_table
    if duration is not None:
        if isinstance(duration, str):
            df_selected = df_selected[df_selected['TimeSinceScheduledStartDate'] == duration]
        elif isinstance(duration, list):
            if len(duration) > 1:
                df_selected = df_selected[df_selected['TimeSinceScheduledStartDate'].isin(duration)]
            elif len(duration) == 1:
                df_selected = df_selected[df_selected['TimeSinceScheduledStartDate'] == duration[0]]
    if license_type != "All":
        df_selected = df_selected[df_selected['LicenseType'] == license_type]
    return df_selected

def update_counts_graph_data(duration, license_type):
    df_counts_selected = df_counts
    if duration is not None:
        if isinstance(duration, str):
            df_counts_selected = df_counts_selected[df_counts_selected['TimeSinceScheduledStartDate'] == duration]
        elif isinstance(duration, list):
            if len(duration) > 1:
                df_counts_selected = df_counts_selected[df_counts_selected['TimeSinceScheduledStartDate'].isin(duration)]
            elif len(duration) == 1:
                df_counts_selected = df_counts_selected[df_counts_selected['TimeSinceScheduledStartDate'] == duration[0]]
    if license_type != "All":
        df_counts_selected = df_counts_selected[df_counts_selected['LicenseType'] == license_type]
    return df_counts_selected

layout = html.Div(
    children=[
        html.H1(
            'Active Jobs With Completed Completeness Checks',
            style = {'margin-top': '10px'}
        ),
        html.H1(
            '(Business Licenses)',
            style={'margin-bottom': '50px'}
        ),
        html.Div([
            html.Div([
                html.P('Time Since Scheduled Start Date of Process'),
                dcc.Dropdown(
                    id='Man001ActiveJobsBL-duration-dropdown',
                    options=duration_options,
                    multi=True
                ),
            ], className='four columns'),
            html.Div([
                html.P('License Type'),
                dcc.Dropdown(
                    id='Man001ActiveJobsBL-licensetype-dropdown',
                    options=licensetype_options_sorted,
                    value='All',
                    searchable=True
                ),
            ], className='six columns'),
        ], className='dashrow filters'),
        html.Div([
            dcc.Graph(
                id='Man001ActiveJobsBL-my-graph',
                figure=go.Figure(
                    data=[
                        go.Bar(
                            x=df_counts[df_counts['JobType'] == 'Application'].groupby(['TimeSinceScheduledStartDate'])['JobCounts'].agg(np.sum).index,
                            y=df_counts[df_counts['JobType'] == 'Application'].groupby(['TimeSinceScheduledStartDate'])['JobCounts'].agg(np.sum),
                            name='BL Application Jobs Active',
                            marker=go.bar.Marker(
                                color='rgb(55, 83, 109)'
                            )
                        ),
                        go.Bar(
                            x=df_counts[df_counts['JobType'] == 'Amendment/Renewal'].groupby(['TimeSinceScheduledStartDate'])['JobCounts'].agg(np.sum).index,
                            y=df_counts[df_counts['JobType'] == 'Amendment/Renewal'].groupby(['TimeSinceScheduledStartDate'])['JobCounts'].agg(np.sum),
                            name='BL Renewal/Amendment Jobs Active',
                            marker=go.bar.Marker(
                                color='rgb(26, 118, 255)'
                            )
                        )
                    ],
                    layout=go.Layout(
                        xaxis=dict(
                            title='Time Since Scheduled Start Date of Process'
                        ),
                        yaxis=dict(
                            title='Active Trade License Jobs'
                        ),
                        showlegend=True,
                        legend=go.layout.Legend(
                            x=.75,
                            y=1
                        )
                    )
                )
            )
        ], style={'margin-left': 'auto', 'margin-right': 'auto', 'float': 'none'},
           className='nine columns'),
        html.Div([
            html.Div([
                html.Div([
                    dt.DataTable(
                        rows=[{}],
                        row_selectable=True,
                        filterable=True,
                        sortable=True,
                        selected_row_indices=[],
                        editable=False,
                        id='Man001ActiveJobsBL-table'
                    )
                ], style={'text-align': 'center'}),
                html.Div([
                    html.A(
                        'Download Data',
                        id='Man001ActiveJobsBL-download-link',
                        download='Man001ActiveJobsBL.csv',
                        href='',
                        target='_blank',
                    )
                ], style={'text-align': 'right'})
            ], style={'margin-top': '70px', 'margin-bottom': '50px'})
        ], className='dashrow')
    ]
)

@app.callback(
    Output('Man001ActiveJobsBL-my-graph', 'figure'),
    [Input('Man001ActiveJobsBL-duration-dropdown', 'value'),
     Input('Man001ActiveJobsBL-licensetype-dropdown', 'value')])
def update_graph(duration, license_type):
    df_counts_updated = update_counts_graph_data(duration, license_type)
    return {
        'data': [
             go.Bar(
                 x=df_counts_updated[df_counts_updated['JobType'] == 'Application'].groupby(['TimeSinceScheduledStartDate'])['JobCounts'].agg(np.sum).index,
                 y=df_counts_updated[df_counts_updated['JobType'] == 'Application'].groupby(['TimeSinceScheduledStartDate'])['JobCounts'].agg(np.sum),
                 name='Applications',
                 marker=go.bar.Marker(
                     color='rgb(55, 83, 109)'
                 )
             ),
             go.Bar(
                 x=df_counts_updated[df_counts_updated['JobType'] == 'Amendment/Renewal'].groupby(['TimeSinceScheduledStartDate'])['JobCounts'].agg(np.sum).index,
                 y=df_counts_updated[df_counts_updated['JobType'] == 'Amendment/Renewal'].groupby(['TimeSinceScheduledStartDate'])['JobCounts'].agg(np.sum),
                 name='Renewals/Amendments',
                 marker=go.bar.Marker(
                     color='rgb(26, 118, 255)'
                 )
             )
        ],
        'layout': go.Layout(
            xaxis=dict(
                title='Time Since Scheduled Start Date of Process'
            ),
            yaxis=dict(
                title='Active Business License Jobs'
            ),
            showlegend=True,
            legend=go.layout.Legend(
                x=.75,
                y=1
            )
        )
    }

@app.callback(
    Output('Man001ActiveJobsBL-table', 'rows'), 
    [Input('Man001ActiveJobsBL-duration-dropdown', 'value'),
     Input('Man001ActiveJobsBL-licensetype-dropdown', 'value')])
def update_table(duration, license_type):
    df = get_data_object(duration, license_type)
    return df.to_dict('records')

@app.callback(
    Output('Man001ActiveJobsBL-download-link', 'href'),
    [Input('Man001ActiveJobsBL-duration-dropdown', 'value'),
     Input('Man001ActiveJobsBL-licensetype-dropdown', 'value')])
def update_download_link(duration, license_type):
    df = get_data_object(duration, license_type)
    csv_string = df.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string
