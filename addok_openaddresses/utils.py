import csv
import os
import json
from progressist import ProgressBar
import sys


from addok.config import config
DEBUGIN=(os.environ.get('DEBUGINPUT')=='1')
DEBUGOUT=(os.environ.get('DEBUGOUTPUT')=='1')
def id_generator(row):
    if row['type'] == "number": row['ID']='N'
    else: row['ID']='S'
    
    return row['ID']


def group_addresses(rows):
    ADDRESSES = {}
    bar = ProgressBar(throttle=10000, template='Grouping addresses… {done}')
    for row in rows:
        ADDR={}
        if DEBUGIN:
            print('\rDEBUG:ROW=', row)

        if not row.get('STREET'):
            if DEBUGIN: print("\rFiltering out street without name", row, file=sys.stderr)
            continue
        if row['STREET'] not in ADDRESSES:
            if row.get('housenumbers')==None:
                ADDR['type'] = "number"
            else:
                ADDR['type'] = "street"

            if not row['ID']: row['ID']=id_generator(row)

            ADDR['importance'] = 0.5
            ADDR['housenumbers'] = {}
            ADDR['id'] = 'street-{}'.format(row['ID'])
            ADDR['lat'] = row['LAT']
            ADDR['lon'] = row['LON']
            if config.OPENADDRESSES_EXTRA: ADDR.update(config.OPENADDRESSES_EXTRA)
            else: ADDR['city']= row['CITY']
            ADDRESSES[row['STREET']] = ADDR
        ADDRESSES[row['STREET']]['housenumbers'][row['NUMBER']] = {
            'lat': row['LAT'],
            'lon': row['LON'],
            'id': row['ID'],
        }
        bar.update()

    for address in ADDRESSES.values():
        if DEBUGOUT: print('\rDEBUG:JSON=', json.dumps(address))
        yield json.dumps(address)


def make_labels(helper, result):
    if not result.labels:
        # FIXME: move to a US dedicated plugin instead.
        result.labels = result._rawattr('STREET')[:]
        label = result.labels[0]
        unit = getattr(result, 'UNIT', None)
        if unit:
            label = '{} {}'.format(label, unit)
        city = getattr(result, 'CITY', None)
        if city and city != label:
            label = '{} {}'.format(label, city)
            postcode = getattr(result, 'POSTCODE', None)
            if postcode:
                label = '{} {}'.format(label, postcode)
            result.labels.insert(0, label)
        housenumber = getattr(result, 'housenumber', None)
        if housenumber:
            label = '{} {}'.format(housenumber, label)
            result.labels.insert(0, label)
