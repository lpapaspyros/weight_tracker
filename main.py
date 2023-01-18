from streamlit_autorefresh import st_autorefresh
import plotly.graph_objects as go
import user_authentication as ua
import database_operations as do
import config_operations as co
from datetime import datetime
import plotly.express as px
import streamlit as st
from PIL import Image
import pandas as pd
import numpy as np
import base64
import time
import os

def streamlit_config():

    current_directory = os.getcwd()
    st.set_page_config(page_title = "Sliced | Weight Tracker", layout = "wide")
    st_autorefresh(interval = 60 * 1000 * 5, key = "autorefresh")
    set_backround_image(f"{current_directory}/images/pikrepo.jpg")
    hide_app_menu()

def hide_app_menu():

    hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        </style>
        """
    st.markdown(hide_menu_style, unsafe_allow_html=True)

def read_config_files():

    current_directory = co.get_current_directory()
    config_file_path = co.get_config_files_directory(current_directory)
    config_jsons = co.read_config_file(config_file_path)
    config_db = config_jsons["config_db"]

    return(config_db)

def set_backround_image(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url(data:image/{"png"};base64,{encoded_string.decode()});
        background-size: cover
    }}
    </style>
    """,
    unsafe_allow_html=True
    )

def login_page_title():

    col1, col2, col3 = st.columns([1,1.5,1])
    html_text = "<h1 style  ='font-family: ThunderExtBd; font-size: calc(1.5em + 7.5vw); text-align:center;'>Sliced</h1>"
    col2.markdown(html_text, unsafe_allow_html = True)

def add_weight_to_db(engine, weight, tbl_column):

    sql_query = "SELECT lampros, panagiotis, nicolas, andreas FROM lp_playground.weight_tracker ORDER BY timestamp DESC LIMIT 1"
    df = do.select_data_from_db(engine, sql_query)
    df[tbl_column] = weight
    df.fillna(value='NULL', inplace = True)
    
    sql_query = f"INSERT INTO lp_playground.weight_tracker \
                (lampros, panagiotis, nicolas, andreas) \
                VALUES({df['lampros'][0]}, {df['panagiotis'][0]}, {df['nicolas'][0]}, {df['andreas'][0]})"
    do.insert_data_to_db(engine, sql_query)

def weight_line_chart(engine):

    sql_query = "SELECT * FROM lp_playground.weight_tracker"
    df = do.select_data_from_db(engine, sql_query)
    df.rename(columns = {"lampros": "Lampros", "panagiotis": "Panagiotis", "andreas": "Andreas", "nicolas": "Nicolas"}, inplace = True)
    df_melt = df.melt(id_vars='timestamp', value_vars=['Lampros', 'Panagiotis', 'Andreas', 'Nicolas'])
    fig = px.line(df_melt, x = 'timestamp' , y = 'value' , color = 'variable', labels = {"timestamp": "Time", "value": "Weight (kg)", "variable": "Soon-to-be Sayian"})
    return(fig)

def get_latest_weight_goal(engine, user):

    sql_query = f"SELECT {user} FROM lp_playground.weight_goal ORDER BY timestamp DESC LIMIT 1"
    df = do.select_data_from_db(engine, sql_query)
    weight_goal = df[user][0]
    return(weight_goal)

def add_weight_goal_to_db(engine, weight_goal, tbl_column):

    sql_query = "SELECT lampros, panagiotis, nicolas, andreas FROM lp_playground.weight_goal ORDER BY timestamp DESC LIMIT 1"
    df = do.select_data_from_db(engine, sql_query)
    df[tbl_column] = weight_goal
    df.fillna(value='NULL', inplace = True)
    
    sql_query = f"INSERT INTO lp_playground.weight_goal \
                (lampros, panagiotis, nicolas, andreas) \
                VALUES({df['lampros'][0]}, {df['panagiotis'][0]}, {df['nicolas'][0]}, {df['andreas'][0]})"
    do.insert_data_to_db(engine, sql_query)

def percentage_completion_chart(engine):

    sql_query = "SELECT lampros, panagiotis, nicolas, andreas FROM lp_playground.weight_tracker ORDER BY timestamp ASC LIMIT 1"
    df_start = do.select_data_from_db(engine, sql_query)

    sql_query = "SELECT lampros, panagiotis, nicolas, andreas FROM lp_playground.weight_tracker ORDER BY timestamp DESC LIMIT 1"
    df_latest = do.select_data_from_db(engine, sql_query)

    sql_query = "SELECT lampros, panagiotis, nicolas, andreas FROM lp_playground.weight_goal ORDER BY timestamp DESC LIMIT 1"
    df_goal = do.select_data_from_db(engine, sql_query)

    df_weight_diff = df_start.subtract(df_latest)
    df_dm_goal =  df_start.subtract(df_goal)
    df_perc = df_weight_diff.divide(df_dm_goal)
    df_perc = df_perc.multiply(100)
    data_list = df_perc.loc[0,:].to_list()

    array1 = np.array([100, 100, 100, 100])
    array2 = np.array(data_list)
    subtracted = np.subtract(array1, array2)
    subtracted_list = list(subtracted)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=['Lampros', 'Panagiotis', 'Nicolas', 'Andreas'],
        x=data_list,
        name='Completion (%)',
        orientation='h',
        marker=dict(
            color='rgba(0.0, 128, 0.0, 0.6)',
            line=dict(color='rgba(0.0, 128, 0.0, 0.9)', width=2)
        )
    ))
    fig.add_trace(go.Bar(
        y=['Lampros', 'Panagiotis', 'Nicolas', 'Andreas'],
        x=subtracted_list,
        name='Target (%)',
        orientation='h',
        marker=dict(
            color='rgba(58, 71, 80, 0.6)',
            line=dict(color='rgba(58, 71, 80, 1.0)', width=2)
        )
    ))

    fig.update_layout(barmode='stack')
    
    return(fig)

