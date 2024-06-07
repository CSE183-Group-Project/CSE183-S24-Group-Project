from py4web import action, request, response, abort, redirect, URL
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated
from pydal.validators import IS_FLOAT_IN_RANGE
from py4web.utils.form import Form, FormStyleBulma
from py4web.utils.grid import Grid
from yatl.helpers import A
from .models import Field

@action('index')
@action.uses('index.html', db, session, T)
def index():
    form = Form(
        [
            Field('latitude', 'float', requires=IS_FLOAT_IN_RANGE(-90, 90)),
            Field('longitude', 'float', requires=IS_FLOAT_IN_RANGE(-180, 180)),
            Field('radius', 'float', default=1.0, requires=IS_FLOAT_IN_RANGE(0, 180)),
        ],
        formstyle=FormStyleBulma
    )

    if form.accepted:
        latitude = form.vars['latitude']
        longitude = form.vars['longitude']
        radius = form.vars['radius']

        query = (db.checklists.latitude > latitude - radius) & \
                (db.checklists.latitude < latitude + radius) & \
                (db.checklists.longitude > longitude - radius) & \
                (db.checklists.longitude < longitude + radius)

        checklists = db(query).select()

        results = []
        for checklist in checklists:
            sightings = db(db.sightings.sampling_event_identifier == checklist.sampling_event_identifier).select()
            for sighting in sightings:
                species = db(db.species.common_name == sighting.common_name).select().first()
                results.append({
                    'common_name': species.common_name,
                    'count': sighting.observation_count,
                    'latitude': checklist.latitude,
                    'longitude': checklist.longitude,
                    'date': checklist.observation_date,
                    'time': checklist.time_observation
                })

        grid = Grid(results, show_header=True)
    else:
        grid = None

    return dict(form=form, grid=grid)
