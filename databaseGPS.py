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
    def dbAddTable (host, user, password, database, tableGPS):
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
            TYPE VARCHAR(5) NOT NULL,
            LAT VARCHAR(20) NOT NULL,  
            LON VARCHAR(20) NOT NULL, 
            PRIMARY KEY (GPS_ID),
            UNIQUE(GPS_ID, LAT, LON) )"""
        curse.execute(createTableGPS)
        print("TABLE " + tableGPS + " CREATED")

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

