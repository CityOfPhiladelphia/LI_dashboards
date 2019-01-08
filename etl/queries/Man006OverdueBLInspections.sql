SELECT biz.address "Business Address",
  lic.externalfilenum "License Number",
  lic.licensetype "License Type",
  (
  CASE
    WHEN jt.name LIKE 'j_BL_Inspection'
    THEN ins.externalfilenum
  END) "Job Number",
  (
  CASE
    WHEN jt.name LIKE 'j_BL_Inspection'
    THEN 'License'
    WHEN jt.name LIKE 'j_BL_Application'
    THEN 'Application'
    WHEN jt.name LIKE 'j_BL_AmendRenew'
    THEN 'Renewal or Amend'
  END ) "Inspection On",
  ins.inspectiontype "Inspection Type",
  ins.objectid "Insp Object Id",
  Extract(MONTH FROM ins.createddate)
  || '/'
  ||Extract(DAY FROM ins.createddate)
  || '/'
  || Extract(YEAR FROM ins.createddate) "Inspection Created Date",
  ROUND(SYSDATE - ins.createddate) "Days Since Insp Created",
  (
  CASE
    WHEN ROUND(SYSDATE - ins.createddate) < 7
    THEN 'Less than a week'
    WHEN ROUND(SYSDATE - ins.createddate) BETWEEN 7 AND 30
    THEN '7-30 days'
    WHEN ROUND(SYSDATE - ins.createddate) BETWEEN 31 AND 365
    THEN '31 - 365 days'
    ELSE 'More than a year'
  END) "Time Since Insp Created",
  Extract(MONTH FROM ins.scheduledinspectiondate)
  || '/'
  ||Extract(DAY FROM ins.scheduledinspectiondate)
  || '/'
  || Extract(YEAR FROM ins.scheduledinspectiondate) "Scheduled Inspection Date",
  ins.scheduledinspectiondate "ScheduledInspectionDateField",
  ins.inspectorname "Inspector",
  'https://eclipseprod.phila.gov/phillylmsprod/int/lms/Default.aspx#presentationId=1244842&objectHandle=' || ins.objectid || '&processHandle=' "Link"
FROM query.j_bl_inspection ins,
  query.r_bl_licenseinspection li,
  query.o_bl_license lic,
  query.o_bl_business biz,
  query.o_jobtypes jt
WHERE ins.objectid               = li.inspectionid
AND ins.jobtypeid                = jt.jobtypeid
AND li.licenseid                 = lic.objectid
AND lic.businessobjectid         = biz.objectid
AND ins.scheduledinspectiondate <= SYSDATE
AND ins.completeddate           IS NULL
UNION
SELECT biz.address "Business Address",
  lic.externalfilenum "License Number",
  lic.licensetype "License Type",
  (
  CASE
    WHEN jt.name LIKE 'j_BL_Inspection'
    THEN ins.externalfilenum
    WHEN jt.name LIKE 'j_BL_Application'
    THEN ap.externalfilenum
  END ) "Job Number",
  (
  CASE
    WHEN jt.name LIKE 'j_BL_Inspection'
    THEN 'License'
    WHEN jt.name LIKE 'j_BL_Application'
    THEN 'Application'
    WHEN jt.name LIKE 'j_BL_AmendRenew'
    THEN 'Renewal or Amend'
  END ) "Inspection On",
  ins.inspectiontype "Inspection Type",
  ins.objectid "Insp Object Id",
  Extract(MONTH FROM ins.createddate)
  || '/'
  ||Extract(DAY FROM ins.createddate)
  || '/'
  || Extract(YEAR FROM ins.createddate) "Inspection Created Date",
  ROUND(SYSDATE - ins.createddate) "Days Since Insp Created",
  (
  CASE
    WHEN ROUND(SYSDATE - ins.createddate) < 7
    THEN 'Less than a week'
    WHEN ROUND(SYSDATE - ins.createddate) BETWEEN 7 AND 30
    THEN '7-30 days'
    WHEN ROUND(SYSDATE - ins.createddate) BETWEEN 31 AND 365
    THEN '31 - 365 days'
    ELSE 'More than a year'
  END) "Time Since Insp Created",
  Extract(MONTH FROM ins.scheduledinspectiondate)
  || '/'
  ||Extract(DAY FROM ins.scheduledinspectiondate)
  || '/'
  || Extract(YEAR FROM ins.scheduledinspectiondate) "Scheduled Inspection Date",
  ins.scheduledinspectiondate "ScheduledInspectionDateField",
  ins.inspectorname "Inspector",
  'https://eclipseprod.phila.gov/phillylmsprod/int/lms/Default.aspx#presentationId=1244842&objectHandle=' || ins.objectid || '&processHandle=' "Link"
