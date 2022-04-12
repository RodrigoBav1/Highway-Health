import pydeck
from flask import Flask, render_template

app = Flask(__name__)

# New Mexico Roads
DATA_URL = "https://raw.githubusercontent.com/RodrigoBav1/Highway-Health/HH-Task-B/DataSets/mod-Unmanipulated-RoadsDataset.geojson"

# Define GeoJsonLayer
layer = pydeck.Layer(
    "GeoJsonLayer",
    DATA_URL,
    opacity= 1,
    stroked=False,
    filled=True,
    extruded=True,
    wireframe=True,
    get_fill_color=[255, 255, 0], #Yellow
    get_line_color=[255, 255, 0], #Yellow
)

# Set the viewport location to Albuquerque, NM
view_state = pydeck.ViewState(
    latitude=35.0844,
    longitude=-106.629181, 
    zoom=14, 
    max_zoom=20, 
    pitch=45, 
    bearing=0)

# Render
r = pydeck.Deck(layers=[layer], initial_view_state=view_state)
r.to_html('templates/demo.html')


@app.route("/")
def home():
    return render_template('demo.html')

if __name__ == "__main__":
    app.run()