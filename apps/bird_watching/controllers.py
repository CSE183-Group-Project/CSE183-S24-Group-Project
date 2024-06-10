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
from py4web.core import Template
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.url_signer import URLSigner
from .models import get_user_email
from py4web.utils.grid import Grid, GridClassStyleBulma
from py4web.utils.form import Form, FormStyleBulma
from pydal.validators import IS_INT_IN_RANGE
from pydal import Field
import json

def safe_int(value, default=0):
    try:
        return int(value)
    except ValueError:
        return default
url_signer = URLSigner(session)

@action('index')
@action.uses('index.html', db, auth, url_signer)
def index():
    return dict(
        my_callback_url = URL('my_callback', signer=url_signer),
    )

# location page
@action('location')
@action.uses('location.html')
def location():
    return dict()


@action('statistics')
@action.uses('statistics.html', db, url_signer)
def statistics():
    ne_lat = request.params.get('ne_lat')
    ne_lng = request.params.get('ne_lng')
    sw_lat = request.params.get('sw_lat')
    sw_lng = request.params.get('sw_lng')

    if not all([ne_lat, ne_lng, sw_lat, sw_lng]):
        abort(400, 'Missing coordinates')

    try:
        ne_lat = float(ne_lat)
        ne_lng = float(ne_lng)
        sw_lat = float(sw_lat)
        sw_lng = float(sw_lng)
    except ValueError:
        abort(400, 'Invalid coordinates')


    query = (db.checklists.latitude <= ne_lat) & (db.checklists.latitude >= sw_lat) & \
            (db.checklists.longitude <= ne_lng) & (db.checklists.longitude >= sw_lng)

    checklists = db(query).select()

    sampling_event_ids = [row.sampling_event_identifier for row in checklists]

    if not sampling_event_ids:
        return dict(
            species_counts=[],
            ne_lat=ne_lat,
            ne_lng=ne_lng,
            sw_lat=sw_lat,
            sw_lng=sw_lng,
            my_callback_url = URL('my_callback', signer=url_signer),
        )

    sightings = db(db.sightings.sampling_event_identifier.belongs(sampling_event_ids)).select()

    species_counts = {}
    for sighting in sightings:
        species = sighting.common_name
        count = safe_int(sighting.observation_count)
        if species not in species_counts:
            species_counts[species] = 0
        species_counts[species] += count

    sorted_species_counts = sorted(species_counts.items(), key=lambda x: x[1], reverse=True)

    return dict(
        species_counts=sorted_species_counts,
        ne_lat=ne_lat,
        ne_lng=ne_lng,
        sw_lat=sw_lat,
        sw_lng=sw_lng,
        my_callback_url = URL('my_callback', signer=url_signer),
    )


class GridSelectButton(object):
    def __init__(self, search_term=None):
        self.url = URL('select', vars={ 'search_term': search_term})
        self.append_id = True
        self.additional_classes = 'button is-primary'
        self.icon = 'fa-Select'
        self.text = 'Select'
        self.message = None
        self.onClick = None

class GridEditButton(object):
    def __init__(self, search_term=None):
        self.url = URL('select', vars={'search_term': search_term})
        self.append_id = True
        self.additional_classes = "grid-edit-button button is-primary"
        self.icon = 'fa-pencil'
        self.text = 'Edit'
        self.message = None
        self.onclick = None

class GridDeletebutton(object):
    def __init__(self):
        self.url = URL('delete') 
        self.append_id = True
        self.additional_classes = "grid-delete-button button is-danger"
        self.icon = 'fa-pencil'
        self.text = 'Delete'
        self.message = 'Are you sure you want to delete this record'
        self.onclick = None

    
@action('checklist')
@action('contact_requests/<path:path>')
@action.uses('checklist.html', db, auth.user, url_signer)
def checklist(path=None):
    user = auth.current_user
    lng = request.params.get('lng')
    lat = request.params.get('lat')

    if not path:
        path = URL('submit_checklist', signer=url_signer)
    
    search_term = request.query.get('search_term', '').strip()

    if request.forms.get('increment'):
        species_id = request.forms.get('increment')
        species = db.species(species_id) or redirect(URL('checklist', vars={'search_term': search_term}))
        bird_data = db((db.User_bird_data.Userid == user.get('id')) & 
                       (db.User_bird_data.bird_name == species.common_name)).select().first()

        if not bird_data:
            db.User_bird_data.insert(
                Userid=user.get('id'),
                bird_name=species.common_name,
                bird_count=1
            )
        else:
            bird_data.update_record(bird_count=bird_data.bird_count + 1)

        redirect(URL('checklist', vars={'search_term': search_term}))

    grid = None
    if search_term:
        search_query = db.species.common_name.contains(search_term)
        grid = Grid(
            path=path,
            query=search_query,
            formstyle=FormStyleBulma,
            grid_class_style=GridClassStyleBulma,
            rows_per_page=1000,
            create=False,
            details=False,
            editable=False,
            deletable=False,
            post_action_buttons=[GridSelectButton(search_term)],
            fields=[
                db.species.common_name,
            ]
        )
   
    return dict(
        grid=grid,
        user=user,
        search_term=search_term,
        my_callback_url=URL('my_callback', signer=url_signer),
        submit_checklist_url=URL('submit_checklist', signer=url_signer),
    )


