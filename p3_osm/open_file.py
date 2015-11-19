
import sys
import os.path
    
ZIP = {'bz2':'bunzip2', 'tbz':'tar -bxvf', 'tgz':'tar -zxvf', 'zip':'unzip'}

def unzip_file(filename):
    ext = os.path.splitext(filename)[1].lower()[1:]

    if ext == 'bz2':
        import bz2
        return bz2.BZ2File(filename)
    else:
        print("ERROR: Currently only bzip2 is supported")
        sys.exit(3)

def open_file(filename):
    ext = os.path.splitext(filename)[1].lower()[1:]
    
    if ext in ZIP:
        inf = unzip_file(filename)
    elif ext == 'xml' or ext == 'osm':
        inf = open(filename, 'r')
    else:
        print("ERROR: Input file must have one of the following extensions: osm, xml, {!r}" .format(list(ZIP.keys())), file=sys.stderr)
        sys.exit(2)

    return inf

