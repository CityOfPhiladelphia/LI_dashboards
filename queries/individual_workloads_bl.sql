SELECT proc.processid,
  pt.description ProcessType,
  jt.description JobType,
  ap.licensetypesdisplayformat LicenseType,
  UPPER(u.name) name,
  proc.scheduledstartdate,
  proc.datecompleted,
  proc.datecompleted - proc.scheduledstartdate AS duration
FROM api.processes PROC,
  api.processtypes pt,
  api.jobs j,
  api.jobtypes jt,
  query.j_bl_application ap,
  api.users u
WHERE proc.jobid           = j.jobid
AND j.jobid                = ap.jobid
AND proc.processtypeid     = pt.processtypeid
AND j.jobtypeid            = jt.jobtypeid
AND proc.completedbyuserid = u.userid
AND proc.datecompleted     > '01-JAN-2016'
AND proc.datecompleted    <= SYSDATE
AND regexp_like(u.name, '[A-Za-z\s]+$')
AND u.name <> 'PPG User'
AND u.name <> 'POSSE system power user'
UNION
SELECT proc.processid,
  pt.description ProcessType,
  jt.description JobType,
  ar.licensetypesdisplayformat LicenseType,
  UPPER(u.name) name,
  proc.scheduledstartdate,
  proc.datecompleted,
  proc.datecompleted - proc.scheduledstartdate AS duration
FROM api.processes PROC,
  api.processtypes pt,
  api.jobs j,
  api.jobtypes jt,
  query.j_bl_amendrenew ar,
  api.users u
WHERE proc.jobid           = j.jobid
AND j.jobid                = ar.jobid
AND proc.processtypeid     = pt.processtypeid
AND j.jobtypeid            = jt.jobtypeid
AND proc.completedbyuserid = u.userid
AND proc.datecompleted     > '01-JAN-2016'
AND proc.datecompleted    <= SYSDATE
AND regexp_like(u.name, '[A-Za-z\s]+$')
AND u.name <> 'PPG User'
AND u.name <> 'POSSE system power user'