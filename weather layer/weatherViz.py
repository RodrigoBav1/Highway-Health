import pydeck
import pandas as pd
import math
from flask import Flask, render_template

app = Flask(__name__)

# Weather URL
WEATHER_DATA_URL = "https://raw.githubusercontent.com/RodrigoBav1/Highway-Health/HH-Task-B-2/OpenWeatherMapsOutput.csv"

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

    icon_data = {
        "url": "http://openweathermap.org/img/wn/" + icon_id + "@2x.png",
        "width": 100,
        "height": 100,
        "anchorY": 100,
    }

    return icon_data

# Append icon data to csv file
data = pd.read_csv(WEATHER_DATA_URL)
data["icon_data"] = None
for i in data.index:
    data["icon_data"][i] = get_icon_image_id(data.iloc[i]["WEATHER_ID"], data.iloc[i]["DATE_TIME_CST"])

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

# Set the viewport location to Richardon, TX
view_state = pydeck.ViewState(
    latitude=33.0012,
    longitude=-96.647, 
    zoom=14, 
    max_zoom=20, 
    pitch=0, 
    bearing=0)

# Render
r = pydeck.Deck(layers=[iconLayer], initial_view_state=view_state)
r.to_html('templates/demo.html')


@app.route("/")
def home():
    return render_template('demo.html')

if __name__ == "__main__":
    app.run()