import pydeck
import pandas
from flask import Flask, render_template
from pathlib import Path #for getting relative paths to get the .csv files
pandas.options.mode.chained_assignment = None

app = Flask(__name__)

# Texas Traffic Incidents csv FILEPATH
newTrafficPath = Path(__file__).parent / "../hereTraffic/traffic_incidents.csv"
#TEXAS_TRAFFIC_INCIDENTS_FILEPATH = "../hereTraffic/traffic_incidents.csv"
TEXAS_TRAFFIC_INCIDENTS_FILEPATH = newTrafficPath

# Texas Weather csv FILEPATH
newWeatherPath = Path(__file__).parent / "../weather/weather_updates.csv"
# WEATHER_DATA_FILEPATH = "../weather/weather_updates.csv"
WEATHER_DATA_FILEPATH = newWeatherPath

# Create specialized icon object
def create_image_data():
    data = pandas.read_csv(WEATHER_DATA_FILEPATH)
    data["icon_data"] = ""
    for i in data.index:
        icon_id = data["WEATHER_ICON"][i]
        icon_data = {
            "url": "http://openweathermap.org/img/wn/" + icon_id + "@2x.png",
            "width": 100,
            "height": 100,
            "anchorY": 100,
        }
        data["icon_data"][i] = icon_data
    return data

ICON_DATA = create_image_data()

# Define a layer to display on a map
scatterplotLayer = pydeck.Layer(
    'ScatterplotLayer',
    data=pandas.read_csv(TEXAS_TRAFFIC_INCIDENTS_FILEPATH),
    get_position='[GEOLOC_ORIGIN_LONGITUDE, GEOLOC_ORIGIN_LATITUDE]',
    auto_highlight=True,
    radius_scale=1,
    radius_min_pixels=5,
    radius_max_pixels=5,
    get_radius=1,  # Radius is given in meters
    get_fill_color=['CRITICALITY_DESCRIPTION == "minor" ? 0 : CRITICALITY_DESCRIPTION == "major" ? 255 : 0', 'CRITICALITY_DESCRIPTION == "minor" ? 204 : CRITICALITY_DESCRIPTION == "major" ? 0 : 128', 'CRITICALITY_DESCRIPTION == "minor" ? 0 : CRITICALITY_DESCRIPTION == "major" ? 0 : 255', 128],  # Set an RGBA value for fill
    pickable=True)

# Define IconLayer
iconLayer = pydeck.Layer(
    type="IconLayer",
    data=ICON_DATA,
    get_icon="icon_data",
    get_size=4,
    size_scale=15,
    get_position=["LONGITUDE", "LATITUDE"],
    pickable=True,
)

hexagonLayer = pydeck.Layer(
    "HexagonLayer",
    data=pandas.read_csv(TEXAS_TRAFFIC_INCIDENTS_FILEPATH),
    get_position='[GEOLOC_ORIGIN_LONGITUDE, GEOLOC_ORIGIN_LATITUDE]',
    auto_highlight=True,
    elevation_scale=1,
    pickable=True,
    elevation_range=[0, 3000],
    extruded=True,
    coverage=0.5,
)

# Define HeatmapLayer
heatmapLayer = pydeck.Layer(
    "HeatmapLayer",
    data=pandas.read_csv(TEXAS_TRAFFIC_INCIDENTS_FILEPATH),
    radiusPixels=100,
    opacity=0.9,
    get_position=["GEOLOC_ORIGIN_LONGITUDE", "GEOLOC_ORIGIN_LATITUDE"],
    aggregation=pydeck.types.String("SUM"),
    threshold=1,
    get_weight='CRITICALITY_DESCRIPTION == "minor" ? 1 : CRITICALITY_DESCRIPTION == "major" ? 2 : 3', #Set weight value
    pickable=True,
)

# Set the viewport location
view_state_homepage = pydeck.ViewState(
    longitude=-96.7970,
    latitude=32.7767,
    zoom=9,
    min_zoom=1,
    max_zoom=20,
    pitch=0,
    bearing=0)

# Set the viewport location
view_state_graph = pydeck.ViewState(
    longitude=-96.7970,
    latitude=32.7767,
    zoom=9,
    min_zoom=1,
    max_zoom=20,
    pitch=45,
    bearing=0)

 # Set the viewport location
view_state_heatmap = pydeck.ViewState(
    longitude=-96.7970,
    latitude=32.7767,
    zoom=9,
    min_zoom=1,
    max_zoom=20,
    pitch=0,
    bearing=0)   

# Render
r = pydeck.Deck(layers=[scatterplotLayer, iconLayer], map_style='road', initial_view_state=view_state_homepage)
# r.to_html('templates/homepage.html')
r.to_html('flaskr/templates/homepage.html')

r = pydeck.Deck(layers=[hexagonLayer], map_style='road', initial_view_state=view_state_graph)
# r.to_html('templates/graph.html')
r.to_html('flaskr/templates/graph.html')

#Uses dark map to see heatmap better
r = pydeck.Deck(layers=[heatmapLayer], initial_view_state=view_state_heatmap)
# r.to_html('templates/heatmap.html')
r.to_html('flaskr/templates/heatmap.html')

@app.route('/')
def homepage():
   return render_template('homepage.html')

@app.route('/graph')
def graph():
   return render_template('graph.html')

@app.route('/heatmap')
def heatmap():
   return render_template('heatmap.html')



if __name__ == '__main__':
   app.run()

# Please see the note about using a Mapbox API token here:
# https://github.com/uber/deck.gl/tree/master/bindings/python/pydeck#mapbox-api-token
