#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from distutils.command.config import config
import json
import sys
import dateutil.parser
import babel
from flask import Flask, render_template,jsonify, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import json

#----------------------------------------------------------------------------#
# App Config.

#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# TODO: connect to a local postgresql database




#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120),nullable=False)
    state = db.Column(db.String(120),nullable=False)
    address = db.Column(db.String(120),nullable=False)
    phone = db.Column(db.String(120),nullable=False)
    image_link = db.Column(db.String(500),nullable=False)
    facebook_link = db.Column(db.String(),nullable=False)
    seeking_talent = db.Column(db.Boolean, default=False)
    genres = db.Column(db.String(),nullable=False)
    website_link = db.Column(db.String(),nullable=False)
    seeking_description = db.Column(db.String(),nullable=True)
    relations = db.relationship('Show', backref='venue', lazy=True)

    def __repr__(self):
        return f'<Venue {self.id} {self.name} {self.city} {self.state}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate-- done

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(),nullable = False)
    image_link = db.Column(db.String(),nullable = False)
    facebook_link = db.Column(db.String(),nullable=False)
    website_link = db.Column(db.String(),nullable=False)
    seeking_description = db.Column(db.String(),nullable = False)
    seeking_venue = db.Column(db.Boolean, default=False)
    relations = db.relationship('Show', backref='artist', lazy=True)

