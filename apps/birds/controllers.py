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

from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.url_signer import URLSigner
from .models import get_user_email
import datetime

url_signer = URLSigner(session)

@action('index')
@action.uses('index.html', db, auth, url_signer)
def index():
    return dict(
        # COMPLETE: return here any signed URLs you need.
        get_stats_url = URL('get_stats'),
        get_species_details_url = URL('get_species_details'),
        get_trends_url = URL('get_trends'),
    )

@action('get_stats')
@action.uses(db, auth.user)
def get_stats():
    # when we sign up is it creating a observer id how to connect email with obsever id
    user_email = get_user_email()
    print(db(db.checklists.observer_id == "obs1644106"))
    # Fetch the list of species seen by the user
    # PROBABLY GONNA GET A LIST FOR OBSERVER ID
    observer_id = db(db.observers.user_email == user_email).select(db.observers.observer_id)
    species_seen = db((db.sightings.sampling_event_identifier == db.checklists.sampling_event_identifier) &
                      (db.checklists.observer_id == observer_id) &
                      (db.sightings.common_name == db.species.common_name)).select(db.species.ALL, distinct=True)
    species_list = [species.common_name for species in species_seen]
    return dict(species_list=species_list)

@action('get_species_details/<species_name>')
@action.uses(db, auth.user)
def get_species_details(species_name=None):
    user_email = get_user_email()
    # Fetch the sightings of the given species by the user
    sightings = db((db.sightings.sampling_event_identifier == db.checklists.sampling_event_identifier) &
                   (db.checklists.observer_id == user_email) &
                   (db.sightings.common_name == species_name)).select(db.sightings.ALL, db.checklists.ALL)
    # Prepare data for visualization
    sightings_data = []
    for sighting in sightings:
        sightings_data.append({
            'date': sighting.checklists.observation_date,
            'count': sighting.sightings.observation_count,
            'location': (sighting.checklists.latitude, sighting.checklists.longitude)
        })
    return dict(species_name=species_name, sightings_data=sightings_data)

@action('get_trends')
@action.uses(db, auth.user)
def get_trends():
    user_email = get_user_email()
    # Fetch all sightings by the user to show trends
    sightings = db((db.sightings.sampling_event_identifier == db.checklists.sampling_event_identifier) &
                   (db.checklists.observer_id == user_email)).select(db.sightings.ALL, db.checklists.ALL)
    # Aggregate data for trends
    trend_data = {}
    for sighting in sightings:
        date = sighting.checklists.observation_date
        if date not in trend_data:
            trend_data[date] = 0
        trend_data[date] += sighting.sightings.observation_count
    # Prepare data for visualization
    trend_list = [{'date': date, 'count': count} for date, count in sorted(trend_data.items())]
    return dict(trend_data=trend_list)

   
    
