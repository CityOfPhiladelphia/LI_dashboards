SELECT DISTINCT j.ExternalFileNum "JobNumber",
  jt.Description "JobType",
  NVL(lt.Name, lt2.Name) "LicenseType",
  stat.Description "JobStatus",
  proc.ProcessId "ProcessID",
  pt.Description "ProcessType",
  extract(MONTH FROM proc.CreatedDate)
  || '/'
  ||extract(DAY FROM proc.CreatedDate)
  || '/'
  || extract(YEAR FROM proc.CreatedDate) "CreatedDate",
  extract(MONTH FROM proc.ScheduledStartDate)
  || '/'
  || extract(DAY FROM proc.ScheduledStartDate)
  || '/'
  ||extract(YEAR FROM proc.ScheduledStartDate) "ScheduledStartDate",
  proc.ProcessStatus "ProcessStatus",
  (
  CASE
    WHEN ROUND(sysdate - proc.ScheduledStartDate) <= 1
    THEN '0-1 Day'
    WHEN ROUND(sysdate - proc.ScheduledStartDate) BETWEEN 2 AND 5
    THEN '2-5 Days'
    WHEN ROUND(sysdate - proc.ScheduledStartDate) BETWEEN 6 AND 10
    THEN '6-10 Days'
    ELSE '11+ Days'
  END) "TimeSinceScheduledStartDate",
  (
  CASE
    WHEN jt.Description LIKE 'Business License Application'
    THEN 'https://eclipseprod.phila.gov/phillylmsprod/int/lms/Default.aspx#presentationId=1239699&objectHandle='
      ||j.JobId
      ||'&processHandle=&paneId=1239699_151'
    WHEN jt.Description LIKE 'Amendment/Renewal'
    THEN 'https://eclipseprod.phila.gov/phillylmsprod/int/lms/Default.aspx#presentationId=1243107&objectHandle='
      ||j.JobId
      ||'&processHandle=&paneId=1243107_175'
  END) "ProcessLink"
FROM api.PROCESSES PROC,
  api.jobs j,
  api.processtypes pt,
  api.jobtypes jt,
  api.statuses stat,
  query.r_bl_amendrenew_license arl,
  query.r_bl_license_licensetype lrl,
  query.o_bl_licensetype lt,
  query.r_bl_application_license apl,
  query.r_bl_license_licensetype lrl2,
  query.o_bl_licensetype lt2
WHERE proc.JobId          = j.JobId
AND proc.ProcessTypeId    = pt.ProcessTypeId
AND proc.DateCompleted   IS NULL
AND j.JobTypeId           = jt.JobTypeId
AND j.StatusId            = stat.StatusId
AND pt.ProcessTypeId NOT IN ('984507','2852606','2853029')
AND jt.JobTypeId         IN ('1240320', '1244773')
AND j.StatusId NOT       IN ('1030266','964970','1014809','1036493','1010379')
AND j.JobId               = arl.AmendRenewId (+)
AND arl.LicenseId         = lrl.LicenseId (+)
AND lrl.LicenseTypeId     = lt.ObjectId (+)
AND j.JobId               = apl.ApplicationObjectId (+)
AND apl.LicenseObjectId   = lrl2.LicenseId (+)
AND lrl2.LicenseTypeId    = lt2.ObjectId (+)