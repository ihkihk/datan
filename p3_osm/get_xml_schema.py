#! python3

import xml.etree.cElementTree as ET
import pprint
from collections import Counter

found_tags =  Counter()

def count_tags(xmlf):
    with xmlf as inf:
        parser = ET.iterparse(inf, events=('end',))
        for _, elem in parser:
                found_tags[elem.tag] += 1
    
    pprint.pprint(found_tags)

tag_tree = {}

def reconstruct_tree(xmlf):
    with xmlf as inf:
        parser = ET.iterparse(inf)
        _, root = parser.next()
        tag_tree[root] = {}
        cur_level = tag_tree[root]
        for _, elem in parser:
            if elem.parent.tag in cur_level:
                tag_tree[elem.parent.tag] = {}
    pass

ZIP = {'bz2':'bunzip2', 'tbz':'tar -bxvf', 'tgz':'tar -zxvf', 'zip':'unzip'}

def unzip_file(filename):
    ext = os.path.splitext(filename)[1].lower()[1:]

    if ext == 'bz2':
        import bz2
        return bz2.BZ2File(filename)
    else:
        print("ERROR: Currently only bzip2 is supported")
        sys.exit(3)



if __name__ == '__main__':
    import sys
    import os.path
    
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        print("ERROR: No input file specified", file=sys.stderr)
        sys.exit(1)

    ext = os.path.splitext(filename)[1].lower()[1:]
    if ext in ZIP:
        inf = unzip_file(filename)
    elif ext == 'xml' or ext == 'osm':
        inf = open(filename, 'r')
    else:
        print("ERROR: Input file must have one of the following extensions: osm, xml, {!r}" .format(list(ZIP.keys())), file=sys.stderr)
        sys.exit(2)

    count_tags(inf)

    reconstruct_tree(inf)

