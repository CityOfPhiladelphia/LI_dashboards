import datetime
from functools import wraps

import dash
import dash_auth
import cx_Oracle
from flask import Flask
from flask_caching import Cache

from li_dbs import ECLIPSE_PROD, GISLICLD
from config import USERNAME_PASSWORD_PAIRS, REDIS_URL


def cache_timeout(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        now = datetime.datetime.now()
        deadline = now.replace(hour=6, minute=0)
        period = (deadline - now)
        f.cache_timeout = period.seconds
        return f(*args, **kwargs)
    return decorated_function

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
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': REDIS_URL
})

now = datetime.datetime.now()
print('App initialized: ' + str(now))
