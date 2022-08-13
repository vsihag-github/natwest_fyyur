from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
from datetime import date

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

  # Name must be similar as defined in view(show_venue.html)
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    website = db.Column(db.String(200))
    shows = db.relationship('Show',backref='venue',lazy=True)  #Foregin key ref relation with Master table
    genres = db.Column(db.ARRAY(db.String()))  
    # past_show = db.relationship('Shows',backref='venue',lazy=True)

    def __repr__(self):
        return f'<VenueID:{self.id} || Venue_Name: {self.name}>'

class Artist(db.Model):
    __tablename__ = 'Artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    shows = db.relationship('Show',backref='artist',lazy=True)  #Foregin key ref relation with Master table

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    
    # get column names from show_artist.html
    # genre = db.Column(db.String(120))
    website = db.Column(db.String(200)) 
    seeking_venue = db.Column(db.Boolean,nullable=False, default=False)
    seeking_description = db.Column(db.String()) 
    
    def __repr__(self):
        return f'<ArtistID:{self.id} || Artist_Name: {self.name}>'



# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
    __tablename__ = 'Shows'
    id = db.Column(db.Integer, primary_key=True)  
    start_time = db.Column(db.DateTime)  
    # foregin key with Venu class
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    # foreign key with Artist
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    updated_datetime = db.Column(db.DateTime, default=date.today())
    
    def __repr__(self):
        return f'<ShowID:{self.id} || Show_Start: {self.start_time}>'
