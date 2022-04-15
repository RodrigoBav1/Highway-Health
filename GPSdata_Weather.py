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
import csv

import herepy #this doesn't seem to work. looking for other options for python application of HERE



#Define Global Variables

## Database creation variables
## Change host/user/password if necessary
host = 'localhost'
user = 'root'
password = 'testnewpassword'
database = 'highwayhealth'
tableGPS = 'GPS'


## API Variables

## OpenWeatherMaps Variables
wGeoCode1 = "https://api.openweathermap.org/data/2.5/weather?lat="
wGeoCode2 = "&lon="
wAppid = '&appid='
openWeatherKey = "aa0247a85f925e67652dd4f439105ec0"

## HERE Variables - Unused?
hDomain = "https://weather.ls.hereapi.com/"
hService = "weather/"
hVersion ="1.0/"    #possibly "3.0.0/" or "3.0/"
hResource = "report"
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
hApiKey = "PdeC4I7TSScmmZZ-RwUscy72xulXMWp_pg_lwvnuAfc"



# Uses data pulled from json to get weather data - this works!
#def openWeatherCall(lat, long)
def openWeatherCall(result):
    print("\nEntering openWeatherCall() function\n")
    # test variables
    '''
    lat = '34.987644195556605'
    long = '-105.21730041503896'
    '''

    for row in result:
        resp = requests.get(wGeoCode1 + row[0] + wGeoCode2 + row[1] + wAppid + openWeatherKey, timeout=5)
        respJson = resp.json()
        print(respJson)

    #which data points do we actually need; sort these out and discard the rest
    print("\nExiting openWeatherCall() function\n")



def main():
    print("Entering main method\n")

    print("CONNECTING TO MYSQL DATABASE")
    conn = mySqlConn.connect(host = host, user = user, password = password, database = database)
    curse = conn.cursor()


    ## WORKING/TESTING - SELECT LAT/LONG FROM DB AND FEED INTO API ##
    
    curse.execute("SELECT LAT, LON FROM GPS WHERE LAT = '34.987644195556605'")
    result = curse.fetchall()
    openWeatherCall(result) #testing weather data
    
    ## WORKING - SELECT LAT/LONG FROM DB AND FEED INTO API ##


    conn.commit
    conn.close

    print("Exiting main method\n")
    

main()
