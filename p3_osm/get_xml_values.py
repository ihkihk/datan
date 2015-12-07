#! /usr/bin/python3

"""Dump to files the values of tag attributes in an OSM XML file.

The unique values of different attributes found in an OSM XML files are
dumped to text files. Examples are the "lon" and "lat" attributes of the
OSM "node" XML tags.

The "tag" XML tags are specially treated since they contain matched pairs of 
"k" and "v" attributes (short for 'key' and 'value'). The values of these 
pairs are harvested together, so that we can easily see for example all the
values of the OSM "amenity" key.

Attributes:
    ATTR_FILE_PREFIX: str -- the prefix for filenames containing attribute dump
    KV_FILE_PREFIX: str -- the prefix for filenames containing kv pairs dump
"""

import xml.etree.cElementTree as ET
import pprint
import re
import open_file

ATTR_FILE_PREFIX = "attr"
KV_FILE_PREFIX = "kv"


def _xpath2filename(xpath):
    """Convert an xpath string to a valid filename.

    For example ".//relation/member[@role]" will become "relation-member-role".
    """
    return re.sub(r"[^a-zA-Z]+", "-", xpath).strip("-")


def get_attrib_values(xmlf, xpaths):
    """Retrieve the values of a specified attributes of a specified tag.

    Args:
       xmlf: fileobject -- the XML file open for reading
       xpaths: list of str -- the XPATHS specifying the tag and
              its attribute, e.g. ".//relation/member[@role]"

    Returns:
       values: dict of sets indexed with each path in xpaths,
               each set contains attribute value strings, e.g.
               {".//relation/member[@role]" : {"way", "node"}}
    """
    values = {}

    with xmlf as inf:
        # We're obliged to use one-time parse (and not iterparse)
        # in order to be able to search via a xpath
        parser = ET.parse(inf)
        for path in xpaths:
            # Get the name of the attribute to be harversted from the xpath
            attr = re.search(r"\[@(.*)\]", path).group(1)
            values[path] = set()
            # Find all occurrences of the tag with the specified attribute
            findings = parser.findall(path)
            # Extract the value of the attribute we're interested in (if
            # available) and add it to the set of values we will return
            for fnd in findings:
                if attr in fnd.attrib.keys():
                    values[path].add(fnd.attrib[attr])

    return values


def harvest_attribs(filename):
    """Retrieve and save to files the values of certain tags' attribute.
    """
    inf = open_file.open_file(filename)
    vals = get_attrib_values(inf, [r".//node[@lat]",
                                   r".//node[@lon]",
                                   r".//node[@user]",
                                   r".//relation[@user]",
                                   r".//relation/member[@role]",
                                   r".//relation/member[@type]",
                                   r".//way[@user]"])

    for xpath in vals.keys():
        name = _xpath2filename(xpath)
        with open("{}-{}.txt".format(ATTR_FILE_PREFIX, name), 'w') as outf:
            pprint.pprint({xpath: vals[xpath]}, stream=outf)


def get_kv(xmlf, xpaths):
    """Retrieve the values of key:value attribute pairs of a specified tag.

    Args:
       xmlf: fileobject -- the XML file open for reading
       xpaths: list of str -- the XPATHS specifying the tag containing
              k:v attribute pairs, e.g. ".//node/tag"

    Returns:
       values: dict indexed with each path in xpaths,
               of dicts indexed with the "key" attribute values,
               of sets contains the "value" attribute value strings, e.g.
               {".//node/tag" : {"addr:postal_code": {"1234", "2345"},
                                 "amenity": {"bar", "school"}}}
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


def harvest_kv_pairs(filename):
    """Retrieve and save to files the k:v values of a set of specified tags.
    """
    inf = open_file.open_file(filename)
    vals = get_kv(inf, [r".//node/tag",
                        r".//way/tag",
                        r".//relation/tag"])

    for xpath in vals.keys():
        name = _xpath2filename(xpath)
        with open("{}-{}.txt".format(KV_FILE_PREFIX, name), 'w') as outf:
            pprint.pprint({xpath: vals[xpath]}, stream=outf)


def main():
    """The main function.
    """
    from argparse import ArgumentParser

    parser = ArgumentParser(description=__doc__)
    parser.add_argument("filename", metavar="FILE",
                        help="input OSM XML file (can be compressed or uncompressed)")
    args = parser.parse_args()

    print("> Input file: " + args.filename)
    print()

    harvest_attribs(args.filename)

    harvest_kv_pairs(args.filename)


if __name__ == '__main__':
    main()

