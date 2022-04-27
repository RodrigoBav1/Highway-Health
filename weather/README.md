# Weather Data README

## Data Source for weather_updates.csv

When the `openWeatherAPICalls.py` daemon is running, latitude/longitude data from the database table `highwayhealth.gps` is used to make calls to the OpenWeatherMaps Current Weather Data API service once per hour. 

The returned data from OpenWeatherMaps is parsed and then overwrites the existing `weather_updates.csv` file.