import sys
import datetime

import petl as etl

from li_dbs import ECLIPSE_PROD, GISLICLD
from utils import get_logger, get_cursor, send_email


def get_extract_query(query):
    with open(query.extract_query_file) as sql:
        return sql.read()

def etl_(query, target, source):
    extract_query = get_extract_query(query)
    target_table = query.target_table

    etl.fromdb(source, extract_query) \
       .todb(get_cursor(target), target_table.upper())

def etl_process(queries):
    logger = get_logger()
    logger.info('---------------------------------')
    logger.info('ETL process initialized: ' + str(datetime.datetime.now()))

    with GISLICLD.GISLICLD() as target, ECLIPSE_PROD.ECLIPSE_PROD() as source:

        for query in queries:
            try:
                etl_(query, target, source)
                logger.info(f'{query.target_table} successfully updated.')
            except:
                logger.error(f'ETL Process into GISLICLD.{query.target_table} failed.', exc_info=True)

    logger.info('ETL process ended: ' + str(datetime.datetime.now()))