def latest_weights_band(engine, latest_weight_goal):

    sql_query = "SELECT lampros, panagiotis, nicolas, andreas FROM lp_playground.weight_tracker ORDER BY timestamp ASC LIMIT 1"
    df_start = do.select_data_from_db(engine, sql_query)

    sql_query = "SELECT lampros, panagiotis, nicolas, andreas FROM lp_playground.weight_tracker ORDER BY timestamp DESC LIMIT 1"
    df_latest = do.select_data_from_db(engine, sql_query)

    col1, col2, col3, col4, col5, col6 = st.columns([2, 1, 1, 1, 1, 2])
    col1.header(f"Your weight goal: {latest_weight_goal} kg | ")
    col2.metric("Lampros", f"{df_latest['lampros'][0]} kg",  round(df_latest["lampros"][0] - df_start["lampros"][0],2), delta_color = "inverse")
    col3.metric("Andreas", f"{df_latest['andreas'][0]} kg",  round(df_latest["andreas"][0] - df_start["andreas"][0],2), delta_color = "inverse")
    col4.metric("Panagiotis", f"{df_latest['panagiotis'][0]} kg",  round(df_latest["panagiotis"][0] - df_start["panagiotis"][0],2), delta_color = "inverse")
    col5.metric("Nicolas", f"{df_latest['nicolas'][0]} kg",  round(df_latest["nicolas"][0] - df_start["nicolas"][0],2), delta_color = "inverse")

def user_inputs_section(engine, username_column_mappings, username):

    user_inputs_expander = st.expander("Update you current weight and goals")

    with user_inputs_expander:

        col1, col2, col3 = st.columns([1, 1, 3])

        try:
            weight = col1.text_input("Latest weight measurement", "")
            if weight == "":
                col1.warning('Please enter your current weight', icon="⚠️")
            else:
                weight = float(weight.replace(",", "."))
                add_weight = col1.button("Submit Weight")
                if add_weight:
                    tbl_column = username_column_mappings[username]
                    add_weight_to_db(engine, weight, tbl_column)
                    col1.success('Weight submitted succesfully!', icon="✅")
        except Exception as error:
            col1.error('Weight should be a number. And you should know that!', icon="🚨")

        try:
            weight_goal = col2.text_input("Update your weight goal", "")
            if weight_goal == "":
                pass
            else:          
                weight_goal = float(weight_goal.replace(",", "."))
                add_goal_weight = col2.button("Submit Goal")
                if add_goal_weight:
                    tbl_column = username_column_mappings[username]
                    add_weight_goal_to_db(engine, weight_goal, tbl_column)
                    col2.success('Weight submitted succesfully!', icon="✅")
                    time.sleep(0.5)
                    st.experimental_rerun()
        except Exception as error:
            print(error)
            col2.error('Weight goal should be a number. And you should know that!', icon="🚨")

def main():

    streamlit_config_setting = streamlit_config()
    current_directory = os.getcwd()
    config_users = ua.read_users_config()
    config_db = read_config_files()
    authenticator = ua.get_authenticator(config_users)

    if st.session_state["logout"] == True \
        or (st.session_state["logout"] == None and "FormSubmitter:Login-Login" not in st.session_state.keys()) \
            or ("FormSubmitter:Login-Login" in st.session_state.keys() and st.session_state["username"] == ''):
        title = login_page_title()
    
    col1, col2, col3 = st.columns([1,1.5,1])
    log_in = col2.expander("Log In")
    with log_in:
        name, authentication_status, username = ua.user_login(authenticator)
        if authentication_status == None:
            st.warning('Please enter your username and password', icon="⚠️")

    if authentication_status == True:

        url = do.generate_postgresql_engine_url_sa(config_db)
        engine = do.generate_postgresql_engine(url)
        st.session_state["logout"] = False
        st.title(f"Sliced | Weight Tracker | {name}")

        username_column_mappings = {"l.papaspyros": "lampros",
                                    "p.erodotou": "panagiotis",
                                    "a.chatzigeorgiou": "andreas",
                                    "n.evangelou": "nicolas"}
        latest_weight_goal = get_latest_weight_goal(engine, username_column_mappings[username])
        latest_weights_band(engine, latest_weight_goal)
        
        col1, col2 = st.columns([1, 1])
        fig = weight_line_chart(engine)
        col1.plotly_chart(fig, use_container_width = True)
        fig_bar = percentage_completion_chart(engine)
        col2.plotly_chart(fig_bar, use_container_width = True)

        user_inputs_section(engine, username_column_mappings, username)

        authenticator.logout('Logout', 'main')
    
    elif authentication_status == False:

        col1, col2, col3 = st.columns([1,1.5,1])
        col2.error('Username/password is incorrect')

if __name__ == "__main__":
    main()