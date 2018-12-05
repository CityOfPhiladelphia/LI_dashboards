SELECT DISTINCT jobtype "JobType",
  processtype "ProcessType",
  licensetype "LicenseType",
  COUNT(DISTINCT processid) "ProcessCounts"
FROM
  (SELECT DISTINCT 
    jt.description JobType,
    NVL(ap.licensetypesdisplayformat, ar.licensetypesdisplayformat) LicenseType,
    proc.processid ProcessID,
    pt.description ProcessType
  FROM api.processes PROC,
    api.jobs j,
    api.processtypes pt,
    api.jobtypes jt,
    api.statuses stat,
    query.j_bl_amendrenew ar,
    query.j_bl_application ap
  WHERE proc.jobid          = j.jobid
  AND proc.processtypeid    = pt.processtypeid
  AND j.jobid               = ar.jobid (+)
  AND j.jobid               = ap.jobid (+)
  AND proc.datecompleted   IS NULL
  AND j.jobtypeid           = jt.jobtypeid
  AND j.statusid            = stat.statusid
  AND pt.processtypeid NOT IN ( '984507', '2852606', '2853029' )
  AND jt.jobtypeid         IN ( '1240320', '1244773' )
  AND j.statusid NOT       IN ( '1030266', '964970', '1014809', '1036493', '1010379' )
  )
GROUP BY jobtype,
  processtype,
  licensetype
