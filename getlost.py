from os import environ
from urllib2 import urlopen
from math import log

from flask import Flask, json, jsonify
app = Flask(__name__)

from hip import get_ranking_array
from utils import jsonp

url = 'http://open.mapquestapi.com/directions/v2/route'
params = '?key={apikey}&ambiguities=ignore&routeType=pedestrian'
rel = url + params + '&from={flat},{flng}&to={tlat},{tlng}'


@app.route("/route/<from_lat>,<from_lng>/<to_lat>,<to_lng>")
@jsonp
def route(from_lat, from_lng, to_lat, to_lng):
    resp = urlopen(rel.format(apikey=environ['MAPQUEST_API_KEY'],
                   flat=from_lat, flng=from_lng, tlat=to_lat, tlng=to_lng))

    route = json.loads(resp.read().decode("utf-8"))
    coords = [(man['startPoint']['lat'], man['startPoint']['lng'])
              for leg in route['route']['legs']
              for man in leg['maneuvers']]
    hip_rank, total_rank = get_ranking_array(coords)
    return jsonify(route=route,
                   hip_rank=list(hip_rank),
                   total_rank=log(total_rank))

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=environ.get('FLASK_DEBUG', False))
