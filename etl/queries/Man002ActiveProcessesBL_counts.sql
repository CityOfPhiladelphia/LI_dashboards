SELECT DISTINCT jobtype "JobType",
  processtype "ProcessType",
  licensetype "LicenseType",
  timesincescheduledstartdate "TimeSinceScheduledStartDate",
  COUNT(DISTINCT processid) "ProcessCounts"
FROM
  (SELECT DISTINCT 
    jt.description JobType,
    NVL(ap.licensetypesdisplayformat, ar.licensetypesdisplayformat) LicenseType,
    proc.processid ProcessID,
    pt.description ProcessType,
    (CASE
      WHEN ROUND(SYSDATE - proc.scheduledstartdate) <= 1
      THEN '0-1 Day'
      WHEN ROUND(SYSDATE - proc.scheduledstartdate) BETWEEN 2 AND 5
      THEN '2-5 Days'
      WHEN ROUND(SYSDATE - proc.scheduledstartdate) BETWEEN 6 AND 10
      THEN '6-10 Days'
      WHEN ROUND(SYSDATE - proc.scheduledstartdate) BETWEEN 11 AND 365
      THEN '11 Days-1 Year'
      ELSE 'Over 1 Year'
    END) TimeSinceScheduledStartDate
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
  licensetype,
  timesincescheduledstartdate