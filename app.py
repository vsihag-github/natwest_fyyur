#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from dataclasses import dataclass
from difflib import diff_bytes
from distutils.command.config import config
from email.policy import default
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging,sys
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_migrate import Migrate
from datetime import date
from forms import *
from model import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

# TODO: connect to a local postgresql database
db.init_app(app)
migrate = Migrate(app,db)

app.config["CACHE_TYPE"] = "null"

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
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  data =[]  #emtpty existint data dictionary
  #refer view Venues.html for argument to be passed
  #get distinct state and city
  distinct_statecity = Venue.query.with_entities(Venue.state,Venue.city).distinct()

  for dsc in distinct_statecity:
      s_state = dsc.state
      c_city = dsc.city
      v_venue =[]  # for adding list venues in data[] dictionary
      venue_filter  = Venue.query.filter_by(state=s_state,city=c_city).all()
      for v in venue_filter:
        #though count is not displayed in all Venues form
        count_upcoming_show = Show.query.filter_by(venue_id=v.id).filter(Show.start_time > datetime.now() ).count() 
        v_venue.append({
          "id":v.id,
          "name": v.name,
          "num_upcoming_shows": count_upcoming_show
        })

      # append venue details with upcoming show to final data
      data.append({
        "city":c_city,
        "state":s_state,
        "venues":v_venue
      })

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  data_venue=[]  # to get venue list temporary and later will add to response data
  response_data=[]
  search  = "%{}%".format(search_term)
  #if using filter use db.users.name object
  s_venue = Venue.query.filter(Venue.name.like(search)).all()
  
  for v in s_venue:
    data_venue.append({ 
      "id" : v.id,
      "name" :v.name,
      "num_upcoming_shows": Show.query.filter(Show.venue_id==v.id).filter(Show.start_time > datetime.now() ).count()
    })
    
  response_data.append({
    'count': len(s_venue),
    'data' : data_venue
  })
 

  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  #}
  return render_template('pages/search_venues.html', results=response_data[0], search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
    # get venue by primary_key
  v_venue = Venue.query.get(venue_id)
  
  #declare blank datadic
  data1 =[]
  d_past_shows=[]
  d_upcom_shows =[]
   
  #get past shows and upcoming shows filter by venue_id and current date
  #p_shows = Show.query.filter_by(venue_id=venue_id).filter(Show.start_time <= datetime.now() ).all()
  #p_shows = Show.query.filter_by(venue_id=venue_id).filter(Show.start_time > datetime.now() ).all()

  #get show and artist detaisl with joining both tabels
  all_shows = db.session.query(Artist,Show.start_time).join(Show).filter(Show.venue_id == venue_id) #(Artist, Show.start_time).join(Show).filter(Show.venue_id == venue_id)

  for artist,start_time in all_shows:
     #add to list of upcoming shows
      if start_time > datetime.now():
        d_upcom_shows.append({
        "artist_id": artist.id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": str(start_time)
        })          
      else:
        #add to list of past shows
        d_past_shows.append({
        "artist_id": artist.id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": str(start_time)
        })

  data1 =({
    "id": venue_id,
    "name": v_venue.name, 
    "genres": v_venue.genres,
    "address":v_venue.address ,
    "city": v_venue.city,
    "state": v_venue.state,
    "phone": v_venue.phone,
    "website": v_venue.website,
    "facebook_link": v_venue.facebook_link,
    "seeking_talent": v_venue.seeking_talent,
    "seeking_description": v_venue.seeking_description,
    "image_link": v_venue.image_link,
    "past_shows":d_past_shows,
    "upcoming_shows": d_upcom_shows,
    "past_shows_count": len(d_past_shows),
    "upcoming_shows_count":len(d_upcom_shows) ,

  })

  return render_template('pages/show_venue.html', venue=data1)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  form = VenueForm(request.form, meta={'csrf': False})
  # TODO: modify data to be the data object returned from db insertion
  # to display in error block
  name = form.name.data 
  error = False
  
  try:
      if form.validate_on_submit():
        venue = Venue(  #instatiate Class object   
          #id : Primary key
          name = name,
          city = form.city.data,
          state = form.state.data,
          address = form.address.data,
          phone = form.phone.data,
          image_link = form.image_link.data,
          facebook_link = form.facebook_link.data,
          website = form.website_link.data,  
          seeking_talent = form.seeking_talent.data,
          seeking_description = form.seeking_description.data,
          genres = form.genres.data,
          )
        db.session.add(venue)
        db.session.commit()
      else:
            raise Exception('Form validation failed')
  except Exception as e:
        print('create_venue_submission: ', e)
        db.session.rollback()
        print(sys.exc_info())
        message = []
        for field, err in form.errors.items():
          message.append(field + ' ' + '|'.join(err))
        error = True
  finally:  
      db.session.close()
  
    #error = True
    #message = []
    #for field, err in form.errors.items():
     #   message.append(field + ' ' + '|'.join(err))
  
  if error :
    flash('An error occurred. Venue ' + name + ' could not be listed: Error '+str(message))
    return render_template('forms/new_venue.html', form=form)
  else:
     flash('Venue ' + request.form['name'] + ' was successfully listed!')
     return render_template('pages/home.html')

  # on successful db insert, flash success
  # flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):

  # TODO: Complete this endpoint for taking a venue_id, and using
  venue = Venue.query.get(venue_id)  # get venue to be deleted
  error = False
   # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    db.session.delete(venue)
    db.session.commt()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  
  if error:
    flash('Could not delete venue due to some error' + venue.name)
  else:
    flash('Successfully removed venue ' + venue.name)

  return redirect(url_for('venues'))

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  data = Artist.query.with_entities(Artist.id,Artist.name).all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')
  data_artists= []  # to get venue list temporary and later will add to response data
  response_data=[]
  search  = "%{}%".format(search_term)
  #if using filter use db.users.name object
  s_artist = Artist.query.filter(Artist.name.like(search)).all()
  
  for art in s_artist:
    data_artists.append({
      "id" : art.id,
      "name" :art.name,
      "num_upcoming_shows": Show.query.filter(Artist.id==art.id).filter(Show.start_time > datetime.now() ).count()
    })
    
  response_data.append({
    'count': len(s_artist),
    'data' : data_artists
  })
 

  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  #}
  return render_template('pages/search_artists.html', results=response_data[0], search_term=request.form.get('search_term', ''))

  

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id

  a_artist = Artist.query.get(artist_id)
  #declare blank datadic
  data1 =[]
  d_past_shows=[]
  d_upcom_shows =[]

 
  #get past shows and upcoming shows filter by venue_id and current date
  #p_shows = Show.query.filter_by(artist_id=artist_id).filter(Show.start_time <= datetime.now() ).all()
  #up_shows = Show.query.filter_by(artist_id=artist_id).filter(Show.start_time > datetime.now() ).all()

 #get show and artist detaisl with joining both tabels
  all_shows = db.session.query(Venue,Show.start_time).join(Show).filter(Show.artist_id == artist_id) #(Artist, Show.start_time).join(Show).filter(Show.venue_id == venue_id)

  for venue, start_time in all_shows:
      #add to list
      if start_time > datetime.now():
        d_upcom_shows.append({
        "venue_id": venue.id,
        "venue_name": venue.name,
        "venue_image_link": venue.image_link,
        "start_time": str(start_time)
        })
      else:
        d_past_shows.append({
        "venue_id": venue.id,
        "venue_name": venue.name,
        "venue_image_link": venue.image_link,
        "start_time": str(start_time)
  })

  
  

  data1={
    "id": artist_id,
    "name": a_artist.name,
    "genres": a_artist.genres, ## convert to comma seprated values
    "city": a_artist.city,
    "state": a_artist.state,
    "phone": a_artist.phone,
    "website":a_artist.website,
    "facebook_link": a_artist.facebook_link,
    "seeking_venue": a_artist.seeking_venue,
    "seeking_description": a_artist.seeking_description,
    "image_link": a_artist.image_link,
    "past_shows":d_past_shows ,
    "upcoming_shows": d_upcom_shows,
    "past_shows_count": len(d_past_shows),
    "upcoming_shows_count": len(d_upcom_shows),
  }  
  return render_template('pages/show_artist.html', artist=data1)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  #get Artist by primary key
  data_artist = Artist.query.get(artist_id)
 
  data_artist.website_link=data_artist.website #mismatch between form and database columns. 
  # assign form fields pass object
  form = ArtistForm(obj=data_artist)
  artist={
    "id": artist_id,
    "name": data_artist.name,
    "genres": data_artist.genres,
    "city": data_artist.city,
    "state": data_artist.state,
    "phone": data_artist.phone,
    "website_link":data_artist.website,
    "facebook_link": data_artist.facebook_link,
    "seeking_venue": data_artist.seeking_venue,
    "seeking_description": data_artist.seeking_description,
    "image_link": data_artist.image_link,
  }
  
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error = False
  form = ArtistForm()
  a_artist = Artist.query.get(artist_id)
  try:
    # start to edit the data after take them from the form
      a_artist.name=form.name.data
      a_artist.genres=form.genres.data
      a_artist.city=form.city.data
      a_artist.state=form.state.data
      a_artist.phone=form.phone.data
      a_artist.image_link=form.image_link.data
      a_artist.facebook_link=form.facebook_link.data
      a_artist.seeking_venue=form.seeking_venue.data
      a_artist.seeking_description=form.seeking_description.data
      a_artist.website=form.website_link.data
      
      db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
        db.session.close()
  if error: 
     # in case of error
    flash('Some error encountered. Artist could not be updated')
  else: 
    # if success
    flash('Successfully updated Artist' + form.name.data)
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  data_venue = Venue.query.get(venue_id)
  data_venue.website_link=data_venue.website # tosync formname and db returned columns names
    
    # assign form fields pass object
  form = VenueForm(obj=data_venue)
  venue={
    "id": venue_id,
    "name": data_venue.name,
    "genres": data_venue.genres,
    "address":  data_venue.address,
    "city":  data_venue.city,
    "state": data_venue.state,
    "phone":  data_venue.phone,
    "website_link":  data_venue.website,
    "facebook_link":  data_venue.facebook_link,
    "seeking_talent":  data_venue.seeking_talent,
    "seeking_description":  data_venue.seeking_description,
    "image_link": data_venue.image_link,
    }

   # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  error = False
  errordesc =''
  form = VenueForm()
  a_venue = Venue.query.get(venue_id)
  try:
      # start to edit the data after take them from the form
        a_venue.name=form.name.data
        a_venue.genres=form.genres.data
        a_venue.city=form.city.data
        a_venue.state=form.state.data
        a_venue.phone=form.phone.data
        a_venue.image_link=form.image_link.data
        a_venue.facebook_link=form.facebook_link.data
        a_venue.seeking_talent=form.seeking_talent.data
        a_venue.seeking_description=form.seeking_description.data
        a_venue.website=form.website_link.data
        
        db.session.commit()
  except Exception as err:
      error = True
      errordesc = f"{err.__class__.__name__}: {err}"
      db.session.rollback()
  finally:
          db.session.close()
  if error: 
      # in case of error
      flash('Some error encountered. Venue could not be updated' + errordesc)
  else: 
      # if success
      flash('Successfully updated Venue' + form.name.data)


  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  form = ArtistForm()
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  name = form.name.data # to print in case of error
  error = False
  try:
    #instatiate Class object
      if form.validate_on_submit():
          artist = Artist(
              #id : Primary key
              name = name,
              city = form.city.data,
              state = form.state.data,        
              phone = form.phone.data,
              image_link = form.image_link.data,
              facebook_link = form.facebook_link.data,
              website = form.website_link.data,  
              seeking_venue = form.seeking_venue.data,
              seeking_description = form.seeking_description.data,
              genres = form.genres.data,
              )
          db.session.add(artist)
          db.session.commit()
      else:
          raise Exception('Form validation failed')
  except Exception as e:
        print('create_venue_submission: ', e)
        db.session.rollback()
        print(sys.exc_info())
        message = []
        for field, err in form.errors.items():
          message.append(field + ' ' + '|'.join(err))
        error = True
  finally:  
      db.session.close()
  
  if error :
    flash('An error occurred. Venue ' + name + ' could not be listed: Error '+str(message))
    return render_template('forms/new_artist.html', form=form)
  else:
     flash('Venue ' + request.form['name'] + ' was successfully listed!')
     return render_template('pages/home.html')
  # on successful db insert, flash success
  # flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data =[]
  all_shows = Show.query.all()
  
  for s in all_shows:
    data.append({
      "venue_id":s.venue_id,
      "venue_name": Venue.query.with_entities(Venue.name).filter(Venue.id==s.venue_id).first().name,
      "artist_id": s.artist_id,
      "artist_name": Artist.query.with_entities(Artist.name).filter(Artist.id==s.artist_id).first().name,
      "artist_image_link":Artist.query.with_entities(Artist.image_link).filter(Artist.id==s.artist_id).first().image_link,
      "start_time": format_datetime(str(s.start_time))
    })

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
  form = ShowForm()
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  
  error = False
  try:
    #instatiate Class object
    show = Show(
        #id : Primary key
        venue_id = form.venue_id.data,
        artist_id = form.artist_id.data,
        start_time = form.start_time.data        
        )
    db.session.add(show)
    db.session.commit()
  except:
      error = True
      db.session.rollback()
  finally:  
    db.session.close()
  
  if error :
    flash('Some error encountered! Show was not listed!')
  else:
     flash('Show was successfully listed!')
  # on successful db insert, flash success
  # flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
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