@action('select', method=['GET', 'POST'])
@action.uses('select.html', db, auth.user, session)
def select(species_id=None):
    user = auth.current_user
    search_term = request.query.get('search_term', '')
    print(search_term)
    values = search_term.split('/')
    search_item = values[0]
    species_id = int(values[1])
  
    species = db.species(species_id) or redirect(URL('checklist'))
    
    bird_data = db((db.User_bird_data.Userid == user.get('id')) & 
                   (db.User_bird_data.bird_name == species.common_name)).select().first()

    if not bird_data:
        bird_data_id = db.User_bird_data.insert(
            Userid=user.get('id'),
            bird_name=species.common_name,
            table_id = species_id,
            bird_count=0,
        )
        bird_data = db.User_bird_data(bird_data_id)

    if request.forms.get('increment'):
        bird_data.update_record(bird_count=bird_data.bird_count + 1)
        

    if request.forms.get('update_count'):
        new_count = request.forms.get('bird_count')
        if new_count.isdigit() and int(new_count) >= 0:
            bird_data.update_record(bird_count=int(new_count))
        redirect(URL('select', vars=dict(search_term=search_term)))

    if request.forms.get('submit_record'):
        if bird_data.bird_count == 0:
            db(db.User_bird_data.id == bird_data.id).delete()
        redirect(URL('checklist', vars=dict(search_term=search_item)))

    return dict(
        species_name=species.common_name,
        bird_count=bird_data.bird_count,
        search_term=search_term,
    )


@action('delete/<id>', method = ['GET', 'POST'])
@action.uses(db, session, auth.user)
def delete(id = None):
    r = db.User_bird_data[id]
    if r:
        db(db.User_bird_data.id == id).delete()
    redirect(URL('mychecklist'))
    

@action('mychecklist', method=['GET', 'POST'])
@action.uses('mychecklist.html', db, auth.user, session, url_signer)
def mychecklist():
    user = auth.current_user
    query = db.User_bird_data.Userid == user.get('id')

    grid = Grid(
        path=URL('mychecklist'),
        query=query,
        formstyle=FormStyleBulma,
        grid_class_style=GridClassStyleBulma,
        create=False,
        editable=False,
        deletable=False,
        details=False,
        pre_action_buttons=[            
            GridDeletebutton()
        ],
        rows_per_page=100,
        fields=[
            db.User_bird_data.bird_name,
            db.User_bird_data.bird_count
        ]
    )
    return dict(grid=grid)

@action('get_checklist_data', method=['GET'])
@action.uses(db)
def get_checklist_data():
    species = request.params.get('species')
    limit = None if species else int(request.params.get('limit', 50000))  
    offset = None if species else int(request.params.get('offset', 0))

    query = (db.sightings.id > 0)
    if species:
        query &= (db.sightings.common_name == species)
    
    if limit is not None and offset is not None:
        sightings = db(query).select(limitby=(offset, offset + limit))
    else:
        sightings = db(query).select()

    checklist_data = []
    for sighting in sightings:
        checklist = db(db.checklists.sampling_event_identifier == sighting.sampling_event_identifier).select().first()
        if checklist:
            checklist_data.append({
                'lat': checklist.latitude,
                'lng': checklist.longitude,
                'count': sighting.observation_count
            })
    
    return dict(data=checklist_data)



@action('get_species')
@action.uses(db)
def get_species():
    rows = db(db.species.id > 0).select(db.species.common_name)
    data = [{'common_name': row.common_name} for row in rows]
    return json.dumps(data)


#stats page

@action('stats')
@action.uses('stats.html', db, auth, url_signer)
def index():
    return dict(
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
                      (db.sightings.common_name == db.species.common_name)).select(db.species.ALL, distinct=True, orderby=db.checklists.observation_date)
    species_list = [species.common_name for species in species_seen]
    if order == "first":
        species_list.reverse()
    return dict(species_list=species_list)

@action('get_species_details/<species_name>')
@action.uses(db, auth.user)
def get_species_details(species_name=None):
    user_email = get_user_email()
    observer_id = db(db.observers.user_email == user_email).select().first()
    if observer_id:
        observer_id = observer_id.observer_id
    else:
        observer_id = None

    sightings = db((db.sightings.sampling_event_identifier == db.checklists.sampling_event_identifier) &
                   (db.checklists.observer_id == observer_id) &
                   (db.sightings.common_name == species_name)).select(db.sightings.ALL, db.checklists.ALL)

    sightings_data = []
    for sighting in sightings:
        sightings_data.append({
            'date': sighting.checklists.observation_date,
            'count': sighting.sightings.observation_count,
            'location': (sighting.checklists.latitude, sighting.checklists.longitude)
        })
    return dict(sightings_data=sightings_data)

@action('get_trends')
@action.uses(db, auth.user)
def get_trends():
    user_email = get_user_email()
    observer_id = db(db.observers.user_email == user_email).select().first()
    if observer_id:
        observer_id = observer_id.observer_id
    else:
        observer_id = None

    sightings = db((db.sightings.sampling_event_identifier == db.checklists.sampling_event_identifier) &
                   (db.checklists.observer_id == observer_id)).select(db.sightings.ALL, db.checklists.ALL)

    trend_data = {}
    for sighting in sightings:
        date = sighting.checklists.observation_date
        if date not in trend_data:
            trend_data[date] = 0
        trend_data[date] += int(float(sighting.checklists.duration_minute))

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


## end of stats page

@action('my_callback')
@action.uses()
def my_callback():
    # The return value should be a dictionary that will be sent as JSON.
    return dict(my_value=3)

