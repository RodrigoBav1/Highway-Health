import json
import configparser
from herepy import TrafficApi

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

# AUTHORIZE THE TRAFFIC API WITH YOUR API KEY USING 'TrafficApi(<you_api_key>)' method
traffic_api = TrafficApi(api_key=my_api_key)

# Fetches a traffic incident information within specified area
response_obj = traffic_api.flow_within_boundingbox(
    top_left=[north_latitude, west_longitude],
    bottom_right=[south_latitude, east_longitude],
)

info = response_obj.as_dict()

with open('data.json', 'w') as f:
    json.dump(info, f, indent=2)