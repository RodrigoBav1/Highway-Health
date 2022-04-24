#
#   Author:         Karin Nielsen
#   Date Created:   3/25/2022
#   File Name:      openWeatherAPIcalls.py
#   Version:        1.1
#   Description:    
#                   Use lat/long from database to make API calls to OpenWeatherMaps. 
#                   Save off applicable info into a .csv file for Deck.GL weather map layer.
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

## Import my modules
#from databaseGPS import dbWork 
import sys
sys.path.insert(0, r'C:\Users\theni\git\VSC-GitHub-Clones\Highway-Health\Highway-Health\database')
from databaseGPS import dbWork #contains class dbWork and db functions

'''
#this doesn't seem to work. Comment out for now
from sympy import true
from herepy import (DestinationWeatherApi, WeatherProductType)
from requests.structures import CaseInsensitiveDict
'''


#Define Global Variables

## path variables for saving API call data, these may need to change
folderPath = 'C:\\Users\\theni\\git\\VSC-GitHub-Clones\\Highway-Health\\Highway-Health\\flaskr\\'
hourlyFile = 'weather_updates.csv'


## Database creation variables
## Change host/user/password if necessary
host = 'localhost'
user = 'root'
password = 'testnewpassword'
database = 'highwayhealth'
tableGPS = 'GPS'
tableWeatherHist = 'WEATHER_HISTORICAL'


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

'''
## HERE Variables - NOT USING NOW; MORE EXPENSIVE AND MORE CHALLENGING TO MAKE FUNCTION
# Access your API key saved in project_config.ini file
my_api_key = config['here']['here_api_key']
base_url = 'https://weather.hereapi.com/v3'
format = ".json"
product = "&product=" 
productObs = 'observation'     # current weather conditions from the eight closest locations to the specified location
productalerts24 = 'alerts'     # forecasted weather alerts for the next 24 hours
productAlertsNWS = 'nws_alerts'    # all active watches and warnings for the US and Canada
# Boolean, if set to true, the response only includes the closest location. 
# Only available when the product parameter is set to observation.
oneObs = 'oneobservation' 
metric = "metric" # If set to false, the response contains imperial units (feet, inch, Fahrenheit, miles). Default: true
'''


