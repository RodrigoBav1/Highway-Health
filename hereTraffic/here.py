import requests
import time
import urllib.parse
from base64 import b64encode
import hmac
import hashlib
import binascii
import configparser
from flask import current_app, flash, jsonify, make_response, redirect, request, url_for
import json


config = configparser.ConfigParser()
config.read('project_config.ini')

grant_type = 'client_credentials'
oauth_consumer_key = config['here']['here_access_key_id']
access_key_secret = config['here']['here_access_key_secret']
oauth_nonce = str(int(time.time()*1000))
oauth_timestamp = str(int(time.time()))
oauth_signature_method = 'HMAC-SHA256'
oauth_version = '1.0'
url = 'https://account.api.here.com/oauth2/token'


# HMAC-SHA256 hashing algorithm to generate the OAuth signature
def create_signature(secret_key, signature_base_string):
    encoded_string = signature_base_string.encode()
    encoded_key = secret_key.encode()
    temp = hmac.new(encoded_key, encoded_string, hashlib.sha256).hexdigest()
    byte_array = b64encode(binascii.unhexlify(temp))
    return byte_array.decode()


# concatenate the six oauth parameters, plus the request parameters
# from above,sorted alphabetically by the key and separated by "&"

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
encoded_base_string = 'POST' + '&' + urllib.parse.quote(url, safe='')
encoded_base_string = encoded_base_string + '&' + encoded_parameter_string

# create the signing key
signing_key = access_key_secret + '&'

oauth_signature = create_signature(signing_key, encoded_base_string)
encoded_oauth_signature = urllib.parse.quote(oauth_signature, safe='')

# ---------------------Requesting Token---------------------
body = {'grant_type': '{}'.format(grant_type)}

headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Authorization': 'OAuth oauth_consumer_key="{0}",oauth_nonce="{1}",oauth_signature="{2}",oauth_signature_method="HMAC-SHA256",oauth_timestamp="{3}",oauth_version="1.0"'.format(oauth_consumer_key, oauth_nonce, encoded_oauth_signature, oauth_timestamp)
}

response = requests.post(url, data=body, headers=headers)


# print(response.text)
json_data = json.loads(response.text)
token = json_data['access_token']

print(token)

base_url = 'https://traffic.ls.hereapi.com/traffic/6.3/incidents/xml/8/134/86'


def create_http_string(url, access_token):
    https_string = ''
    https_string = https_string + base_url
    https_string = https_string + '/oauth2'
    https_string = https_string + '/' + token
    return https_string


httpss_string = create_http_string(base_url, token)
print(httpss_string)

r = requests.get(httpss_string)
print(r)
