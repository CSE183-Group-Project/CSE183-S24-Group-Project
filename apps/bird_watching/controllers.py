"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""

import json
from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.url_signer import URLSigner
from .models import get_user_email

url_signer = URLSigner(session)

@action('index')
@action.uses('index.html', db, auth, url_signer)
def index():
    return dict(
        # COMPLETE: return here any signed URLs you need.
        my_callback_url = URL('my_callback', signer=url_signer),
        
   )

@action('get_checklist_data')
@action.uses(db)
def get_checklist_data():
    species = request.params.get('species', '')
    query = (db.checklists.id > 0)
    if species:
        query &= (db.sightings.common_name == species) & (db.checklists.sampling_event_identifier == db.sightings.sampling_event_identifier)
    
    rows = db(query).select(db.checklists.latitude, db.checklists.longitude, db.sightings.observation_count)
    data = [{'lat': row.checklists.latitude, 'lng': row.checklists.longitude, 'count': row.sightings.observation_count} for row in rows]
    return json.dumps(data)

@action('get_species')
@action.uses(db)
def get_species():
    rows = db(db.species.id > 0).select(db.species.common_name)
    data = [{'common_name': row.common_name} for row in rows]
    return json.dumps(data)


@action('my_callback')
@action.uses() # Add here things like db, auth, etc.
def my_callback():
    # The return value should be a dictionary that will be sent as JSON.
    return dict(my_value=3)