FROM query.j_bl_inspection ins,
  query.r_bl_applicationinspection api,
  query.j_bl_application ap,
  query.o_jobtypes jt,
  query.r_bl_application_license apl,
  query.o_bl_license lic,
  query.o_bl_business biz
WHERE ins.objectid               = api.inspectionid
AND api.applicationid            = ap.objectid
AND ap.jobtypeid                 = jt.jobtypeid
AND ap.objectid                  = apl.applicationobjectid
AND apl.licenseobjectid          = lic.objectid
AND lic.businessobjectid         = biz.objectid
AND ins.scheduledinspectiondate <= SYSDATE
AND ins.completeddate           IS NULL
UNION
SELECT biz.address "Business Address",
  lic.externalfilenum "License Number",
  lic.licensetype "License Type",
  (
  CASE
    WHEN jt.name LIKE 'j_BL_Inspection'
    THEN ins.externalfilenum
    WHEN jt.name LIKE 'j_BL_AmendRenew'
    THEN ar.externalfilenum
  END ) "Job Number",
  (
  CASE
    WHEN jt.name LIKE 'j_BL_Inspection'
    THEN 'License'
    WHEN jt.name LIKE 'j_BL_Application'
    THEN 'Application'
    WHEN jt.name LIKE 'j_BL_AmendRenew'
    THEN 'Renewal or Amend'
  END ) "Inspection On",
  ins.inspectiontype "Inspection Type",
  ins.objectid "Insp Object Id",
  Extract(MONTH FROM ins.createddate)
  || '/'
  ||Extract(DAY FROM ins.createddate)
  || '/'
  || Extract(YEAR FROM ins.createddate) "Inspection Created Date",
  ROUND(SYSDATE - ins.createddate) "Days Since Insp Created",
  (
  CASE
    WHEN ROUND(SYSDATE - ins.createddate) < 7
    THEN 'Less than a week'
    WHEN ROUND(SYSDATE - ins.createddate) BETWEEN 7 AND 30
    THEN '7-30 days'
    WHEN ROUND(SYSDATE - ins.createddate) BETWEEN 31 AND 365
    THEN '31 - 365 days'
    ELSE 'More than a year'
  END) "Time Since Insp Created",
  Extract(MONTH FROM ins.scheduledinspectiondate)
  || '/'
  ||Extract(DAY FROM ins.scheduledinspectiondate)
  || '/'
  || Extract(YEAR FROM ins.scheduledinspectiondate) "Scheduled Inspection Date",
  ins.scheduledinspectiondate "ScheduledInspectionDateField",
  ins.inspectorname "Inspector",
  'https://eclipseprod.phila.gov/phillylmsprod/int/lms/Default.aspx#presentationId=1244842&objectHandle=' || ins.objectid || '&processHandle=' "Link"
FROM query.j_bl_inspection ins,
  query.r_bl_amendrenewinspection ari,
  query.j_bl_amendrenew ar,
  query.o_jobtypes jt,
  query.r_bl_amendrenew_license arl,
  query.o_bl_license lic,
  query.o_bl_business biz
WHERE ins.objectid               = ari.inspectionid
AND ari.amendrenewid             = ar.jobid
AND ar.jobtypeid                 = jt.jobtypeid
AND ar.objectid                  = arl.amendrenewid
AND arl.licenseid                = lic.objectid
AND lic.businessobjectid         = biz.objectid
AND ins.scheduledinspectiondate <= SYSDATE
AND ins.completeddate           IS NULL