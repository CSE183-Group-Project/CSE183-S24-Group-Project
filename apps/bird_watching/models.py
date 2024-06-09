"""
This file defines the database models
"""

import csv
import datetime
from .common import db, Field, auth
from pydal.validators import *


def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None

def get_time():
    return datetime.datetime.utcnow()


### Define your table below
db.define_table('species', 
                Field('common_name')
                )

db.define_table('checklists',
    Field('sampling_event_identifier'),
    Field('latitude', 'double'), 
    Field('longitude', 'double'),
    Field('observation_date', 'date'),
    Field('time_observation', 'time'),
    Field('observer_id', 'integer'),
    Field('duration_minute', 'integer')
)

db.define_table('sightings',
    Field('sampling_event_identifier'),
    Field('common_name'),
    Field('observation_count', 'integer')
)
db.define_table(
    'User_bird_data',
    Field('Userid', 'reference auth_user'),
    Field('bird_name'),
    Field('bird_count', 'integer')
)

def safe_int(value, default=0):
    try:
        return int(value)
    except ValueError:
        return default

if db(db.species).isempty():
    with open('apps/bird_watching/data/species.csv', 'r') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i == 0: 
                continue
            db.species.insert(common_name=row[0])

if db(db.sightings).isempty():
    with open('apps/bird_watching/data/sightings.csv', 'r') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i == 0: 
                continue
            db.sightings.insert(
                sampling_event_identifier=row[0],
                common_name=row[1],
                observation_count=safe_int(row[2])
            )

if db(db.checklists).isempty():
    with open('apps/bird_watching/data/checklists.csv', 'r') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i == 0:
                continue
            db.checklists.insert(
                sampling_event_identifier=row[0],
                latitude=float(row[1]),
                longitude=float(row[2]),
                observation_date=row[3],
                time_observation=row[4],
                observer_id=safe_int(row[5]),
                duration_minute=safe_int(row[6]) 
            )

# Always commit your models to avoid problems later
db.commit()


