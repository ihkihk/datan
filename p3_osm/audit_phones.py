#!/usr/bin/python3

import pprint
import re

# Swiss numbering plan E.164/2002
# NDC = National Destination Code (aka Area code)
# nubmer = 0 + NDC2 + SUBSCRIBER7

NDC_ZURICH = ('43', '44')
NDC_ENTERP = ('51', '58')
NDC_MOBILE = ('74', '75', '76', '77', '78', '79')
NDC2 = NDC_ZURICH + NDC_ENTERP + NDC_MOBILE
NDC3 = ('800', '840', '842', '844', '848', '900', '901', '906')

NDC2_RE = "({})".format("|".join(NDC2))
NDC3_RE = "({})".format("|".join(NDC3))

NUM9_RE = "[0-9]{9}"
SBN7_RE = "[0-9]{7}"
SBN6_RE = "[0-9]{6}"

AREA_NUMB = "(({}{})|({}{}))".format(NDC2_RE, SBN7_RE, NDC3_RE, SBN6_RE)

SHORT_NB = ('11[1-3]', '114[1,4-5]', '115[1-4,9]', '117', '118', '140', '1414', '1415',
        '143', '144', '145', '147', '1600', '16[1-4]', '171', '17[5-6]', '18[7-8]',
        '1811', '1818', '1850')

SHORT_NB_RE = "({})".format('|'.join(SHORT_NB))

ph_class = ( {'class_desc': "Containing characters different from: 0-9, -, +, (, ), <space>",
              'class_id': "PH_BAD_CHARS",
              'action': 'reject',
              're': re.compile(r"[^\+\s\-\(\)0-9]+"),
              'array': [],
              'fix': None},

             {'class_desc': 'Short numbers',
              'class_id': 'PH_SHORT',
              're': re.compile(r"^{SHORT_NB}$".format(SHORT_NB=SHORT_NB_RE)),
              'action': 'none',
              'array': [],
              'fix': None},

             {'class_desc': "Wrongly starting with both + and 0s before the country code (41)",
              'class_id': "PH_PLUS_ZERO_41",
              'action': 'fix',
              're': re.compile(r"^\+0+41(\(0\)0+){AREA_NUMB}$".format(AREA_NUMB=AREA_NUMB)),
              'array': [],
              'fix': r're.sub("\+0+41(\(0\)0*)*({{NUMB}})".format(NUMB=NUM9_RE), r"\2", "{}")'},

             {'class_desc': "Starting with +, country code (41), followed wrongly by several 0s",
              'class_id': "PH_PLUS_41_MANY_ZEROS",
              're': re.compile(r"^\+41(\(0\)0+){AREA_NUMB}$".format(AREA_NUMB=AREA_NUMB)),
              'action': 'fix',
              'array': [],
              'fix': r're.sub("\+41(\(0\)0*)*({{NUMB}})".format(NUMB=NUM9_RE), r"\2", "{}")'},
              
             {'class_desc': "Wrongly not placing the 0 in front of the area code in ()",
              'class_id': "PH_41_ZERO_NO_PAREN",
              'action': 'fix',
              're': re.compile(r"^\+410{AREA_NUMB}$".format(AREA_NUMB=AREA_NUMB)),
              'array': [],
              'fix': r're.sub("\+410({{NUMB}})".format(NUMB=NUM9_RE), r"\1", "{}")'},            
 
             {'class_desc': "Wrongly placing the whole 2-digit area code in ()",
              'class_id': "PH_41_ALL_AREA2_IN_PAREN",
              'action': 'fix',
              're': re.compile(r"^\+41\(0{AREA}\){NUMB}$".format(AREA=NDC2_RE, NUMB=SBN7_RE)),
              'array': [],
              'fix': r're.sub("\+41\(0(\d\d)\)({{NUMB}})".format(NUMB=SBN7_RE), r"\1\2", "{}")'},
             
             {'class_desc': "Wrongly placing the whole 3-digit area code in ()",
              'class_id': "PH_41_ALL_AREA3_IN_PAREN",
              'action': 'fix',
              're': re.compile(r"^\+41\(0{AREA}\){NUMB}$".format(AREA=NDC3_RE, NUMB=SBN6_RE)),
              'array': [],
              'fix': r're.sub("\+41\(0(\d\d\d)\)({{NUMB}})".format(NUMB=SBN6_RE), r"\1\2", "{}")'},
             
             {'class_desc': "Starting with +, country code (41), optional (0), then number",
              'class_id': "PH_PLUS_41_NORMAL",
              'action': 'fix',
              're': re.compile(r"^\+41(\(0\)){{0,1}}{AREA_NUMB}$".format(AREA_NUMB=AREA_NUMB)),
              'array': [],
              'fix': r're.sub("\+41(\(0\))*({{NUMB}})".format(NUMB=NUM9_RE), r"\2", "{}")'},
             
             {'class_desc': "Wrongly starting directly with the country code (41)",
              'class_id': "PH_NO_PLUS_41",
              'action': 'fix',
              're': re.compile(r"^41(\(0\)){{0,1}}{AREA_NUMB}$".format(AREA_NUMB=AREA_NUMB)),
              'array': [],
              'fix': r're.sub("41(\(0\))*({{NUMB}})".format(NUMB=NUM9_RE), r"\2", "{}")'},
             
             {'class_desc': "Starting with 00 and the country code (41)",
              'class_id': "PH_00_41_NORMAL",
              'action': 'fix',
              're': re.compile(r"^0041(\(0\)){{0,1}}{AREA_NUMB}$".format(AREA_NUMB=AREA_NUMB)),
              'array': [],
              'fix': r're.sub("0041(\(0\))*({{NUMB}})".format(NUMB=NUM9_RE), r"\2", "{}")'},
             
             {'class_desc': "Starting directly with a 0 and area code or mobile prefix",
              'class_id': "PH_0_AREA",
              'action': 'fix',
              're': re.compile(r"^0{AREA_NUMB}$".format(AREA_NUMB=AREA_NUMB)),
              'array': [],
              'fix': r're.sub("0({{NUMB}})".format(NUMB=NUM9_RE), r"\1", "{}")'},
             
             {'class_desc': "Wrongly starting with a + followed by the area code or mobile prefix",
              'class_id': "PH_PLUS_AREA",
              'action': 'fix',
              're': re.compile(r"^\+0*{AREA_NUMB}$".format(AREA_NUMB=AREA_NUMB)),
              'array': [],
              'fix': r're.sub("\+0*({{NUMB}})".format(NUMB=NUM9_RE), r"\1", "{}")'},

             # This is the last catch-all classifier. It must be placed really at the END of the tuple.
             # If it is reached during classification, it means that no other classifier above matched.
             # This essentially classifies the "phone number" as UNCLASSIFIED and performs no action on it
             {'class_desc': "UNCLASSIFIED (e.g. due to wrong number of digits, unexpected area code, etc.)",
              'class_id': "PH_UNCLASSIFIED",
              'action': 'check_manually',
              're': re.compile(r".*"),
              'array': [],
              'fix': None}
           )


