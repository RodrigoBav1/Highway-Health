#
#   Author:         Karin Nielsen
#   Date Created:   3/25/2022
#   File Name:      GPSdata_Weather.py
#   Description:    
#                   Import geojson file containing US Highway lat/long data. 
#                   Create Database -> Tables to hold info.
#                   Store pertinent json data in database tables.
#                   Use lat/long from database to make API calls to OpenWeatherMaps (or HERE Traffic data)
#                   Store historical data from results into separate table in database. 
#


## Import statement(s)

## Import packages
import mysql.connector as mySqlConn
import requests
import json
import pandas as pd
import configparser

# for recording when API calls occurred
from datetime import datetime
import pytz

# for time delays on API calls
import time

#this doesn't seem to work. Exploring other options
from sympy import true
from herepy import (DestinationWeatherApi, WeatherProductType)



#Define Global Variables

## Database creation variables
## Change host/user/password if necessary
host = 'localhost'
user = 'root'
password = 'testnewpassword'
database = 'highwayhealth'
tableGPS = 'GPS'


## API Variables

## Using configparser object to read your API secret data
config = configparser.ConfigParser()
config.read('project_config.ini')

## OpenWeatherMaps Variables
wGeoCode1 = "https://api.openweathermap.org/data/2.5/weather?lat="
wGeoCode2 = "&lon="
wAppid = '&appid='
openWeatherKey = config['open']['open_api_key']
wUnits = '&units=imperial'
wlang = '&lang=en'


## HERE Variables - NOT USING NOW
# Access your API key saved in project_config.ini file
my_api_key = config['here']['here_api_key']

# Construct the URL needed for the API call request - UNUSED?
base_url = 'https://weather.hereapi.com/v3'
endpoint1 = '/report'
endpoint2 = '/alerts'
URLreport = base_url + endpoint1
URLalert = base_url + endpoint2

hFormat = ".json"
hProd = "?product=" #could also be "&product="
# WeatherProductType
hProductObs = 'observation'     # current weather conditions from the eight closest locations to the specified location
hProductalerts24 = 'alerts'     # forecasted weather alerts for the next 24 hours
hProductAlertsNWS = 'nws_alerts'    # all active watches and warnings for the US and Canada
# Boolean, if set to true, the response only includes the closest location. 
# Only available when the product parameter is set to observation.
hOneObs = 'oneobservation' 
hMetric = "metric" # If set to false, the response contains imperial units (feet, inch, Fahrenheit, miles). Default: true




