#!/usr/bin/python3

"""Perform an audit and cleaning of phone numbers in an OSM (OpenStreetMap) XML.

Input can come from 1.) a text file containing a dump of the OSM XML attribute
values (e.g. one output by get_xml_values.py); or 2.) a MongoDB database
containing OSM map data (e.g. data created by osm_to_json.py).

Phone numbers are checked for numeric validity according to the Swiss
Numbering Plan E.164/2002 -- i.e. they specify the correct area code and
contain the correct number of significant digits.

Numerically correct numbers are then rewritten (cleaned) so that they have a
uniform textual representation. The cleaned phones will have the following
string forms which are common in Switzerland:
1.) For 2-digit area codes: "+41 (0)xx yyy yy yy"
2.) For 3-digit area codes: "+41 (0)xxx yyy yyy"

An exception is made for the short numbers starting with "1" and containing
3 to 4 digits. They will be unchanged and will read e.g. "114", "1818".
"""

from collections import defaultdict
import re
from pymongo import MongoClient


# Swiss numbering plan E.164/2002
# (see https://en.wikipedia.org/wiki/Telephone_numbers_in_Switzerland)
#
# NDC = National Destination Code (aka Area code)
# SBN = Subscriber Number
#
# There are three formats for valid numbers:
# 3-to-5 digit short numbers: 1 + 2-to-4-digits
# 10-digit-number (format 1): 0 + 2-digit-NDC + 7-digit-SBN
# 10-digit-number (format 2): 0 + 3-digit-NDC + 6-digit-SBN

# Expected NDC (area codes) for numbers in Zurich
NDC_ZURICH = ('43', '44')
NDC_ENTERP = ('51', '58')
NDC_MOBILE = ('74', '75', '76', '77', '78', '79')
NDC2 = NDC_ZURICH + NDC_ENTERP + NDC_MOBILE
NDC3 = ('800', '840', '842', '844', '848', '900', '901', '906')

# Regexp for verifying NDC (area code) validity
NDC2_RE = "({})".format("|".join(NDC2))
NDC3_RE = "({})".format("|".join(NDC3))

# Regexp for verifying SBN (subscriber number) validity
NUM9_RE = "[0-9]{9}"
SBN7_RE = "[0-9]{7}"
SBN6_RE = "[0-9]{6}"

# Regexp for verifying a complete 9-digit (NDC+SBN) number validity
AREA_NUMB = "(({}{})|({}{}))".format(NDC2_RE, SBN7_RE, NDC3_RE, SBN6_RE)

# Valid short numbers
SHORT_NB = ('11[1-3]', '114[1,4-5]', '115[1-4,9]', '117', '118', '140', '1414',
            '1415', '143', '144', '145', '147', '1600', '16[1-4]', '171',
            '17[5-6]', '18[7-8]', '1811', '1818', '1850')

# Regexp for verifying short number validity
SHORT_NB_RE = "({})".format('|'.join(SHORT_NB))

