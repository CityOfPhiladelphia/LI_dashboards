from li_dbs import GISLNI
from flask import request
from datetime import datetime

def log_visitor():
    with GISLNI.GISLNI() as conn:
        user_id = request.environ['REMOTE_ADDR']
        date = datetime.now()
        data = (user_id, date)
        cursor = conn.cursor()
        cursor.prepare('INSERT INTO dashboard_visitors (ip_address, datetime) VALUES (:1, :2)')
        cursor.execute(None, data)
        conn.commit()