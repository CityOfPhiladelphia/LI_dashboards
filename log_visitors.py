import sqlite3
from flask import request
from datetime import datetime


def log_visitor():
    with sqlite3.connect('li_dashboards.db') as conn:
        user_id = request.environ['REMOTE_ADDR']
        date = datetime.now()
        data = (user_id, date)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO dashboard_visitors (ip_address, datetime) VALUES (?, ?)', data)
        conn.commit()