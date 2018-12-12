import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from dash.dependencies import Input, Output
import urllib.parse

from app import app, con

print("Man002ActiveProcessesTL.py")

# Definitions: TL Apps and Renewals
# excludes jobs in Statuses More Information Required, Denied, Draft, Withdrawn, Approved
# excludes processes of Pay Fees, Provide More Information for Renewal, Amend License
# No completion date on processes
with con() as con:
    sql = 'SELECT * FROM li_dash_activeproc_tl_ind'
    df_table = pd.read_sql_query(sql=sql, con=con)
    sql = 'SELECT * FROM li_dash_activeproc_tl_counts'
    df_counts = pd.read_sql_query(sql=sql, con=con)

# Remove the words "Trade License" just to make it easier for user to read
df_table['JOBTYPE'] = df_table['JOBTYPE'].map(lambda x: x.replace("Trade License ", ""))
df_counts['JOBTYPE'] = df_counts['JOBTYPE'].map(lambda x: x.replace("Trade License ", ""))

processtype_options_unsorted = []
for processtype in df_counts['PROCESSTYPE'].unique():
    processtype_options_unsorted.append({'label': str(processtype),'value': processtype})
processtype_options_sorted = sorted(processtype_options_unsorted, key=lambda k: k['label'])

licensetype_options_unsorted = [{'label': 'All', 'value': 'All'}]
for licensetype in df_table['LICENSETYPE'].unique():
    if str(licensetype) != "nan":
        licensetype_options_unsorted.append({'label': str(licensetype), 'value': licensetype})
licensetype_options_sorted = sorted(licensetype_options_unsorted, key=lambda k: k['label'])

def get_data_object(process_type, license_type):
    df_selected = df_table
    if process_type is not None:
        if isinstance(process_type, str):
            df_selected = df_selected[df_selected['PROCESSTYPE'] == process_type]
        elif isinstance(process_type, list):
            if len(process_type) > 1:
                df_selected = df_selected[df_selected['PROCESSTYPE'].isin(process_type)]
            elif len(process_type) == 1:
                df_selected = df_selected[df_selected['PROCESSTYPE'] == process_type[0]]
    if license_type != "All":
        df_selected = df_selected[df_selected['LICENSETYPE'] == license_type]
    return df_selected

def update_counts_graph_data(process_type, license_type):
    df_counts_selected = df_counts
    if process_type is not None:
        if isinstance(process_type, str):
            df_counts_selected = df_counts_selected[df_counts_selected['PROCESSTYPE'] == process_type]
        elif isinstance(process_type, list):
            if len(process_type) > 1:
                df_counts_selected = df_counts_selected[df_counts_selected['PROCESSTYPE'].isin(process_type)]
            elif len(process_type) == 1:
                df_counts_selected = df_counts_selected[df_counts_selected['PROCESSTYPE'] == process_type[0]]
    if license_type != "All":
        df_counts_selected = df_counts_selected[df_counts_selected['LICENSETYPE'] == license_type]
    return df_counts_selected

layout = html.Div([
    html.H1(
        'Active Processes',
        style={'margin-top': '10px'}
    ),
    html.H1(
        '(Trade Licenses)',
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
    html.Div([
        dcc.Graph(
            id='002TL-graph',
            figure=go.Figure(
                data=[
                    go.Bar(
                        x=df_counts[df_counts['JOBTYPE'] == 'Application'].groupby(['PROCESSTYPE'])['PROCESSCOUNTS'].agg(np.sum).index,
                        y=df_counts[df_counts['JOBTYPE'] == 'Application'].groupby(['PROCESSTYPE'])['PROCESSCOUNTS'].agg(np.sum),
                        name='Applications',
                        marker=go.bar.Marker(
                            color='rgb(55, 83, 109)'
                        )
                    ),
                    go.Bar(
                        x=df_counts[df_counts['JOBTYPE'] == 'Amend/Renew'].groupby(['PROCESSTYPE'])['PROCESSCOUNTS'].agg(np.sum).index,
                        y=df_counts[df_counts['JOBTYPE'] == 'Amend/Renew'].groupby(['PROCESSTYPE'])['PROCESSCOUNTS'].agg(np.sum),
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
                        y=1
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
        )
    ], style={'margin-left': 'auto', 'margin-right': 'auto', 'float': 'none'},
        className='eight columns'),
    html.Div([
        html.Div([
            html.Div([
                dt.DataTable(
                    # Initialise the rows
                    rows=[{}],
                    filterable=True,
                    sortable=True,
                    selected_row_indices=[],
                    editable=False,
                    id='Man002ActiveProcessesTL-table'
                )
            ], style={'text-align': 'center'}),
            html.Div([
                html.A(
                    'Download Data',
                    id='Man002ActiveProcessesTL-download-link',
                    download='Man002ActiveProcessesTL.csv',
                    href='',
                    target='_blank',
                )
            ], style={'text-align': 'right'}),
        ], style={'margin-top': '70px', 'margin-bottom': '50px'})
    ], className='dashrow'),
    html.Details([
        html.Summary('Query Description'),
        html.Div(
            'Incomplete processes (excluding "Pay Fees", "Provide More Information for Renewal", and "Amend License" '
            'processes) associated with trade license application or amend/renew jobs that have statuses of "Approved", '
            '"Draft", "Withdrawn", "More Information Required", or "Denied" (i.e. not "In Review", "Payment Pending", '
            '"Submitted",  "Distribute", "Cancelled")')
    ])
])

@app.callback(
    Output('002TL-graph', 'figure'),
    [Input('processtype-dropdown', 'value'),
     Input('licensetype-dropdown', 'value')])
def update_graph(process_type, license_type):
    df_counts_updated = update_counts_graph_data(process_type, license_type)
    return {
        'data': [
            go.Bar(
                x=df_counts_updated[df_counts_updated['JOBTYPE'] == 'Application'].groupby(['PROCESSTYPE'])['PROCESSCOUNTS'].agg(np.sum).index,
                y=df_counts_updated[df_counts_updated['JOBTYPE'] == 'Application'].groupby(['PROCESSTYPE'])['PROCESSCOUNTS'].agg(np.sum),
                name='Applications',
                marker=go.bar.Marker(
                    color='rgb(55, 83, 109)'
                )
            ),
            go.Bar(
                x=df_counts_updated[df_counts_updated['JOBTYPE'] == 'Amend/Renew'].groupby(['PROCESSTYPE'])['PROCESSCOUNTS'].agg(np.sum).index,
                y=df_counts_updated[df_counts_updated['JOBTYPE'] == 'Amend/Renew'].groupby(['PROCESSTYPE'])['PROCESSCOUNTS'].agg(np.sum),
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
    Output('Man002ActiveProcessesTL-table', 'rows'), 
    [Input('processtype-dropdown', 'value'),
     Input('licensetype-dropdown', 'value')])
def update_table(process_type, license_type):
    df = get_data_object(process_type, license_type)
    return df.to_dict('records')

@app.callback(
    Output('Man002ActiveProcessesTL-download-link', 'href'),
    [Input('processtype-dropdown', 'value'),
     Input('licensetype-dropdown', 'value')])
def update_download_link(process_type, license_type):
    df = get_data_object(process_type, license_type)
    csv_string = df.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string
