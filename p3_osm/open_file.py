"""
Library for opening OSM XML files that can be optionally compressed.
"""

import sys
import os.path

ZIP = {'gz': 'gzip', 'bz2': 'bzip2', 'zip': 'zip',
       'tbz': 'tar:bz2', 'tar.bz2': 'tar:bz2', 'tb2': 'tar:bz2',
       'tgz': 'tar:gz', 'tar.gz': 'tar:gz'}

ERR_UNSUPPORTED_COMPRESSION = 1
ERR_BAD_EXTENSION = 2


def _get_ext(filename):
    """Return the lowercased extension of the given filename, without a dot."""
    return os.path.splitext(filename)[1].lower()[1:]


def _get_zip_ext():
    """Return a string listing the accepted compressed format extensions."""
    return ", ".join(list(ZIP.keys()))


def unzip_file(filename):
    """Open the specified compressed file and return a reader fileobject of it.
    Args:
        filename: str -- filename of the compressed file to be opened
    """
    ext = _get_ext(filename)

    if ext not in ZIP:
        print("ERROR: Unknown compressed format. Supported extensions: " +
              _get_zip_ext(), file=sys.stderr)
        sys.exit(ERR_BAD_EXTENSION)

    if ZIP[ext] == 'bzip2':
        import bz2
        return bz2.BZ2File(filename)
    elif ZIP[ext] == 'gzip':
        import gzip
        return gzip.GzipFile(filename)
    elif ZIP[ext] == 'zip':
        import zipfile
        zipf = zipfile.ZipFile(filename)
        # We support only the first archive member of the zip file
        return zipf.open(zipf.namelist()[0])
    elif ZIP[ext].startswith('tar'):
        import tarfile
        tar = tarfile.open(filename, encoding="UTF-8")
        # We support only the first archive member in the tar file
        return tar.extractfile(tar.getnames()[0])
    else:
        print("ERROR: Currently this format is not supported", file=sys.stderr)
        sys.exit(ERR_UNSUPPORTED_COMPRESSION)


def open_file(filename):
    """Open a specified OSM XML file, which can be plain-text or compressed.

    The decision how to handle the file is taken based on its extension.

    Args:
       filename: str -- the name of the file to open

    Return:
       inf -- the open for reading fileobject
    """
    ext = _get_ext(filename)

    if ext in ZIP:
        inf = unzip_file(filename)
    elif ext == 'xml' or ext == 'osm':
        inf = open(filename, 'r')
    else:
        print("ERROR: Unknown input file format. Supported extensions: " +
              "osm, xml, osm.xml, " + _get_zip_ext(), file=sys.stderr)
        sys.exit(ERR_BAD_EXTENSION)

    return inf
