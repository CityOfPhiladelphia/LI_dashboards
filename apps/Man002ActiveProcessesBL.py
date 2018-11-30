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
print("Man002ActiveProcessesBL.py")
print("Testing mode? " + str(testing_mode))

#Definitions: BL Apps and Renewals
#excludes jobs in Statuses More Information Required, Denied, Draft, Withdrawn, Approved
#excludes processes of Pay Fees, Provide More Information for Renewal, Amend License
#No completion date on processes

if testing_mode:
    df_table = pd.read_csv("test_data/Man002ActiveProcessesBL_ind_records_test_data.csv")
    df_counts = pd.read_csv("test_data/Man002ActiveProcessesBL_counts_test_data.csv")
else:
    with con() as con:
        with open(r'queries/Man002ActiveProcessesBL_ind_records.sql') as sql:
            df_table = pd.read_sql_query(sql=sql.read(), con=con)
        with open(r'queries/Man002ActiveProcessesBL_counts.sql') as sql:
            df_counts = pd.read_sql_query(sql=sql.read(), con=con)

# Remove the words "Business License" just to make it easier for user to read
df_table['JobType'] = df_table['JobType'].map(lambda x: x.replace("Business License ", ""))
df_counts['JobType'] = df_counts['JobType'].map(lambda x: x.replace("Business License ", ""))

processtype_options_unsorted = []
for processtype in df_counts['ProcessType'].unique():
    processtype_options_unsorted.append({'label': str(processtype),'value': processtype})
processtype_options_sorted = sorted(processtype_options_unsorted, key=lambda k: k['label'])

licensetype_options_unsorted = [{'label': 'All', 'value': 'All'}]
for licensetype in df_table['LicenseType'].unique():
    if str(licensetype) != "nan":
        licensetype_options_unsorted.append({'label': str(licensetype), 'value': licensetype})
licensetype_options_sorted = sorted(licensetype_options_unsorted, key=lambda k: k['label'])

def get_data_object(process_type, license_type):
    df_selected = df_table
    if process_type is not None:
        if isinstance(process_type, str):
            df_selected = df_selected[df_selected['ProcessType'] == process_type]
        elif isinstance(process_type, list):
            if len(process_type) > 1:
                df_selected = df_selected[df_selected['ProcessType'].isin(process_type)]
            elif len(process_type) == 1:
                df_selected = df_selected[df_selected['ProcessType'] == process_type[0]]
    if license_type != "All":
        df_selected = df_selected[df_selected['LicenseType'] == license_type]
    return df_selected

def update_counts_graph_data(process_type, license_type):
    df_counts_selected = df_counts
    if process_type is not None:
        if isinstance(process_type, str):
            df_counts_selected = df_counts_selected[df_counts_selected['ProcessType'] == process_type]
        elif isinstance(process_type, list):
            if len(process_type) > 1:
                df_counts_selected = df_counts_selected[df_counts_selected['ProcessType'].isin(process_type)]
            elif len(process_type) == 1:
                df_counts_selected = df_counts_selected[df_counts_selected['ProcessType'] == process_type[0]]
    if license_type != "All":
        df_counts_selected = df_counts_selected[df_counts_selected['LicenseType'] == license_type]
    return df_counts_selected

