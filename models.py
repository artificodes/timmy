
from app import db



class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean,default=False,server_default ='f',nullable=False)
    website_link = db.Column(db.String(120))
    seeking_description = db.Column(db.String(500))

    def __init__(self, name,city,state,address,phone,seeking_description,facebook_link,seeking_talent,image_link,website_link):
        self.name = name
        self.city = city
        self.state = state
        self.address = address
        self.phone= phone
        self.facebook_link = facebook_link
        self.seeking_talent = seeking_talent
        self.website_link = website_link
        self.seeking_description = seeking_description
        self.image_link=image_link
    def __repr__(self):
        return f"{self.name}:{self.city}"
    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean,default=False,server_default ='f',nullable=False)
    seeking_description = db.Column(db.String(500))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    def __init__(self, name,city,state,phone,seeking_description,genres, facebook_link,seeking_venue,image_link,website_link):
        self.name = name
        self.city = city
        self.state = state
        self.phone= phone
        self.genres = genres
        self.facebook_link = facebook_link
        self.seeking_venue = seeking_venue
        self.website_link = website_link
        self.seeking_description = seeking_description
        self.image_link=image_link
    def __repr__(self):
        return f"{self.name}:{self.city}"
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    show_time = db.Column(db.DateTime, index=True, nullable=True)
    artist_id = db.Column(db.Integer,nullable=True)
    venue_id = db.Column(db.Integer,nullable=True)

    
    def __init__(self, show_time,artist_id,venue_id):
        self.show_time = show_time
        self.artist_id = artist_id
        self.venue_id = venue_id
       
    def __repr__(self):
        return f"{self.id}"