#!/usr/bin/python3

"""Obtain the XML schema of an OSM (OpenStreetMap) file.

Three sets of informations for the OSM XML can be obtained:
- Flat mode: The number of occurrences of each tag, irrespective of its
  position in the XML tree
- Tree mode: The number of occurrences of each fully specified tag
- Attribute mode: The attributes that have been found for each fully
  specified tag

Any combination of the above informations can be specified via command flags.

Example for Flat mode:
    { 'member': 65783,
      'tag': 359396  # Note that there can be node.tag and way.tag tags
    }

Example for Tree mode:
    { 'osm.relation.member': 65783,
      'osm.node.tag': 87143,
      'osm.way.tag': 265276
    }

Example for Attribute mode:
    { 'osm.relation.member': {'type', 'role', 'ref'},
      'osm.node.tag': {'v', 'k'},
      'osm.way.tag': {'v', 'k'}
    }
"""

from collections import Counter
import xml.etree.cElementTree as ET
import pprint
import open_file


def parse_tree(xmlf):
    """Find all tags and their attributes in the input XML file and count them.

    Tag hierarchy is represented in a "dot" way, e.g. "osm.role.member".

    Args:
        xmlf: FileObject input XML file, already open for reading

    Returns:
        (tag_tree, tag_tree_counters, tag_counters) where
        tag_tree -- A dictionary {<tag_path>: set(<tag attributes>)}
        tag_tree_counters -- A collections.Counter dictionary of the form
                             {<tag_path>: <int number of occurrences>}
        tag_counters -- A collections.Counter dictionary of the form
                             {<simple tag>: <int number of occurrences>}

    Notes:
        The input file object will be closed at the end of this function.
    """
    tag_tree = {}  # Will contain the attribute set for each tag
    tag_tree_counters = Counter()  # Will count hierarchical tags
    tag_counters = Counter()  # Will count separate tags

    with xmlf as inf:
        parser = ET.iterparse(inf, events=('start', 'end'))
        tag = []  # Will contain all the parent tags of the current tag
        cur_level = -1  # The level of descent in the XML tree
        for event, elem in parser:
            if event == 'start':
                cur_level += 1
                # Store in the "tag" array the path to the current tag.
                # So, if the current tag is osm/relation/member, the "tag"
                # array will contain ['osm', 'relation', 'tag'].
                if len(tag) <= cur_level:
                    tag.append(elem.tag)
                else:
                    tag[cur_level] = elem.tag
                # tag_path will contain 'osm.relation.member' for example
                tag_path = '.'.join(tag)
                tag_tree_counters[tag_path] += 1

                # Store the attributes of the current tag in a set, indexed
                # by the tag path
                attrs = list(elem.attrib.keys())
                if tag_path in tag_tree.keys():
                    tag_tree[tag_path].union(attrs)
                else:
                    tag_tree[tag_path] = set(attrs)
            else:
                # At the end of each tag climb one level up the tree
                cur_level -= 1
                tag = tag[:cur_level+1]
                tag_counters[elem.tag] += 1

                # Release the memory of the current tag and all its children.
                # This is acceptable since we will never access it again.
                # This saves enormous amounts of operational RAM.
                elem.clear()

    return (tag_tree, tag_tree_counters, tag_counters)


def main():
    """The main function.
    """
    from argparse import ArgumentParser, FileType

    parser = ArgumentParser(description=__doc__)
    parser.add_argument("-a", "--attr", action="store_true",
                        help="print the tree of the found tags and their attributes")
    parser.add_argument("-f", "--flat", action="store_true",
                        help="print flat statistics of the found tags")
    parser.add_argument("-t", "--tree", action="store_true",
                        help="print the tree of the found tags and their statistics")
    parser.add_argument("-o", "--out", dest="outf", default="-",
                        type=FileType("w", encoding="UTF-8"),
                        help="output file (if not specified, then sys.stdout)")
    parser.add_argument("filename", metavar="FILE",
                        help="input OSM XML file (can be compressed or uncompressed)")
    args = parser.parse_args()

    if not (args.flat or args.attr or args.tree):
        args.flat = True
    if args.flat:
        print("> Flat mode enabled")
    if args.attr:
        print("> Attribute mode enabled")
    if args.tree:
        print("> Tree mode enabled")
    print("> Input file: " + args.filename)
    print("> Output will go to: " + args.outf.name)
    print()

    inf = open_file.open_file(args.filename)
    (tag_tree, tag_tree_counters, tag_counters) = parse_tree(inf)

    if args.flat:
        pprint.pprint(tag_counters, stream=args.outf)
    if args.attr:
        pprint.pprint(tag_tree, stream=args.outf)
    if args.tree:
        pprint.pprint(tag_tree_counters, stream=args.outf)


if __name__ == '__main__':
    main()
