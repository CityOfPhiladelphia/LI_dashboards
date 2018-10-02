import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
from dash.dependencies import Input, Output
from gevent.pywsgi import WSGIServer
from flask import request
from datetime import datetime

from app import app, server
from log_visitors import log_visitor

from apps import Man001ActiveJobsBL, Man001ActiveJobsTL, Man002ActiveProcessesBL, Man002ActiveProcessesTL, Man004BLJobVolumesBySubmissionType, Man004TLJobVolumesBySubmissionType, Man005BLExpirationVolumesBySubmissionType, Man005TLExpirationVolumesBySubmissionType, Man006OverdueBLInspections

time = datetime.strftime(datetime.now(), '%I:%M %p %m/%d/%y')

app.layout = html.Div([
    html.Nav(className = 'navbar navbar-dark bg-dark', 
             children =[
                html.A('Home', className="navbar-brand", href='/'),
                       ]
            ),
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
    html.Div(dt.DataTable(rows=[{}]), style={'display': 'none'})
])

index_page = html.Div([
    html.Img(src='/assets/city-of-philadelphia-logo.png'),
    html.H2('Licenses & Inspections'),
    html.Br(),
    html.H3('Dashboards'),
    html.Br(),
    html.P(f'Data last updated: {time}', id='time-stamp'),
    html.Br(),
    html.Div(
        html.Table(children=[
            html.Tr([
                html.Th('Dashboard Name'), html.Th('Business License'), html.Th('Trade License')
            ]),
            html.Tr([
                html.Td(
                    html.P('Active Jobs With Completed Completeness Checks')
                ),
                html.Td(
                    dcc.Link('BL Link', href='/ActiveJobsBL')
                ),
                html.Td(
                    dcc.Link('TL Link', href='/ActiveJobsTL'),
                )
            ]),
            html.Tr([
                html.Td(
                    html.P('Active Processes')
                ),
                html.Td(
                    dcc.Link('BL Link', href='/ActiveProcessesBL'),
                ),
                html.Td(
                    dcc.Link('TL Link', href='/ActiveProcessesTL'),
                )
            ]),
            html.Tr([
                html.Td(
                    html.P('Job Volumes by Submission Type')
                ),
                html.Td(
                    dcc.Link('BL Link', href='/JobVolumesBySubmissionTypeBL'),
                ),
                html.Td(
                    dcc.Link('TL Link', href='/JobVolumesBySubmissionTypeTL'),
                )
            ]),
            html.Tr([
                html.Td(
                    html.P('Expiration Volumes by Submission Type')
                ),
                html.Td(
                    dcc.Link('BL Link', href='/ExpirationVolumesBySubmissionTypeBL')
                ),
                html.Td(
                    dcc.Link('TL Link', href='/ExpirationVolumesBySubmissionTypeTL')
                )
            ]),
            html.Tr([
                html.Td(
                    html.P('Inspections Past their Scheduled Completion Date')
                ),
                html.Td(
                    dcc.Link('BL Link', href='/OverdueInspectionsBL')
                ),
                html.Td(
                    html.P(' ')
                )
            ])
        ], style={'margin': '0px auto'})
    )
], style={'text-align': 'center'})


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    log_visitor()
    if pathname == '/ActiveJobsTL':
        return Man001ActiveJobsTL.layout
    elif pathname == '/ActiveJobsBL':
        return Man001ActiveJobsBL.layout
    elif pathname == '/ActiveProcessesBL':
        return Man002ActiveProcessesBL.layout
    elif pathname == '/ActiveProcessesTL':
        return Man002ActiveProcessesTL.layout
    elif pathname == '/JobVolumesBySubmissionTypeBL':
        return Man004BLJobVolumesBySubmissionType.layout
    elif pathname == '/JobVolumesBySubmissionTypeTL':
        return Man004TLJobVolumesBySubmissionType.layout
    elif pathname == '/ExpirationVolumesBySubmissionTypeBL':
        return Man005BLExpirationVolumesBySubmissionType.layout
    elif pathname == '/ExpirationVolumesBySubmissionTypeTL':
        return Man005TLExpirationVolumesBySubmissionType.layout
    elif pathname == '/OverdueInspectionsBL':
        return Man006OverdueBLInspections.layout
    else:
        return index_page

if __name__ == '__main__':
    # app.run_server(host='127.0.0.1', port=5001)
    http_server = WSGIServer(('0.0.0.0', 8000), server)
    http_server.serve_forever()
