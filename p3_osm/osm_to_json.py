#! /usr/bin/python3

import xml.etree.cElementTree as ET
import codecs
import pprint
import re
import open_file
import json

lower = re.compile(r'^([a-z]|_)*$')
addr = re.compile(r'^addr:(([a-z]|_)*)')
lower_two_colons = re.compile(r'^([a-z]|_)*:([a-z]|_)*:([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]


def shape_element(element):
    node = {}
    node['created'] = {}
    node['address'] = {}
    node['node_refs'] = []
                        
    if element.tag == "node" or element.tag == "way" :
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
            
            if problemchars.search(key):
                continue
            
            m = addr.search(key)
            if not m is None:
                if not lower_two_colons.search(key):
                    g = m.group(1)
                    node['address'][g] = val
                    continue
                    
            node[key] = val
            
        for tag in element.iter('nd'):
            node['node_refs'].append(tag.attrib['ref'])
        
        if node['address'] == {}:
            del(node['address'])
        if node['node_refs'] == []:
            del(node['node_refs'])
           
        return node
    else:
        return None

 
def process_map(file_in, filename, pretty = False):
    # You do not need to change this file
    file_out = "{0}.json".format(filename)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data


if __name__ == '__main__':

    import sys
    
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        print("ERROR: No input file specified", file=sys.stderr)
        sys.exit(1)

    inf = open_file.open_file(filename)
    process_map(inf, filename.split('.')[0], True)
    