# A tuple of phone number classifiers (NC)
#
# NCs allow to check if phone numbers contain only allowed characters and to
# classify them into different buckets, depending on the way there are written.
#
# This check is performed by matching a given regexp (specified in the "re"
# field) on the phone number. To ensure performance, it is recommended that
# the regexp be a compiled-regexp objects (obtained via the 're.compile'
# function).
#
# Each NC also specifies how to treat the number in question (the "action" field).
# Actions can be:
#   * 'inspect': The number could not be meaningfully classified by this script
#                and has to be manually expected/corrected/cleaned.
#   * 'fix'    : The phone number was found to be numerically correct and
#                can be automatically rewritten (cleaned).
#   * 'none'   : The phone number does not need to be rewritten, i.e. it
#                is numerically valid and already has the expected shape.
#   * 'reject' : The phone number was found to be invalid (e.g. containing
#                invalid characters). It will not be rewritten (cleaned) and
#                has to be inspected and corrected manually.
#
# If the allowed action is 'fix', then the significant digits (NDC and SBN) can
# be extracted by applying the operation given in the 'fix' field. This field
# specifies a valid Python program that will be executed via an 'eval()' call.
# The extracted phone number digits can then be used in later steps to
# rewrite (clean) the phone number.
#
# If a number cannot be classified by any of the NCs, then it is labeled as an
# "UNCLASSIFIED" one and will have to be manually checked & cleaned. Phone
# numbers can fall into this group e.g. for containing the wrong number of
# significant digits, or having an unexpected area code, or for being written
# in a way that has not been foreseen and parsed by the NCs before. Note that
# it is perfectly possible that such a number is still valid - it's just that
# this script couldn't recognize it as such.
#
# Each classifier is described by an ID string suitable to be used as a
# dictionary key ('class_id'), and a free-form human-readable description
# string ('class_desc').
#
# IMPORTANT: The order of the NCs in the tuple below is arbitrary, except for
# the last catch-all NC that serves to label the "UNCLASSIFIED" phone numbers.
# It really must be given as the last one in the tuple.
#
PH_CLASS = ({'class_desc': "Containing characters different from: 0-9, -, +, (, ), <space>",
             'class_id': "PH_BAD_CHARS",
             'action': 'reject',
             're': re.compile(r"[^\+\s\-\(\)0-9]+"),
             'fix': None},

            {'class_desc': 'Short numbers',
             'class_id': 'PH_SHORT',
             're': re.compile(r"^{SHORT_NB}$".format(SHORT_NB=SHORT_NB_RE)),
             'action': 'none',
             'fix': None},

            {'class_desc': "Wrongly starting with both + and 0s before the country code (41)",
             'class_id': "PH_PLUS_ZERO_41",
             'action': 'fix',
             're': re.compile(r"^\+0+41(\(0\)0+){AREA_NUMB}$".format(AREA_NUMB=AREA_NUMB)),
             'fix': r're.sub("\+0+41(\(0\)0*)*({{NUMB}})".format(NUMB=NUM9_RE), r"\2", "{}")'},

            {'class_desc': "Starting with +, country code (41), followed wrongly by several 0s",
             'class_id': "PH_PLUS_41_MANY_ZEROS",
             're': re.compile(r"^\+41(\(0\)0+){AREA_NUMB}$".format(AREA_NUMB=AREA_NUMB)),
             'action': 'fix',
             'fix': r're.sub("\+41(\(0\)0*)*({{NUMB}})".format(NUMB=NUM9_RE), r"\2", "{}")'},

            {'class_desc': "Wrongly not placing the 0 in front of the area code in ()",
             'class_id': "PH_41_ZERO_NO_PAREN",
             'action': 'fix',
             're': re.compile(r"^\+410{AREA_NUMB}$".format(AREA_NUMB=AREA_NUMB)),
             'fix': r're.sub("\+410({{NUMB}})".format(NUMB=NUM9_RE), r"\1", "{}")'},

            {'class_desc': "Wrongly placing the whole 2-digit area code in ()",
             'class_id': "PH_41_ALL_AREA2_IN_PAREN",
             'action': 'fix',
             're': re.compile(r"^\+41\(0{AREA}\){NUMB}$".format(AREA=NDC2_RE, NUMB=SBN7_RE)),
             'fix': r're.sub("\+41\(0(\d\d)\)({{NUMB}})".format(NUMB=SBN7_RE), r"\1\2", "{}")'},

            {'class_desc': "Wrongly placing the whole 3-digit area code in ()",
             'class_id': "PH_41_ALL_AREA3_IN_PAREN",
             'action': 'fix',
             're': re.compile(r"^\+41\(0{AREA}\){NUMB}$".format(AREA=NDC3_RE, NUMB=SBN6_RE)),
             'fix': r're.sub("\+41\(0(\d\d\d)\)({{NUMB}})".format(NUMB=SBN6_RE), r"\1\2", "{}")'},

            {'class_desc': "Starting with +, country code (41), optional (0), then number",
             'class_id': "PH_PLUS_41_NORMAL",
             'action': 'fix',
             're': re.compile(r"^\+41(\(0\)){{0,1}}{AREA_NUMB}$".format(AREA_NUMB=AREA_NUMB)),
             'fix': r're.sub("\+41(\(0\))*({{NUMB}})".format(NUMB=NUM9_RE), r"\2", "{}")'},

            {'class_desc': "Wrongly starting directly with the country code (41)",
             'class_id': "PH_NO_PLUS_41",
             'action': 'fix',
             're': re.compile(r"^41(\(0\)){{0,1}}{AREA_NUMB}$".format(AREA_NUMB=AREA_NUMB)),
             'fix': r're.sub("41(\(0\))*({{NUMB}})".format(NUMB=NUM9_RE), r"\2", "{}")'},

            {'class_desc': "Starting with 00 and the country code (41)",
             'class_id': "PH_00_41_NORMAL",
             'action': 'fix',
             're': re.compile(r"^0041(\(0\)){{0,1}}{AREA_NUMB}$".format(AREA_NUMB=AREA_NUMB)),
             'fix': r're.sub("0041(\(0\))*({{NUMB}})".format(NUMB=NUM9_RE), r"\2", "{}")'},

            {'class_desc': "Starting directly with a 0 and area code or mobile prefix",
             'class_id': "PH_0_AREA",
             'action': 'fix',
             're': re.compile(r"^0{AREA_NUMB}$".format(AREA_NUMB=AREA_NUMB)),
             'fix': r're.sub("0({{NUMB}})".format(NUMB=NUM9_RE), r"\1", "{}")'},

            {'class_desc': "Wrongly starting with a + followed by the area code or mobile prefix",
             'class_id': "PH_PLUS_AREA",
             'action': 'fix',
             're': re.compile(r"^\+0*{AREA_NUMB}$".format(AREA_NUMB=AREA_NUMB)),
             'fix': r're.sub("\+0*({{NUMB}})".format(NUMB=NUM9_RE), r"\1", "{}")'},

            # This is the last catch-all classifier. It must be placed really at the END of the tuple.
            # If it is reached during classification, it means that no other classifier above matched.
            # This essentially labels the "phone number" as UNCLASSIFIED and performs no action on it
            {'class_desc': "UNCLASSIFIED (e.g. due to wrong number of digits, unexpected area code, etc.)",
             'class_id': "PH_UNCLASSIFIED",
             'action': 'inspect',
             're': re.compile(r".*"),
             'fix': None}
           )


