class SqlQuery():
    def __init__(self, extract_query_file, target_table):
        self.extract_query_file = 'queries/' + extract_query_file
        self.target_table = target_table

    @property
    def columns(self):
        '''Returns the column names from the target_table in GISLICLD.'''
        from li_dbs import GISLICLD

        with GISLICLD.GISLICLD() as con:
            with con.cursor() as cursor:
                sql = f"""SELECT 
                              column_name
                          FROM 
                              all_tab_cols
                          WHERE 
                              table_name = '{self.target_table.upper()}'"""
                cursor.execute(sql)
                cols = cursor.fetchall()
                cols = [col[0] for col in cols]
        return cols

    @property
    def insert_query(self):
        '''Generates the insert query based on the target_table and columns.'''
        insert_q = f'''INSERT INTO {self.target_table} (
                            {", ".join(column for column in self.columns)})
                       VALUES ({", ".join(":" + str(num + 1) for num in range(len(self.columns)))})'''
        return insert_q

IndividualWorkloadsBL = SqlQuery(
    extract_query_file = 'individual_workloads_bl.sql',
    target_table = 'li_dash_indworkloads_bl' 
)

IndividualWorkloadsTL = SqlQuery(
    extract_query_file = 'individual_workloads_tl.sql',
    target_table = 'li_dash_indworkloads_tl' 
)

Man001ActiveJobsBLInd = SqlQuery(
    extract_query_file = 'Man001ActiveJobsBL_ind_records.sql',
    target_table = 'li_dash_activejobs_bl_ind'
)

Man001ActiveJobsBLCount = SqlQuery(
    extract_query_file = 'Man001ActiveJobsBL_counts.sql',
    target_table = 'li_dash_activejobs_bl_counts'
)

Man001ActiveJobsTLInd = SqlQuery(
    extract_query_file = 'Man001ActiveJobsTL_ind_records.sql',
    target_table = 'li_dash_activejobs_tl_ind'
)

Man001ActiveJobsTLCount = SqlQuery(
    extract_query_file = 'Man001ActiveJobsTL_counts.sql',
    target_table = 'li_dash_activejobs_tl_counts'
)

Man002ActiveProcessesBLInd = SqlQuery(
    extract_query_file = 'Man002ActiveProcessesBL_ind_records.sql',
    target_table = 'li_dash_activeproc_bl_ind'
)

Man002ActiveProcessesBLCount = SqlQuery(
    extract_query_file = 'Man002ActiveProcessesBL_counts.sql',
    target_table = 'li_dash_activeproc_bl_counts'
)

Man002ActiveProcessesTLInd = SqlQuery(
    extract_query_file = 'Man002ActiveProcessesTL_ind_records.sql',
    target_table = 'li_dash_activeproc_tl_ind'
)

Man002ActiveProcessesTLCount = SqlQuery(
    extract_query_file = 'Man002ActiveProcessesTL_counts.sql',
    target_table = 'li_dash_activeproc_tl_counts'
)

Man004BLJobVolumesBySubmissionTypes = SqlQuery(
    extract_query_file = 'Man004BLJobVolumesBySubmissionType.sql',
    target_table = 'li_dash_jobvolsbysubtype_bl'
)

Man004TLJobVolumesBySubmissionTypes = SqlQuery(
    extract_query_file = 'Man004TLJobVolumesBySubmissionType.sql',
    target_table = 'li_dash_jobvolsbysubtype_tl'
)

Man005BLExpirationDates = SqlQuery(
    extract_query_file = 'Man005BLExpirationDates.sql',
    target_table = 'li_dash_expirationdates_bl'
)

Man005TLExpirationDates = SqlQuery(
    extract_query_file = 'Man005TLExpirationDates.sql',
    target_table = 'li_dash_expirationdates_tl'
)

Man006OverdueBLInspections = SqlQuery(
    extract_query_file = 'Man006OverdueBLInspections.sql',
    target_table = 'li_dash_overdueinsp_bl' 
)

SLA_BL = SqlQuery(
    extract_query_file = 'SLA_BL.sql',
    target_table = 'li_dash_sla_bl' 
)

LicensesWithCompletenessChecksButNoCompletedInspections = SqlQuery(
    extract_query_file = 'LicensesWithCompletenessChecksButNoCompletedInspections.sql',
    target_table = 'li_dash_licenseswcompleteness' 
)

queries = [
    IndividualWorkloadsBL,
    IndividualWorkloadsTL,
    LicensesWithCompletenessChecksButNoCompletedInspections,
    Man001ActiveJobsBLInd,
    Man001ActiveJobsBLCount,
    Man001ActiveJobsTLInd, 
    Man001ActiveJobsTLCount,
    Man002ActiveProcessesBLInd,
    Man002ActiveProcessesBLCount, 
    Man002ActiveProcessesTLInd,
    Man002ActiveProcessesTLCount,
    Man004BLJobVolumesBySubmissionTypes,
    Man004TLJobVolumesBySubmissionTypes,
    Man005BLExpirationDates,
    Man005TLExpirationDates,
    Man006OverdueBLInspections,
    SLA_BL,
]