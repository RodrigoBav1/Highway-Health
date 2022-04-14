import os
import pydeck
from flask import Flask, render_template
app = Flask(__name__)

# 2014 locations of car accidents in the UK
TexasTrafficIncidents = ('traffic_incidents.csv')
print(TexasTrafficIncidents)

# Define a layer to display on a map
layer = pydeck.Layer(
    'ScatterplotLayer',
    TexasTrafficIncidents,
    get_position='[GEOLOC_ORIGIN_LONGITUDE, GEOLOC_ORIGIN_LATITUDE]',
    auto_highlight=True,
    get_radius=1000,  # Radius is given in meters
    get_fill_color=[180, 0, 200, 140],  # Set an RGBA value for fill
    pickable=True)

# Set the viewport location
view_state = pydeck.ViewState(
    longitude=-99.9018,
    latitude=31.9686,
    zoom=4.2,
    min_zoom=1,
    max_zoom=20,
    pitch=0,
    bearing=0)

# Render
r = pydeck.Deck(layers=[layer], map_style='road', initial_view_state=view_state)
r.to_html('templates/demo.html')

@app.route('/')
def home():
   return render_template('demo.html')


if __name__ == '__main__':
   app.run()

# Please see the note about using a Mapbox API token here:
# https://github.com/uber/deck.gl/tree/master/bindings/python/pydeck#mapbox-api-token
