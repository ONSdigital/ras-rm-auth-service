import psycopg2
import cfenv
import logging
import os

from ras_rm_auth_service.ras_rm_auth_service.settings.default import get_default_db_configuration

stdlogger = logging.getLogger(__name__)

psycopg2.autocommit = True

DB_HOST = 'localhost'
DB_NAME = 'postgres'
DB_USERNAME = 'postgres'
DB_PASSWORD = 'postgres'
DB_PORT = os.getenv('DB_PORT', '6432')
DB_SCHEMA = os.getenv('DB_SCHEMA', 'public')

if 'VCAP_SERVICES' in os.environ:
    stdlogger.info('VCAP_SERVICES found in environment')

    cf_env = cfenv.AppEnv()
    credentials = cf_env.services[0].credentials
    DB_HOST = credentials.get('host')
    DB_NAME = credentials.get('db_name', 'postgres')
    DB_USERNAME = credentials.get('username', 'postgres')
    DB_PASSWORD = credentials.get('password', 'postgres')
    DB_PORT = '5432'

database = get_default_db_configuration()

db1 = psycopg2.connect(
    database=database.get("NAME"),
    user=database.get("USER"),
    password=database.get("PASSWORD"),
    host=database.get("HOST"),
    port=database.get("PORT")
)

cursor = db1.cursor()
sql = f'CREATE SCHEMA IF NOT EXISTS {DB_SCHEMA};'
cursor.execute(sql)
db1.commit()
print("Finished")
