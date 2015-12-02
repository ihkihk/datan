#! /usr/bin/python3

import xml.etree.cElementTree as ET
import pprint
import re
import open_file

def get_attrib_values(xmlf, xpath):

    values = {}

    with xmlf as inf:
        parser = ET.parse(inf)
        for p in xpath:
            attr = re.search(r"\[@(.*)\]", p).group(1)
            print(p)
            print(attr)
            values[p] = set()
            findings = parser.findall(p)

            for f in findings:
                if attr in f.attrib.keys():
                    values[p].add(f.attrib[attr])
    
    return values
    
def get_attribs(filename):
    inf = open_file.open_file(filename)
    vals = get_attrib_values(inf, [r".//node[@lat]",
                                   r".//node[@lon]",
                                   r".//node[@user]",
                                   r".//node/tag[@k]",
                                   r".//node/tag[@v]",
                                   r".//relation[@user]",
                                   r".//relation/member[@role]",
                                   r".//relation/member[@type]",
                                   r".//relation/tag[@k]",
                                   r".//relation/tag[@v]",
                                   r".//way[@user]",
                                   r".//way/tag[@k]",
                                   r".//way/tag[@v]"
                                   ])

    for n in vals.keys():
        name = re.sub(r"[^a-zA-Z]+", "-", n).strip("-")
        with open("valattr-{}.txt".format(name), 'w') as of:
            pprint.pprint({n:vals[n]}, stream=of)
            

def get_kv(xmlf, xpath):

    values = {}

    with xmlf as inf:
        parser = ET.parse(inf)
        for p in xpath:
            values[p] = {}
            findings = parser.findall(p)

            for f in findings:
                k = f.attrib['k']
                v = f.attrib['v']
                if  k not in values[p].keys():
                    values[p][k] = set()
                values[p][k].add(v)
    
    return values
    
    
def get_kv_pairs(filename):
    inf = open_file.open_file(filename)
    vals = get_kv(inf, [r".//node/tag",
                        r".//way/tag",
                        r".//relation/tag"])
    
    for n in vals.keys():
        name = re.sub(r"[^a-zA-Z]+", "-", n).strip("-")
        with open("kv-{}.txt".format(name), 'w') as of:
            pprint.pprint({n:vals[n]}, stream=of)

    
if __name__ == '__main__':

    import sys
    
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        print("ERROR: No input file specified", file=sys.stderr)
        sys.exit(1)

    get_attribs(filename)
    
    get_kv_pairs(filename)
    



