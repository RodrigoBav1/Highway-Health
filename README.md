# Highway-Health README

## Description

Highway Health will use data from APIs supplied by the following company's APIs: OpenWeatherMaps, Here Real-Time Traffic, Twitter. The data gathered from those APIs will be utilitized to create a map visualization via Deck.gl. This project supports an end user that requires knowledge of the status of roads, such as shipping and trucking companies. 

## Dependencies

Have Python installed with pip or conda

[Install webpack (needed to install Deck.gl)](https://github.com/webpack/webpack "Webpack Github")

[Install Deck.gl (this example applies it via Leaflet)](https://github.com/visgl/deck.gl/tree/8.7-release/examples/get-started/pure-js/leaflet "Deck.gl Github")

## Usage

Install the following dependencies: 
1. webpack-cli@3.3.2 --save-dev
2. #deck.gl/core #deck.gl/layers 

Python packages: 
1. geojson (maybe)
2. requests
3. ?

Using the command (replacing _dependency_ with the listed dependencies above): 
```bash
npm install _dependency_
```

Commands to run:
* `npm start` within the source directory (development)
