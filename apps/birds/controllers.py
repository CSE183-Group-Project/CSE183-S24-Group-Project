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

@action('stats')
@action.uses('stats.html', db, auth, url_signer)
def index():
    return dict(
        # COMPLETE: return here any signed URLs you need.
        get_stats_url = URL('get_stats'),
        get_species_details_url = URL('get_species_details'),
        get_trends_url = URL('get_trends'),
        search_species_url = URL('search_species'),
    )

@action('get_stats/<order>')
@action.uses(db, auth.user)
def get_stats(order="recent"):
    user_email = get_user_email()
    observer_id = db(db.observers.user_email == user_email).select().first()
    if observer_id:
        observer_id = observer_id.observer_id
    else:
        observer_id = None
    
    species_seen = db((db.sightings.sampling_event_identifier == db.checklists.sampling_event_identifier) &
                      (db.checklists.observer_id == observer_id) &
                      (db.sightings.common_name == db.species.common_name)).select(db.species.ALL, distinct=True, orderby = db.checklists.observation_date)
    species_list = [species.common_name for species in species_seen]
    print("Species List:", species_list) 
    if order == "first":
        species_list.reverse() 
    return dict(species_list=species_list)


@action('get_species_details/<species_name>')
@action.uses(db, auth.user)
def get_species_details(species_name=None):
    print("SPECIES:", species_name)
    user_email = get_user_email()
    observer_id = db(db.observers.user_email == user_email).select().first()
    if observer_id:
        observer_id = observer_id.observer_id
    else:
        observer_id = None
    # Fetch the sightings of the given species by the user
    sightings = db((db.sightings.sampling_event_identifier == db.checklists.sampling_event_identifier) &
                   (db.checklists.observer_id == observer_id) &
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
    observer_id = db(db.observers.user_email == user_email).select().first()
    if observer_id:
        observer_id = observer_id.observer_id
    else:
        observer_id = None
    # Fetch all sightings by the user to show trends
    sightings = db((db.sightings.sampling_event_identifier == db.checklists.sampling_event_identifier) &
                   (db.checklists.observer_id == observer_id)).select(db.sightings.ALL, db.checklists.ALL)
    # Aggregate data for trends
    trend_data = {}
    for sighting in sightings:
        date = sighting.checklists.observation_date
        if date not in trend_data:
            trend_data[date] = 0
        trend_data[date] += int(float(sighting.checklists.duration_minute))
    # Prepare data for visualization
    trend_list = [{'date': date, 'count': count} for date, count in sorted(trend_data.items())]
    return dict(trend_data=trend_list)

@action('search_species')
@action.uses(db, auth.user)
def search_species():
    query = request.params.get('query', '').strip().lower()
    results = []
    if query:
        results = db(db.species.common_name.lower().contains(query)).select(db.species.ALL)
    species_list = [species.common_name for species in results]
    return dict(species_list=species_list)
