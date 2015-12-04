#!/usr/bin/python3

"""Obtain the XML schema of an OSM file."""

from collections import Counter
import xml.etree.cElementTree as ET
import pprint
import open_file


tag_tree = {}
tag_tree_counters = Counter()
tag_counters = Counter()


def parse_tree(xmlf):
    """Find all tags and their attributes in the input XML file, and count them.

    Tag hierarchy is represented in a "dot" way, e.g. "osm.role.member".

    Args:
        xmlf: FileObject input XML file, already open for reading
    """
    with xmlf as inf:
        parser = ET.iterparse(inf, events=('start', 'end'))
        tag = []
        cur_level = -1
        for ev, elem in parser:
            if ev == 'start':
                cur_level += 1
                if len(tag) <= cur_level:
                    tag.append(elem.tag)
                else:
                    tag[cur_level] = elem.tag
                attrs = list(elem.attrib.keys())
                tag_path = '.'.join(tag)
                tag_tree_counters[tag_path] += 1
                if tag_path in tag_tree.keys():
                    tag_tree[tag_path].union(attrs)
                else:
                    tag_tree[tag_path] = set(attrs)
            else:
                cur_level -= 1
                tag = tag[:cur_level+1]
                tag_counters[elem.tag] += 1

                # Release the memory of the current tag and all its children
                # This is acceptable since we will never access it again
                # This saves enormous amounts of operational RAM
                elem.clear()


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser(description=__doc__)
    parser.add_argument("-a", "--attr", action="store_true",
                        help="print the tree of the found tags and their attributes")
    parser.add_argument("-f", "--flat", action="store_true",
                        help="print flat statistics of the found tags")
    parser.add_argument("-t", "--tree", action="store_true",
                        help="print the tree of the found tags and their statistics")
    parser.add_argument("filename", metavar="FILE",
                        help="input OSM XML file (can be compressed or uncompressed)")
    args = parser.parse_args()

    if not (args.flat or args.attr or args.tree):
        args.flat = True
    if args.flat: print("> Flat mode enabled\n")
    if args.attr: print("> Attribute mode enabled\n")
    if args.tree: print("> Tree mode enabled\n")

    inf = open_file.open_file(args.filename)
    parse_tree(inf)

    if args.flat:
        pprint.pprint(tag_counters)
    if args.attr:
        pprint.pprint(tag_tree)
    if args.tree:
        pprint.pprint(tag_tree_counters)
