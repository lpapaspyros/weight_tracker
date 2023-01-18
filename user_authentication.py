import streamlit_authenticator as stauth
import database_operations as do
from datetime import datetime
from yaml import SafeLoader
import streamlit as st
import bcrypt
import yaml

def read_users_config():

    with open('./config_files/users.yaml') as file:
        config_users = yaml.load(file, Loader=SafeLoader)
    return(config_users)

def write_users_config(config_users):

    with open('./config_files/users.yaml', 'w') as file:
        yaml.dump(config_users, file, default_flow_style=False)

def get_authenticator(config):

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized'])
    
    return(authenticator)

def user_login(authenticator):

    name, authentication_status, username = authenticator.login('Login', 'main')
    return(name, authentication_status, username)