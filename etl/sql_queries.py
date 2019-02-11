class SqlQuery():
    def __init__(self, extract_query_file, target_table):
        self.extract_query_file = 'queries/' + extract_query_file
        self.target_table = target_table

IndividualWorkloads = SqlQuery(
    extract_query_file = 'individual_workloads.sql',
    target_table = 'li_dash_indworkloads'
)

IncompleteProcessesBL = SqlQuery(
    extract_query_file = 'incomplete_processes_bl.sql',
    target_table = 'li_dash_incompleteprocesses_bl'
)

IncompleteProcessesTL = SqlQuery(
    extract_query_file = 'incomplete_processes_tl.sql',
    target_table = 'li_dash_incompleteprocesses_tl'
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

SLA_TL = SqlQuery(
    extract_query_file = 'SLA_TL.sql',
    target_table = 'li_dash_sla_tl'
)

UninspectedBLsWithCompCheck = SqlQuery(
    extract_query_file = 'UninspectedBLsWithCompChecks.sql',
    target_table = 'li_dash_uninsp_bl_comp_check'
)

queries = [
    IndividualWorkloads,
    IncompleteProcessesBL,
    IncompleteProcessesTL,
    UninspectedBLsWithCompCheck,
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
    SLA_TL
]