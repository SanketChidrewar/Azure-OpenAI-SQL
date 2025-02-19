# main_app.py

import streamlit as st
import sqlite3
import pandas as pd
import sql_db
from prompts.prompts import SYSTEM_MESSAGE
from azure_openai import get_completion_from_messages
import json
import os
import sqlparse

def query_database(query, conn):
    """ Run SQL query and return results in a dataframe """
    return pd.read_sql_query(query, conn)

# Create or connect to SQLite database
conn = sql_db.create_connection()
 
# Schema Representation for finances table
schemas = sql_db.get_schema_representation()

image_path = os.path.join(os.getcwd(), "slb_logo.svg")

# Set the page config with the logo
st.set_page_config(
    page_title="SLB SQL Query Generator",
    page_icon="slb_logo.png",
    layout="wide"
)
# Read the SVG file content
with open(image_path, "r") as file:
    svg_content = file.read()

# Add the SVG image at the top left with some padding using the SVG content
st.markdown(f"""
    <img style="position: absolute; top: 0; left: 0; padding: 1rem;">
        {svg_content}
""", unsafe_allow_html=True)

st.title("SQL Query Generator with GPT-4")
st.write("Enter your message to generate SQL and view results.")



# Input field for the user to type a message
user_message = st.text_input("Enter your message:")

if user_message:
    # Format the system message with the schema
    formatted_system_message = SYSTEM_MESSAGE.format(schema=schemas['finances'])

    # Use GPT-4 to generate the SQL query
    response = get_completion_from_messages(formatted_system_message, user_message)
    json_response = json.loads(response.choices[0].message["content"])
    query = json_response['query']

    # Display the generated SQL query
    st.write("Generated SQL Query:")
    formatted_query = sqlparse.format(query, reindent=True, keyword_case='upper')

    st.code(formatted_query, language="sql")
    st.write(response)

    try:
        # Run the SQL query and display the results
        sql_results = query_database(query, conn)
        st.write("Query Results:")
        st.dataframe(sql_results)

    except Exception as e:
        st.write(f"An error occurred: {e}")
