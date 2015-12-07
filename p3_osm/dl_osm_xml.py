#! /usr/bin/python3
# vim: set fileencoding: utf-8 -*-

"""
Script for downloading OSM (OpenStreeMap) data via an OverPass query.

Arguments:
    MAP_QUERY: str -- the OverPass query to be executed
    OVERPASS_URL: str -- the URL of the server exposing the OverPass API
    OUTF: str -- the name of the output file to store the map

Dependencies:
    requests -- for performing HTTP requests
"""

import sys
import requests

# Overpass API server

#OVERPASS_URL = r"http://overpass.osm.ch/api/interpreter"
OVERPASS_URL = r"http://overpass-api.de/api/interpreter"

# Bounding box coordinates for Zurich-city (S, W, N, E)
#BBOX = (47.31858, 8.44574, 47.43819, 8.62684)
#MAP_QUERY = r"[out:xml];(node{BBOX};<;);out meta;".format(BBOX=BBOX)

# Download all data within the administrative boundary of Zurich city
MAP_QUERY = r"""[out:xml];
area['name:de'='Zürich'][place='city'];
(
  rel(pivot)->.a;
  way(r.a)->.b;
  node(area)->.c;
  way(area)->.d;
  rel(area)->.e;
);
out meta;"""

OUTF = "test.osm.xml"


print("> Downloading from OverPass server: " + OVERPASS_URL)
print("> Executing OverPass query: >>>")
print(MAP_QUERY)
print("<<<\n")

try:
    resp = requests.post(OVERPASS_URL, data=MAP_QUERY.encode("utf-8"), stream=True)
except:
    print("ERROR accessing OverPass API. No data downloaded", file=sys.stderr)
    exit()

print("> OverPass server returned status code: {}".format(resp.status_code))
print("> Storing received map data to: {}\n".format(OUTF))

with open(OUTF, 'wb') as fd:
    for chunk in resp.iter_content(8192):
        fd.write(chunk)