def audit_phone(phone: str):
    """Check a phone number for numeric validity and possibly rewrite (clean) it.

    The number classifiers found in the PH_CLASS tuple are run successively on the
    input number, until one of them matches. Then the action specified by the
    classifier is carried out. In case the action is 'fix' (for numerically
    valid numbers), the phone number is rewritten (cleaned) into one of the
    following Swiss-common text shapes:
       1.) For numbers with 2-digit area code: "+41 (0)xx yyy yy yy"
       2.) For numbers with 3-digit area code: "+41 (0)xxx yyy yyy"

    Inputs:
       phone: str - the phone number to audit and clean

    Output:
       output: str - The cleaned phone number, or the original if not cleaned.

       action: str - The action performed. Can be:
            1.) 'inspect' - the validity of the number could not be
                            automatically determined. It must be manually
                            inspected. The original number is returned unchanged
                            in 'output'.
            2.) 'fix' - the number was found numerically valid and has
                        been cleaned. Cleaned result is in 'output'.
            3.) 'none' - the number could not be classified or was
                         found to already have the expected shape.
                         Nothing is changed and the originalpe. The original
                         number is returned unchanged in 'output'.
            4.) 'reject' - the number is numerically invalid. It must
                           be manually inspected/corrected/cleaned. The
                           original number is returned unchanged in 'output'.

       class_id: str - The ID string of the matched classifier. Can be used as
                       a dictionary key if needed.

       class_desc: str - The human-readable description of the matched
                         classifier.
    """
    original_phone = phone

    # Remove blanks and dashes from the phone number
    phone = re.sub(r"[-\s]", "", phone)

    # Run all classifiers on the phone number
    for check in PH_CLASS:
        if check['re'].search(phone):
            # The current classifier matched
            if check['action'] == 'fix':
                # The classifier recommends fixing the phone number
                # 1. Extract the meaningful digits (NDC + SBN)
                raw_phone = eval(check['fix'].format(phone))
                # 2. Check if we have a 2-digit NDC (area code)
                m = re.match("{}({})".format(NDC2_RE, SBN7_RE), raw_phone)
                if m:
                    # Yes we have a 2-digit area code
                    ndc = m.group(1)
                    sbn = m.group(2)
                    fixed = "+41 (0){} {} {} {}".format(ndc, sbn[0:3], sbn[3:5], sbn[5:7])
                else:
                    # 3. Try for a 3-digit area code
                    m = re.match("{}({})".format(NDC3_RE, SBN6_RE), raw_phone)
                    if m:
                        # Yes we have a 3-digit area code
                        ndc = m.group(1)
                        sbn = m.group(2)
                        fixed = "+41 (0){} {} {}".format(ndc, sbn[0:3], sbn[3:6])
                    else:
                        # Program error
                        fixed = None
                        assert "Incorrect phone format! This shouldn't happen!"

                output = fixed
            else:
                # The classified matched but it says either to reject the phone
                # number as invalid, or leave it unchanged
                output = original_phone

            return (output, check['action'], check['class_id'], check['class_desc'])

    # If we arrive here, it means no classifier has matched --> program error!
    assert False, "BUG: No phone classifier matched. Did you forget the last "\
                  "catch-all classifier in the PH_CLASS tuple?"


