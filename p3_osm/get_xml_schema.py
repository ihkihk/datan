#! python3

import xml.etree.cElementTree as ET
import pprint
from collections import Counter

found_tags =  Counter()

def count_tags(filename):
    with open(filename, 'r') as inf:
        parser = ET.iterparse(inf, events=('end',))
        for _, elem in parser:
                found_tags[elem.tag] += 1
    
    pprint.pprint(found_tags)

tag_tree = {}

def obtain_tree(xmlf):
    with open(xmlf, 'r') as inf:
        parser = ET.iterparse(inf)
        for _, elem in parser:
            if not elem.tag in tag_tree:
                tag_tree[elem.tag] = {}
    pass

ZIP = {'bz2':'bunzip2', 'tbz':'tar -bxvf', 'tgz':'tar -zxvf', 'zip':'unzip'}

def unzip_file(filename):
    pass


if __name__ == '__main__':
    import sys
    import os.path
    
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        print("ERROR: No input file specified", file=sys.stderr)
        sys.exit(1)

    ext = os.path.splitext(filename)[1].lower()
    if ext in ZIP:
        inf = prepare_file(filename)
    elif ext == '.xml' or ext == '.osm':
        inf = filename
    else:
        print("ERROR: Input file must have one of the following extensions: osm, xml, {!r}" .format(list(ZIP.keys())), file=sys.stderr)
        sys.exit(2)

    count_tags(inf)

    obtain_tree(inf)

