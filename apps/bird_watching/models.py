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

db.define_table(
    'User_bird_data',
    Field('Userid', 'reference auth_user'),
    Field('bird_name'),
    Field('bird_count', 'integer')
)
if db(db.species).isempty():
    with open('apps/bird_watching/data/species.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            db.species.insert(common_name=row[0])

if db(db.sightings).isempty():
    with open('apps/bird_watching/data/sightings.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            db.sightings.insert(sampling_event_identifier=row[0], common_name=row[1], observation_count=row[2])

if db(db.checklists).isempty():
    with open('apps/bird_watching/data/checklists.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            db.checklists.insert(sampling_event_identifier=row[0], latitude=row[1], longitude=row[2], observation_date=row[3], time_observation=row[4], observer_id=row[5], duration_minute=row[6])

## always commit your models to avoid problems later
db.commit()


