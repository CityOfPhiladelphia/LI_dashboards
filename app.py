import dash
import dash_auth
import cx_Oracle
from flask import Flask
from li_dbs import ECLIPSE_PROD
from config import USERNAME_PASSWORD_PAIRS


con = ECLIPSE_PROD.ECLIPSE_PROD

server = Flask(__name__)
app = dash.Dash(server=server)
auth = dash_auth.BasicAuth(app, USERNAME_PASSWORD_PAIRS)
app.config.suppress_callback_exceptions = True
