#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import os

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import *

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():

  venues = Venue.query.all()
  results = [
            {
                "name": venue.name,
                "city": venue.city,
                "phone": venue.phone,
            } for venue in venues]
  print(results)
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  venues = Venue.query.all()
  all_venues = []
  for venue in venues:
        all_venues.append({
                "city": venue.city,
                "state": venue.state,
            })
  data = []
  for venue in venues:
      if len(data) > 0:
        for distinct_venue in data:
          if distinct_venue['city'] == venue.city and distinct_venue['state'] == venue.state:
            already_exist = False
            for appended_venue in distinct_venue['venues']:
              if appended_venue['id'] == venue.id:
                already_exist = True
            if already_exist:
              pass
            else:
              distinct_venue['venues'].append({
                      "id": venue.id,
                      "name": venue.name,
                      "phone": venue.phone,
                  })
          else:

            data.append({
                "city": venue.city,
                "state": venue.state,
              'venues':[{
                "id": venue.id,
                "name": venue.name,
                "phone": venue.phone,
            }]
            })
      else:
        data.append({
                "city": venue.city,
                "state": venue.state,
                'venues':[{
                "id": venue.id,
                "name": venue.name,
                "phone": venue.phone,
            }]
            })
  # results = [
  #           {
  #               "name": venue.name,
  #               "city": venue.city,
  #               "phone": venue.phone,
  #           } for venue in venues]

  # data=[{
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "venues": [{
  #     "id": 1,
  #     "name": "The Musical Hop",
  #     "num_upcoming_shows": 0,
  #   }, {
  #     "id": 3,
  #     "name": "Park Square Live Music & Coffee",
  #     "num_upcoming_shows": 1,
  #   }]
  # }, {
  #   "city": "New York",
  #   "state": "NY",
  #   "venues": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }]
  # print(data)
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST','GET'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  response={}
  if request.method == 'POST':
    q = request.form['search_term']
    venues = Venue.query.filter(func.lower(Venue.name).contains(func.lower(q)))
    venues_list = []
    for venue in venues:
      venues_list.append(venue)
    response={
      "count": len(venues_list),
      "data": []
      }
    for venue in venues_list:
      venues_obj = {'id':venue.id,'name':venue.name}
      shows = Show.query.filter_by(venue_id=venue.id).all()
      shows_list = []
      for show in shows:
        print(show.show_time)
        shows_list.append(show)
      upcoming_shows = list(filter(lambda x:x.show_time > datetime.now(),shows_list))
      venues_obj['num_upcoming_shows'] = len(upcoming_shows)
      response['data'].append(venues_obj)
  else:
    pass

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  print(venue.genres)
  data = {
    'id':venue.id,
    'name':venue.name,
    'genres':str(venue.genres).split(','),
    'address':venue.address,
    'city':venue.city,
    'state':venue.state,
    'phone':venue.phone,
    'website':venue.website_link,
    'facebook_link':venue.facebook_link,
    'seeking_talent':venue.seeking_talent,
    'seeking_description':venue.seeking_description,
    'image_link':venue.image_link,
    'past_shows':[],
    'upcoming_shows':[],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,  
    }
  shows = Show.query.filter_by(venue_id=venue.id).all()
  shows_list = []
  for show in shows:
    shows_list.append(show)
  upcoming_shows = list(filter(lambda x:x.show_time > datetime.now(),shows_list))
  past_shows = list(filter(lambda x:x.show_time < datetime.now(),shows_list))
  data['upcoming_shows_count'] = len(upcoming_shows)
  data['past_shows_count'] = len(past_shows)
  for show in past_shows:
    artist = Artist.query.get(show.artist_id)
    past_show_obj = {
    "artist_id": show.artist_id,
    "artist_name": artist.name,
    "artist_image_link": artist.image_link,
    "start_time": str(show.show_time)
  }
    data['past_shows'].append(past_show_obj)

  for show in upcoming_shows:
    artist = Artist.query.get(show.artist_id)
    upcoming_show_obj = {
    "artist_id": show.artist_id,
    "artist_name": artist.name,
    "artist_image_link": artist.image_link,
    "start_time": str(show.show_time)
  }
    data['upcoming_shows'].append(upcoming_show_obj)


  data = data
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    if request.method == 'POST':
          
            data = request.form
            name = data['name']
            city = data['city']
            state = data['state']
            phone_number = data['phone']
            facebook_link = data['facebook_link']
            seeking_talent = data['seeking_talent']
            website_link = data['website_link']
            address =data['address']
            seeking_description = data['seeking_description']
            image_link= data['image_link']
            if seeking_talent== 'y':
              seeking_talent=1
            else:
              seeking_talent= 0
            # try:
            new_venue = Venue(name=name,address=address, city=city,state=state,phone=phone_number,seeking_description=seeking_description,
            facebook_link=facebook_link,image_link = image_link,seeking_talent=seeking_talent,website_link=website_link)
            db.session.add(new_venue)
            db.session.commit()
            print('success')
            flash('Venue ' + data['name'] + ' was successfully listed!')

            # except Exception:
            #   print(Exception)
            #   flash('An error occurred. Venue ' + data['name'] + ' could not be listed.')
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  venue = Venue.query.filter_by(id=venue_id).delete()
  db.session.commit()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect('/')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists = Artist.query.all()
  data = [
            {
                "id": artist.id,
                "name": artist.name,
                "phone": artist.phone,
            } for artist in artists]

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response={}
  if request.method == 'POST':
    q = request.form['search_term']
    artists = Artist.query.filter(func.lower(Artist.name).contains(func.lower(q)))
    artists_list = []
    for artist in artists:
      artists_list.append(artist)
    response={
      "count": len(artists_list),
      "data": []
      }
    for artist in artists_list:
      artists_obj = {'id':artist.id,'name':artist.name}
      shows = Show.query.filter_by(artist_id=artist.id).all()
      shows_list = []
      for show in shows:
        print(show.show_time)
        shows_list.append(show)
      upcoming_shows = list(filter(lambda x:x.show_time > datetime.now(),shows_list))
      artists_obj['num_upcoming_shows'] = len(upcoming_shows)
      response['data'].append(artists_obj)
  else:
    pass
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id

  artist = Artist.query.get(artist_id)
  data = {
    'id':artist.id,
    'name':artist.name,
    'genres':str(artist.genres).split(','),
    'city':artist.city,
    'state':artist.state,
    'phone':artist.phone,
    'website':artist.website_link,
    'facebook_link':artist.facebook_link,
    'seeking_venue':artist.seeking_venue,
    'seeking_description':artist.seeking_description,
    'image_link':artist.image_link,
    'past_shows':[],
    'upcoming_shows':[],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,  }


  data1={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "past_shows": [{
      "venue_id": 1,
      "venue_name": "The Musical Hop",
      "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data2={
    "id": 5,
    "name": "Matt Quevedo",
    "genres": ["Jazz"],
    "city": "New York",
    "state": "NY",
    "phone": "300-400-5000",
    "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "past_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data3={
    "id": 6,
    "name": "The Wild Sax Band",
    "genres": ["Jazz", "Classical"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "432-325-5432",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "past_shows": [],
    "upcoming_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 0,
    "upcoming_shows_count": 3,
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist_instance = Artist.query.get(artist_id)
  artist={
    "id": artist_instance.id,
    "name": artist_instance.name,
    "genres": str(artist_instance.genres).split(','),
    "city": artist_instance.city,
    "state": artist_instance.state,
    "phone": artist_instance.phone,
    "website": artist_instance.website_link,
    "facebook_link": artist_instance.facebook_link,
    "seeking_venue": artist_instance.seeking_venue,
    "seeking_description": artist_instance.seeking_description,
    "image_link": artist_instance.image_link  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist_instance = Artist.query.filter_by(id=artist_id)
  if request.method == 'POST':
    data = request.form
    genres =data.getlist('genres')
    full_genres = ''
    for genre in range(len(genres)):
      if(genre == len(genres)-1):
        full_genres+=genres[genre]
      else:
        full_genres+=genres[genre]+','
    try:
      seeking_venue = data['seeking_venue']
    except Exception:
      seeking_venue = 0
    if seeking_venue== 'y':
      seeking_venue=1
    else:
      seeking_venue= 0
    data = dict(data)
    data['seeking_venue'] = seeking_venue
    data['genres']=full_genres

    artist_instance.update(data)
    db.session.commit()
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue_instance = Venue.query.get(venue_id)
  form = VenueForm(instance=venue_instance)
  venue={
    "id": venue_instance.id,
    "name": venue_instance.name,
    "genres": str(venue_instance.genres).split(','),
    "address": venue_instance.address,
    "city": venue_instance.city,
    "state": venue_instance.state,
    "phone": venue_instance.phone,
    "website": venue_instance.website_link,
    "facebook_link": venue_instance.facebook_link,
    "seeking_talent": venue_instance.seeking_talent,
    "seeking_description": venue_instance.seeking_description,
    "image_link": venue_instance.image_link  }

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue_instance = Venue.query.filter_by(id=venue_id)
  if request.method == 'POST':
    data = request.form
    genres =data.getlist('genres')
    full_genres = ''
    for genre in range(len(genres)):
      if(genre == len(genres)-1):
        full_genres+=genres[genre]
      else:
        full_genres+=genres[genre]+','
    try:
      seeking_talent = data['seeking_talent']
    except Exception:
      seeking_talent = 0
    if seeking_talent== 'y':
      seeking_talent=1
    else:
      seeking_talent= 0
    data = dict(data)
    data['seeking_talent'] = seeking_talent
    data['genres']=full_genres

    venue_instance.update(data)
    db.session.commit()
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  if request.method == 'POST':
      try:
          data = request.form
          name = data['name']
          city = data['city']
          state = data['state']
          phone_number = data['phone']
          facebook_link = data['facebook_link']
          seeking_venue = data['seeking_venue']
          website_link = data['website_link']
          seeking_description = data['seeking_description']
          image_link= data['image_link']
          genres =data.getlist('genres')
          full_genres = ''
          for genre in range(len(genres)):
            if(genre == len(genres)-1):
              full_genres+=genres[genre]
            else:
              full_genres+=genres[genre]+','

          print(full_genres)
          if seeking_venue== 'y':
            seeking_venue=1
          else:
            seeking_venue= 0
          # try:
          new_artist = Artist(name=name,genres =full_genres, city=city,state=state,phone=phone_number,seeking_description=seeking_description,
          facebook_link=facebook_link,image_link = image_link,seeking_venue=seeking_venue,website_link=website_link)
          db.session.add(new_artist)
          db.session.commit()
          print(full_genres)
          flash('Artist ' + request.form['name'] + ' was successfully listed!')

      except Exception:
        flash('Artist was not added. Kindly check the data entered')

  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows = Show.query.all()
  data = []
  for show in shows:
    show_obj = {
    "venue_id":show.venue_id,
    "artist_id": show.artist_id,
    "start_time": str(show.show_time),
            }
    show_artist = Artist.query.get(show.artist_id)
    show_obj['artist_name'] = show_artist.name
    show_obj['artist_image_link'] = show_artist.image_link
    show_venue = Venue.query.get(show.venue_id)
    show_obj['venue_name'] = show_venue.name
    data.append(show_obj)
 
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  if request.method == 'POST':
      try:
          data = request.form
          artist_id = data['artist_id']
          venue_id = data['venue_id']
          show_time = data['start_time']
          new_show = Show(artist_id=artist_id,venue_id =venue_id, show_time=show_time,)
          db.session.add(new_show)
          db.session.commit()
          flash('Show was successfully listed!')
      except Exception:
          flash('Show was not successfully listed! Kindly check data entered')

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