def audit_phone(phone: str):

    # Remove blanks and dashes from the phone number
    phone = re.sub("[-\s]", "", phone)

    # Run all classifiers on the phone number
    for check in ph_class:
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

                return (fixed, 'fix', check['class_id'], check['class_desc'])
            else:
                # The classified matched but it says either to reject the phone number
                # as invalid, or leave it unchanged
                return (phone, check['action'], check['class_id'], check['class_desc'])

    # If we arrive here, it means no classifier has matched --> program error!
    assert False, "BUG: No phone classifier matched"


def audit_from_file(filename):
    with open(filename) as fd:

        kv = eval(fd.read())

        kv = kv['.//node/tag']

        phones = []
        [phones.extend(p) for p in [kv['phone'], kv['contact:phone'], kv['fax'], kv['contact:fax']]]


        from collections import defaultdict
        cleaned = defaultdict(list)

        for p in phones:
            (fixed, action, class_id, class_desc) = audit_phone(p)
            cleaned[class_id].append(fixed)

    for k in cleaned.keys():
        print()
        print(k)
        print("="*len(k))
        for p in cleaned[k]:
            print(p)


def audit_from_mongodb(host, db):
    import pymongo as mongo

    db = mongo.connect(host, db)

    phones = db.findall("{'phone', 'contact:phone'}")
    

#    print("{:<30} -> {:<20}    {:<30} {}".format(p, fixed, class_id, class_desc))

