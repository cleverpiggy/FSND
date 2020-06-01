#This module works by calling register_view_funcs(app) in the
#app.py file.

import sys
from flask import render_template, request, flash, redirect, url_for
from sqlalchemy import func
from datetime import datetime

from forms import ArtistForm, VenueForm, ShowForm
from models import Venue, Artist, Show
from db import db


#We'll populate this with tuples of (viewfunc, urlrule, kwargs)
_views = []

#The point of the following is to avoid importing the app object
#from app.py resulting in a circular import.
#The view functions will not be accessable (and don't need to be),
#only used through register_view_funcs

def route(rule, **kwargs):
  def inner(view_func):
    _views.append((rule, view_func, kwargs))
  return inner

def register_view_funcs(app):
  for rule, view_func, kwargs in _views:
    app.add_url_rule(rule, view_func=view_func, **kwargs)

#----------------------------------------------------------------------------#
# Helpers.
#----------------------------------------------------------------------------#

def dictify(row):
    """Return a python dict"""
    if hasattr(row, '__table__'):
        d = {col.name: getattr(row, col.name) for col in row.__table__.columns}
    elif hasattr(row, 'keys'):
        d = {key: getattr(row, key) for key in row.keys()}
    else:
        raise TypeError("Expected query result type, got {}".format(type(row)))
    return d


def search_response(search_term, model):
  """
  Return response data of the correct form for artist and venue search pages.
  response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }
  """
  response = {"count": 0, "data":[]}
  if search_term:
    now = datetime.now()
    future_shows = db.session.query(Show).\
                              filter(Show.start_time > now).\
                              subquery()
    data = db.session.query(model.id,
                            model.name,
                            func.count(future_shows.c.start_time).label('num_upcoming_shows')).\
                      filter(model.name.ilike(f'%{search_term}%')).\
                      outerjoin(future_shows).\
                      group_by(model.id)
    response["count"] = data.count()
    response["data"] = data.all()
  return response


def create_submission(model):
  modelname = model.__tablename__.upper()
  seeking_label = {Venue: 'seeking_talent', Artist: 'seeking_venue'}[model]
  error = False
  try:
    #necessary because request.form may have multiple key/values
    #for genres
    genres = request.form.getlist('genres')
    genres = ','.join(genres)
    fields = dict(request.form)
    fields.pop('genres')
    fields[seeking_label] = bool(fields.get(seeking_label))
    submission = model(genres=genres, **fields)
    db.session.add(submission)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash(f'An error occurred {modelname} {request.form.get("name", "")} could not be listed.')
  else:
    flash(f'{modelname} {request.form.get("name", "")} was successfully listed!')


def delete(model, id_):
  modelname = model.__tablename__.upper()
  error = False
  try:
    item = model.query.get(id_)
    name = item.name
    db.session.delete(item)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash(f'An error occurred. {modelname} could not be deleted.')
  else:
    flash(f'{modelname} {name} was successfully deleted!')
  return ''

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#----------------------------------------------------------------

@route('/venues')
def venues():
#returns a list of venues each with .city, .state, .id, .name attrs, num_upcoming_shows
  now = datetime.now()
  future_shows = Show.query.filter(Show.start_time > now).subquery()
  query = db.session.query(
    Venue.name,
    Venue.city,
    Venue.state,
    Venue.id,
    func.count(future_shows.c.start_time).label('num')).\
                     outerjoin(future_shows).\
                     group_by(Venue.id).\
                     order_by(Venue.state, Venue.city)
  #get the data in the correct format
  areas = []
  c, s = None, None
  for name, city, state, id_, num in query.all():
    if (city, state) == (c, s):
        areas[-1]["venues"].append({"id": id_, "name": name, "num_upcoming_shows": num})
    else:
        c, s = city, state
        area = {
            "city": city,
            "state": state,
            "venues": [{"id": id_, "name": name, "num_upcoming_shows": num}]
        }
        areas.append(area)

  return render_template('pages/venues.html', areas=areas);


@route('/venues/search', methods=['POST'])
def search_venues():
  search_term=request.form.get('search_term', '')
  response = search_response(search_term, Venue)
  return render_template('pages/search_venues.html', results=response, search_term=search_term)


