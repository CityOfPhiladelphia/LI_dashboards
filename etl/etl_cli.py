import click

from etl import etl_process
from sql_queries import queries_lists


@click.command()
@click.option(
    '--name',
    '-n',
    multiple=True,
    prompt='Names of dashboard table(s) to ETL',
    help='The dashboard tables to ETL.'
)
def main(name):
    global queries_lists
    tables1 = []
    tables2 = []
    for counter, queries_list in enumerate(queries_lists):
        for query in queries_list:
            if query.target_table in name:
                if counter == 0:
                    tables1.append(query)
                elif counter == 1:
                    tables2.append(query)
    tuple_of_tables = (tables1, tables2)
    etl_process(tuple_of_tables)

if __name__ == '__main__':
    main()