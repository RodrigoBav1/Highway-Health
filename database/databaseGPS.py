#
#   Author:         Karin Nielsen
#   Date Created:   4/6/2022
#   File Name:      databaseGPS.py
#   Version:        1.0
#   Description:    
#                   Functions within class dbWork designed to:
#                       - create highwayhealth database
#                       - and tables within database
#                       - add information to database


## Import statement(s)
import mysql.connector as mySqlConn


## Class dbWork is designed to create/modify DB
class dbWork:
    def __init__(self, host, user, password, database, tableGPS):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.tableGPS = tableGPS



    ## Function dbCreate() will connect to MySQL and create highwayhealth DB
    def dbCreate (host, user, password, database):
        print("Entering dbCreate() function\n")

        # Connect to MySQL local host
        print("CONNECTING TO MYSQL")
        connSQL = mySqlConn.connect(host = host, user = user, password = password)
        curseSQL = connSQL.cursor()
        print("CONNECTION TO MYSQL SUCCESSFUL\n")

        ## Create database if it does not exist
        curseSQL.execute("CREATE DATABASE IF NOT EXISTS " + database)

        ## Following two lines of code used during testing, ##
        ## commented out after DB creation finalized ##
        #curseSQL.execute("DROP DATABASE IF EXISTS " + database) 
        #curseSQL.execute('CREATE DATABASE ' + database)
        
        connSQL.commit()
        connSQL.close()

        print("Exiting dbCreate() function\n")



    ## Function dbAddTable() creates any associated table(s) in highwayhealth database
    def dbAddTable (host, user, password, database, tableGPS, tableWeatherHist):
        print("Entering dbAddTable() function\n")

        # Connect to MySQL highwayhealth database
        print("CONNECTING TO MYSQL DATABASE")
        conn = mySqlConn.connect(host = host, user = user, password = password, database = database)
        curse = conn.cursor()
        curse.execute("USE " + database)
        print("CONNECTION TO MYSQL DATABASE SUCCESSFUL")


        ## Following three lines of code used during testing, ##
        ## commented out after table creation finalized ##
        #curse.execute("DROP TABLE IF EXISTS " + tableGPS) 
        #print("TABLE " + tableGPS + " DELETED") 
        #'CREATE TABLE IF NOT EXISTS ' + tableGPS + """

        ## Create table 'gps' if it does not exist
        createTableGPS = 'CREATE TABLE IF NOT EXISTS ' + tableGPS + """
            (GPS_ID INT NOT NULL AUTO_INCREMENT, 
            NAME VARCHAR(100) NOT NULL, 
            TYPE VARCHAR(5) NOT NULL
            LAT VARCHAR(10) NOT NULL,  
            LON VARCHAR(10) NOT NULL, 
            PRIMARY KEY (GPS_ID),
            UNIQUE KEY u_latlong (LAT,LON))"""
        curse.execute(createTableGPS)
        print("TABLE " + tableGPS + " CREATED")



        ## Create table 'WEATHER_HISTORICAL' if it does not exist
        createTableWeatherHist = 'CREATE TABLE IF NOT EXISTS ' + tableWeatherHist + """
            (W_ID INT NOT NULL AUTO_INCREMENT,
            REF_ID INT NOT NULL, 
            DATETIME_CST VARCHAR(20) NOT NULL, 
            LAT VARCHAR(10) NOT NULL,  
            LON VARCHAR(10) NOT NULL, 
            WEATHER_ID INT NOT NULL,
            WEATHER_DESC VARCHAR(100) NOT NULL,
            WEATHER_ICON VARCHAR(5) NOT NULL,
            TEMP_F DECIMAL(5,2) NOT NULL,
            HUMIDITY_PERCENT INT NOT NULL,
            VISIBILITY_M INT NOT NULL,
            WINDSPEED_MPH INT NOT NULL,
            DANGER_LEVELS VARCHAR(20) NOT NULL,
            PRIMARY KEY (W_ID, REF_ID),
            FOREIGN KEY (REF_ID) REFERENCES GPS (GPS_ID) )"""
        curse.execute(createTableWeatherHist)
        print("TABLE " + tableWeatherHist + " CREATED")

        conn.commit()
        conn.close()

        print("\nExiting createDB() function\n")



    ## Function addToGPS() inserts data from our geojson 
    ## dataset into the highwayhealth database / gps table
    def addToGPS (conn, curse, tableGPS, hwyName, hwyType, lat, lon):

        insertIntoGPS = 'INSERT INTO ' + tableGPS + """ 
        (NAME, TYPE, LAT, LON) 
        VALUES ('""" + hwyName + """','""" + hwyType + """','""" + lat + """','""" + lon + """')"""
        curse.execute(insertIntoGPS)

        conn.commit()



    ## Function addToWeather() inserts data from our weather API calls
    ## into the highwayhealth database / weather_historical table
    def addToWeather (conn, curse, tableWeatherHist, ID, DATE_TIME, LATITUDE, LONGITUDE, WEATHER_ID, WEATHER_DESCRIPTION, WEATHER_ICON,
        TEMPERATURE, HUMIDITY, VISIBILITY, WIND_SPEED, DANGER):

        insertIntoWeather = 'INSERT INTO ' + str(tableWeatherHist) + """ 
        (REF_ID, DATETIME_CST, LAT, LON, WEATHER_ID, WEATHER_DESC, WEATHER_ICON, TEMP_F, HUMIDITY_PERCENT, VISIBILITY_M, WINDSPEED_MPH, DANGER_LEVELS) 
        VALUES ('""" + str(ID) + """','""" + str(DATE_TIME) + """','""" + str(LATITUDE) + """','""" + str(LONGITUDE) + """
        ','""" + str(WEATHER_ID) + """','""" + str(WEATHER_DESCRIPTION) + """','""" + str(WEATHER_ICON)  + """','""" + str(TEMPERATURE) + """','""" + str(HUMIDITY) + """
        ','""" + str(VISIBILITY) + """','""" + str(WIND_SPEED) + """','""" + str(DANGER) + """')"""

        curse.execute(insertIntoWeather)

        conn.commit()

