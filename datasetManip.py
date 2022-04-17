#
#   Author:         Karin Nielsen
#   Date Created:   4/7/2022
#   File Name:      datasetManip.py
#   Version:        1.0
#   Description:    
#                   Function(s) that will import, load, and manipulate the geojson file
#                   and add manipulated data to the database
# 


## Import statement(s)

## Import packages
import mysql.connector as mySqlConn
import itertools
import json
import csv

import pandas as pd


## Import my modules
import databaseGPS #contains class dbWork and functions dbCreate and dbAddTable


## Define Global Variables

## Source dataset
file_path = "DataSets/TxDOT_Roadway_Inventory_RICHARDSON.geojson"

## Database creation variables
## Change host/user/password if necessary
host = 'localhost'
user = 'root'
password = 'testnewpassword'
database = 'highwayhealth'
tableGPS = 'GPS' 



## Function datasetWork() will open, read, and manipulate the geojson 
## data needed to request information from APIs (latitude/longitude)
## and a) store into database /  b) save to a .csv file
def datasetWork():
    print("Entering datasetWork() function\n")

    ## Open dataset file and store read data into a variable
    with open(file_path) as f:
        data = json.loads(f.read())


    ## Obtain count of items in file so we can accurately iterate 
    count = 0
    for item in data["features"]:
        count += 1 
    print("TEST - COUNT VALUE IS: " + str(count))



    ## Define empty list for writing to csv file
    writeToFile = [] 



    ## While loop saves the street names and street types
    ## into stNameData and stTypeData lists respectively
    i = 0
    stName = '' 
    stType = '' 
    stNameData = []
    stTypeData = []
    stDict = {}
    substring1 = "'"
    substring2 = '"'


    while i < count: 

        print("Iteration number: " + str(i))  #test 

        ## street TYPE value, this tells us where to look for the name
        stType = ''
        for propertyType in data["features"][i]["properties"]["HSYS"]:
            stType = stType + propertyType 
        stTypeData.append(stType)


        ## street NAME value
        stName = '' # reset string to empty for a new item in list
        if (stType == "US" or stType == "SH"):

            #replace any nulls (if needed here)
            for propertyName in data["features"][i]["properties"]["HWY"]:
                stName = stName + propertyName

            print(stName) #test

            ## Check for apostrophes/quotations and remove
            if substring1 in stName:
                stName = stName.replace("'", "")
                stNameData.append(stName)
            elif substring2 in stName: 
                stName = stName.replace('"', "")
                stNameData.append(stName)
            else: 
                stNameData.append(stName)

        elif stType == "LS":
            
            #replace any nulls
            localStName = pd.Series(data["features"][i]["properties"]["STE_NAM"], dtype='object', index=['Name'])
            localStNameNoNulls = localStName.fillna("missing name")

            #loop through replaced null Series
            for propertyName in localStNameNoNulls:
                stName = str(propertyName)

            print(stName) #test

            ## Check for apostrophes/quotations and remove
            if substring1 in stName:
                stName = stName.replace("'", "")
                stNameData.append(stName)
            elif substring2 in stName: 
                stName = stName.replace('"', "")
                stNameData.append(stName)
            else: 
                stNameData.append(stName)

        elif stType == "TL":

            #replace any nulls (if needed here)
            for propertyName in data["features"][i]["properties"]["TOLL_NM"]:
                stName = stName + propertyName

            print(stName) #test

            ## Check for apostrophes/quotations and remove
            if substring1 in stName:
                stName = stName.replace("'", "")
                stNameData.append(stName)
            elif substring2 in stName: 
                stName = stName.replace('"', "")
                stNameData.append(stName)
            else: 
                stNameData.append(stName)

        i += 1


 
    ## Assign lists of street Name/Type to street dictionary with keys "Name", "Type" respectively, 
    ## and place keys into street dictionary. Dictionary will be used to store into database
    listOfKeys = ["Type","Name"]
    stDict = dict.fromkeys(listOfKeys,None)  
    stDict["Name"] = stNameData
    stDict["Type"] = stTypeData

   

    ## While loop to iterate each item in dataset to assign Latitude and Longitude
    ## keynames for GPS dictionary due to many nested GPS items for each street:
    ## This will align lat/long keynames with indices for the street dictionary indices
    j = 0
    gpsDict = {}
    while j < count:
        gpsDict.fromkeys("LatKey"+str(j),None)
        gpsDict.fromkeys("LonKey"+str(j),None)
        j += 1


    
    ## Outer loop to iterate each street name/type
    k = 0
    latData = []
    lonData = []
    while k < count: 

        ## Empty out latitude/longitude lists on each loop 
        ## so we can add the next set to the dictionary
        latData = []
        lonData = []

        ## Inner loop to iterate all gps coordinates within 
        ## each street name/type pair and store into gps dictionary
            # note: lat/long have a limit of 16 digits, they will round from the source dataset
        for gps in data["features"][k]["geometry"]["coordinates"]:
            
            ## Store latitude/longitude into string
            ## and append strings to latitude/longitude lists
            for row in gps:
                
                lat = str(row[1])   
                lon = str(row[0])   
                latData.append(lat)
                lonData.append(lon)
            
        ## Now store latitude/longitude lists for 
        ## appropriate keynames in the gps dictionary
        gpsDict["LatKey"+str(k)] = latData
        gpsDict["LonKey"+str(k)] = lonData
        k += 1



    ## Connect to highwayhealth database so we can insert data into gps table
    print("CONNECTING TO MYSQL DATABASE")
    conn = mySqlConn.connect(host = host, user = user, password = password, database = database)
    curse = conn.cursor()
    print("SUCCESSFULLY CONNECTED TO DATABASE")

    

    ## While loop through item in the dataset. 
    ## Allows us to insert each row of matching data 
    ## (NAME, TYPE, LAT, LON) into database table
    x = 0 
    y = 0
    roadType = ''
    roadName = ''
    latIndex = ''
    lonIndex = ''
    listLat = []
    listLon = []

    
    while x < count:

        print("INSERTION NUMBER : " + str(x) + " OUT OF " + str(count)) 
        
        ## We know this dictionary only has 2 keys, so create variables
        ## that lets us assign names / types to insert into database
        ## reassign y to zero on each outer loop for next type/name assignment
        y = 0 
        for key, value in stDict.items():
            if y == 0:
                roadType = str(value[x])
                print(roadType) #test print
            elif y == 1:
                roadName = str(value[x])
                print(roadName) #test print
            y += 1 
            


        ## Obtain all gps coordinates from gps dictionary for specified keyname 
        ## and store into latitude/longitude lists to iterate and store into database
        latIndex = "LatKey"+str(x)
        lonIndex = "LonKey"+str(x)
        listLat = gpsDict.get(latIndex)
        listLon = gpsDict.get(lonIndex)
        
        
        ## Iterate through each latitude/longitude pair assigned to current street 
        ## name/type and insert into database and/or save to a .csv file 
        for (lat, lon) in itertools.zip_longest(listLat, listLon):
            
            ## INSERTS NAME, TYPE, LATITUDE, LONGITUDE INTO DATABASE - THIS TAKES A WHILE
            ## comment out following line if only saving to .csv file
            databaseGPS.dbWork.addToGPS(conn, curse, tableGPS, roadName, roadType, lat, lon)

            ## Appends items to a list for saving to .csv file
            ## comment out following line if only inserting to database
            writeToFile.append(str(roadName + " , " + roadType + " , " + lat + " , " + lon))
        
        x += 1
        


    ## WRITES NAME, TYPE, LATITUDE, LONGITUDE TO .CSV FILE
    ## comment out the following 4 lines if only inserting to database
    listFile = open("output.csv", "a")
    writer = csv.writer(listFile)
    for item in writeToFile: #should have 1600 items
        writer.writerow([str(item)]) 


    conn.commit
    conn.close


    print("\nExiting datasetWork() function\n")



## Call datasetWork() function
datasetWork()