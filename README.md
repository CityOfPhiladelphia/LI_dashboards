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

## Overview
- Data is ETL'd from Hansen / Eclipse into AWS RDS nightly for each dashboard
- Data is cached in Redis
- Dashboards are served by Dash / Flask

## Requirements
- Python 3.6+
- Pip
- [Redis](https://github.com/rgl/redis/downloads)

## Usage
- Install dependencies

`pip install -r requirements.txt`
- Get the config.py file from one of us containing usernames and password logins and put it in your LI_dashboards folder.
- [Install Redis](https://github.com/rgl/redis/downloads)
- Launch Redis

`C:\Program Files\Redis\redis-server`
- Launch the application

`python index.py`
- Run the etl process for all queries

`python etl/etl.py`
- Run the etl process for one dashboard

`python etl/etl_cli.py -n dashboard_table_name` 
    - Ex: 
    
        `python etl/etl_cli.py -n li_dash_indworkloads_bl`
- Run the etl process for multiple specified dashboards

`python etl/etl_cli.py -n dashboard_table_name1 -n dashboard_table_name2` 
    - Ex: 
    
        `python etl/etl_cli.py -n li_dash_indworkloads_bl -n li_dash_activejobs_bl_counts`
