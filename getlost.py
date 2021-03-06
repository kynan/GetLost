from os import environ
from urllib2 import urlopen
from math import log, sqrt

from flask import Flask, Markup, json, jsonify, render_template
from markdown import markdown
app = Flask(__name__)

from hip import get_ranking_array
from utils import jsonp

url = 'http://open.mapquestapi.com/directions/v2/route'
params = '?key={apikey}&ambiguities=ignore&routeType=pedestrian'
rel = url + params + '&from={flat},{flng}&to={tlat},{tlng}'


@app.route("/")
def landing():
    with open("README.md") as f:
        content = Markup(markdown(f.read()))
    return render_template('landing.html', **locals())


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
    total_rank /= sqrt((float(to_lng) - float(from_lng))**2 +
                       (float(to_lat) - float(from_lat))**2)
    return jsonify(route=route,
                   hip_rank=list(hip_rank),
                   total_rank=log(total_rank))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(environ.get('PORT', 5000)),
            debug=environ.get('FLASK_DEBUG', False))
