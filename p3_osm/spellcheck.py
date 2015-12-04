#! /usr/bin/python3

import xml.etree.cElementTree as ET
import pprint
import open_file
import 


if __name__ == '__main__':
    import sys
     
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        print("ERROR: No input file specified", file=sys.stderr)
        sys.exit(1)

    inf = open_file.open_file(filename)
    spell_check(inf)

