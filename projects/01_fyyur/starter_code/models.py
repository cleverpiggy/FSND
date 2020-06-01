from db import db
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False, default='')
    facebook_link = db.Column(db.String(120), nullable=False, default='')
    website = db.Column(db.String(120), nullable=False, default='')
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(240), nullable=False, default='')

    #without a venue there is no show, thus 'delete-orphan'
    shows = db.relationship('Show', backref='venue', lazy=True, cascade='all, delete-orphan')

    #comma joined string
    genres = db.Column(db.String(120), nullable=False, default='')

    def __repr__(self):
        return f'<Venue :: {self.id} : {self.name} : {self.city}>'


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False, default='')
    facebook_link = db.Column(db.String(120), nullable=False, default='')
    website = db.Column(db.String(120), nullable=False, default='')
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(240), nullable=False, default='')

    #without an artist there is no show, thus 'delete-orphan'
    shows = db.relationship('Show', backref='artist', lazy=True, cascade='all, delete-orphan')

    #comma joined string
    genres = db.Column(db.String(120), nullable=False, default='')

    def __repr__(self):
        return f'<Artist :: {self.id} : {self.name} : {self.city}>'


class Show(db.Model):
    __tablename__ = 'show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    start_time = db.Column(db.DateTime(), nullable=False)

    def __repr__(self):
        return f'<Show :: {self.id} : venue {self.venue_id} : artist {self.artist_id} : {self.start_time}>'
