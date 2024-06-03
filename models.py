"""
This file defines the database models
"""

import datetime
from .common import db, Field, auth
from pydal.validators import *


def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None

def get_time():
    return datetime.datetime.utcnow()


### Define your table below
#
db.define_table('species', Field('common_name'))
db.define_table('sightings', Field('sampling_event_identifier'),Field('common_name'), Field('observation_count'))
db.define_table('checklists', Field('sampling_event_identifier'),Field('latitude'), Field('longitude'), Field('observation_date'), Field('time_observation'), Field('observer_id'), Field('duration_minute'))
#
## always commit your models to avoid problems later

db.commit()
