import dash
import dash_auth
import cx_Oracle
from flask import Flask
from li_dbs import ECLIPSE_PROD, GISLICLD
from config import USERNAME_PASSWORD_PAIRS
import datetime


con = GISLICLD.GISLICLD

external_stylesheets = ['https://unpkg.com/phila-standards@0.11.2/dist/css/phila-app.min.css']

meta_tags=[
    {
        'og:image': 'https://beta.phila.gov/media/20160715133810/phila-gov.jpg',
        'content': 'LI Stat'
    }]

server = Flask(__name__)
app = dash.Dash(server=server, external_stylesheets=external_stylesheets, meta_tags=meta_tags)
auth = dash_auth.BasicAuth(app, USERNAME_PASSWORD_PAIRS)
app.config.suppress_callback_exceptions = True
print('App initialized: ' + str(datetime.datetime.now()))