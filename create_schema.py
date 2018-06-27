import psycopg2
import cfenv
import logging
import os


stdlogger = logging.getLogger(__name__)

psycopg2.autocommit = True

DB_HOST = 'localhost'
DB_NAME = 'postgres'
DB_USERNAME = 'postgres'
DB_PASSWORD = 'postgres'
DB_PORT = '6432'
DB_SCHEMA = os.getenv('DATABASE_SCHEMA', 'public')

if 'VCAP_SERVICES' in os.environ:
    stdlogger.info('VCAP_SERVICES found in environment')

    cf_env = cfenv.AppEnv()
    credentials = cf_env.services[0].credentials
    DB_HOST = credentials.get('host')
    DB_NAME = credentials.get('db_name', 'postgres')
    DB_USERNAME = credentials.get('username', 'postgres')
    DB_PASSWORD = credentials.get('password', 'postgres')
    DB_PORT = '5432'

db1 = psycopg2.connect(database=DB_NAME, user=DB_USERNAME,
                       password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
cursor = db1.cursor()
sql = f'CREATE SCHEMA IF NOT EXISTS {DB_SCHEMA};'
cursor.execute(sql)
db1.commit()
print("Finished")
