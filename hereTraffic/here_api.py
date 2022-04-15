import csv
import requests
import configparser
from flask import current_app, flash, jsonify, make_response, redirect, request, url_for
import json
from requests.auth import HTTPBasicAuth
import sys
import pandas as pd
from herepy import (
    TrafficApi,
    IncidentsCriticalityStr,
    IncidentsCriticalityInt,
    FlowProximityAdditionalAttributes,
)
from typing import List, Optional
from enum import Enum

# Using configparser object to read your API secret data
config = configparser.ConfigParser()
config.read('project_config.ini')
# Access your API key saved in project_config.ini file
my_api_key = config['here']['here_api_key']

# Construct the URL needed for the API call request
base_url = 'https://data.traffic.hereapi.com/v7'
endpoint = '/incidents'
URL = base_url + endpoint

# DALLAS BOUNDING BOX LATTITUDES AND LONGITUDES
west_longitude = -97.000482
east_longitude = -96.463632
south_latitude = 32.613216
north_latitude = 33.023937

# AUTHORIZE THE TRAFFIC API WITH YOUR API KEY USING 'TrafficApi(<you_api_key>)' method
traffic_api = TrafficApi(api_key=my_api_key)

# Fetches a traffic incident information within specified area
response_obj = traffic_api.incidents_in_bounding_box(
    top_left=[north_latitude, west_longitude],
    bottom_right=[south_latitude, east_longitude],
    criticality=[
        IncidentsCriticalityStr.minor,
        IncidentsCriticalityStr.major,
        IncidentsCriticalityStr.critical,
    ],
)

# Convert the traffic object to a dictionary
response_dict_items = response_obj.as_dict()

# Filter the dictionary to Traffic Item dictionary
traffic_items = response_dict_items['TRAFFIC_ITEMS']
traffic_incidents = traffic_items['TRAFFIC_ITEM']

formatted_data = []


column_headers = [
    'TRAFFIC_ITEM_ID',
    'TRAFFIC_ITEM_TYPE_DESC',
    'CRITICALITY_DESCRIPTION',
    'GEOLOC_ORIGIN_LATITUDE',
    'GEOLOC_ORIGIN_LONGITUDE',
    'GEOLOC_TO_LATITUDE',
    'GEOLOC_TO_LONGITUDE',
]


def get_traffic_details():
    for traffic_detail in traffic_incidents:
        TRAFFIC_ITEM_ID = traffic_detail['TRAFFIC_ITEM_ID']
        TRAFFIC_ITEM_TYPE_DESC = traffic_detail['TRAFFIC_ITEM_TYPE_DESC']
        CRITICALITY = traffic_detail['CRITICALITY']['DESCRIPTION']
        GEOLOC_ORIGIN_LATITUDE = traffic_detail['LOCATION']['GEOLOC']['ORIGIN']['LATITUDE']
        GEOLOC_ORIGIN_LONGITUDE = traffic_detail['LOCATION']['GEOLOC']['ORIGIN']['LONGITUDE']
        GEOLOC_TO = traffic_detail['LOCATION']['GEOLOC']['TO']
        for geoloc_to in GEOLOC_TO:
            GEOLOC_TO_LATITUDE = geoloc_to['LATITUDE']
            GEOLOC_TO_LONGITUDE = geoloc_to['LONGITUDE']

        formatted_data.append(
            [TRAFFIC_ITEM_ID, TRAFFIC_ITEM_TYPE_DESC, CRITICALITY, GEOLOC_ORIGIN_LATITUDE, GEOLOC_ORIGIN_LONGITUDE, GEOLOC_TO_LATITUDE, GEOLOC_TO_LONGITUDE])
    return formatted_data


data = get_traffic_details()

df = pd.DataFrame(data, columns=column_headers)

df.to_csv('../flaskr/traffic_incidents.csv')


print(df)
# with open('traffic_incident_detail.json', 'w') as f:
#     json.dump(traffic_incidents, f)