################################################################################

# Default location of the MongoDB server
DEFAULT_MONGODB_HOST = "mongodb://localhost:27017"

# Tuple listing all common OSM XML keys that can tag a phone number
OSM_PHONE_KEYS = ('phone', 'mobile', 'fax',
                  'contact:phone', 'contact:mobile', 'contact_fax')


def print_audit_results(results: dict):
    """Print the results of an audit.

    """
    def get_class_desc(class_id: str):
        """Obtain the text description of a phone number classifier."""
        for clsf in PH_CLASS:
            if clsf['class_id'] == class_id:
                return clsf['class_desc']

    # Print the results of the audit
    bad_phones_classes = {"PH_BAD_CHARS", "PH_UNCLASSIFIED"}

    # First print the numerically valid numbers
    for class_id in set(results.keys()) - bad_phones_classes:
        print()
        class_desc = get_class_desc(class_id)
        print(class_desc)
        print("="*len(class_desc))
        for (dirty, clean) in results[class_id]:
            print("{:<30} -> {:<20}".format(dirty, clean))

    # Then print the invalid/unclassified numbers
    print("\n##############################################################")
    print("\nThe following phone numbers need manual inspection/correction!\n")
    for class_id in set(results.keys()) & bad_phones_classes:
        print()
        class_desc = get_class_desc(class_id)
        print(class_desc)
        print("="*len(class_desc))
        for (dirty, clean) in results[class_id]:
            print("{:<30}".format(dirty))


