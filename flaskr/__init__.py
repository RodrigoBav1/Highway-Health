import pydeck
import pandas
import math
from flask import Flask, render_template
app = Flask(__name__)

# 2014 locations of car accidents in the UK
TexasTrafficIncidents = ('https://raw.githubusercontent.com/RodrigoBav1/Highway-Health/main/flaskr/traffic_incidents.csv')

# Weather URL
WEATHER_DATA_URL = "https://raw.githubusercontent.com/RodrigoBav1/Highway-Health/main/flaskr/weather_updates.csv"

# Create specialized icon object
def get_icon_image_id(id, date_time):
    #Decode weather ID
    MSD = math.floor(id/100)                     #Most Significant Digit
    SSD = math.floor((id%100)/10)    #Middle digit
    LSD = id%10                      #Least Significant Digit

    png_id = "02" #Cloudy icon default value

    if(MSD == 2):
       png_id = "11"
    elif(MSD == 3):
        png_id = "09"
    elif(MSD == 5):
        if(SSD == 0):
            png_id = "10"
        elif(SSD == 1):
            png_id = "13"
        elif(SSD == 2 or SSD == 3):
            png_id = "09"
    elif(MSD == 6):
        png_id = "13"
    elif(MSD == 7):
        png_id = "50"
    elif(MSD == 8):
        if(LSD == 0):
            png_id = "01"
        elif(LSD == 1):
            png_id = "02"
        elif(LSD == 2):
            png_id = "03"
        elif(LSD == 3 or LSD == 4):
            png_id == "04"

    #Get night/day image
    time = date_time.split(" ")
    hour = time[1].split(":")

    time_id = "d" #Day icon default value

    #Night icon from 8 pm to 7 am
    if(int(hour[0]) > 19 or int(hour[0]) < 7):
        time_id = "n"

    icon_id = png_id + time_id
    icon_id = "02d"
    icon_data = {
        "url": "http://openweathermap.org/img/wn/" + icon_id + "@2x.png",
        "width": 100,
        "height": 100,
        "anchorY": 100,
    }
    print(icon_data)
    return icon_data

# Append icon data to csv file
data = pandas.read_csv(WEATHER_DATA_URL)
data["icon_data"] = None
for i in data.index:
    data["icon_data"][i] = get_icon_image_id(data.iloc[i]["WEATHER_ID"], data.iloc[i]["DATE_TIME_CST"])

# Define a layer to display on a map
scatterplotLayer = pydeck.Layer(
    'ScatterplotLayer',
    TexasTrafficIncidents,
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
    data=data,
    get_icon="icon_data",
    get_size=4,
    size_scale=15,
    get_position=["LONGITUDE", "LATITUDE"],
    pickable=True,
)

hexagonLayer = pydeck.Layer(
    "HexagonLayer",
    TexasTrafficIncidents,
    get_position='[GEOLOC_ORIGIN_LONGITUDE, GEOLOC_ORIGIN_LATITUDE]',
    auto_highlight=True,
    elevation_scale=1,
    pickable=True,
    elevation_range=[0, 3000],
    extruded=True,
    coverage=1,
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

# Render
r = pydeck.Deck(layers=[scatterplotLayer, iconLayer], map_style='road', initial_view_state=view_state_homepage)
r.to_html('templates/homepage.html')

r = pydeck.Deck(layers=[hexagonLayer], map_style='road', initial_view_state=view_state_graph)
r.to_html('templates/graph.html')

@app.route('/')
def homepage():
   return render_template('homepage.html')

@app.route('/graph')
def graph():
   return render_template('graph.html')



if __name__ == '__main__':
   app.run()

# Please see the note about using a Mapbox API token here:
# https://github.com/uber/deck.gl/tree/master/bindings/python/pydeck#mapbox-api-token
