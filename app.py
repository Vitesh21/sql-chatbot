import vanna as vn
import streamlit as st
import time
import pandas as pd
import pyodbc
import psycopg2
import hashlib
import os
from datetime import datetime
from streamlit_option_menu import option_menu
from vanna.remote import VannaDefault
import plotly.express as px
from typing import Optional
import json
from pathlib import Path

# Set page configuration
st.set_page_config(
    page_title="SQL Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
        border-radius: 10px;
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #0066cc;
        color: white;
    }
    .success-message {
        padding: 1rem;
        border-radius: 5px;
        background-color: #d4edda;
        color: #155724;
        margin: 1rem 0;
    }
    .error-message {
        padding: 1rem;
        border-radius: 5px;
        background-color: #f8d7da;
        color: #721c24;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'history' not in st.session_state:
    st.session_state.history = []
if 'connected' not in st.session_state:
    st.session_state.connected = False
if 'connection_details' not in st.session_state:
    st.session_state.connection_details = None
if 'auth_attempts' not in st.session_state:
    st.session_state.auth_attempts = 0
if 'favorites' not in st.session_state:
    st.session_state.favorites = []
if 'saved_connections' not in st.session_state:
    st.session_state.saved_connections = []

# Vanna AI configuration
vanna_api_key = "b53be6531860478cbd26e83581869a25"
vanna_model_name = 'chinook'
vn = VannaDefault(model=vanna_model_name, api_key=vanna_api_key)

# Load saved connections and favorites
def load_saved_data():
    try:
        if Path('saved_data.json').exists():
            with open('saved_data.json', 'r') as f:
                data = json.load(f)
                st.session_state.favorites = data.get('favorites', [])
                st.session_state.saved_connections = data.get('saved_connections', [])
    except Exception as e:
        st.error(f"Error loading saved data: {str(e)}")

def save_data():
    try:
        data = {
            'favorites': st.session_state.favorites,
            'saved_connections': st.session_state.saved_connections
        }
        with open('saved_data.json', 'w') as f:
            json.dump(data, f)
    except Exception as e:
        st.error(f"Error saving data: {str(e)}")

# Security functions
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def validate_input(input_str: str) -> bool:
    dangerous_chars = ["'", '"', ';', '--', '/*', '*/']
    return not any(char in input_str for char in dangerous_chars)

# UI Components
def show_header():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🤖 SQL Chatbot Assistant")
        st.markdown("*Your intelligent database companion*")
    with col2:
        if st.session_state.connected:
            st.success("🟢 Connected")
        else:
            st.error("🔴 Disconnected")

def show_saved_connections():
    if st.session_state.saved_connections:
        st.subheader("💾 Saved Connections")
        for conn in st.session_state.saved_connections:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{conn['name']}** ({conn['type']})")
                st.write(f"Host: {conn['host']}, Database: {conn['database']}")
            with col2:
                if st.button("Connect", key=f"saved_{conn['name']}"):
                    return conn
    return None

def show_connection_form():
    with st.form("connection_form"):
        connection_name = st.text_input("Save as (optional)", placeholder="My Connection")
        server_host = st.text_input("Hostname", placeholder="Enter domain url or IPv4 Address")
        col1, col2 = st.columns(2)
        with col1:
            server_port = st.number_input("Port", min_value=0, max_value=65535)
            database_name = st.text_input("Database Name", placeholder="Database name")
        with col2:
            username = st.text_input("Username", placeholder="Username")
            password = st.text_input("Password", type="password")
        
        save_connection = st.checkbox("Save connection details")
        submitted = st.form_submit_button("Connect")
        
        if submitted:
            if not all([server_host, database_name, username, password]):
                st.error("Please fill in all required fields")
                return None
            
            return {
                'host': server_host,
                'port': server_port,
                'database': database_name,
                'username': username,
                'password': password,
                'save': save_connection,
                'name': connection_name if save_connection else None
            }
    return None

def show_query_interface():
    st.subheader("💬 Ask your question")
    query = st.text_area("What would you like to know?", key="query", height=100)
    
    col1, col2 = st.columns([1, 5])
    with col1:
        execute = st.button("🔍 Execute")
    with col2:
        save = st.button("❤️ Save Query")
    
    return query, execute, save

def process_query(query: str):
    if not validate_input(query):
        st.error("Invalid input detected")
        return

    try:
        with st.spinner("🤔 Generating SQL..."):
            sql = vn.generate_sql(query)
            st.code(sql, language='sql')
        
        with st.spinner("⚡ Running query..."):
            df = vn.run_sql(sql)
            
        # Save to history
        st.session_state.history.append({
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'query': query,
            'sql': sql
        })
        
        # Show results
        st.subheader("📊 Results")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.dataframe(df, use_container_width=True)
        with col2:
            st.download_button(
                label="📥 Download CSV",
                data=df.to_csv(index=False),
                file_name="query_results.csv",
                mime="text/csv"
            )
        
        # Visualization
        st.subheader("📈 Visualization")
        try:
            fig = vn.get_plotly_figure(
                plotly_code=vn.generate_plotly_code(question=query, sql=sql, df=df),
                df=df
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception:
            st.info("No visualization available for this query")
            
    except Exception as e:
        st.error(f"Error processing query: {str(e)}")

def show_history():
    if st.session_state.history:
        st.subheader("📜 Query History")
        for idx, item in enumerate(reversed(st.session_state.history)):
            with st.expander(f"Query {len(st.session_state.history) - idx}: {item['timestamp']}"):
                st.write("Question:", item['query'])
                st.code(item['sql'], language='sql')
                if st.button("Use this query", key=f"use_history_{idx}"):
                    return item['query']
    return None

def show_favorites():
    if st.session_state.favorites:
        st.subheader("❤️ Favorite Queries")
        for idx, fav in enumerate(st.session_state.favorites):
            with st.expander(f"Query {idx + 1}: {fav['timestamp']}"):
                st.write(fav['query'])
                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.button("Use", key=f"use_fav_{idx}"):
                        return fav['query']
                with col2:
                    if st.button("Remove", key=f"remove_fav_{idx}"):
                        st.session_state.favorites.pop(idx)
                        save_data()
                        st.experimental_rerun()
    return None

def connect_to_database(conn_details):
    try:
        with st.spinner(f"Connecting to {conn_details['host']}..."):
            if st.session_state.selected_db == "MySQL":
                vn.connect_to_mysql(
                    host=conn_details['host'],
                    user=conn_details['username'],
                    password=conn_details['password'],
                    database=conn_details['database'],
                    port=conn_details['port']
                )
            elif st.session_state.selected_db == "SQL Server":
                conn_str = f"DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={conn_details['host']};DATABASE={conn_details['database']};UID={conn_details['username']};PWD={conn_details['password']}"
                con_database = pyodbc.connect(conn_str)
                vn.run_sql = lambda sql: pd.read_sql(sql, con_database)
            elif st.session_state.selected_db == "PostgreSQL":
                vn.connect_to_postgres(
                    host=conn_details['host'],
                    dbname=conn_details['database'],
                    user=conn_details['username'],
                    password=conn_details['password'],
                    port=conn_details['port']
                )
            
            st.session_state.connected = True
            st.session_state.connection_details = conn_details
            
            if conn_details.get('save') and conn_details.get('name'):
                st.session_state.saved_connections.append({
                    'name': conn_details['name'],
                    'type': st.session_state.selected_db,
                    'host': conn_details['host'],
                    'database': conn_details['database'],
                    'username': conn_details['username'],
                    'password': conn_details['password'],
                    'port': conn_details['port']
                })
                save_data()
            
            st.success("Connected successfully!")
            st.experimental_rerun()
    except Exception as e:
        st.error(f"Connection failed: {str(e)}")
        st.session_state.auth_attempts += 1
        if st.session_state.auth_attempts >= 3:
            st.error("Too many failed attempts. Please try again later.")
            time.sleep(5)

def main():
    show_header()
    
    with st.sidebar:
        st.session_state.selected_db = option_menu(
            menu_title="🔗 Database Connection",
            options=["Demo Database", "MySQL", "SQL Server", "PostgreSQL"],
            icons=["database-fill", "server", "windows", "diagram-3-fill"]
        )
        
        if st.session_state.connected:
            if st.button("❌ Disconnect"):
                st.session_state.connected = False
                st.session_state.connection_details = None
                st.experimental_rerun()
        
        saved_conn = show_saved_connections()
        if saved_conn:
            connect_to_database(saved_conn)
    
    if st.session_state.selected_db == "Demo Database":
        if not st.session_state.connected:
            if st.button("🎯 Connect to Demo"):
                with st.spinner("Connecting to demo database..."):
                    try:
                        vn.connect_to_sqlite('https://vanna.ai/Chinook.sqlite')
                        st.session_state.connected = True
                        st.success("Connected to demo database!")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Connection failed: {str(e)}")
        else:
            query, execute, save = show_query_interface()
            
            if execute and query:
                process_query(query)
            
            if save and query:
                st.session_state.favorites.append({
                    'query': query,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                save_data()
                st.success("Query saved to favorites!")
            
            col1, col2 = st.columns(2)
            with col1:
                history_query = show_history()
                if history_query:
                    st.session_state.query = history_query
                    st.experimental_rerun()
            
            with col2:
                fav_query = show_favorites()
                if fav_query:
                    st.session_state.query = fav_query
                    st.experimental_rerun()
    
    else:
        if not st.session_state.connected:
            st.info(f"Connect to your {st.session_state.selected_db} database")
            conn_details = show_connection_form()
            if conn_details:
                connect_to_database(conn_details)
        else:
            query, execute, save = show_query_interface()
            
            if execute and query:
                process_query(query)
            
            if save and query:
                st.session_state.favorites.append({
                    'query': query,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                save_data()
                st.success("Query saved to favorites!")
            
            col1, col2 = st.columns(2)
            with col1:
                history_query = show_history()
                if history_query:
                    st.session_state.query = history_query
                    st.experimental_rerun()
            
            with col2:
                fav_query = show_favorites()
                if fav_query:
                    st.session_state.query = fav_query
                    st.experimental_rerun()

if __name__ == "__main__":
    load_saved_data()
    main()
