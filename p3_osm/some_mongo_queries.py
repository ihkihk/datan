#!/usr/bin/python3

from pymongo import MongoClient

client = MongoClient()

db = client.osm

res = db.map.aggregate(
    [
        {'$project': { 'type':1, '_id':0 }},
        {'$match': {'type': {'$nin': ['way', 'node']}}},
        {'$group': {'_id':'', 'types':{'$addToSet':'$type'}}}
    ]
)

print(repr(res))

res1 = db.map.aggregate(
    [
        {'$project': {'type':1, '_id':0}},
        {'$match': {'type': {'$nin': ['way', 'node']}}},
        {'$group': {'_id':'$type', 'count':{'$sum':1}}},
        {'$sort': {'count':-1}},
        {'$limit': 1}
    ]
)

print(repr(res1))

res2 = db.map.aggregate(
    [
        {'$project':{'x-audit-op':1,
                     'phonenum':{'$ifNull': ['$phone',
                                 {'$ifNull':['$contact:phone',
                                 {'$ifNull':['$contact:mobile', '$contact:fax']}]}]}}},
        {'$match':{'x-audit-op':'reject'}},
        {'$group':{'_id':'$x-audit-op', 'bad_phones':{'$addToSet':'$phonenum'}}}
    ]
)

print(repr(res2))

res3 = db.map.aggregate(
    [
        {'$project':{'x-audit-op':1,
                     'phonenum':{'$ifNull': ['$phone',
                                 {'$ifNull':['$contact:phone',
                                 {'$ifNull':['$contact:mobile', '$contact:fax']}]}]}}},
        {'$match':{'x-audit-op':'inspect'}},
        {'$group':{'_id':'$x-audit-op', 'strange_phones':{'$addToSet':'$phonenum'}}}
    ]
)

print(repr(res3))
