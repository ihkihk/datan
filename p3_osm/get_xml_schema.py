#! /usr/bin/python3

import xml.etree.cElementTree as ET
import pprint
import open_file

from collections import Counter

tags_counters =  Counter()

def count_tags(xmlf):
    with xmlf as inf:
        parser = ET.iterparse(inf, events=('end',))
        for ev, elem in parser:
            tags_counters[elem.tag] += 1
            elem.clear()
    
    pprint.pprint(tags_counters)

tag_tree = {}
tag_tree_counters = Counter()

def add_elem_to_tree(tag, attr):
    tag_tree_counters[tag] += 1
    if tag in tag_tree.keys():
        tag_tree[tag].union(attr)
    else:
        tag_tree[tag] = set(attr)

def reconstruct_tree(xmlf):
    with xmlf as inf:
        parser = ET.iterparse(inf, events = ('start','end'))
        tag = []
        cur_level = -1
        for ev, elem in parser:
            if ev == 'start':
                cur_level += 1
                if len(tag) <= cur_level:
                    tag.append(elem.tag)
                else:
                    tag[cur_level] = elem.tag
                attribs = list(elem.attrib.keys())
                add_elem_to_tree('.'.join(tag), attribs)
            else:
                if elem.text is not None or elem.tail is not None:
                    add_elem_to_tree('.'.join(tag)+'.TEXT', [])

                cur_level -= 1
                tag = tag[:cur_level+1]

    pprint.pprint(tag_tree)
    pprint.pprint(tag_tree_counters)
    pass


if __name__ == '__main__':
    import sys
     
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        print("ERROR: No input file specified", file=sys.stderr)
        sys.exit(1)

    inf = open_file.open_file(filename)
    count_tags(inf)

    inf = open_file.open_file(filename)
    reconstruct_tree(inf)