## OpenWeatherMaps API call using queried lat/lon data from the database
def openWeatherCall(result, columnHeaders, columnHeadersDB, conn, curse):
    print("\nEntering openWeatherCall() function\n")

    ## Define variables to use in below for loop
    writeToFile = []    # Empty list for writing results to .csv file
    writeToDB = []      # Empty list for writing results to historical database
    x = 1 #iteration variable for my testing

    ## For loop moves through each row in the SQL SELECT result object passed from main() 
        ## Index[0] is latitude, Index [1] is longitude
    for row in result:
        #print("API call count: " + str(x)) #test print

        ## GET from OpenWeatherMaps using current latitude/longitude and store results as a dictionary
        resp = requests.get(wGeoCode1 + str(row[0])[:7] + wGeoCode2 + str(row[1])[:7] + wAppid + openWeatherKey + wUnits + wlang, timeout=5)
        respJson = resp.json()
        #print(respJson) #test print


        ## Get the current date/time for historical data (CST timezone)     
        ## Name of timezone via pytz: 'US/Central'
        tzVar = pytz.timezone('US/Central')
        nowCST = datetime.now(tzVar)
        dateTimeStr2 = nowCST.strftime('%m-%d-%Y %H:%M:%S')
        #print(dateTimeStr2) #test print


        ## Assign values to columns from API results
        DATE_TIME = dateTimeStr2
        LATITUDE = respJson['coord']['lat']
        LONGITUDE = respJson['coord']['lon']
        WEATHER_ID = respJson['weather'][0]['id']
        WEATHER_DESCRIPTION = respJson['weather'][0]['description']
        WEATHER_ICON = respJson['weather'][0]['icon']
        TEMPERATURE = respJson['main']['temp']
        HUMIDITY = respJson['main']['humidity']
        VISIBILITY = respJson['visibility']
        WIND_SPEED = respJson['wind']['speed']


        ## Mark specific weather IDs and other markers as MODERATE, IGNORE, or DANGER for traffic purposes
        if (WEATHER_ID == 201 or WEATHER_ID == 211 or WEATHER_ID == 232 or WEATHER_ID == 302
        or WEATHER_ID == 311 or WEATHER_ID == 321 or WEATHER_ID == 501 or WEATHER_ID == 521
        or WEATHER_ID == 600 or WEATHER_ID == 701 or WEATHER_ID == 721 or WEATHER_ID == 731
        or WEATHER_ID == 751 or WEATHER_ID == 761 
        or (int(VISIBILITY) > 100 and int(VISIBILITY) < 300) 
        or (int(WIND_SPEED) > 30 and int(WIND_SPEED) <40)):
            DANGER = 'MODERATE'

        elif (WEATHER_ID == 200 or WEATHER_ID == 210 or WEATHER_ID == 230 or WEATHER_ID == 231
        or WEATHER_ID == 300 or WEATHER_ID == 301 or WEATHER_ID == 310 or WEATHER_ID == 500 
        or WEATHER_ID == 520 or WEATHER_ID == 800 or WEATHER_ID == 801 or WEATHER_ID == 802
        or WEATHER_ID == 803 or WEATHER_ID == 804):
            DANGER = "IGNORE"

        elif (WEATHER_ID == 202 or WEATHER_ID == 212 or WEATHER_ID == 221 or WEATHER_ID == 312
        or WEATHER_ID == 313 or WEATHER_ID == 314 or WEATHER_ID == 502 or WEATHER_ID == 503
        or WEATHER_ID == 504 or WEATHER_ID == 511 or WEATHER_ID == 522 or WEATHER_ID == 531
        or WEATHER_ID == 601 or WEATHER_ID == 602 or WEATHER_ID == 611 or WEATHER_ID == 612
        or WEATHER_ID == 613 or WEATHER_ID == 615 or WEATHER_ID == 616 or WEATHER_ID == 620
        or WEATHER_ID == 621 or WEATHER_ID == 622 or WEATHER_ID == 711 or WEATHER_ID == 741
        or WEATHER_ID == 762 or WEATHER_ID == 771 or WEATHER_ID == 781
        or int(WIND_SPEED) > 40
        or int(VISIBILITY) < 100): 
            DANGER = 'DANGER'

        else:
            DANGER = 'something went wrong' #for testing, should not occur


        ## Append data to list for writing to csv file. Only save MODERATE/DANGER level items. 
        if (DANGER == ("MODERATE" or 'DANGER')):
            writeToFile.append([DATE_TIME, LATITUDE, LONGITUDE, WEATHER_ID, WEATHER_DESCRIPTION, WEATHER_ICON, 
            TEMPERATURE, HUMIDITY, VISIBILITY, WIND_SPEED, DANGER])


        ## SELECT GPS_ID from GPS table to save a reference ID that would function as the foreign key
        ## in the WEATHER_HISTORICAL table in relation to GPS table's primary key.
        selectKey = "SELECT GPS_ID FROM " + str(tableGPS) + " WHERE LAT = '" + str(row[0])[:7] + "' AND LON = '" + str(row[1])[:7] + "'"
        curse.execute(selectKey)
        resultIDobj = str(curse.fetchone())
        ## Remove non-numbers from result to prevent errors
        resultID = resultIDobj.translate({ord(c):None for c in "(,)"}) 
        ID = int(resultID) 


        ## Append all data to list for writing to the WEATHER_HISTORICAL table in the database 
        writeToDB.append([ID, DATE_TIME, LATITUDE, LONGITUDE, WEATHER_ID, WEATHER_DESCRIPTION, WEATHER_ICON,
        TEMPERATURE, HUMIDITY, VISIBILITY, WIND_SPEED, DANGER])
        
        '''
        ## Write full json response to a json file - may be unneeded
        jsonString = json.dumps(respJson)
        jsonFile = open("OpenWeatherMaps.json", "a")
        jsonFile.write(jsonString + "\n")
        '''
        
        ## Wait for 1 second(s) before next API call
        time.sleep(1)

        x += 1
    
    #jsonFile.close() #close json file


    ## Writes data obtained from json response to csv file - overwrites each hour
    data = writeToFile
    df = pd.DataFrame(data, columns=columnHeaders)
    df.to_csv(path_or_buf=(folderPath + hourlyFile))


    ## Inserts historical weather data obtained from the API into the DB every hour
    ## Also saves off historical data into a csv file, appends every hour
    z = 1
    dataDB = writeToDB

    ## in the future can add an if statement that won't use the headers on each append

    dfDB = pd.DataFrame(dataDB, columns=columnHeadersDB)
    dfDB.to_csv("OpenWeatherMaps_Historical.csv", mode='a') 

    for index, series in dfDB.iterrows():
        #print("Insert into database count: " + str(z)) # test
        dbWork.addToWeather(conn, curse, tableWeatherHist, series[0], series[1], series[2], 
        series[3], series[4], series[5], series[6], series[7], series[8], series[9], series[10], series[11])
        z += 1
   

    conn.commit()

    print("\nExiting openWeatherCall() function\n")


