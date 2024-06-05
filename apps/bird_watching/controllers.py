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


url_signer = URLSigner(session)

@action('index')
@action.uses('index.html', db, auth, url_signer)
def index():
    return dict(
        my_callback_url = URL('my_callback', signer=url_signer),
    )

class GridSelectButton(object):
    def __init__(self):
        self.url = URL('select') 
        self.append_id = True
        self.additional_classes = 'button is-primary'
        self.icon = 'fa-Select'
        self.text = 'Select'
        self.message = None
        self.onClick = None

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
            post_action_buttons=[GridSelectButton()],
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



@action('select/<species_id>', method=['GET', 'POST'])
@action.uses('select.html', db, auth.user, session)
def select(species_id=None):
    user = auth.current_user
    species = db.species(species_id) or redirect(URL('checklist'))

    search_term = request.query.get('search_term', '')

    bird_data = db((db.User_bird_data.Userid == user.get('id')) & 
                   (db.User_bird_data.bird_name == species.common_name)).select().first()

    if not bird_data:
        bird_data_id = db.User_bird_data.insert(
            Userid=user.get('id'),
            bird_name=species.common_name,
            bird_count=0
        )
        bird_data = db.User_bird_data(bird_data_id)

    if request.forms.get('increment'):
        bird_data.update_record(bird_count=bird_data.bird_count + 1)
        redirect(URL('select', species_id, vars=dict(search_term=search_term)))

    if request.forms.get('submit_record'):
        redirect(URL('checklist', vars=dict(search_term=search_term)))

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
        pre_action_buttons=[GridDeletebutton()],
        rows_per_page=100,
        fields=[
            db.User_bird_data.bird_name,
            db.User_bird_data.bird_count
        ]
    )
    return dict(grid=grid)

@action('my_callback')
@action.uses()
def my_callback():
    # The return value should be a dictionary that will be sent as JSON.
    return dict(my_value=3)

