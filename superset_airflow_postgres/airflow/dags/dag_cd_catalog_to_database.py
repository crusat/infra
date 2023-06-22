from airflow.models import DAG
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.models import Variable
from airflow.providers.postgres.operators.postgres import PostgresOperator
from datetime import datetime

default_args = {
    'start_date': datetime(2020, 1, 1)
}


def _processing_xml_to_json(ti):
    import json
    import xmltodict
    filename = '/files/cd_catalog.xml'
    cd_catalog_json_data = []
    with open(filename, encoding='utf8') as xml_file:
        data = xmltodict.parse(xml_file.read())
        print('data:', data)
        for element in data['CATALOG']['CD']:
            print('CD:', element)
            cd_catalog_json_data.append(element)
    Variable.set("cd_catalog_json_data", json.dumps(cd_catalog_json_data))


def _processing_contries(ti):
    import json
    cd_catalog = json.loads(Variable.get("cd_catalog_json_data"))
    result_sql = 'SELECT 1;'  # Если не будет никаких данных, чтобы не зафейлился шаг
    countries = []
    for cd in cd_catalog:
        country_title = cd['COUNTRY']
        if country_title not in countries:
            result_sql += """INSERT INTO countries (id, title)
                      VALUES ('{pk}', '{title}');
                        """.format(
                pk=country_title.replace('\'', '\'\''),
                title=country_title.replace('\'', '\'\''),
            )
            countries.append(country_title)
    Variable.set("countries_sql", result_sql)


def _processing_companies(ti):
    import json
    cd_catalog = json.loads(Variable.get("cd_catalog_json_data"))
    result_sql = 'SELECT 1;'  # Если не будет никаких данных, чтобы не зафейлился шаг
    companies = []
    for cd in cd_catalog:
        company_title = cd['COMPANY']
        if company_title not in companies:
            result_sql += """INSERT INTO companies (id, title)
                      VALUES ('{pk}', '{title}');
                        """.format(
                pk=company_title.replace('\'', '\'\''),
                title=company_title.replace('\'', '\'\''),
            )
            companies.append(company_title)
    Variable.set("companies_sql", result_sql)


def _processing_cd(ti):
    import json
    cd_catalog = json.loads(Variable.get("cd_catalog_json_data"))
    result_sql = 'SELECT 1;'  # Если не будет никаких данных, чтобы не зафейлился шаг
    for cd in cd_catalog:
        title = cd['TITLE']
        artist = cd['ARTIST']
        country_title = cd['COUNTRY']
        company_title = cd['COMPANY']
        price = str(cd['PRICE'])
        published_at = '{year}-01-01'.format(year=cd['YEAR'])  # ISO format
        result_sql += """INSERT INTO cd (title, artist, price, country, company, published_at)
            VALUES ('{title}', '{artist}', {price}, '{country}', '{company}', '{published_at}');
                """.format(
            title=title.replace('\'', '\'\''),
            artist=artist.replace('\'', '\'\''),
            price=price,
            country=country_title.replace('\'', '\'\''),
            company=company_title.replace('\'', '\'\''),
            published_at=published_at
        )
    Variable.set("cd_sql", result_sql)


with DAG('cd_catalog_to_database',
         schedule_interval='@daily',
         default_args=default_args,
         render_template_as_native_obj=True,
         catchup=False) as dag:

    create_countries_table = PostgresOperator(
        task_id="create_countries_table",
        postgres_conn_id='dataset_postgres',
        sql="""
                DROP TABLE IF EXISTS countries;
                CREATE TABLE IF NOT EXISTS countries (
                    id VARCHAR(100) NOT NULL PRIMARY KEY,
                    title VARCHAR(100) NOT NULL
                );
              """,
    )

    create_companies_table = PostgresOperator(
        task_id="create_companies_table",
        postgres_conn_id='dataset_postgres',
        sql="""
            DROP TABLE IF EXISTS companies;
            CREATE TABLE IF NOT EXISTS companies (
                id VARCHAR(100) NOT NULL PRIMARY KEY,
                title VARCHAR(100) NOT NULL
            );
          """,
    )

    create_cd_table = PostgresOperator(
        task_id="create_cd_table",
        postgres_conn_id='dataset_postgres',
        sql="""
            DROP TABLE IF EXISTS cd;
            CREATE TABLE IF NOT EXISTS cd (
                id SERIAL PRIMARY KEY,
                title VARCHAR(100) NOT NULL,
                artist VARCHAR(100) NOT NULL,
                price DECIMAL NOT NULL DEFAULT 0,
                country VARCHAR(100) NOT NULL,
                company VARCHAR(100) NOT NULL,
                published_at DATE NOT NULL
            );
          """,
    )

    processing_xml_to_json = PythonOperator(
        task_id='processing_xml_to_json',
        python_callable=_processing_xml_to_json
    )

    processing_contries = PythonOperator(
        task_id='processing_contries',
        python_callable=_processing_contries
    )
    processing_companies = PythonOperator(
        task_id='processing_companies',
        python_callable=_processing_companies
    )
    processing_cd = PythonOperator(
        task_id='processing_cd',
        python_callable=_processing_cd
    )

    populate_countries_table = PostgresOperator(
        task_id="populate_countries_table",
        postgres_conn_id='dataset_postgres',
        sql="""{{ var.value.countries_sql }}""",
    )
    populate_companies_table = PostgresOperator(
        task_id="populate_companies_table",
        postgres_conn_id='dataset_postgres',
        sql="""{{ var.value.companies_sql }}""",
    )
    populate_cd_table = PostgresOperator(
        task_id="populate_cd_table",
        postgres_conn_id='dataset_postgres',
        sql="""{{ var.value.cd_sql }}""",
    )

create_countries_table >> processing_contries >> populate_countries_table >> processing_cd
create_companies_table >> processing_companies >> populate_companies_table >> processing_cd
processing_xml_to_json >> processing_contries
processing_xml_to_json >> processing_companies
processing_xml_to_json >> processing_cd
create_cd_table >> processing_cd >> populate_cd_table
