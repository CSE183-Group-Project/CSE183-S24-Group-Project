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
db.define_table('observers', 
                Field('observer_id'),
                Field('user_email'))
db.define_table('species', 
                Field('common_name')
                )

db.define_table('sightings', 
                Field('sampling_event_identifier'),
                Field('common_name'), 
                Field('observation_count')
                )

db.define_table('checklists', 
                Field('sampling_event_identifier'),
                Field('latitude'), 
                Field('longitude'), 
                Field('observation_date'), 
                Field('time_observation'), 
                Field('observer_id'), 
                Field('duration_minute')
            )


if db(db.species).isempty():
    with open('apps/birds/species.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            # print(row[0])
            db.species.insert(common_name=row[0])

if db(db.sightings).isempty():
    with open('apps/birds/sightings.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            db.sightings.insert(sampling_event_identifier=row[0], common_name=row[1], observation_count=row[2])

if db(db.checklists).isempty():
    with open('apps/birds/checklists.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            db.checklists.insert(sampling_event_identifier=row[0], latitude=row[1], longitude=row[2], observation_date=row[3], time_observation=row[4], observer_id=row[5], duration_minute=row[6])

## always commit your models to avoid problems later
db.commit()