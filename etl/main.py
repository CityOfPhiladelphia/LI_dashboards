from etl import etl_process
from sql_queries import queries

def main():
    global queries
    etl_process(queries)

if __name__ == '__main__':
    try:
        main()
    except:
        send_email()