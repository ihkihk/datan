#! python3

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

if __name__ == '__main__':

    import sys
    import os.path
    
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        print("ERROR: No input file specified", file=sys.stderr)
        sys.exit(1)

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
        name = re.sub(r"[^a-zA-Z]+", "-", n)
        name = name.strip("-")
        valsdict = {}
        valsdict[n] = vals[n]
        with open("valattr-{}.txt".format(name), 'w') as of:
            pprint.pprint(valsdict, stream=of)



