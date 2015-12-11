#!/usr/bin/python3

import pprint
import re

fd = open("kv-node-tag.txt")

kv = eval(fd.read())

ph_class = [ { 'text': "Containing unacceptable characters",
               're': re.compile(r"[^\+\s\-\(\)0-9]+"),
               'array': [],
               'fix': None},
             { 'text': "Starting with + and the country code (41)",
               're': re.compile(r"^\+\s*41[-\s]*(\(0\)){0,1}[-\s0-9]*$"),
               'array': [],
               'fix': r're.sub("(\+41)(\(0\))*(\d\d)(\d\d\d)(\d\d)(\d\d)", r"\1 \3 \4 \5 \6", "{}")'},
             { 'text': "Wrongly starting directly with the country code (41)",
               're': re.compile(r"^41[-\s]*(\(0\)){0,1}[-\s0-9]*$"),
               'array': [],
               'fix': None},
             { 'text': "Starting with two zeros and the country code (41)",
               're': re.compile(r"^00\s*41[-\s]*(\(0\)){0,1}[-\s0-9]*$"),
               'array': [],
               'fix': None},
             { 'text': "Starting directly with area code or mobile prefix (41)",
               're': re.compile(r"^0(43|44|76|77|78|79)[-\s0-9]*$"),
               'array': [],
               'fix': None},
             { 'text': "Wrongly starting with a + followed by the area code (43/44)",
               're': re.compile(r"^\+\s*(43|44)"),
               'array':[],
               'fix': None}
           ]

ph_no_class = []



for p in kv['.//node/tag']['phone']:
    p = p.strip()
    matched = False
    for check in ph_class:
        if check['re'].search(p):
            check['array'].append(p)
            matched = True
            break
    if not matched:
        ph_no_class.append(p)


for check in ph_class:
    print("\n" + check['text'])
    print("="*len(check['text']))
    #pprint.pprint(check['array'])
    for p in check['array']:
        if check['fix']:
            cleaned = re.sub("[^\+\(\)0-9]", "", p)
            fixed = eval(check['fix'].format(cleaned))
            print("{} -> {}".format(p, fixed))
        else:
            print(p)

print("\nUNCLASSIFIED")
pprint.pprint(ph_no_class)
