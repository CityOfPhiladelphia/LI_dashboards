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

## Setup
1. Install dependencies 
```bash
$ pip install -r requirements.txt
```
2. Get the config.py file from one of us containing usernames and password logins and put it in your LI_dashboards base directory.
3. [Install Redis](https://github.com/rgl/redis/downloads)
4. Launch Redis 
```bash
$ C:\Program Files\Redis\redis-server
```

## Web Server
`$ python index.py`

## ETL
Run the etl process for all queries 
```bash
$ cd etl
$ python etl.py
```
Run the etl process for one dashboard 

```bash
$ cd etl
$ python etl_cli.py -n dashboard_table_name
``` 
Run the etl process for multiple specified dashboards 
```bash
$ cd etl
$ python etl_cli.py -n dashboard_table_name1 -n dashboard_table_name2
``` 
