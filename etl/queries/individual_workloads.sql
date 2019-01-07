SELECT proc.processid,
  pt.description ProcessType,
  REPLACE(REPLACE(jt.description, 'Business License ', ''), 'Amendment/Renewal', 'Amend/Renew') JobType,
  'Business' LicenseKind,
  ap.licensetypesdisplayformat LicenseType,
  INITCAP(u.name) name,
  Extract(month FROM proc.scheduledstartdate) || '/' ||Extract(day FROM proc.scheduledstartdate) || '/' || Extract(year FROM proc.scheduledstartdate) ScheduledStartDate,
  Extract(month FROM proc.datecompleted) || '/' ||Extract(day FROM proc.datecompleted) || '/' || Extract(year FROM proc.datecompleted) DateCompleted,
  proc.datecompleted DateCompletedField,
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
AND proc.datecompleted     > add_months(TRUNC(SYSDATE, 'MM'),-13)
AND proc.datecompleted    <= SYSDATE
AND regexp_like(u.name, '[A-Za-z\s]+$')
AND u.name <> 'PPG User'
AND u.name <> 'POSSE system power user'
UNION
SELECT proc.processid,
  pt.description ProcessType,
  REPLACE(REPLACE(jt.description, 'Business License ', ''), 'Amendment/Renewal', 'Amend/Renew') JobType,
  'Business' LicenseKind,
  ar.licensetypesdisplayformat LicenseType,
  INITCAP(u.name) name,
  Extract(month FROM proc.scheduledstartdate) || '/' ||Extract(day FROM proc.scheduledstartdate) || '/' || Extract(year FROM proc.scheduledstartdate) ScheduledStartDate,
  Extract(month FROM proc.datecompleted) || '/' ||Extract(day FROM proc.datecompleted) || '/' || Extract(year FROM proc.datecompleted) DateCompleted,
  proc.datecompleted DateCompletedField,
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
AND proc.datecompleted     > add_months(TRUNC(SYSDATE, 'MM'),-13)
AND proc.datecompleted    <= SYSDATE
AND regexp_like(u.name, '[A-Za-z\s]+$')
AND u.name <> 'PPG User'
AND u.name <> 'POSSE system power user'
UNION
SELECT proc.processid,
  pt.description ProcessType,
  REPLACE(jt.description, 'Trade License ', '') JobType,
  'Trade' LicenseKind,
  lt.title LicenseType,
  INITCAP(u.name) name,
  Extract(month FROM proc.scheduledstartdate) || '/' ||Extract(day FROM proc.scheduledstartdate) || '/' || Extract(year FROM proc.scheduledstartdate) ScheduledStartDate,
  Extract(month FROM proc.datecompleted) || '/' ||Extract(day FROM proc.datecompleted) || '/' || Extract(year FROM proc.datecompleted) DateCompleted,
  proc.datecompleted DateCompletedField,
  proc.datecompleted - proc.scheduledstartdate AS duration
FROM api.processes PROC,
  api.processtypes pt,
  api.jobs j,
  api.jobtypes jt,
  query.j_tl_application ap,
  query.r_tllicensetype lrl,
  query.o_tl_licensetype lt,
  api.users u
WHERE proc.jobid            = j.jobid
AND j.jobid                 = ap.objectid
AND ap.tradelicenseobjectid = lrl.licenseobjectid (+)
AND lrl.licensetypeobjectid = lt.objectid (+)
AND proc.processtypeid      = pt.processtypeid
AND j.jobtypeid             = jt.jobtypeid
AND proc.completedbyuserid  = u.userid
AND proc.datecompleted      > add_months(TRUNC(SYSDATE, 'MM'),-13)
AND proc.datecompleted     <= SYSDATE
AND regexp_like(u.name, '[A-Za-z\s]+$')
AND u.name <> 'PPG User'
AND u.name <> 'POSSE system power user'
UNION
SELECT proc.processid,
  pt.description ProcessType,
  REPLACE(jt.description, 'Trade License ', '') JobType,
  'Trade' LicenseKind,
  lt.title LicenseType,
  INITCAP(u.name) name,
  Extract(month FROM proc.scheduledstartdate) || '/' ||Extract(day FROM proc.scheduledstartdate) || '/' || Extract(year FROM proc.scheduledstartdate) ScheduledStartDate,
  Extract(month FROM proc.datecompleted) || '/' ||Extract(day FROM proc.datecompleted) || '/' || Extract(year FROM proc.datecompleted) DateCompleted,
  proc.datecompleted DateCompletedField,
  proc.datecompleted - proc.scheduledstartdate AS duration
FROM api.processes PROC,
  api.processtypes pt,
  api.jobs j,
  api.jobtypes jt,
  query.j_tl_amendrenew ar,
  query.r_tl_amendrenew_license arl,
  query.r_tllicensetype lrl,
  query.o_tl_licensetype lt,
  api.users u
WHERE proc.jobid            = j.jobid
AND j.externalfilenum       = ar.externalfilenum
AND ar.objectid             = arl.amendrenewid (+)
AND arl.licenseid           = lrl.licenseobjectid (+)
AND lrl.licensetypeobjectid = lt.objectid (+)
AND proc.processtypeid      = pt.processtypeid
AND j.jobtypeid             = jt.jobtypeid
AND proc.completedbyuserid  = u.userid
AND proc.datecompleted      > add_months(TRUNC(SYSDATE, 'MM'),-13)
AND proc.datecompleted     <= SYSDATE
AND regexp_like(u.name, '[A-Za-z\s]+$')
AND u.name <> 'PPG User'
AND u.name <> 'POSSE system power user'