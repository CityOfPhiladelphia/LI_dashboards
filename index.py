import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
from dash.dependencies import Input, Output
from gevent.pywsgi import WSGIServer
from flask import request
from datetime import datetime

from app import app, server
from send_email import send_email
#from log_visitors import log_visitor

from apps import (Man001ActiveJobsBL, Man001ActiveJobsTL, Man002ActiveProcessesBL, Man002ActiveProcessesTL,
                  Man004BLJobVolumesBySubmissionType, Man004TLJobVolumesBySubmissionType,
                  Man005BLExpirationVolumesBySubmissionType, Man005TLExpirationVolumesBySubmissionType,
                  Man006OverdueBLInspections, IndividualWorkloadsBL, SLA_BL, ExpiringLicensesTaxIssues,
                  LicensesWithCompletenessChecksButNoCompletedInspections)

time = datetime.strftime(datetime.now(), '%I:%M %p %m/%d/%y')

app.layout = html.Div([
                html.Nav([
                    html.P('City of Philadelphia | LI Dashboards'),
                    html.Div([
                        html.Button('Miscellaneous', className='dropbtn'),
                        html.Div([
                            html.A('Expiring Licenses with Tax Issues', href='/ExpiringLicensesTaxIssues')
                        ], className='dropdown-content')
                    ], className='dropdown'),
                    html.Div([
                        html.Button('Trade Licenses', className='dropbtn'),
                        html.Div([
                            html.A('Active Jobs', href='/ActiveJobsTL'),
                            html.A('Active Processes', href='/ActiveProcessesTL'),
                            html.A('Job Volumes by Submission Type', href='/JobVolumesBySubmissionTypeTL'),
                            html.A('License Expiration Volumes by Submission Type', href='/ExpirationVolumesBySubmissionTypeTL'),
                        ], className='dropdown-content')
                    ], className='dropdown'),
                    html.Div([
                        html.Button('Business Licenses', className='dropbtn'),
                        html.Div([
                            html.A('Active Jobs', href='ActiveJobsBL'),
                            html.A('Active Processes', href='/ActiveProcessesBL'),
                            html.A('Job Volumes by Submission Type', href='/JobVolumesBySubmissionTypeBL'),
                            html.A('License Expiration Volumes by Submission Type', href='/ExpirationVolumesBySubmissionTypeBL'),
                            html.A('Inspections Past their Scheduled Completion Date', href='/OverdueInspectionsBL'),
                            html.A('Individual Workloads', href='/IndividualWorkloadsBL'),
                            html.A('SLA License Issuance', href='/SLA_BL'),
                            html.A('Licenses with Completed Completeness Checks but no Completed Inspections', href='/LicensesWithCompletenessChecksButNoCompletedInspections')
                        ], className='dropdown-content')
                    ], className='dropdown'),
                ], className='navbar'),
                html.Div([
                    dcc.Location(id='url', refresh=False),
                    html.Div(id='page-content'),
                    html.Div(dt.DataTable(rows=[{}]), style={'display': 'none'})
                ], className='container', style={'margin': 'auto', 'margin-bottom': '45px'}),
                html.Nav([
                    html.A('Questions? Click Here to Contact LI GIS Team', href='mailto:ligisteam@phila.gov')
                ], className='footer-navbar')
            ])

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
#    log_visitor()
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
    elif pathname == '/IndividualWorkloadsBL':
        return IndividualWorkloadsBL.layout
    elif pathname == '/SLA_BL':
        return SLA_BL.layout
    elif pathname == '/ExpiringLicensesTaxIssues':
        return ExpiringLicensesTaxIssues.layout
    elif pathname == '/LicensesWithCompletenessChecksButNoCompletedInspections':
        return LicensesWithCompletenessChecksButNoCompletedInspections.layout
    else:
        return Man001ActiveJobsBL.layout

if __name__ == '__main__':
    # app.run_server(host='127.0.0.1', port=5001)
    try:
        http_server = WSGIServer(('0.0.0.0', 8000), server)
        http_server.serve_forever()
    except:
        send_email()