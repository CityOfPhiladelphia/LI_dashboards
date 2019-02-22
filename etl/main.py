from etl import etl_process
from sql_queries import queries_lists
from utils import send_email


def main():
    global queries_lists
    etl_process(queries_lists)

if __name__ == '__main__':
    try:
        main()
    except:
        send_email()