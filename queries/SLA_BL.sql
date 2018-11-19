SELECT j.jobid, 
  proc.processid,
  REPLACE(jt.description, 'Business License ', '') JobType,
  Extract(MONTH FROM ap.createddate)
  || '/'
  ||Extract(DAY FROM ap.createddate)
  || '/'
  || Extract(YEAR FROM ap.createddate) JobCreatedDate,
  ap.createddate JobCreatedDateField,
  ap.completeddate JobCompletedDateField,
  Extract(MONTH FROM proc.scheduledstartdate)
  || '/'
  ||Extract(DAY FROM proc.scheduledstartdate)
  || '/'
  || Extract(YEAR FROM proc.scheduledstartdate) ProcessScheduledStartDate,
  proc.scheduledstartdate ProcessScheduledStartDateField,
  (
  CASE
    WHEN proc.datecompleted IS NOT NULL
    THEN Extract(MONTH FROM proc.datecompleted)
      || '/'
      ||Extract(DAY FROM proc.datecompleted)
      || '/'
      || Extract(YEAR FROM proc.datecompleted)
    WHEN proc.datecompleted IS NULL
    THEN NULL
  END) ProcessDateCompleted,
  proc.datecompleted ProcessDateCompletedField
FROM api.processes PROC,
  api.processtypes pt,
  api.jobs j,
  api.jobtypes jt,
  query.j_bl_application ap
WHERE proc.jobid       = j.jobid
AND j.jobid            = ap.jobid
AND proc.processtypeid = pt.processtypeid
AND j.jobtypeid        = jt.jobtypeid
AND ap.createddate     > '01-JUN-2018'
AND ap.createddate    <= SYSDATE
AND pt.processtypeid LIKE '1239327'
ORDER BY ap.createddate