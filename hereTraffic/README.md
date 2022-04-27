# Traffic Data README

## Data Source for traffic_incidents.csv

When the `here_traffic_api.py` daemon is running, Dallas, TX latitude/longitude range information is used to make calls to the HERE Traffic Incidents API service once per hour. 

The returned data from HERE is parsed and then overwrites the existing `traffic_incidents.csv` file.