def audit_file(filename: str):
    """Extract phone numbers from a text file, audit & clean them, and print the
    results.

    The data file is expected to be a valid Python dictionary, that can be
    eval'd. A suitable format is the one output by the get_xml_values.py script
    when dumping the k:v attribute pairs of a given OSM XML tag like
    osm.node.tag. This format looks like this:
    { './/node/tag': {'contact:mobile': {'+41 76 412 47 85'},
                      'contact:phone':  {'+044 411 84 42',
                                         '+41 (0)43 268 59 30'}}}

    The function extracts phone numbers marked by keys specified in the
    OSM_PHONE_KEYS tuple.

    Input:
        filename: str - the filename of the file containing phone numbers

    Returns:
        None
    """
    with open(filename) as fd:
        # Read the input file expecting it to be a valid Python dictionary
        try:
            kv = eval(fd.read())
        except SyntaxError:
            print("ERROR: The input file is not a valid Python dictionary!")
            return

        # Extract the main dictionary behind the top-level key
        # e.g. './/node/tag'
        kv = kv.popitem()[1]

        # Extract all the phones specified by the applicable OSM XML keys
        phones = []
        for key in OSM_PHONE_KEYS:
            if key in kv.keys():
                phones.extend(kv[key])

        # Audit and clean the extracted numbers
        results = defaultdict(list)

        for dirty in phones:
            (fixed, _, class_id, _) = audit_phone(dirty)
            results[class_id].append((dirty, fixed))

    print_audit_results(results)


def audit_mongodb(host, dbase, coll):
    """Extract phone numbers from a MongoDB database, audit & clean them, and
    store the results back to the DB.

    The function searches in the specified collection for documents containing
    top-level phone numbers marked by keys specified in the OSM_PHONE_KEYS tuple.

    The found phone numbers are audited and, if possible, cleaned. If the
    number could be cleaned (i.e. the audit result was 'fix'), the cleaned
    version is stored in the original document under a new key: 'x-audit-clean'.

    In any case the performed audit operation ('inspect', 'fix', 'none',
    'reject') will be stored in the original document under a new key:
    'x-audit-op'.

    Input:
        host: str - the host:port of the MongoDB server

        dbase: str - the name of the MongoDB database

        coll: str - the name of the MongoDB collection containing the map data

    Returns:
        None
    """
    client = MongoClient(host)
    dbase = client[dbase]
    coll = dbase[coll]

    # Extract all the phones specified by the applicable OSM XML keys

    db_keys = []
    for key in OSM_PHONE_KEYS:
        db_keys.append({key:{'$exists':1}})

    records_with_phones = coll.find({'$or': db_keys})

    phones = []
    for rec in records_with_phones:
        for key in OSM_PHONE_KEYS:
            if key in rec:
                phones.append((rec['_id'], key, rec[key]))

    # Audit and clean the extracted numbers

    results = defaultdict(list)

    for (db_id, osm_key, dirty) in phones:
        (fixed, action, class_id, _) = audit_phone(dirty)
        if action == 'fix':
            new_osm_key = "x-audit-clean:{}".format(osm_key)
            coll.update({'_id':db_id}, {'$set':{new_osm_key:fixed, 'x-audit-op':'fix'}})
        else:
            coll.update({'_id':db_id}, {'$set':{'x-audit-op':action}})
        results[class_id].append((dirty, fixed))

    print_audit_results(results)


################################################################################


def main():
    """The main function.
    """
    from argparse import ArgumentParser, FileType, RawDescriptionHelpFormatter

    parser = ArgumentParser(
        description=__doc__,
        formatter_class=RawDescriptionHelpFormatter
        )
    parser.add_argument("-m", "--mongodb", metavar="[host:port/]DB/COLLECTION",
                        help="take input from a MongoDB")
    parser.add_argument("-d", "--dump", metavar="FILE",
                        help="take input from an OSM K:V dump file")
    args = parser.parse_args()

    if args.mongodb:
        print("> MongoDB mode enabled")
        m = re.match(r"(.*:.*/)*(.*)/(.*)", args.mongodb)
        if not m:
            print("ERROR: Invalid specification of MongoDB database")
            return
        host = m.group(1) or DEFAULT_MONGODB_HOST
        dbase = m.group(2)
        collection = m.group(3)
        print("> MongoDB: host {}, dbase: {}, collection: {}".format(
            host, dbase, collection))
        print()
        audit_mongodb(host, dbase, collection)

    if args.dump:
        print("> Dump file mode enabled")
        print("> Input file: " + args.dump)
        print()
        audit_file(args.dump)


if __name__ == '__main__':
    main()
