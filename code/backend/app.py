import argparse
from flask import Flask, render_template, request, jsonify
import json
from src.api import SBBWrapper
from src.utils import generate_instructions

app = Flask(__name__)

# Load stations data
with open('stations.json', 'r') as f:
    stations_data = json.load(f)

# Extract relevant station information
stations = [
    {
        'id': station.get('operatingpointkilometermasternumber', ''),
        'name': station.get('designationofficial', '')
    }
    for station in stations_data
    if 'operatingpointkilometermasternumber' in station and 'designationofficial' in station
]

wrapper = None


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        station_id = request.form['station']
        from_track = request.form['from-track']
        to_track = request.form['to-track']

        try:
            data = wrapper.get('transfer', client='webshop', clientVersion='latest', lang='en',
                               fromStationID=station_id, toStationID=station_id,
                               fromTrack=from_track, toTrack=to_track, accessible='true')
            instructions = generate_instructions(data['features'])
        except Exception as e:
            instructions = [f"An error occurred: {str(e)}"]

        return render_template('index.html', instructions=instructions)

    return render_template('index.html')

@app.route('/stations', methods=['GET'])
def get_stations():
    query = request.args.get('query', '').lower()
    filtered_stations = [
        {'id': station['id'], 'name': station['name']}
        for station in stations
        if query in station['name'].lower()
    ]
    return jsonify(filtered_stations)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="SBB API Key")
    parser.add_argument("api_key", help="Your SBB API key")
    args = parser.parse_args()
    wrapper = SBBWrapper('https://journey-maps.api.sbb.ch', args.api_key)
    app.run(debug=True)