layout = html.Div([
    html.H1(
        'Active Processes',
        style={'margin-top': '10px'}
    ),
    html.H1(
        '(Business Licenses)',
        style={'margin-bottom': '50px'}
    ),
    html.Div([
        html.Div([
            html.P('Process Type'),
            dcc.Dropdown(
                id='processtype-dropdown',
                options=processtype_options_sorted,
                multi=True
            ),
        ], className='four columns'),
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
    dcc.Graph(
        id='002BL-graph',
        figure=go.Figure(
            data=[
                go.Bar(
                    x=df_counts[df_counts['JobType'] == 'Application'].groupby(['ProcessType'])['ProcessCounts'].agg(np.sum).index,
                    y=df_counts[df_counts['JobType'] == 'Application'].groupby(['ProcessType'])['ProcessCounts'].agg(np.sum),
                    name='Applications',
                    marker=go.bar.Marker(
                        color='rgb(55, 83, 109)'
                    )
                ),
                go.Bar(
                    x=df_counts[df_counts['JobType'] == 'Amendment/Renewal'].groupby(['ProcessType'])['ProcessCounts'].agg(np.sum).index,
                    y=df_counts[df_counts['JobType'] == 'Amendment/Renewal'].groupby(['ProcessType'])['ProcessCounts'].agg(np.sum),
                    name='Renewals/Amendments',
                    marker=go.bar.Marker(
                        color='rgb(26, 118, 255)'
                    )
                )
            ],
            layout=go.Layout(
                showlegend=True,
                legend=go.layout.Legend(
                    x=.75,
                    y=1,
                ),
                xaxis=dict(
                    autorange=True,
                    tickangle=30,
                    tickfont=dict(
                        size=11
                    )
                ),
                yaxis=dict(
                    title='Active Processes'
                ),
                margin=go.layout.Margin(l=40, r=0, t=40, b=100)
            )
        )
    ),
    html.Div([
        html.Div([
            html.Div([
                dt.DataTable(
                    # Initialise the rows
                    rows=[{}],
                    row_selectable=True,
                    filterable=True,
                    sortable=True,
                    selected_row_indices=[],
                    editable=False,
                    id='Man002ActiveProcessesBL-table'
                )
            ], style={'text-align': 'center'}),
            html.Div([
                html.A(
                    'Download Data',
                    id='Man002ActiveProcessesBL-download-link',
                    download='Man002ActiveProcessesBL.csv',
                    href='',
                    target='_blank',
                )
            ], style={'text-align': 'right'}),
        ], style={'margin-top': '70px', 'margin-bottom': '50px'})
    ], className='dashrow')
])

@app.callback(
    Output('002BL-graph', 'figure'),
    [Input('processtype-dropdown', 'value'),
     Input('licensetype-dropdown', 'value')])
def update_graph(process_type, license_type):
    df_counts_updated = update_counts_graph_data(process_type, license_type)
    return {
        'data': [
            go.Bar(
                x=df_counts_updated[df_counts_updated['JobType'] == 'Application'].groupby(['ProcessType'])['ProcessCounts'].agg(np.sum).index,
                y=df_counts_updated[df_counts_updated['JobType'] == 'Application'].groupby(['ProcessType'])['ProcessCounts'].agg(np.sum),
                name='Applications',
                marker=go.bar.Marker(
                    color='rgb(55, 83, 109)'
                )
            ),
            go.Bar(
                x=df_counts_updated[df_counts_updated['JobType'] == 'Amendment/Renewal'].groupby(['ProcessType'])['ProcessCounts'].agg(np.sum).index,
                y=df_counts_updated[df_counts_updated['JobType'] == 'Amendment/Renewal'].groupby(['ProcessType'])['ProcessCounts'].agg(np.sum),
                name='Renewals/Amendments',
                marker=go.bar.Marker(
                    color='rgb(26, 118, 255)'
                )
            )
        ],
        'layout': go.Layout(
            showlegend=True,
            legend=go.layout.Legend(
                x=.75,
                y=1,
            ),
            xaxis=dict(
                autorange=True,
                tickangle=30,
                tickfont=dict(
                    size=11
                )
            ),
            yaxis=dict(
                title='Active Processes'
            ),
            margin=go.layout.Margin(l=40, r=0, t=40, b=100)
        )
    }

@app.callback(
    Output('Man002ActiveProcessesBL-table', 'rows'),
    [Input('processtype-dropdown', 'value'),
     Input('licensetype-dropdown', 'value')])
def update_table(process_type, license_type):
    df = get_data_object(process_type, license_type)
    return df.to_dict('records')

@app.callback(
    Output('Man002ActiveProcessesBL-download-link', 'href'),
    [Input('processtype-dropdown', 'value'),
     Input('licensetype-dropdown', 'value')])
def update_download_link(process_type, license_type):
    df = get_data_object(process_type, license_type)
    csv_string = df.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string
