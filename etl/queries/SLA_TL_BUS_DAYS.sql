SELECT sla.JOBID,
  sla.PROCESSID,
  sla.jobtype,
  sla.JOBCREATEDDATEFIELD,
  bds1.BUSINESSDAYSSINCE BDSinceJobCreated,
  sla.PROCESSDATECOMPLETEDFIELD,
  (
  CASE
    WHEN sla.PROCESSDATECOMPLETEDFIELD is not null
    THEN 1
    ELSE 0
  END ) ProcessCompleted,
  bds2.BUSINESSDAYSSINCE BDSinceProcessCompleted,
  bds2.BUSINESSDAYSSINCE - bds1.BUSINESSDAYSSINCE BDOpen,
  (
  CASE
    WHEN bds2.BUSINESSDAYSSINCE - bds1.BUSINESSDAYSSINCE <= 2
    THEN 1
    ELSE 0
  END ) WithinSLA
FROM LI_DASH_SLA_TL sla,
  BUSINESS_DAYS_SINCE_2017 bds1,
  BUSINESS_DAYS_SINCE_2017 bds2
WHERE TO_DATE(TO_CHAR(sla.JOBCREATEDDATEFIELD, 'mm')
  || TO_CHAR(sla.JOBCREATEDDATEFIELD, 'dd')
  || TO_CHAR(sla.JOBCREATEDDATEFIELD, 'yyyy'), 'MMDDYYYY') = bds1.DATEOFYEAR (+)
AND TO_DATE(TO_CHAR(sla.PROCESSDATECOMPLETEDFIELD, 'mm')
  || TO_CHAR(sla.PROCESSDATECOMPLETEDFIELD, 'dd')
  || TO_CHAR(sla.PROCESSDATECOMPLETEDFIELD, 'yyyy'), 'MMDDYYYY') = bds2.DATEOFYEAR (+)