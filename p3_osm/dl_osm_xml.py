#! /usr/bin/python3

import requests

# Overpass API server

#OVERPASS_URL = r"http://overpass.osm.ch/api/interpreter"
OVERPASS_URL = r"http://overpass-api.de/api/interpreter"

# Bounding box coordinates for Zurich-city (S, W, N, E)
#BBOX = (47.31858, 8.44574, 47.43819, 8.62684)


#MAP_QUERY = r"[out:xml];(node{BBOX};<;);out meta;".format(BBOX=BBOX)
MAP_QUERY = r"""
[out:xml];
area['name:de'~'Z.rich'][admin_level=8][place='city'];
(
  rel(pivot)->.a;
  way(r.a)->.b;
  node(area)->.c;
  way(area)->.d;
  rel(area)->.e;
);
out meta;"""

print(MAP_QUERY)

r = requests.post(OVERPASS_URL, data=MAP_QUERY, stream = True)
#print(r.text)
#print(r.request.body)
#print(r.status_code)

with open("zurich.osm.xml", 'wb') as fd:
    for chunk in r.iter_content(8192):
        fd.write(chunk)




