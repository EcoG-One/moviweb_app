from models import User, Movie
from datamanager.data_manager_interface import DataManagerInterface

class SQLiteDataManager(DataManagerInterface):
    def __init__(self, app, database):
        """
        Initializes the database manager with a Flask app
        and database connection
        """
        self.db = database
        self.app = app

    def get_all_users(self):
        """
        Returns a list of all users or an empty list if an error occurs
        """
        try:
            users = User.query.all()
            return users
        except Exception as e:
            return []

    def get_user_movies(self, user_id):
        """
        Returns a list of movies for a given user
        or an empty list if the user doesn't exist
        """
        try:
            user = User.query.get(user_id)
            if user:
                return user.movies
            return []
        except Exception as e:
            return []

    def add_movie(self, user_id, title, director, year, rating, poster, genre):
        """
        Adds a movie to a user's list and returns True if successful,
        otherwise False
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return False

            movie = Movie(title=title, director=director, year=year,
                          rating=rating, genre=genre, poster=poster)
            user.movies.append(movie)
            self.db.session.add(movie)
            self.db.session.commit()
            return True
        except Exception as e:
            self.db.session.rollback()
            return False

    def update_movie(self, movie_id, title, director, year, rating):
        """
        Updates a movie and returns True if successful, otherwise False
        """
        try:
            movie = Movie.query.get(movie_id)
            if not movie:
                return False

            movie.title = title
            movie.director = director
            movie.year = year
            movie.rating = rating
            self.db.session.commit()
            return True
        except Exception as e:
            self.db.session.rollback()
            return False

    def delete_movie(self, movie_id):
        """
        Deletes a movie and returns True if successful, otherwise False
        """
        try:
            movie = Movie.query.get(movie_id)
            if not movie:
                return False

            self.db.session.delete(movie)
            self.db.session.commit()
            return True
        except Exception as e:
            self.db.session.rollback()
            return False

    def get_user(self, user_id):
        """
        Returns a User object by ID or None if not found
        """
        try:
            user = User.query.get(user_id)
            if user:
                return user
        except Exception as e:
            return None

    def get_movie(self, movie_id):
        """
        Returns a Movie object by ID or None if not found
        """
        try:
            movie = Movie.query.get(movie_id)
            if movie:
                return movie
        except Exception as e:
            return None

    def add_user(self, username):
        """
        Adds a new user and returns True if successful, otherwise False
        """
        try:
            new_user = User(name=username)
            self.db.session.add(new_user)
            self.db.session.commit()
            return True
        except Exception as e:
            self.db.session.rollback()
            return False