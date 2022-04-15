import os
import pydeck
from flask import Flask, render_template
app = Flask(__name__)

# 2014 locations of car accidents in the UK
TexasTrafficIncidents = ('https://raw.githubusercontent.com/RodrigoBav1/Highway-Health/Surya/flaskr/traffic_incidents.csv')

# Define a layer to display on a map
layer = pydeck.Layer(
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
