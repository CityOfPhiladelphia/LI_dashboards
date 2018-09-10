# License & Inspections Dashboards

This repository is used for constructing dashboards for City of Philadelphia License & Inspections.

The dashboards are as follows:

- (MAN-001) WORKLOAD OVERVIEW DASHBOARD	3
- (MAN-002) WORKLOAD DETAIL DASHBOARD	4
- (MAN-003) JOB STATUS OVERVIEW	5
- (MAN-004) APPLICATION VOLUMES BY TYPE	7
- (MAN-005) EXPIRATION VOLUMES BY TYPE	7
- (MAN-006) OVERDUE LICENSE INSPECTIONS	8
- (MAN-007) APPLICATIONS RETURNED VS ACCEPTED	10
- (MAN-008) REFUNDS DUE TO DOUBLE PAYMENT	10
- (MAN-010) INSPECTION FAILURE RATES BY REASON	11

## Dependencies (need to be updated)
- dash==0.22.0
- plotly==3.1.0
- dash_core_components==0.26.0
- dash_html_components==0.11.0
- pandas==0.22.0
- dash_table_experiments==0.6.0
- dash_auth==1.0.2
- cx_Oracle==6.4.1
- gevent==1.3.5

## Usage
Copy li_dbs folder from G:\PythonModules and paste in the \Lib\site-packages folder of your Python installation.

Get config.py file from one of us containing usernames and password logins and put it in your LI_dashboards folder.

Run index.py to launch the application and copy and paste the address of the server shown in the python command prompt into your web browser (http://192.168.104.203:8000/)
