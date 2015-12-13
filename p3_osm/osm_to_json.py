#! /usr/bin/python3

"""Convert an OSM (OpenStreeMap) XML file to JSON.

The code for this script is taken from Udacity's "Data Wrangling with MongoDB"
lesson.

The output JSON has the following structure:
{
    "id": "2406124091",
    "type: "node",
    "visible":"true",
    "created": {
          "version":"2",
          "changeset":"17206049",
          "timestamp":"2013-08-03T16:43:42Z",
          "user":"linuxUser16",
          "uid":"1219059"
          },
    "pos": [41.9757030, -87.6921867],
    "address": {
          "housenumber": "5157",
          "postcode": "60625",
          "street": "North Lincoln Ave"
          },
    "amenity": "restaurant",
    "cuisine": "mexican",
    "name": "La Cabana De Don Luis",
    "phone": "1 (773)-271-5176"
}
"""

import xml.etree.cElementTree as ET
import codecs
import re
import json
import sys
import open_file


LOWER_RE = re.compile(r'^([a-z]|_)*$')
ADDR_RE = re.compile(r'^addr:(([a-z]|_)*)')
LOWER_TWO_COLONS = re.compile(r'^([a-z]|_)*:([a-z]|_)*:([a-z]|_)*$')
LOWER_COLON = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
BAD_CHARS_RE = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = ["version", "changeset", "timestamp", "user", "uid"]


def shape_element(element):
    """Convert an OSM XML element to a JSON representation."""
    node = {}
    node['created'] = {}
    node['address'] = {}
    node['node_refs'] = []

    if element.tag == "node" or element.tag == "way":
        node['type'] = element.tag
        node['id'] = element.attrib['id']
        if 'visible' in element.attrib:
            node['visible'] = element.attrib['visible']
        else:
            node['visible'] = None
        if 'lat' in element.attrib and 'lon' in element.attrib:
            node['pos'] = [float(element.attrib['lat']), float(element.attrib['lon'])]
        else:
            node['pos'] = None

        for i in CREATED:
            if i in element.attrib:
                node['created'][i] = element.attrib[i]

        for tag in element.iter('tag'):
            key = tag.attrib['k']
            val = tag.attrib['v']

            if BAD_CHARS_RE.search(key):
                continue

            addr_tag = ADDR_RE.search(key)
            if addr_tag is not None:
                if not LOWER_TWO_COLONS.search(key):
                    node['address'][addr_tag.group(1)] = val
                    continue

            node[key] = val

        for tag in element.iter('nd'):
            node['node_refs'].append(tag.attrib['ref'])

        if node['address'] == {}:
            del node['address']
        if node['node_refs'] == []:
            del node['node_refs']

        return node
    else:
        return None


def process_map(file_in, filename, pretty=False):
    """Process each XML element in the input map and write it to a JSON file."""
    # You do not need to change this file
    file_out = "{0}.json".format(filename)
    data = []
    with codecs.open(file_out, "w") as fout:
        for _, element in ET.iterparse(file_in):
            elem_json = shape_element(element)
            if elem_json:
                data.append(elem_json)
                if pretty:
                    fout.write(json.dumps(elem_json, indent=2)+"\n")
                else:
                    fout.write(json.dumps(elem_json) + "\n")
    return data


def main():
    """The main function."""
    if len(sys.argv) > 1:
        file = sys.argv[1]
    else:
        print("ERROR: No input file specified", file=sys.stderr)
        sys.exit(1)

    inf = open_file.open_file(file)
    process_map(inf, file.split('.')[0])


if __name__ == '__main__':
    main()
