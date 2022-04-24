#
#   Author:         Karin Nielsen
#   Date Created:   4/7/2022
#   File Name:      datasetManip.py
#   Version:        1.0
#   Description:    
#                   Function(s) that will import, load, and manipulate the geojson file.
#                   Need to trim latitude/longitude to 7 characters long and remove duplicates 
#                   for street Name, Type, Latitude, Longitude. Once manipulated, insert into 
#                   gps table in database.
# 


## Import statement(s)

## Import gen packages
import mysql.connector as mySqlConn
import itertools
import json
import csv
import pandas as pd

## Import my modules
from databaseGPS import dbWork  # for function dbAddTable


## Define Global Variables

## file/folder path(s)
file_path = "C:\\Users\\theni\\git\\VSC-GitHub-Clones\\Highway-Health\\Highway-Health\\DataSets\\TxDOT_Roadway_Inventory_RICHARDSON.geojson"

## Database creation variables, change host/user/password if necessary
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

    ## Obtain count of rows in file so we can accurately iterate
    count = 0
    for item in data["features"]:
        count += 1 
    #print("TEST - COUNT VALUE IS: " + str(count))

     


    ## Define variables for below while loop
    a = 0
    stType = '' 
    stName = '' 
    substring1 = "'"
    substring2 = '"'
    stNameData = []
    stTypeData = []
    stListIDs = []
    tempStDict = {}
    
    ## While loop saves the street names and street types
    ## into stNameData and stTypeData lists respectively
    while a < count: 

        ## Obtain TYPE value from geojson, this tells us where to look 
        ## for the street name in the dataset
        stType = ''     # reset string to empty for a new item in list
        for propertyType in data["features"][a]["properties"]["HSYS"]:
            stType = stType + propertyType 
        stTypeData.append(stType)
        

        ## street NAME value from geojson
        stName = ''     # reset string to empty for a new item in list
            ## These types indicate US = Interstate and SH = State Highway
        if (stType == "US" or stType == "SH"): 

            # could add null value handling in the future if different dataset, not necessary here

            for propertyName in data["features"][a]["properties"]["HWY"]:
                stName = stName + propertyName

            ## Check for apostrophes/quotations and remove
            if substring1 in stName:
                stName = stName.replace("'", "")
                stNameData.append(stName)
            elif substring2 in stName: 
                stName = stName.replace('"', "")
                stNameData.append(stName)
            else: 
                stNameData.append(stName)

            ## This type indicates LS = Local Street
        elif stType == "LS":
            
            #replace any nulls
            localStName = pd.Series(data["features"][a]["properties"]["STE_NAM"], dtype='object', index=['Name'])
            localStNameNoNulls = localStName.fillna("missing name")

            #loop through replaced null Series
            for propertyName in localStNameNoNulls:
                stName = str(propertyName)

            ## Check for apostrophes/quotations and remove
            if substring1 in stName:
                stName = stName.replace("'", "")
                stNameData.append(stName)
            elif substring2 in stName: 
                stName = stName.replace('"', "")
                stNameData.append(stName)
            else: 
                stNameData.append(stName)

            ## This type indicates TL = Toll Road
        elif stType == "TL":

            # could add null value handling in the future if different dataset, not necessary here

            for propertyName in data["features"][a]["properties"]["TOLL_NM"]:
                stName = stName + propertyName

            ## Check for apostrophes/quotations and remove
            if substring1 in stName:
                stName = stName.replace("'", "")
                stNameData.append(stName)
            elif substring2 in stName: 
                stName = stName.replace('"', "")
                stNameData.append(stName)
            else: 
                stNameData.append(stName)

        ## Add iteration number to a list that is used as a value for an ID key
        ## in a temp dictionary to count # of street name/types
        stListIDs.append(a)
        a += 1


    ## Assign lists of street ID/Name/Type to street dictionary with keys "ID, ""Name", "Type" 
    ## respectively. Place keys into temp street dictionary. Will be deduplicated later. 
    listOfKeys = ["ID","Type","Name"]
    tempStDict = dict.fromkeys(listOfKeys,None)
    tempStDict["ID"] = stListIDs
    tempStDict["Name"] = stNameData
    tempStDict["Type"] = stTypeData


    ## Define variables for below while loop
    k = 0
    latNoDups = []
    lonNoDups = []
    tempLatNoDups = []
    tempLonNoDups = []
    unmodDict = {} # temp dictionary to store gps coordinates before name/type deduplication

    ## This loop should be able to dedup the latitude longitude pairs and also remove 
    ## the applicable Name/Type pairs in the tempStDict{}
        ## this outermost while loop will iterate through 
        ## the known # of rows in the original dataset
    while k < count: 
        
        ## Temp dict to help us peel out the name/type
        ## Keynames in this dict will have the same index # as the street name/type dict;
        ## helps us remove the applicable pairs so they match appropriately when deduped
        unmodDict.fromkeys("tempLatKey"+str(k),None)
        unmodDict.fromkeys("tempLatKey"+str(k),None)

        ## Empty the lat/long lists for the next row's info to add to unmodDict{}
        tempLatNoDups = []
        tempLonNoDups = []


        ## This inner loop iterates through each row in the original 
        ## dataset and obtains the full list from each row of the gps 
        ## coordinates will store into unmodDict{} 
        for gps in data["features"][k]["geometry"]["coordinates"]:
            

            ## This last inner loop will iterate through each set of 
            ## latitude/longitude pairs in each row and will convert into
            ## 7-char long strings and appends strings to latitude/longitude lists
            for row in gps:
                

                ## Shorten the lat/long to 7 characters; the API results are never 
                ## longer than 7 characters and we don't want duplicates
                lat = str(row[1])[:7]
                lon = str(row[0])[:7]


                ## Remove the duplicates from the lat/long lists.   
                    ## LOGIC HERE STATES THAT:
                        ## IF (lat variable IS NOT in the latNoDups list) OR (lon variable IS NOT in longNoDups list)
                        ## THEN: add it to the list.
                ## ~ Designed this way because we are fine with latitudes in the latitude list matching, but NOT when 
                ## paired latitude AND longitude in the lists both match: this second example is what we're de-duplicating
                if ((lat not in latNoDups) or (lon not in lonNoDups)):
                    
                    ## append current lat/long to appropriate lists
                        ## These lists must remain unchanged for if condition to work
                    latNoDups.append(lat)
                    lonNoDups.append(lon)
                        ## These lists must be emptied on each loop for appending to the temp dictionary
                    tempLatNoDups.append(lat)
                    tempLonNoDups.append(lon)
            
        ## Add current row's coordinates lists to applicable key for unmodDict{}
        unmodDict["tempLatKey"+str(k)] = tempLatNoDups
        unmodDict["tempLonKey"+str(k)] = tempLonNoDups

        k += 1



    ## Define variables for below while loop
    e = 0
    q = 0 
    ## These are the final Street / GPS lists to add to dictionaries
    stListIDsFinal = []
    stNameFinal = []
    stTypeFinal = []
    ## These are the final Street / GPS dictionaries
    stDict = {} 
    gpsDict = {}

    ## This loop is intended to loop over all 1600 keys/values pairs in the unmodDict{}
    while e < count:
        #print("Iteration number: " + str(p)) # for testing
    

        ## If any value exists in unmodDict{}, append the current index of the street 
        ## name/type pairs to final street/type lists. Also define new key/value pairs
        ## for the final lat/long dictionary. 
        ## Otherwise, do nothing.
            ## This will effectively remove the duplicates from Name/Type/Lat/Long
        if unmodDict["tempLatKey"+str(e)]:

            ## Add values to street ID, Name, and Type lists to add to final stDict{} later
            stListIDsFinal.append(q)
            stNameFinal.append(stNameData[e])
            stTypeFinal.append(stTypeData[e])

            ## Create new set of keys for final gpsDict{} that match street name/type
            gpsDict.fromkeys("LatKey"+str(q),None)
            gpsDict.fromkeys("LonKey"+str(q),None)

            ## Obtain values by key from unmodDict{} and add them to appropriate key for gpsDict{}
            tempLat = unmodDict.get("tempLatKey"+str(e))
            tempLon = unmodDict.get("tempLonKey"+str(e))
            gpsDict["LatKey"+str(q)] = tempLat
            gpsDict["LonKey"+str(q)] = tempLon

            q += 1

        e += 1
    

    ## Add final set of street ID/name/type lists to stDict{} after de-duplication
    listOfKeysFinal = ["ID","Type","Name"]
    stDict = dict.fromkeys(listOfKeysFinal,None)
    stDict["ID"] = stListIDsFinal
    stDict["Name"] = stNameFinal
    stDict["Type"] = stTypeFinal
    

    ## Connect to highwayhealth database so we can insert data into gps table
    print("CONNECTING TO MYSQL DATABASE")
    conn = mySqlConn.connect(host = host, user = user, password = password, database = database)
    curse = conn.cursor()
    print("SUCCESSFULLY CONNECTED TO DATABASE")


    ## Define variables for below while loop
    x = 0 
    y = 0
    count = q   # reassign count to be how many values we know we have after deduplication; should be 310
    roadType = ''
    roadName = ''
    latIndex = ''
    lonIndex = ''
    listLat = []
    listLon = []
    ## Define empty list for writing to csv file
    writeToFile = []
    
    ## Loop through remaining items in the dataset.
    ## Allows us to insert each row of matching data 
    ## (NAME, TYPE, LAT, LON) into highwayhealth database GPS table
    while x < count :
        #print("INSERTION NUMBER : " + str(x) + " OUT OF " + str(count)) 
        
        ## We know this dictionary only has 3 keys, so create variables
        ## that lets us assign names / types to insert into database
        ## reassign y to one on each outer loop for next type/name assignment
        y = 0 
        for key, value in stDict.items():
            if y == 0:
                num = str(value[x]) #unused, is the ID
                #print(num) #test print
            elif y == 1:
                roadType = str(value[x])
                #print(roadType) #test print
            elif y == 2:
                roadName = str(value[x])
                #print(roadName) #test print
            y += 1 
            

        ## Obtain all gps coordinates from gps dictionary for specified keyname 
        ## and store into latitude/longitude lists to iterate and store into database
        latIndex = "LatKey"+str(x)
        lonIndex = "LonKey"+str(x)
        listLat = gpsDict.get(latIndex)
        listLon = gpsDict.get(lonIndex)
        
        ## Iterate through each latitude/longitude pair assigned to current street 
        ## name/type and insert into database and/or save to a .csv file 
        for (lats, longs) in itertools.zip_longest(listLat, listLon):
            
            ## INSERTS NAME, TYPE, LATITUDE, LONGITUDE INTO DATABASE
            ## comment out following line if only saving to .csv file
            dbWork.addToGPS(conn, curse, tableGPS, roadName, roadType, lats, longs)
            
            ## Appends items to a list for saving to .csv file
            ## comment out following line if only inserting to database
            writeToFile.append(str(roadName + " , " + roadType + " , " + lats + " , " + longs))
        
        x += 1
        
    

    ## WRITES NAME, TYPE, LATITUDE, LONGITUDE TO .CSV FILE
    ## comment out the following 4 lines if only inserting to database
    listFile = open("sameAsDatabase.csv", "a")
    writer = csv.writer(listFile)
    for item in writeToFile: 
        writer.writerow([str(item)]) 
    
    conn.commit
    conn.close

    print("\nExiting datasetWork() function\n")


## Call datasetWork() function
datasetWork()