class Show(db.Model):
  __tablename__ = 'Show'

  id = db.Column(db.Integer, primary_key=True)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
  start_time = db.Column(db.DateTime())
 

       
   

    # TODO: implement any missing fields, as a database migration using Flask-Migrate -- done

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

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
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data. -- done
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue
  data = []
  venues = Venue.query.distinct(Venue.city).all()
  for venue in venues:
    data.append({
      'city': venue.city,
      'state' : venue.state,
      'venues': []

    })
  
  all_venues = Venue.query.all()
  for venue in all_venues:
    for single in data:
      if single['city'] == venue.city:
        single['venues'].append({
          'id': venue.id,
          'name': venue.name,
        })
        upcoming_shows_list = []
        all_shows_at_venues = Show.query.filter_by(venue_id=venue.id).all()
        for item in all_shows_at_venues:
          if item.start_time > datetime.now():
            upcoming_shows_list.append({
              'artist_id': item.artist_id,
            })
        single['venues'][-1]['num_upcoming_shows'] = len(upcoming_shows_list)
  
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee" --done
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  response = {}
  search_term = request.form.get('search_term', '')
  venues = Venue.query.filter(Venue.name.ilike('%'+ search_term + '%')).all()
  response['count'] = len(venues)
  response['data'] = []
  for venue in venues:
    response['data'].append({
      'id': venue.id,
      'name': venue.name,
      'num_upcoming_shows': len(Show.query.filter(Show.venue_id == venue.id and Show.start_time > datetime.now()).all())
    })
  print(response)


  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id -- done
  # TODO: replace with real venue data from the venues table, using venue_id -- done
  try:
    data = []
    venue_results = Venue.query.get(venue_id);
    data.append({
      'id': venue_id,
      'name': venue_results.name,
      'genres': venue_results.genres.split(','),
      'address': venue_results.address,
      'city': venue_results.city,
      'state': venue_results.state,
      'phone': venue_results.phone,
      'website_link': venue_results.website_link,
      'facebook_link': venue_results.facebook_link,
      'seeking_talent': venue_results.seeking_talent,
      'seeking_description': venue_results.seeking_description,
      'image_link': venue_results.image_link,
      'past_shows': [],
      'upcoming_shows': [],
    })
  # retrive all the shows at that venue for past and upcoming show
    def past_shows_fxn(venue_id):
      shows_query = db.session.query(Show).join(Artist).filter(Show.venue_id == venue_id)
      for shows in shows_query:
       if shows.start_time < datetime.now():
            data[0]['past_shows'].append({
              'artist_id': shows.artist_id,
              'artist_name': Artist.query.get(shows.artist_id).name,
              'artist_image_link': Artist.query.get(shows.artist_id).image_link,
              'start_time': shows.start_time.strftime('%Y-%m-%d %H:%M:%S')
            })
       else:
          data[0]['upcoming_shows'].append({
            'artist_id': shows.artist_id,
            'artist_name': Artist.query.get(shows.artist_id).name,
            'artist_image_link': Artist.query.get(shows.artist_id).image_link,
            'start_time': shows.start_time.strftime('%Y-%m-%d %H:%M:%S')
          })
          data[0]['upcoming_shows_count'] = len(data[0]['upcoming_shows'])
          data[0]['past_shows_count'] = len(data[0]['past_shows'])
    past_shows_fxn(venue_id)
  except:
    print(sys.exc_info())
  finally:
     data = list(filter(lambda d: d['id'] == venue_id, data))[0]
     print(data)
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  # -- 
  try:
    print(request.form)
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    def genres():
      genre = ''
      data = request.form.getlist('genres')
      for t in data:
        genre += t + ','
      print(genre)
      return genre
    genres = genres()
    image_link = request.form['image_link']
    website_link = request.form['website_link']
    facebook_link = request.form['facebook_link']
    def seeking():
      if request.form.get('seeking_talent') == 'y':
        return True
      else:
        return False
    seeking_talent = seeking()
    seeking_description = request.form.get('seeking_description')
    venue = Venue(name=name, city=city, state=state, address=address, phone=phone, genres=genres, facebook_link=facebook_link, image_link=image_link, website_link=website_link, seeking_talent=seeking_talent, seeking_description=seeking_description)
    db.session.add(venue)
    db.session.commit()
      # on successful db insert, flash success
    flash('Venue ' + name + ' was successfully listed!')
  except:
    name = request.form.get('name')
    db.session.rollback()
    print(sys.exc_info())
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Venue ' + name + ' could not be listed.')
  finally:
    db.session.close()
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>/delete', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using --done
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    venue = Venue.query.with_entities(Venue.name).filter_by(id=venue_id).first()
    # query shows table to find all the shows at that venue_id
    show = Show.query.filter_by(venue_id=venue_id).all()
    #if shows have such venue first delete them to prevent break in the app
    # if no shows, delete the venue from the db.venues table and flash the success message
    if len(show) == 0:
      Venue.query.filter_by(id=venue_id).delete()
      db.session.commit()
      # on successful db insert, flash success
      flash('Venue ' + venue.name + ' was successfully deleted!')
    if len(show) > 0:
      Show.query.filter_by(venue_id=venue_id).delete()
      Venue.query.filter_by(id=venue_id).delete()
      db.session.commit()
    # flash success note to the frontend
    flash('Venue ' + venue.name + ' was successfully deleted!')
  except: 
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Venue ' + venue.name + ' could not be deleted.')
  finally:
    db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  # Note we gonna use fetch method in the frontend , hence the redirect to homepage is not necessary
  #  We will return a success message to the frontend
  # return render_template('pages/home.html')
  return {'success': True}

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database --done
  needed_fields =[Artist.id,Artist.name]

  data = Artist.query.with_entities(*needed_fields)
 
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  #--done
  response = {}
  try:
    # get the query string from  the request
    query_string = request.form.get('search_term')
    # get the data from the db
    data = Artist.query.filter(Artist.name.ilike('%' + query_string + '%')).all()
    # get the data in the needed format
    response['count'] = len(data)
    response['data'] = []
    for d in data:
      response.get('data').append({'id':d.id, 'name':d.name})
      # determine the number of upcoming shows for each artist
      shows = Show.query.filter(Show.artist_id == d.id).all()
      # if returned shows are not empty, shows for artist is obviously 0
      if len(shows) == 0:
        response.get('data')[-1]['num_upcoming_shows'] = 0
      else:
        for show in shows:
         count = 0
         if show.start_time > datetime.now():
          count += 1
          response.get('data')[-1]['num_upcoming_shows'] = count
  except:
     print(sys.exc_info())
  finally:
    db.session.close()
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


  


  
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id --done
  artist_information = Artist.query.get(artist_id)
  data = {}
  data['id'] = artist_information.id
  data['name'] = artist_information.name
  data['city'] = artist_information.city
  data['state'] = artist_information.state
  data['phone'] = artist_information.phone
  data['genres'] = artist_information.genres.split(',')
  data['website_link'] = artist_information.website_link
  data['facebook_link'] = artist_information.facebook_link
  data['seeking_venue'] = artist_information.seeking_venue
  data['seeking_description'] = artist_information.seeking_description
  data['image_link'] = artist_information.image_link
  data['past_shows'] = []
  data['upcoming_shows'] = []
  query_show_for_shows = Show.query.filter_by(artist_id=artist_id).all()
  for allshows in query_show_for_shows:
    if allshows.start_time > datetime.now():
      data['upcoming_shows'].append({
        "venue_id": allshows.venue_id,
        "venue_name": allshows.venue.name,
        "venue_image_link": allshows.venue.image_link,
        "start_time": str(allshows.start_time)
      })
    else:
      data['past_shows'].append({
        "venue_id": allshows.venue_id,
        "venue_name": allshows.venue.name,
        "venue_image_link": allshows.venue.image_link,
        "start_time": str(allshows.start_time)
      })
  data['past_shows_count'] = len(data['past_shows'])
  data['upcoming_shows_count'] = len(data['upcoming_shows'])

  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # TODO: populate form with fields from artist with ID <artist_id> --done
  artist = Artist.query.get(artist_id)
  form = ArtistForm(obj=artist)
   # we gonna populate the form with the data of the artist we are editing
  
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    # get the data with the artist_id we are editing
    artist = Artist.query.get(artist_id)
    artist.name = request.form.get('name')
    artist.city = request.form.get('city')
    artist.state = request.form.get('state')
    artist.phone = request.form.get('phone')
    artist.genres = request.form.get('genres')
    artist.website_link = request.form.get('website_link')
    def genres():
      genre = ''
      data = request.form.getlist('genres')
      for t in data:
        genre += t + ','
      return genre
    artist.genres = genres()
    artist.facebook_link = request.form.get('facebook_link')
    artist.seeking_description = request.form.get('seeking_description')
    artist.image_link = request.form.get('image_link')
    def seeking_venue():
      if request.form.get('seeking_venue') == 'y':
        return True
      else:
        return False
    artist.seeking_venue = seeking_venue()
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully updated!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  form = VenueForm(obj=venue)
  # TODO: populate form with values from venue with ID <venue_id> -- done partial
  venue = Venue.query.get(venue_id)
  print(venue)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try:
    edit_current_venue = Venue.query.get(venue_id)
    edit_current_venue.name = request.form['name']
    edit_current_venue.city = request.form['city']
    edit_current_venue.state = request.form['state']
    edit_current_venue.phone = request.form['phone']
    edit_current_venue.address = request.form['address']
    # this function would loop through the genres and concantenate them into a string for 
    # 
    def genres():
      genre = ''
      data = request.form.getlist('genres')
      for t in data:
        genre += t + ','
      return genre
    edit_current_venue.genres =  genres()
    
    edit_current_venue.facebook_link = request.form['facebook_link']
    edit_current_venue.image_link = request.form['image_link']
    edit_current_venue.website_link = request.form['website_link']
    def seekvalues():
      if request.form['seeking_talent'] == 'y':
        return True
      else:
        return False
    edit_current_venue.seeking_talent = seekvalues()
    edit_current_venue.seeking_description = request.form['seeking_description']
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully updated!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
  finally:
    db.session.close()

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
  # TODO: insert form data as a new Venue record in the db, instead --done
  # TODO: modify data to be the data object returned from db insertion --done
  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    def get_genres():
      genre = ''
      data = request.form.getlist('genres')
      for t in data:
        genre += t + ','
      return genre
    genres = get_genres()
    facebook_link = request.form['facebook_link']
    image_link = request.form['image_link']
    website_link = request.form['website_link']
    def seeking_venue():
      if request.form['seeking_venue'] == 'y':
        return True
      else:
        return False
    seeking_venue = seeking_venue()
    seeking_description = request.form['seeking_description']
    artist = Artist(name=name, city=city, state=state, phone=phone, genres=genres, facebook_link=facebook_link, image_link=image_link, website_link=website_link, seeking_venue=seeking_venue, seeking_description=seeking_description)
    db.session.add(artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    artist_name = request.form['name']
    db.session.rollback()
    print(sys.exc_info())
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Artist ' + artist_name + ' could not be listed.')
  finally:
   return render_template('pages/home.html')


# shows the recently linked shows at the homepage

@app.route('/recently-listed-artist' , methods=['GET'])
def recently_linked_shows():
  # get the most recent shows from the database
  data = []
  recent_shows = Artist.query.order_by(Artist.id.desc()).limit(10)
  for all in recent_shows:
    data.append({
      "artist_id": all.id,
      "artist_name": all.name,
      "artist_image_link": all.image_link,
      "upcoming_shows": len(Show.query.filter_by(artist_id = all.id).filter(Show.start_time > datetime.now()).all()),
    })
  return jsonify(data)


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data. -- done
  allshows = Show.query.all()

  data = []

  for show in allshows:
    # get artist_id,venue_id
    current_artist_id = show.artist_id
    current_venue_id = show.venue_id
    # retrieve artist and venue data using their ids
    artist_id_info = Artist.query.get(current_artist_id)
    venue_id_info = Venue.query.get(current_venue_id)
    # append the required data into the data list

    data.append({
      "venue_id": venue_id_info.id,
      "venue_name": venue_id_info.name,
      "artist_id": artist_id_info.id,
      "artist_name": artist_id_info.name,
      "artist_image_link": artist_id_info.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S') 
    })
    # create a view using the data from the model 
    
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead --done
  try:
    data = request.form
    artist_id = data['artist_id']
    venue_id = data['venue_id']
    start_date = data['start_time']
    shows = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_date)
    db.session.add(shows)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    # TODO: on unsuccessful db insert, flash an error instead. -- done
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
  
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
