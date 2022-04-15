# Highway-Health README

## Description

Highway Health will use data from APIs supplied by the following company's APIs: OpenWeatherMaps, Here Real-Time Traffic, Twitter. The data gathered from those APIs will be utilitized to create a map visualization via Deck.gl. This project supports an end user that requires knowledge of the status of roads, such as shipping and trucking companies. 


## Requirements

Python 3.10

MySQL or MariaDB SQL Database for local database usage

PIP (to install Python dependencies)

## Requirements

Python 3.10

MySQL or MariaDB SQL Database for local database usage


PIP (to install Python dependencies)
1. Download ( ...list of files... )

2. Run `pip install -r requirements.txt` to install Python dependencies. 

3. Install the following dependencies: 

[Install webpack (needed to install Deck.gl)](https://github.com/webpack/webpack "Webpack Github")

[Install Deck.gl (this example applies it via Leaflet)](https://github.com/visgl/deck.gl/tree/8.7-release/examples/get-started/pure-js/leaflet "Deck.gl Github")


## Usage

4. Make necessary changes: 
    1. Database connections: change user/password as needed for local database


5. Commands to run:

   First time setup: 

* `python initCreateDB.py` to create the local database and table(s).
* `python datasetManip.py` to insert all .geojson data into local database (this will take some time).

   To run program: 
   
* `python XXX`

2. Run `pip install -r requirements.txt` to install Python dependencies. 

3. Install the following dependencies: 
    1. webpack-cli@3.3.2 --save-dev
    2. #deck.gl/core #deck.gl/layers  

Using the command (replacing _dependency_ with the listed dependencies above): 
```bash
npm install _dependency_
```

4. Make necessary changes: 
    1. Database connections: change user/password as needed for local database


5. Commands to run:

   First time setup: 

* `python initCreateDB.py` to create the local database and table(s).
* `python datasetManip.py` to insert all .geojson data into local database (this will take some time).

   To run program: 
   
* `python XXX`
* `npm start` within the source directory (development)
