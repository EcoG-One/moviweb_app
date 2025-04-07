from abc import ABC, abstractmethod

class DataManagerInterface(ABC):
    """
    Abstract base class defining the interface for data management.
    """
    def __init__(self):
        pass

    def __str__(self):
        return "Data Manager Interface"

    def __repr__(self):
        return "Data Manager Interface"

    @abstractmethod
    def get_all_users(self):
        """ Retrieve all users from the database """
        pass

    @abstractmethod
    def get_user_movies(self, user_id):
        """ Retrieve all movies associated with a given user """
        pass

    @abstractmethod
    def add_movie(self, user_id, title, director, year, rating, genre, poster):
        """ Add a movie to a user's collection """
        pass

    @abstractmethod
    def update_movie(self, movie_id, title, director, year, rating):
        """ Update details of a movie in the database """
        pass

    @abstractmethod
    def delete_movie(self, movie_id):
        """ Remove a movie from the database """
        pass

    @abstractmethod
    def get_user(self, user_id):
        """ Retrieve a user by their ID """
        pass

    @abstractmethod
    def get_movie(self, movie_id):
        """ Retrieve a movie by its ID """
        pass