'''
def hereDestWeather(result): # CURRENTLY DOES NOT WORK. MAY REMOVE.
    print("\nEntering hereDestWeather() function\n")

    ### TEST
    resp = requests.get(url, headers=headers)
    print(resp.status_code)
 
    ## AUTHORIZE THE WEATHER API WITH YOUR API KEY USING 'WeatherApi(<your_api_key>)' method
    weather_api =  DestinationWeatherApi(api_key=my_api_key)
    lat = 32.980571
    lon = -96.721951
    prod = 'observation'

    ## Fetches weather report at a latitude/longitude
        # CURRENTLY GETTING AN ERROR ON HEREPY. THIS MAY NOT BE SOMETHING WE CAN USE
    response_obj = weather_api.weather_for_coordinates(latitude=lat, longitude=lon, product=prod, one_observation=True, metric=False)

    response_dict_items = response_obj.as_dict()
    print(response_dict_items)
    
    ## Define empty list for writing API results to csv file
    writeToFile = [] 

    print("\nExiting hereDestWeather() function\n")
'''


def main():
    print("Entering main method\n")

    print("CONNECTING TO MYSQL DATABASE")
    conn = mySqlConn.connect(host = host, user = user, password = password, database = database)
    curse = conn.cursor()

    curse.execute("SELECT LAT, LON FROM GPS WHERE LAT = '32.9750' AND LON = '-96.716'") #test
    #curse.execute("SELECT LAT, LON FROM GPS WHERE TYPE IN('US','SH','TL')") # tests 425 rows call to API

    ## ALL LAT/LON PAIRS
    #selectStmt = "SELECT LAT, LON FROM " + str(tableGPS) 
    #curse.execute(selectStmt)
    result = curse.fetchall()

    columnHeaders = ['DATE_TIME_CST','LATITUDE','LONGITUDE',
        'WEATHER_ID','WEATHER_DESCRIPTION', 'WEATHER_ICON', 'TEMPERATURE','HUMIDITY_PERCENT', 
        'VISIBILITY_METERS','WIND_SPEED_MPH','DANGER_LEVELS']

    columnHeadersDB = ['ID','DATE_TIME_CST','LATITUDE','LONGITUDE',
        'WEATHER_ID','WEATHER_DESCRIPTION','WEATHER_ICON','TEMPERATURE','HUMIDITY_PERCENT', 
        'VISIBILITY_METERS','WIND_SPEED_MPH','DANGER_LEVELS']
    
    openWeatherCall(result, columnHeaders, columnHeadersDB, conn, curse) #testing weather data
    #hereDestWeather(result) #currently does not work

    # commit any changes to database and close connection to it
    conn.commit
    conn.close

    print("Exiting main method\n")
    
main()
