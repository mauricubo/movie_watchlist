import datetime
import uuid
from flask import (
    abort,
    Blueprint, current_app, 
    redirect, render_template, 
    request, session, 
    url_for
)
from dataclasses import asdict
from movie_library.forms import MovieForm
from movie_library.models import Movie

pages = Blueprint(
    "pages", __name__, template_folder="templates", static_folder="static"
)

@pages.route("/")
def index():
    movie_data = current_app.db.movie.find({})
    movies = [Movie(**movie) for movie in movie_data]
    return render_template(
        "index.html",
        title="Movies Watchlist",
        movies_data = movies
    )

@pages.route("/add", methods=["GET", "POST"])
def add_movie():
    form = MovieForm()
    
    if form.validate_on_submit():
        movie = Movie(
            _id = uuid.uuid4().hex,
            title = form.title.data,
            director = form.director.data,
            year = form.year.data
        )

        current_app.db.movie.insert_one(asdict(movie))

        return redirect(url_for("pages.movie", _id=movie._id))

    return render_template(
        "new_movie.html",
        title="Movies Watchlist - Add Movie",
        form=form
    )

@pages.get("/movie/<string:_id>")
def movie(_id: str):
    movie_data = current_app.db.movie.find_one({ "_id": _id })
    if not movie_data:
        abort(404)
    movie = Movie(**movie_data)
    return render_template("movie_details.html", movie=movie)


@pages.get("/movie/<string:_id>/rate")
def rate_movie(_id):
    rating = int(request.args.get("rating"))
    current_app.db.movie.update_one({"_id": _id}, {"$set": { "rating": rating }})

    return redirect(url_for("pages.movie", _id=_id))

@pages.get("/movie/<string:_id>/watch")
def watch_today(_id):
    current_app.db.movie.update_one(
        {"_id": _id}, 
        {"$set": {"last_watched": datetime.datetime.today()}}
    )

    return redirect(url_for("pages.movie", _id=_id))

@pages.get("/toggle-theme")
def toggle_theme():
    current_theme = session.get("theme")
    session["theme"] = "light" if current_theme == "dark" else "dark"

    return redirect(request.args.get("current_page"))