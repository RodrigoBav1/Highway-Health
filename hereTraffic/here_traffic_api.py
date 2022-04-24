from contextlib import redirect_stdout
import configparser
from flask import current_app, flash, jsonify, make_response, redirect, request, url_for
import pandas as pd
import schedule
import time
from herepy import (
    TrafficApi,
    IncidentsCriticalityStr
)

# Using configparser object to read your API secret data
config = configparser.ConfigParser()
config.read('project_config.ini')

# Access your API key saved in project_config.ini file
my_api_key = config['here']['here_api_key']

# DALLAS BOUNDING BOX LATTITUDES AND LONGITUDES
west_longitude = -97.000482
east_longitude = -96.463632
south_latitude = 32.613216
north_latitude = 33.023937

# AUTHORIZE THE TRAFFIC API
traffic_api = TrafficApi(api_key=my_api_key)


#----------------------------------Incident API call with Specified Area----------------------------------#
# Fetches a traffic incident information within specified area
def here_api_calls():
    incident_response = traffic_api.incidents_in_bounding_box(
        top_left=[north_latitude, west_longitude],
        bottom_right=[south_latitude, east_longitude],
        criticality=[
            IncidentsCriticalityStr.minor,
            IncidentsCriticalityStr.major,
            IncidentsCriticalityStr.critical
        ]
    )

    # Convert the traffic object to a dictionary
    response_dict_items = incident_response.as_dict()
    return response_dict_items
#--------------------------------------------------------------------------------------------------------#


#-------------------------------get_traffic_incident_details() function----------------------------------#
'''
# get_traffic_incident_details() method:
# returns traffic incident details such as:
# TRAFFIC_TIMESTAMP,
# TRAFFIC_START_TIME,
# TRAFFIC_END_TIME,
# RAFFIC_ITEM_ID,
# TRAFFIC_ITEM_TYPE_DESC,
# CRITICALITY,
# GEOLOC_ORIGIN_LATITUDE,
# GEOLOC_ORIGIN_LONGITUDE,
# GEOLOC_TO_LATITUDE,
# GEOLOC_TO_LONGITUDE
'''

formatted_data = []
column_headers = [
    'TRAFFIC_TIMESTAMP',
    'TRAFFIC_START_TIME',
    'TRAFFIC_END_TIME',
    'TRAFFIC_ITEM_ID',
    'TRAFFIC_ITEM_TYPE_DESC',
    'CRITICALITY_DESCRIPTION',
    'GEOLOC_ORIGIN_LATITUDE',
    'GEOLOC_ORIGIN_LONGITUDE',
    'GEOLOC_TO_LATITUDE',
    'GEOLOC_TO_LONGITUDE',
]


def get_traffic_incident_details():

    # makin here api call and storing the result to t_incidents var
    t_incidents = here_api_calls()

    '''
    # Storing results into variables 
    '''
    TRAFFIC_TIMESTAMP = t_incidents['TIMESTAMP']
    traffic_items = t_incidents['TRAFFIC_ITEMS']
    traffic_incidents = traffic_items['TRAFFIC_ITEM']
    for traffic_detail in traffic_incidents:
        TRAFFIC_START_TIME = traffic_detail['START_TIME'].replace(
            '"', '').replace('(', '').replace(',', '')
        TRAFFIC_END_TIME = traffic_detail['END_TIME'].replace(
            '"', '').replace('(', '').replace(',', '')
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
            [TRAFFIC_TIMESTAMP, TRAFFIC_START_TIME, TRAFFIC_END_TIME,
             TRAFFIC_ITEM_ID, TRAFFIC_ITEM_TYPE_DESC, CRITICALITY,
             GEOLOC_ORIGIN_LATITUDE, GEOLOC_ORIGIN_LONGITUDE,
             GEOLOC_TO_LATITUDE, GEOLOC_TO_LONGITUDE])

    # converting the data into dataframe, then saving it to a csv file
    df = pd.DataFrame(formatted_data, columns=column_headers)
    return df.to_csv('traffic_incidents1.csv', index=False)
#--------------------------------------------------------------------------------------------------------#


#---------------------------------scheduled_here_api_call() function-------------------------------------#
'''
# This function returns a scheduled traffic details every hour 
'''


def scheduled_here_api_call():
    schedule.every().hour.do(get_traffic_incident_details)
    while True:
        schedule.run_pending()
        time.sleep(1)


scheduled_here_api_call()  # making a call to here traffic call every hour
#--------------------------------------------------------------------------------------------------------#


#-------------------------------------Flow API with Specified Area---------------------------------------#
# # traffic flow information within specified area
# flow_response = traffic_api.flow_within_boundingbox(
#     top_left=[north_latitude, west_longitude],
#     bottom_right=[south_latitude, east_longitude]
# )
# flow_response_dict = flow_response.as_dict()
# with open('traffic_flow_detail.json', 'w') as f:
#     json.dump(flow_response_dict, f)
#--------------------------------------------------------------------------------------------------------#


#-------------------------------------Flow API with Defined Route----------------------------------------#
# traffic flow for a defined route
# flow_route_response = traffic_api.flow_in_corridor(
#     # points=[[51.5072, -0.1275], [51.50781, -0.13112], [51.51006, -0.1346]],
#     width=1000,
# )
# print(flow_route_response.as_dict())
#--------------------------------------------------------------------------------------------------------#
