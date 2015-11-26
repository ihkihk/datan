#! /usr/bin/python3

import xml.etree.cElementTree as ET
import pprint
import re
import open_file



if __name__ == '__main__':

    import sys
    
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        print("ERROR: No input file specified", file=sys.stderr)
        sys.exit(1)

    #get_attribs(filename)
    
    get_kv_pairs(filename)
    

