from sqlalchemy.engine import make_url
from sqlalchemy.engine.url import URL
from datetime import datetime
from sqlalchemy import *
import sqlalchemy as sa
import pandas as pd
import psycopg2
import json

#------------------------------------------------------------------------------------------------------
#------------------------------------- Database connections -------------------------------------------
def generate_postgresql_engine_url_sa(config_db):

    print('Generating connection URL')
    print('_________________________')

    try:

        url = make_url("postgresql+psycopg2://{}:{}@{}/{}" .format(config_db['dbuser'],
                                                                config_db['dbpassword'],
                                                                config_db['dbhost'],
                                                                config_db['db']))
        print('Connection URL: ', url)
        print('_______________________')
        return(url)
    
    except:

        print('Failed to generate connection URL. Check configuration file for incorrect inputs.')
        print('_______________________')

def generate_postgresql_engine(url):

    print('Trying to connect to SQL Server.')

    try:
        engine = sa.create_engine(url)
        print('Successfully logged in!')
        print('_______________________')
        return(engine)
    except:
        print('Unable to connect. Check server credentials provided in config file.')
        print('_______________________')

def generate_connection_url_mssql(config):

    print('Generating connection URL')
    print('_______________________')

    try:

        connection_url = URL.create(
            "mssql+pyodbc",
            username=config['dbuser'],
            password=config['dbpassword'],
            host=config['dbhost'],
            port=config['port'],
            database=config['db'],
            query={
                "driver": config['dbdriver'],
            }
        )

        print('Connection URL: ', connection_url)
        print('_______________________')
        return(connection_url)

    except:

        print('Failed to generate connection URL. Check configuration file for incorrect inputs.')
        print('_______________________')

def connect_to_sql_db(connection_url):

    print('Trying to connect to SQL Server.')
    print('_______________________')

    try:
        engine = sa.create_engine(connection_url)
        print('Successfully logged in!')
        print('_______________________')
        return(engine)
    except:
        print('Unable to connect. Check server credentials provided in config file.')
        print('_______________________')
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------

#------------------------------------------------------------------------------------------------------
#------------------------ Select/Insert data from/to database - General -------------------------------
def select_data_from_db(engine, sql_query):

    with engine.connect() as conn:
        df = pd.read_sql(sql_query, conn)

    return(df)

def insert_data_to_db(engine, sql_query):

    with engine.connect() as conn:
        conn.execute(sql_query)
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
