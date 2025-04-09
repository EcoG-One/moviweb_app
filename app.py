import os
from flask import Flask, render_template, request, redirect, url_for
from models import db, User
import requests
from dotenv import load_dotenv
from datamanager.sqlite_data_manager import SQLiteDataManager

load_dotenv()
API_KEY = os.getenv("OMDB_API_KEY")
OMDB_URL = "http://www.omdbapi.com/"

app = Flask(__name__)

db_path = os.path.join(os.getcwd(), "data", "movies.sqlite")
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
try:
    db.init_app(app)
except Exception as e:
    print("An Error occurred: ", str(e))
    render_template("index.html")

data_manager = SQLiteDataManager(app, db)

@app.route("/")
def index():
    """ Render the home page """
    try:
        users = data_manager.get_all_users()
        return render_template('index.html', users=users)
    except Exception as e:
        return "An error occurred", 500


@app.route('/users')
def list_users():
    """ Display a list of all users  registered in app"""
    try:
        users = data_manager.get_all_users()
        return render_template('users.html', users=users)
    except Exception as e:
        return "An error occurred", 500


@app.route('/users/<user_id>')
def user_movies(user_id):
    """ Show a user's list of favorite movies """
    try:
        user = data_manager.get_user(user_id)
        if not user:
            return "User not found", 404

        movies = data_manager.get_user_movies(user_id)
        return render_template('user_movies.html', user=user, movies=movies)

    except Exception as e:
        return "An unexpected error occurred", 500



@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    """
    Presents a form that enables the addition of a new user to the App
    """
    try:
        if request.method == 'POST':
            username = request.form.get('username')
            if not username:
                return "Username is required!", 400

            # Generate avatar URL from initials
            avatar_url = f"https://ui-avatars.com/api/?name={username}&background=random&color=fff&size=128&rounded=true"

            # Create user with avatar
            new_user = User(name=username, avatar=avatar_url)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('list_users'))

        return render_template('add_user.html')

    except Exception as e:
        return "An unexpected error occurred", 500


@app.route('/users/<int:user_id>/add_movie', methods=['GET', 'POST'])
def add_movie(user_id):
    """Displays a form to add a new movie to a user’s list
        of favorite movies.
    """
    try:
        user = data_manager.get_user(user_id)
        if not user:
            return "User not found", 404

        if request.method == 'POST':
            title = request.form.get('title')
            if not title:
                return "Movie title is required!", 400
            movies_list = data_manager.get_user_movies(user_id)
            for movie in movies_list:
                if title == movie.title:
                    return render_template('add_movie.html', message="Movie already in your favorites.<br>Please try another.",
                                       user_id=user_id), 400
            raw_data = fetch_movie_data(title)
            if not raw_data or "Error" in raw_data:
                error_message = raw_data.get("Error", "Movie not found. Check the title and try again.")
                return render_template('add_movie.html', message=error_message, user_id=user_id), 400

            movie_data = extract_movie_data(raw_data)

            success = data_manager.add_movie(
                user_id,
                movie_data["Title"],
                movie_data["Director"],
                movie_data["Year"],
                movie_data["Rating"],
                movie_data["Poster"],
                movie_data["Genre"]
            )

            if success:
                return redirect(url_for('user_movies', user_id=user_id))
            else:
                return "Error adding movie", 500

        return render_template('add_movie.html', user=user)

    except Exception as e:
        return "An unexpected error occurred", 500


@app.route('/users/<user_id>/update_movie/<movie_id>', methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    """
    Displays a form allowing for the updating of details
    of a specific movie in a user’s list.
    """
    try:
        user = data_manager.get_user(user_id)
        if not user:
            return "User not found", 404

        movie = data_manager.get_movie(movie_id)
        if not movie or movie not in user.movies:
            return "Movie not found", 404

        if request.method == 'POST':
            title = request.form.get('title')
            director = request.form.get('director')
            year = request.form.get('year')
            rating = request.form.get('rating')

            if not title or not director or not year or not rating:
                return "All fields are required!", 400

            data_manager.update_movie(movie_id, title, director, year, rating)
            return redirect(url_for('user_movies', user_id=user_id))

        return render_template('update_movie.html', user=user, movie=movie)

    except Exception as e:
        return "An unexpected error occurred", 500


@app.route('/users/<user_id>/delete_movie/<movie_id>', methods=['POST'])
def delete_movie(user_id, movie_id):
    """
    Deletes a movie from a user's collection
    """
    try:
        user = data_manager.get_user(user_id)
        if not user:
            return "User not found", 404

        movie = data_manager.get_movie(movie_id)
        if not movie or movie not in user.movies:
            return "Movie not found", 404

        data_manager.delete_movie(movie_id)
        return redirect(url_for("user_movies", user_id=user_id))

    except Exception as e:
        return "An unexpected error occurred", 500


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return "Something went wrong on our end. We're on it!", 500


def fetch_movie_data(title):
    """ Fetch movie data from the OMDb API by title """
    try:
        url = f"{OMDB_URL}?apikey={API_KEY}&t={title}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            if data.get("Response") == "True":
                return data
            else:
                return {"Error": data.get("Error", "Movie not found!")}

        return {"Error": f"Request failed with status code {response.status_code}"}

    except Exception as e:
        return None


def extract_movie_data(raw_data):
    """ Extracts relevant fields from raw OMDb data """
    try:
        title = raw_data.get("Title", "N/A")
        director = raw_data.get("Director", "N/A")
        year = raw_data.get("Year", "N/A")
        if len(year) > 4:
            year = year[:4]
        rating = raw_data.get("imdbRating", "N/A")
        if rating == "N/A":
            rating = -1
        genre = raw_data.get("Genre", "N/A")
        poster = raw_data.get("Poster", "N/A")

        return {"Title": title, "Director": director, "Year": year, "Rating": rating, "Genre":genre, "Poster": poster}

    except Exception as e:
        return {"Error": str(e)}


if __name__ == "__main__":
    print("Running Flask App...")
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)