## OpenWeatherMaps API call using queried lat/lon data from the database
def openWeatherCall(result, columnHeaders):
    print("\nEntering openWeatherCall() function\n")

    ## Define empty list for writing API results to csv file
    writeToFile = [] 

    ## Loops through each row in the SQL SELECT result object. 
    ## Index[0] is latitude
    ## Index [1] is longitude
    for row in result:
        resp = requests.get(wGeoCode1 + row[0] + wGeoCode2 + row[1] + wAppid + openWeatherKey + wUnits + wlang, timeout=5)
        respJson = resp.json() #this stores as a dict
        #print(respJson) #test print

        ## Get the current date/time for historical data (CST timezone)     
        ## Name of timezone via pytz: 'US/Central'
        tzVar = pytz.timezone('US/Central')
        nowCST = datetime.now(tzVar)
        dateTimeStr2 = nowCST.strftime('%m-%d-%Y %H:%M:%S') # format datetime 
        #print(dateTimeStr2) #test print

        ## Assign values to columns from API results
        DATE_TIME = dateTimeStr2
        LATITUDE = respJson['coord']['lat']
        LONGITUDE = respJson['coord']['lon']
        WEATHER_ID = respJson['weather'][0]['id']
        WEATHER_DESCRIPTION = respJson['weather'][0]['description']
        TEMPERATURE = respJson['main']['temp']
        VISIBILITY = respJson['visibility']
        WIND_SPEED = respJson['wind']['speed']
        CLOUDS = respJson['clouds']['all']
        RAIN1H = respJson.get('rain', {}).get('1h',{})
        RAIN3H = respJson.get('rain', {}).get('3h',{})
        SNOW1H = respJson.get('snow', {}).get('1h',{})
        SNOW3H = respJson.get('snow', {}).get('3h',{})

        ## add if / else for assignments here since these can be null
        if RAIN1H: 
            RAIN1H = RAIN1H
        else: 
            RAIN1H = 'No Result'
        if RAIN3H:
            RAIN3H = RAIN3H
        else:
            RAIN3H = 'No Result'
        if SNOW1H:
            SNOW1H = SNOW1H
        else:
            SNOW1H = 'No Result'
        if SNOW3H:
            SNOW3H = SNOW3H
        else:
            SNOW3H = 'No Result'
        
        ## for writing to csv file / saving to a database for historical records
        writeToFile.append([DATE_TIME, LATITUDE, LONGITUDE, WEATHER_ID, WEATHER_DESCRIPTION, 
        TEMPERATURE, VISIBILITY, WIND_SPEED, CLOUDS, RAIN1H, RAIN3H, SNOW1H, SNOW3H])

        ## Write full json response to a json file - may be unneeded
        jsonString = json.dumps(respJson)
        jsonFile = open("OpenWeatherMaps.json", "a")
        jsonFile.write(jsonString + "\n")

        ## Wait for 1 second(s) before next API call
        time.sleep(1) 
        
    jsonFile.close() #close json file

    ## Writes data obtained from json response to csv file
    data = writeToFile
    df = pd.DataFrame(data, columns=columnHeaders) 
    df.to_csv("OpenWeatherMapsOutput.csv")

    print("\nExiting openWeatherCall() function\n")



def hereDestWeather(result): # CURRENTLY DOES NOT WORK. MAY REMOVE.
    print("\nEntering hereDestWeather() function\n")

    ## AUTHORIZE THE WEATHER API WITH YOUR API KEY USING 'WeatherApi(<your_api_key>)' method
    weather_api =  DestinationWeatherApi(api_key=my_api_key)
    lat = 32.980571
    lon = -96.721951
    prod = WeatherProductType.observation #'observation'

    ## Fetches weather report at a latitude/longitude
        # CURRENTLY GETTING AN ERROR ON HEREPY. THIS MAY NOT BE SOMETHING WE CAN USE
    response_obj = weather_api.weather_for_coordinates(
        latitude=lat, 
        longitude=lon, 
        product=prod, 
        one_observation=True, 
        metric=False)

    response_dict_items = response_obj.as_dict()
    print(response_dict_items)
    
    ## Define empty list for writing API results to csv file
    writeToFile = [] 

    #for row in result:
    #    resp = requests.get()=

    print("\nExiting hereDestWeather() function\n")



def main():
    print("Entering main method\n")

    print("CONNECTING TO MYSQL DATABASE")
    conn = mySqlConn.connect(host = host, user = user, password = password, database = database)
    curse = conn.cursor()

    # tests 47 rows call to API
    curse.execute("SELECT LAT, LON FROM GPS WHERE NAME = 'missing name' AND GPS_ID < 9000") 
    
    ## use this for group of 1400ish
    #curse.execute("SELECT LAT, LON FROM GPS WHERE TYPE IN('US','SH','TL')") 
    result = curse.fetchall()
    
    columnHeaders = ['DATE_TIME_CST','LATITUDE','LONGITUDE',
        'WEATHER_ID','WEATHER_DESCRIPTION','TEMPERATURE', 
        'VISIBILITY_METERS','WIND_SPEED_MPH','CLOUDS_PERCENT',
        'RAIN1H_MM','RAIN3H_MM','SNOW1H_MM','SNOW3H_MM']

    openWeatherCall(result, columnHeaders) #testing weather data
    #hereDestWeather(result) #currently does not work

    # commit any changes to database and close connection to it
    conn.commit
    conn.close

    print("Exiting main method\n")
    
main()
