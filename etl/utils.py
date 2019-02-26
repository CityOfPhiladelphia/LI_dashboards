def get_logger():
    import logging
    
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # Create a file handler
    handler = logging.FileHandler('log.txt')
    handler.setLevel(logging.INFO)

    # Create a logging format
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)

    return logger

def send_email():
    from email.mime.text import MIMEText
    from phila_mail import server

    recipientslist = ['peter.dannemann@Phila.gov', 
                      'dani.interrante@phila.gov', 
                      'philip.ribbens@phila.gov',
                      'shannon.holm@phila.gov']
    sender = 'peter.dannemann@phila.gov'
    commaspace = ', '
    email = 'LI Dashboards ETL failed. Please read the log file and troubleshoot this issue.'
    text = f'AUTOMATIC EMAIL: \n {email}'
    msg = MIMEText(text)
    msg['To'] = commaspace.join(recipientslist)
    msg['From'] = sender
    msg['X-Priority'] = '2'
    msg['Subject'] = 'Important Email'
    server.server.sendmail(sender, recipientslist, msg.as_string())
    server.server.quit()

class CursorProxy(object):
    def __init__(self, cursor):
        self._cursor = cursor
    def executemany(self, statement, parameters, **kwargs):
        # convert parameters to a list
        parameters = list(parameters)
        # pass through to proxied cursor
        return self._cursor.executemany(statement, parameters, **kwargs)
    def __getattr__(self, item):
        return getattr(self._cursor, item)

def get_cursor(conn):
    return CursorProxy(conn.cursor())