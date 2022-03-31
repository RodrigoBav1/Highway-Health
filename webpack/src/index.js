import { GoogleMapsOverlay } from "@deck.gl/google-maps";
import { ScatterplotLayer } from "@deck.gl/layers";

//starting coordinates for map
const utdLat = 32.9490;
const utdLong = -96.7651;

//create deck.gl layer
const scatterplot = () => new   ScatterplotLayer({
    id: 'scatter',
    data: './query.json',
    opacity: 0.8,
    filled: true,
    radiusMinPixels: 2,
    radiusMaxPixels: 5,
    getPosition: d => [d.geometry.x, d.geometry.y],
    getFillColor: [255, 0, 0]
});

//initialize google map
window.initMap = () => {
    const map = new google.maps.Map(document.getElementById('map'), {
            center: {lat: utdLat, lng: utdLong},
            zoom: 18,
    });

    //create deck.gl overlay
    const overlay = new GoogleMapsOverlay({
        layers: [
            scatterplot(),
        ],
    });

    overlay.setMap(map);
}