from li_dbs import ECLIPSE_PROD, GISLICLD
import sys


def etl(query):
    # extract data from source db
    with ECLIPSE_PROD.ECLIPSE_PROD() as source:
        with source.cursor() as source_cursor:
            with open(query.extract_query_file) as sql:
                extract_query = sql.read()
            source_cursor.execute(extract_query)
            data = source_cursor.fetchall()

    with GISLICLD.GISLICLD() as target:
        with target.cursor() as target_cursor:
            # truncate the target db
            target_cursor.execute(f'TRUNCATE TABLE {query.target_table}')
            # load data into target db
            target_cursor.executemany(query.insert_query, data)
        target.commit()
        print(f'{len(data)} rows loaded into GISLICLD.{query.target_table}.')

def etl_process(queries):
    # loop through sql queries
    for query in queries:
        try:
            etl(query)
        except Exception as e:
            # send_email()
            print(f'ETL Process into GISLICLD.{query.target_table} failed.')
            exc_type, exc_obj, tb = sys.exc_info()
            lineno = tb.tb_lineno
            print('Exception on line {}'.format(lineno))
            print(f'Error Message: {e}')

