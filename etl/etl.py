import sys
import datetime

import petl as etl

from li_dbs import ECLIPSE_PROD, GISLICLD
from utils import timeout, get_logger, get_cursor, send_email


def get_source_db(query):
    if query.source_db == 'ECLIPSE_PROD':
        return ECLIPSE_PROD.ECLIPSE_PROD
    elif query.source_db == 'GISLICLD':
        return GISLICLD.GISLICLD

def get_extract_query(query):
    with open(query.extract_query_file) as sql:
        return sql.read()

@timeout(1800)
def etl_(query, target):
    source_db = get_source_db(query)
    extract_query = get_extract_query(query)
    target_table = query.target_table

    with source_db() as source:
        etl.fromdb(source, extract_query) \
           .todb(get_cursor(target), target_table.upper())

def etl_process(queries_lists):
    logger = get_logger()
    logger.info('---------------------------------')
    logger.info('ETL process initialized: ' + str(datetime.datetime.now()))

    with GISLICLD.GISLICLD() as target:
        for queries_list in queries_lists:
            for query in queries_list:
                try:
                    etl_(query, target)
                    logger.info(f'{query.target_table} successfully updated.')
                except:
                    logger.error(f'ETL Process into GISLICLD.{query.target_table} failed.', exc_info=True)

    logger.info('ETL process ended: ' + str(datetime.datetime.now()))
