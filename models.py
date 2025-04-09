from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, Column, String, Float
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    """ Represents a user in the digital library """
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    avatar = Column(String(200), default="")
    movies = relationship('Movie', secondary='user_movies', backref='users')

    def __repr__(self):
        return f'User name: {self.name}'


class Movie(db.Model):
    __tablename__ = 'movies'
    """ Represents a film in the digital library """
    id = Column(Integer, primary_key=True)
    title = Column(String(100))
    director = Column(String(100))
    year = Column(Integer)
    rating = Column(Float)
    poster = Column(String(300))
    genre = Column(String(200))

    def __repr__(self):
        return f'Film {self.name} from {self.year}'

user_movies = db.Table('user_movies',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('movie_id', db.Integer, db.ForeignKey('movies.id'), primary_key=True)
)

