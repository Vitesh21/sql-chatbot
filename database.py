import vanna as vn
import pandas as pd
import pyodbc
import psycopg2
import hashlib
from vanna.remote import VannaDefault
import plotly.express as px
import streamlit as st
import os

# Vanna AI configuration
vanna_api_key = os.getenv('VANNA_API_KEY', "b53be6531860478cbd26e83581869a25")
vanna_model_name = 'chinook'
vn = VannaDefault(model=vanna_model_name, api_key=vanna_api_key)

def hash_password(password: str) -> str:
    """Hash password for security."""
    return hashlib.sha256(password.encode()).hexdigest()

def validate_input(input_str: str) -> bool:
    """Validate input to prevent SQL injection."""
    dangerous_chars = ["'", '"', ';', '--', '/*', '*/']
    return not any(char in input_str for char in dangerous_chars)

def connect_to_demo():
    """Connect to the demo SQLite database."""
    try:
        vn.connect_to_sqlite('https://vanna.ai/Chinook.sqlite')
        return True, None
    except Exception as e:
        return False, str(e)

def connect_to_database(conn_details, db_type):
    """Connect to specified database type."""
    try:
        if db_type == "MySQL":
            vn.connect_to_mysql(
                host=conn_details['host'],
                user=conn_details['username'],
                password=conn_details['password'],
                database=conn_details['database'],
                port=conn_details['port']
            )
        elif db_type == "SQL Server":
            conn_str = f"DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={conn_details['host']};DATABASE={conn_details['database']};UID={conn_details['username']};PWD={conn_details['password']}"
            con_database = pyodbc.connect(conn_str)
            vn.run_sql = lambda sql: pd.read_sql(sql, con_database)
        elif db_type == "PostgreSQL":
            vn.connect_to_postgres(
                host=conn_details['host'],
                dbname=conn_details['database'],
                user=conn_details['username'],
                password=conn_details['password'],
                port=conn_details['port']
            )
        return True, None
    except Exception as e:
        return False, str(e)

def process_query(query: str):
    """Process natural language query and return results."""
    if not validate_input(query):
        return None, None, None, "Invalid input detected"

    try:
        # Generate SQL
        sql = vn.generate_sql(query)
        
        # Execute query
        df = vn.run_sql(sql)
        
        # Generate visualization
        try:
            fig = vn.get_plotly_figure(
                plotly_code=vn.generate_plotly_code(question=query, sql=sql, df=df),
                df=df
            )
        except Exception:
            fig = None
        
        return df, sql, fig, None
    except Exception as e:
        return None, None, None, str(e)

def get_table_schema():
    """Get schema information for all tables."""
    try:
        tables = vn.run_sql("SELECT name FROM sqlite_master WHERE type='table';")
        schema = {}
        for table in tables['name']:
            columns = vn.run_sql(f"PRAGMA table_info({table});")
            schema[table] = columns[['name', 'type']].values.tolist()
        return schema, None
    except Exception as e:
        return None, str(e)
