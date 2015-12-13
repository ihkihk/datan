Files for the "OSM Data Wrangling with MongoDB" project
=======================================================
(c) 2015 Ivailo Kassamakov


Main document
-------------

The main text is in "p3_osm.pdf".
The LaTeX source for this file is in "p3_osm-LaTeX source_zip".


Python scripts
--------------

These scripts are an indispensable part of the project. They are also referenced
in the main text. Note that all scripts use Python3.

(Scroll below to see an example of complete Python session based on these scripts.)

* audit_phones.py - Python script for automatic auditing and cleaning of OSM
  phone numbers.

  To obtain usage help:
    > ./audit_phones.py -h

  To quickly see this script in operation:
    > ./audit_phones.py -d kv-node-tag.txt

    (The kv-node-tag.txt can be found in the valattr.zip or recreated by
     running "./get_xml_values.py zurich-area.osm.bz2")

  To audit and clean the phone numbers in a MongoDB database:
    > ./audit_phones.py -m osm/map

    (The MongoDB database has to be prepared as stated in Section 5 of p3_osm.pdf,
     basically running "mongoimport --db osm --collection map < zurich-area.json")


* dl_osm_xml.py - Python script for downloading from and Overpass API server
  OSM data specified via an Overpass QL query. Currently set to download the
  Zurich-city area into a "zurich-area.osm" file.

  Example run:
    > ./dl_osm_xml.py

* get_xml_schema.py - Python script for printing some statistics about the OSM
  XML data, like tag occurrences and tag attributes.

  Example run:
    > ./get_xml_schema.py zurich-area.osm.bz2

* get_xml_values.py - Python script for extracting the values of all attributes.
  The k:v attributes of <tag> elements are extracted as pairs. Attribute values
  are dumped to text files (in valid JSON format), such as "attr-node-lat.txt"
  or "kv-node-tag.txt".

  Example run:
    > ./get_xml_values.py zurich-area.osm.bz2

    (Note this will create a lot of "attr-*.txt" and "kv-*.txt" files in
     current folder.)

* open_file.py - A helper Python script allowing the transparent opening of
  clear-text or compressed OSM XML files. Imported by the other scripts.

* osm_to_json.py - The Python script that transforms the OSM XML file into a JSON
  file following the format specified in Lesson 6 of the Udacity "OSM Data Wrangling
  with MongoDB" course.

  Example run:
    > ./osm_to_json.py zurich-area.osm.bz2

    (This will create the "zurich-area.json" file)

* some_mongo_queries.py - A hodge-podge throw-away script used to debug some Mongo queries.


Example Python session using the scripts above
----------------------------------------------

> ./dl_osm_xml.py
> bzip2 zurich-area.osm
> ./get_xml_schema.py zurich-area.osm.bz2
> ./get_xml_values.py zurich-area.osm.bz2
> ./osm_to_json.py zurich-area.osm.bz2
> mongoimport --db osm --collection map < zurich-area.json
> ./audit_phones.py -m osm/map

In case no MongoDB test is desired the "audit_phones.py" script can also be run
on one of the "kv-*"" files output by "get_xml_values.py". Like this:
> ./audit_phones.py -d kv-node-tag.txt


Other files in the project folder
---------------------------------

audit.txt - A throw-away file containing issues found during the manual auditing
  of the OSM k:v values.

valattr.zip - A zip file containing all "attr-*.txt" and "kv-*.txt" files
  created by the "get_xml_values.py" script

zurich-area.json.bz2 - The compressed result of running "osm_to_json.py"

zurich-area.osm.bz2 - The compressed result of running "dl_osm_xml.py"

img/zurich-area.png - A map produced by the Maperitive tool from zurich-area.osm.

<< EOF >>
