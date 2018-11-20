SELECT DISTINCT jobtype "JobType",
  processtype "ProcessType",
  licensetype "LicenseType",
  COUNT(DISTINCT processid) "ProcessCounts"
FROM
  (SELECT DISTINCT j.externalfilenum JobExtNum,
    j.statusid,
    jt.description JobType,
    NVL(ap.licensetypesdisplayformat, ar.licensetypesdisplayformat) LicenseType,
    stat.description JobStatus,
    pt.processtypeid,
    proc.processid ProcessID,
    pt.description ProcessType,
    Extract( MONTH FROM proc.createddate)
    || '/'
    ||Extract(DAY FROM proc.createddate)
    || '/'
    || Extract(YEAR FROM proc.createddate) CreatedDate,
    Extract( MONTH FROM proc.scheduledstartdate)
    || '/'
    || Extract(DAY FROM proc.scheduledstartdate)
    || '/'
    ||Extract(YEAR FROM proc.scheduledstartdate) ScheduledStartDate ,
    (
    CASE
      WHEN proc.datecompleted IS NOT NULL
      THEN Extract(MONTH FROM proc.datecompleted)
        || '/'
        || Extract( DAY FROM proc.datecompleted)
        || '/'
        ||Extract(YEAR FROM proc.datecompleted)
      ELSE NULL
    END) DateCompleted,
    proc.processstatus,
    (
    CASE
      WHEN ROUND(SYSDATE - proc.scheduledstartdate) <= 1
      THEN '0-1 Day'
      WHEN ROUND(SYSDATE - proc.scheduledstartdate) BETWEEN 2 AND 5
      THEN '2-5 Days'
      WHEN ROUND(SYSDATE - proc.scheduledstartdate) BETWEEN 6 AND 10
      THEN '6-10 Days'
      ELSE '11+ Days'
    END ) TimeSinceScheduledStartDate
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