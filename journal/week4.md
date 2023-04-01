# Week 4 — Postgres and RDS

## Provisioned RDS instance

aws rds create-db-instance \
  --db-instance-identifier cruddur-db-instance \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version  14.6 \
  --master-username dbroot \
  --master-user-password ****** \
  --allocated-storage 20 \
  --availability-zone us-east-1a \
  --backup-retention-period 0 \
  --port 5432 \
  --no-multi-az \
  --db-name cruddur \
  --storage-type gp2 \
  --publicly-accessible \
  --storage-encrypted \
  --enable-performance-insights \
  --performance-insights-retention-period 7 \
  --no-deletion-protection

  ## Created a Postgres DBase

Created a Dbase in the postgres client by using below command;

  CREATE Database cruddur;

  ## Added UUID Extension
Had postgres generate UUID..

  CREATE EXTENSION IF NOT EXISTS "uuid-ossp";


  ## Set environment connections for both connection url and prod connection url

  created an environment variable to login to postgres dbase automatically

    export CONNECTION_URL='postgresql://postgres:password@localhost:5432/cruddur'

    set it for gitpod environment so we don't have to set it again when gitpod is launched
    gp env CONNECTION_URL='postgresql://postgres:password@localhost:5432/cruddur'

    For production;
    export PROD_CONNECTION_URL='postgresql://dbroot:password**@cruddur-db-instance.c832fz70rks9.us-east-1.rds.amazonaws.com:5432/cruddur'
    gp env PROD_CONNECTION_URL='postgresql://dbroot:password**@cruddur-db-instance.c832fz70rks9.us-east-1.rds.amazonaws.com:5432/cruddur'


## Created Shell script to create, connect, drop, load schema, load seed data

### shell to create table
bin/db-create

        #! /usr/bin/bash

        CYAN='\033[1;36m'
        NO_COLOR='\033[0m'
        LABEL="db-create"
        printf "${CYAN}== ${LABEL}${NO_COLOR}\n"

        NO_DB_CONNECTION_URL=$(sed 's/\/cruddur//g' <<<"$CONNECTION_URL")
        createdb cruddur $NO_DB_CONNECTION_URL

### Shell to load schema
bin/db-schema-load

        #! /usr/bin/bash

        CYAN='\033[1;36m'
        NO_COLOR='\033[0m'
        LABEL="db-schema-load"
        printf "${CYAN}== ${LABEL}${NO_COLOR}\n"

        schema_path="$(realpath .)/db/schema.sql"

        NO_DB_CONNECTION_URL=$(sed 's/\/cruddur//g' <<<"$CONNECTION_URL")
        psql $NO_DB_CONNECTION_URL cruddur < $schema_path


### shell to load seed data
bin/db-seed

        #! /usr/bin/bash

        CYAN='\033[1;36m'
        NO_COLOR='\033[0m'
        LABEL="db-seed"
        printf "${CYAN}== ${LABEL}${NO_COLOR}\n"


        schema_path="$(realpath .)/db/schema.sql"

        echo $schema_path

        psql $CONNECTION_URL cruddur < $schema_path

### shell to see dbase sessions
bin/db-sessions

        #! /usr/bin/bash
        
        CYAN='\033[1;36m'
        NO_COLOR='\033[0m'
        LABEL="db-sessions"
        printf "${CYAN}== ${LABEL}${NO_COLOR}\n"


        if [ "$1" = "prod" ]; then
            echo "using production"
            CON_URL=$PROD_CONNECTION_URL
        else
            CON_URL=$CONNECTION_URL
        fi


        NO_DB_CON_URL=$(sed 's/\/cruddur//g' <<<"$CON_URL")
        psql $NO_DB_CON_URL -c "select pid as process_id, \
            usename as user,  \
            datname as db, \
            client_addr, \
            application_name as app,\
            state \
        from pg_stat_activity;"

### shell to execute dbase jobs
bin/db-setup

        #! /usr/bin/bash
        -e # stop if it fails at any point
        
        CYAN='\033[1;36m'
        NO_COLOR='\033[0m'
        LABEL="db-setup"
        printf "${CYAN}=== ${LABEL}${NO_COLOR}\n"

        bin_path='$(realpath .)/bin'

        source "$bin_path/db-drop"
        source "$bin_path/db-create"
        source "$bin_path/db-schema-load"
        source "$bin_path/db-seed"

### Add the following to our #requirments.txt

  psycopg[binary]
  psycopg[pool]

### installed the drivers

  pip install -r requirements.txt


### Created a new DB object and Connection pool in the backend-flask folder # lib/db.py

    from psycopg_pool import ConnectionPool
    import os

    connection_url = os.getenv("CONNECTION_URL")
    pool = ConnectionPool(connection_url)

## Replaced the home activities mock endpoint with a real api call;
    from lib.db import pool

        sql = """
        SELECT * FROM activities
        """
        with pool.connection() as conn:
            with conn.cursor() as cur:
              cur.execute(sql)
              # this will return a tuple
              # the first field being the data
              json = cur.fetchall()
        return json[0]


update security roles
### Connecting to our RDS instance via GITPOD
To connect to the RDS instance we provide our Gitpod IP and whitelist for inbound traffic on port 5432. Get our Gitpod IP by using below bash command;
    GITPOD_IP=$(curl ifconfig.me)


### Created an inbound rule for Postgres (5432) and provided our GITPOD_ID
Got the security group rule id so can easily modify it in the future from the terminal in Gitpod

      export DB_SG_ID="sg-0808ee10ff73520da"
      gp env DB_SG_ID="sg-0808ee10ff73520da"

      export DB_SG_RULE_ID="sgr-0cecfdc1194563b74"
      gp env DB_SG_RULE_ID="sgr-0cecfdc1194563b74"

### To update our security groups when we need, we can do this for access.

      aws ec2 modify-security-group-rules \
          --group-id $DB_SG_ID \
          --security-group-rules "SecurityGroupRuleId=$DB_SG_RULE_ID,SecurityGroupRule={Description=GITPOD,IpProtocol=tcp,FromPort=5432,ToPort=5432,CidrIpv4=$GITPOD_IP/32}"