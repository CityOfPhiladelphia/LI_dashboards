SELECT DISTINCT JobType "JobType",
  ProcessType "ProcessType",
  LicenseType "LicenseType",
  COUNT(DISTINCT ProcessID) "ProcessCounts"
FROM
  (SELECT DISTINCT j.ExternalFileNum JobExtNum,
    j.StatusId,
    jt.Description JobType,
    NVL(lt.description, lt2.description) LicenseType,
    stat.Description JobStatus,
    pt.ProcessTypeId,
    proc.ProcessId ProcessID,
    pt.Description ProcessType,
    extract(MONTH FROM proc.CreatedDate)
    || '/'
    ||extract(DAY FROM proc.CreatedDate)
    || '/'
    || extract(YEAR FROM proc.CreatedDate) CreatedDate,
    extract(MONTH FROM proc.ScheduledStartDate)
    || '/'
    || extract(DAY FROM proc.ScheduledStartDate)
    || '/'
    ||extract(YEAR FROM proc.ScheduledStartDate) ScheduledStartDate,
    (
    CASE
      WHEN proc.DateCompleted IS NOT NULL
      THEN extract(MONTH FROM proc.DateCompleted)
        || '/'
        || extract(DAY FROM proc.DateCompleted)
        || '/'
        ||extract(YEAR FROM proc.DateCompleted)
      ELSE NULL
    END) DateCompleted,
    proc.ProcessStatus,
    (
    CASE
      WHEN ROUND(sysdate - proc.ScheduledStartDate) <= 1
      THEN '0-1 Day'
      WHEN ROUND(sysdate - proc.ScheduledStartDate) BETWEEN 2 AND 5
      THEN '2-5 Days'
      WHEN ROUND(sysdate - proc.ScheduledStartDate) BETWEEN 6 AND 10
      THEN '6-10 Days'
      ELSE '11+ Days'
    END) Duration
  FROM api.PROCESSES PROC,
    api.jobs j,
    api.processtypes pt,
    api.jobtypes jt,
    api.statuses stat,
    query.r_tl_amendrenew_license arl,
    query.o_tl_license lic,
    query.o_tl_licensetype lt,
    query.r_tllicenselicense apl,
    query.o_tl_license lic2,
    query.o_tl_licensetype lt2
  WHERE proc.JobId          = j.JobId
  AND proc.ProcessTypeId    = pt.ProcessTypeId
  AND proc.DateCompleted   IS NULL
  AND j.JobTypeId           = jt.JobTypeId
  AND j.StatusId            = stat.StatusId
  AND pt.ProcessTypeId NOT IN ('984507','2852606','2853029')
  AND jt.JobTypeId         IN ('2853921', '2857525')
  AND j.StatusId NOT       IN ('1030266','964970','1014809','1036493','1010379')
  AND j.jobid               = arl.amendrenewid (+)
  AND arl.licenseid         = lic.objectid (+)
  AND lic.revenuecode       = lt.revenuecode (+)
  AND j.jobid               = apl.tlapp (+)
  AND apl.license           = lic2.objectid (+)
  AND lic2.revenuecode      = lt2.revenuecode (+)
  )
GROUP BY JobType,
  ProcessType,
  LicenseType