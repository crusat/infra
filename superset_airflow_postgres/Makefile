init:
    cp ./airflow/.env.example ./airflow/.env
    cp ./superset/.env.example ./superset/.env
    cp ./superset/.env.example ./superset/.env
    docker-compose -f ./airflow/docker-compose.yml up airflow-init
    docker-compose -f ./superset/docker-compose.yml up superset-init

up:
    docker-compose -f ./airflow/docker-compose.yml up -d
    docker-compose -f ./superset/docker-compose.yml up -d
    docker-compose -f ./dataset_postgres/docker-compose.yml up -d

start:
    docker-compose -f ./airflow/docker-compose.yml start
    docker-compose -f ./superset/docker-compose.yml start
    docker-compose -f ./dataset_postgres/docker-compose.yml start

stop:
    docker-compose -f ./airflow/docker-compose.yml stop
    docker-compose -f ./superset/docker-compose.yml stop
    docker-compose -f ./dataset_postgres/docker-compose.yml stop

restart:
    docker-compose -f ./airflow/docker-compose.yml restart
    docker-compose -f ./superset/docker-compose.yml restart
    docker-compose -f ./dataset_postgres/docker-compose.yml restart

down:
    docker-compose -f ./dataset_postgres/docker-compose.yml down
    docker-compose -f ./airflow/docker-compose.yml down
    docker-compose -f ./superset/docker-compose.yml down

destroy:
    make down
    rm -f ./airflow/.env
    rm -f ./superset/.env
    rm -f ./superset/.env