@route('/venues/<int:venue_id>')
def show_venue(venue_id):
  now = datetime.now()
  venue = Venue.query.get(venue_id)
  shows = db.session.query(Show.artist_id,
                           Show.start_time,
                           Artist.name.label('artist_name'),
                           Artist.image_link.label('artist_image_link')).\
                     join(Artist).\
                     filter(Show.venue_id == venue_id)

  past_shows = shows.filter(Show.start_time < now)
  upcoming_shows = shows.filter(Show.start_time > now)
  data = dictify(venue)
  data["past_shows_count"] = past_shows.count()
  data["upcoming_shows_count"] = upcoming_shows.count()
  data["past_shows"] = past_shows.all()
  data["upcoming_shows"] = upcoming_shows.all()
  data["genres"] = data["genres"].split(',')

  return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@route('/venues/create', methods=['POST'])
def create_venue_submission():
  create_submission(Venue)
  return render_template('pages/home.html')


@route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  delete(Venue, venue_id)
  return ''

#  Artists
#  ----------------------------------------------------------------

@route('/artists')
def artists():
  data = db.session.query(Artist.id, Artist.name).all()

  return render_template('pages/artists.html', artists=data)


@route('/artists/search', methods=['POST'])
def search_artists():
  search_term=request.form.get('search_term', '')
  response = search_response(search_term, Artist)
  return render_template('pages/search_artists.html', results=response, search_term=search_term)


@route('/artists/<int:artist_id>')
def show_artist(artist_id):
  now = datetime.now()
  artist = Artist.query.get(artist_id)
  shows = db.session.query(Show.venue_id,
                           Show.start_time,
                           Venue.name.label('venue_name'),
                           Venue.image_link.label('venue_image_link')).\
                     join(Venue).\
                     filter(Show.artist_id == artist_id)

  past_shows = shows.filter(Show.start_time < now)
  upcoming_shows = shows.filter(Show.start_time > now)
  data = dictify(artist)
  data["past_shows_count"] = past_shows.count()
  data["upcoming_shows_count"] = upcoming_shows.count()
  data["past_shows"] = past_shows.all()
  data["upcoming_shows"] = upcoming_shows.all()
  data["genres"] = data["genres"].split(',')

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------

@route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  row = Artist.query.get(artist_id)
  artist = dictify(row)
  artist['genres'] = artist['genres'].split(',')
  return render_template('forms/edit_artist.html', form=form, artist=artist)


@route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error = False
  try:
    artist = Artist.query.get(artist_id)
    #necessary because request.form may have multiple key/values
    #for genres
    genres = request.form.getlist('genres')
    artist.genres = ','.join(genres)
    #an unchecked box doesnt appear in reqest.form so this is necessary
    artist.seeking_venue = bool(request.form.get('seeking_venue'))
    for k, v in request.form.items():
      if k not in ('genres', 'seeking_venue'):
        setattr(artist, k, v)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash(f'An error occurred. Artist {request.form.get("name", "")} could not be updated.')
  else:
    flash(f'Artist {request.form.get("name", "")} was successfully updated.')
  return redirect(url_for('show_artist', artist_id=artist_id))


@route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  row = Venue.query.get(venue_id)
  venue = dictify(row)
  venue['genres'] = venue['genres'].split(',')
  return render_template('forms/edit_venue.html', form=form, venue=venue)


@route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False
  try:
    venue = Venue.query.get(venue_id)
    #necessary because request.form may have multiple key/values
    #for genres
    genres = request.form.getlist('genres')
    venue.genres = ','.join(genres)
    #an unchecked box doesnt appear in reqest.form so this is necessary
    venue.seeking_talent = bool(request.form.get('seeking_talent'))

    for k, v in request.form.items():
      if k not in ('genres', 'seeking_talent'):
        setattr(venue, k, v)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash(f'An error occurred. Artist {request.form.get("name", "")} could not be updated.')
  else:
    flash(f'Venue {request.form.get("name", "")} was successfully updated.')

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)


@route('/artists/create', methods=['POST'])
def create_artist_submission():
  create_submission(Artist)
  return render_template('pages/home.html')


@route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  delete(Artist, artist_id)
  return ''

#  Shows
#  ----------------------------------------------------------------

@route('/shows')
def shows():
  now = datetime.now()
  data = db.session.query(
    Show.venue_id,
    Show.artist_id,
    Show.start_time,
    Artist.name.label('artist_name'),
    Venue.name.label('venue_name'),
    Artist.image_link.label('artist_image_link')
    ).join(Artist, Venue)
  return render_template('pages/shows.html', shows=data)


@route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)


@route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  try:
    # we'll just fail and show the error if they form doesn't
    # have the correct fields
    show = Show(
      artist_id=request.form['artist_id'],
      venue_id=request.form['venue_id'],
      start_time=(datetime.fromisoformat(request.form['start_time']))
      )
    db.session.add(show)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  if error:
    flash('An error occurred. Show could not be listed.')
  else:
    flash('Show was successfully listed!')

  return render_template('pages/home.html')
