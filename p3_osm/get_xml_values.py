#! /usr/bin/python3

"""Retrieve the values of tag attributes in an OSM XML file."""

import sys
import xml.etree.cElementTree as ET
import pprint
import re
import open_file


def get_attrib_values(xmlf, xpaths):
    """Retrieve the values of attributes of a specified tag.
    """
    values = {}

    with xmlf as inf:
        parser = ET.parse(inf)
        for path in xpaths:
            attr = re.search(r"\[@(.*)\]", path).group(1)
            print(path)
            print(attr)
            values[path] = set()
            findings = parser.findall(path)

            for fnd in findings:
                if attr in fnd.attrib.keys():
                    values[path].add(fnd.attrib[attr])

    return values


def get_attribs(filename):
    """Retrieve and save to files the attribute values of a set of tags.
    """
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
                                   r".//way/tag[@v]"])

    for attr in vals.keys():
        name = re.sub(r"[^a-zA-Z]+", "-", attr).strip("-")
        with open("valattr-{}.txt".format(name), 'w') as outf:
            pprint.pprint({attr: vals[attr]}, stream=outf)


def get_kv(xmlf, xpaths):
    """Retrieve the values of key:value attributes of a tag.
    """
    values = {}

    with xmlf as inf:
        parser = ET.parse(inf)
        for path in xpaths:
            values[path] = {}
            findings = parser.findall(path)

            for fnd in findings:
                key = fnd.attrib['k']
                val = fnd.attrib['v']
                if key not in values[path].keys():
                    values[path][key] = set()
                values[path][key].add(val)

    return values


def get_kv_pairs(filename):
    """Retrieve and save to files the k:v values of a set of specified tags.
    """
    inf = open_file.open_file(filename)
    vals = get_kv(inf, [r".//node/tag",
                        r".//way/tag",
                        r".//relation/tag"])

    for tag in vals.keys():
        name = re.sub(r"[^a-zA-Z]+", "-", tag).strip("-")
        with open("kv-{}.txt".format(name), 'w') as outf:
            pprint.pprint({tag: vals[tag]}, stream=outf)


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

    if len(sys.argv) > 1:
        afilename = sys.argv[1]
    else:
        print("ERROR: No input file specified", file=sys.stderr)
        sys.exit(1)

    get_attribs(afilename)

    get_kv_pairs(afilename)


if __name__ == '__main__':
    main()
