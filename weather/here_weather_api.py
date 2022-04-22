import configparser
import json
import requests  # Needed for making HTTP requests
import time  # Needed to generate the OAuth timestamp
import urllib.parse  # Needed to URLencode the parameter string
from base64 import b64encode  # Needed for create_signature function
import hmac  # Needed for create_signature function
import hashlib  # Needed for create_signature functionx
import binascii  # Needed for create_signature function

# Using configparser object to read your API secret data
config = configparser.ConfigParser()
config.read('project_config.ini')

here_api_key = config['here']['here_weather_api_key']

grant_type = 'client_credentials'
oauth_consumer_key = config['here']['here_access_key_id']
access_key_secret = config['here']['here_access_key_secret']
oauth_nonce = str(int(time.time()*1000))
oauth_timestamp = str(int(time.time()))
oauth_signature_method = 'HMAC-SHA256'
oauth_version = '1.0'
here_token_url = 'https://account.api.here.com/oauth2/token'

# HMAC-SHA256 hashing algorithm to generate the OAuth signature


def create_signature(secret_key, signature_base_string):
    encoded_string = signature_base_string.encode()
    encoded_key = secret_key.encode()
    temp = hmac.new(encoded_key, encoded_string, hashlib.sha256).hexdigest()
    byte_array = b64encode(binascii.unhexlify(temp))
    return byte_array.decode()


# concatenate the six oauth parameters, plus the request parameters
def create_parameter_string(grant_type,  oauth_consumer_key, oauth_nonce, oauth_signature_method, oauth_timestamp, oauth_version):
    parameter_string = ''
    parameter_string = parameter_string + 'grant_type=' + grant_type
    parameter_string = parameter_string + '&oauth_consumer_key=' + oauth_consumer_key
    parameter_string = parameter_string + '&oauth_nonce=' + oauth_nonce
    parameter_string = parameter_string + \
        '&oauth_signature_method=' + oauth_signature_method
    parameter_string = parameter_string + '&oauth_timestamp=' + oauth_timestamp
    parameter_string = parameter_string + '&oauth_version=' + oauth_version
    return parameter_string


parameter_string = create_parameter_string(
    grant_type,  oauth_consumer_key, oauth_nonce, oauth_signature_method, oauth_timestamp, oauth_version)
encoded_parameter_string = urllib.parse.quote(parameter_string, safe='')
encoded_base_string = 'POST' + '&' + \
    urllib.parse.quote(here_token_url, safe='')
encoded_base_string = encoded_base_string + '&' + encoded_parameter_string

# create the signing key
signing_key = access_key_secret + '&'

oauth_signature = create_signature(signing_key, encoded_base_string)
encoded_oauth_signature = urllib.parse.quote(oauth_signature, safe='')

# ---------------------Requesting Token---------------------
body = {'grant_type': '{}'.format(grant_type)}

token_request_headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Authorization': 'OAuth oauth_consumer_key="{0}",oauth_nonce="{1}",oauth_signature="{2}",oauth_signature_method="HMAC-SHA256",oauth_timestamp="{3}",oauth_version="1.0"'.format(oauth_consumer_key, oauth_nonce, encoded_oauth_signature, oauth_timestamp)
}

response = requests.post(here_token_url, data=body,
                         headers=token_request_headers)
json_data = json.loads(response.text)
token = json_data['access_token']

# print(token)

# base_url = 'https://traffic.ls.hereapi.com/traffic/6.3/incidents/xml/8/134/86'
base_url = 'https://weather.hereapi.com/v3/report/'
# base_url = 'https://weather.ls.hereapi.com/report/'

weather_report_products = {
    'observation': 'product=observation',
    'forecast7days': 'forecast7days',
    'forecast7daysSimple': 'forecast7daysSimple',
    'forecastHourly': 'forecastHourly',
    'alerts': 'alerts',
    'nwsAlerts': 'nwsAlerts'
}

location_query = {
    # string, free-text query
    'city_name': 'city='+input('Enter the quried city name:'),
    # string. ZIP code of the location
    # 'zip_code': 'zipcode'+input('Enter the location zipcode: '),
    # 'lat_long': [{'latitude': 'latitude='+input('Enter the location latitude: '),
    #               'longitude': 'longitude='+input('Enter the location longitude: ')}]
}

# + weather_report_products['observation'] + '&' + location_query['city_name'] + '/'
url_query = base_url

# endpoint = config['here']['here_token_endpoint_url']
# data = {"base_url": base_url}
authorization_header = {"Authorization": "Bearer " + token}
# final_url = endpoint + '/' + headers["Authorization"]
URL = url_query + authorization_header["Authorization"]
URL = URL + '?' + \
    weather_report_products['observation'] + '&' + location_query['city_name']

print(URL)
# , params=location_query, headers=authorization_header)
re = requests.get(URL)
print(re)


# 'https://1.traffic.maps.ls.hereapi.com/maptile/2.1/traffictile/newest/{scheme}/{zoom}/{column}/{row}/{size}/{format}?apiKey={YOUR_API_KEY}&{param}={value}'
# 'https://1.traffic.maps.ls.hereapi.com/maptile/2.1/traffictile/newest/{scheme}/{zoom}/{column}/{row}/{size}/{format}?apiKey={YOUR_API_KEY}&{param}={value}'
# base_map_tile_URL = 'https://1.base.maps.ls.hereapi.com/maptile/2.1/traffictile/newest/normal.day'

# query_params = {
#     'apikey': here_api_key,
#     'min_traffic_congestion': 'heavy',
#     'time': 'YYYY-MM-DDThh:mm:ss.szzzzzz'
# }
