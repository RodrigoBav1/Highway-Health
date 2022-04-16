#
#   Author:         Karin Nielsen
#   Date Created:   4/7/2022
#   File Name:      initCreateDB.py
#   Version:        1.0
#   Description:    
#                   File that calls functions to create highwayhealth database and GPS table
#


## Import statement(s)
from database import databaseGPS

## Define Variables

## Database creation variables
## Change host/user/password if necessary
host = 'localhost'
user = 'root'
password = 'testnewpassword'
database = 'highwayhealth'
tableGPS = 'GPS'


## Call functions to create database and database table(s)
databaseGPS.dbWork.dbCreate(host, user, password, database) #creates DB highwayhealth
databaseGPS.dbWork.dbAddTable(host, user, password, database, tableGPS) #adds gps table
