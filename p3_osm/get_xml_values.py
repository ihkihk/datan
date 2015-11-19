#! python3

import xml.etree.cElementTree as ET
import pprint
import open_file

def get_attrib_values(xmlf, xpath, attr):
    values = set()
    with xmlf as inf:
        parser = ET.parse(inf)
        #_, root = next(parser)
        findings = parser.findall(r"*")
        pprint.pprint(findings)

        for f in findings:
            if attr in f.attrib.keys():
                set.add(f.attrib[attr])
    
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
    vals = get_attrib_values(inf, r".//relation/member[@role]", "role")

    pprint.pprint(vals)



