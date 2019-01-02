import dash
import dash_auth
import cx_Oracle
from flask import Flask
from li_dbs import ECLIPSE_PROD, GISLICLD
from config import USERNAME_PASSWORD_PAIRS
import datetime
from flask_caching import Cache


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
app.css.config.serve_locally = True
app.scripts.config.serve_locally = True
cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory'
})
now = datetime.datetime.now()
print('App initialized: ' + str(now))

#Set cache timeout to however long it is between now and tomorrow at 5am
today = datetime.date.today()
tomorrow = today + datetime.timedelta(days=1)
tomorrow_midnight = datetime.datetime.combine(tomorrow, datetime.datetime.min.time())
refresh_day_and_time = tomorrow_midnight.replace(hour=5, minute=0)
TIMEOUT = (refresh_day_and_time - now).total_seconds()
print('Cache timeout: ' + str(TIMEOUT))
