import json
import pandas as pd
import os

#------------------------------------------------------------------------------------------------------
#---------------------------------- Configuration jsons operations ------------------------------------
def get_current_directory():

    current_directory = os.getcwd()
    return(current_directory)

def get_config_files_directory(current_directory):

    config_file_path = current_directory + '\\config_files\\'
    return(config_file_path)

def read_config_file(config_file_path):

    config_files = os.listdir(config_file_path)
    config_jsons = {}

    for config_file in config_files:
            
        if ".json" in config_file:

            config_json_path = config_file_path + config_file
            config_file_key = config_file[0:config_file.index(".")]

            with open(config_json_path) as config_json:
                config = json.load(config_json)
                config_jsons[config_file_key] = config

    return(config_jsons)

def update_config_json(config):

    current_directory = get_current_directory()
    file_path = current_directory + '/config_files/config.json'

    with open(file_path, "w") as config_json:
        json.dump(config, config_json, indent=4)
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
