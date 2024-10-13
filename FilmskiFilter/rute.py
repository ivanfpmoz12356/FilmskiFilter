import uuid
import datetime
import functools
from flask import (
    Blueprint,
    render_template,
    session, 
    redirect, 
    request,
    current_app,
    url_for,
    abort,
    flash
)
from dataclasses import asdict
from FilmskiFilter.forme import MovieForm, ExtendedMovieForm, RegisterForm, LoginForm, SearchForm
from FilmskiFilter.modeli import Movie, User
from passlib.hash import pbkdf2_sha256
from sqlalchemy import or_
from pymongo import TEXT
from flask import jsonify

pages = Blueprint(
    "pages", __name__, template_folder="templates", static_folder="static"
)


def login_required(route):
    @functools.wraps(route)
    def route_wrapper(*args, **kwargs):
        if session.get("email") is None:
            return redirect(url_for(".login"))
        
        return route(*args, **kwargs)
    return route_wrapper

@pages.route("/")
def root():
   return redirect(url_for('pages.pocetna'))

@pages.route("/pocetna")
def pocetna():
   return render_template(
        "pocetna.html",
        title="Pocetna Stranica",
    )


@pages.route("/index")
@login_required
def index():
    user_data = current_app.db.user.find_one({"email": session["email"]})
    user = User(**user_data)
    movie_data = current_app.db.movie.find({"user_id": user._id})
    movies = [Movie(**movie) for movie in movie_data]
    return render_template(
        "index.html",
        title="FilmskiFilter",
        movies_data=movies
    )




@pages.route("/search", methods=["GET"])
@login_required
def search():
    q = request.args.get("q")
    print(f"Search query: {q}")

    if q:
        try:
            year_query = int(q)
            results_cursor = current_app.db.movie.find(
                {"user_id": session["user_id"], "year": year_query}
            ).sort([("year", -1)]).limit(100)

           
            results = list(results_cursor)
            print(f"Search results: {results}")
        except ValueError:
            regex_query = {"$regex": q, "$options": "i"}
            results_cursor = current_app.db.movie.find(
                {
                    "user_id": session["user_id"],
                    "$or": [
                        {"title": regex_query},
                        {"director": regex_query},
                        {"year": regex_query}
                    ]
                }
            ).sort([("year", -1)]).limit(100)

            results = list(results_cursor)
            print(f"Rezultati pretrage: {results}")
    else:
        results = []

    return render_template("rezultati_pretrage.html", search_results=results)


@pages.route("/register", methods=["GET", "POST"])
def register():
    if session.get("email"):
        return redirect(url_for(".index"))
    
    form = RegisterForm()

    if form.validate_on_submit():
        user = User(
            _id=uuid.uuid4().hex,
            email=form.email.data,
            password=pbkdf2_sha256.hash(form.password.data),
        )
        current_app.db.user.insert_one(asdict(user))

        flash("Korisnik registriran uspješno!", "success")

        return redirect(url_for(".login"))

    return render_template("register.html", title="FilmskiFilter - Registracija", form = form)


@pages.route("/login", methods=["GET", "POST"])
def login():
    if session.get("email"):
        return redirect(url_for(".index"))

    form = LoginForm()

    if form.validate_on_submit():
        
        user_data = current_app.db.user.find_one({"email": form.email.data})

        if user_data:
            user = User(**user_data)

            if pbkdf2_sha256.verify(form.password.data, user.password):
                session["user_id"] = user._id
                session["email"] = user.email

                return redirect(url_for(".index"))
            else:
                flash("Podaci za prijavu nisu točni", category="danger")
        else:
            flash("Podaci za prijavu nisu točni", category="danger")

    return render_template("login.html", title="FilmskiFilter - Prijava", form=form)




@pages.route("/logout")
def logout():

    current_theme = session.get("theme")
    session.clear()
    session["theme"] = current_theme

    return redirect(url_for(".login"))


@pages.route("/add", methods=["GET", "POST"])
@login_required
def add_movie():
    form = MovieForm()

    if form.validate_on_submit():
        movie = Movie(
            _id=uuid.uuid4().hex,
            user_id=session["user_id"],
            title=form.title.data,
            director=form.director.data,
            year=form.year.data
        )

        print(f"User ID adding movie: {session['user_id']}") 

        current_app.db.movie.insert_one(asdict(movie))
        current_app.db.user.update_one(
            {"_id": session["user_id"]},
            {"$push": {"movies": movie._id}}
        )

        return redirect(url_for(".index"))

    return render_template( 
        "novi_film.html",
        title="FilmskiFilter - Dodaj Film",
        form=form
    )



@pages.route("/edit/<string:_id>", methods=["GET", "POST"])
@login_required
def edit_movie(_id:str):
    movie = Movie(**current_app.db.movie.find_one({"_id":_id}))
    form = ExtendedMovieForm(obj=movie)
    if form.validate_on_submit():
        movie.cast = form.cast.data
        movie.series = form.series.data
        movie.tags = form.tags.data
        movie.director = form.director.data
        movie.video_link = form.video_link.data
        movie.title = form.title.data
        movie.description = form.description.data
        movie.year = form.year.data
        
        current_app.db.movie.update_one(
            {"_id":movie._id},
            {"$set": asdict(movie)}
            )
        return redirect(url_for(".movie", _id=movie._id))
    return render_template("film_form.html", movie=movie, form=form)



@pages.route("/delete/<string:_id>", methods=["DELETE"])
@login_required
def delete(_id):
    try:
        current_app.db.movie.delete_one({"_id": _id})
        return jsonify({"message": "Movie deleted successfully", "redirect": url_for("pages.index")})
    except:
        return jsonify({"error": "Error deleting movie"}), 500


@pages.get("/movie/<string:_id>")
def movie(_id:str):
    movie_data = current_app.db.movie.find_one({"_id":_id})
    if not movie_data:
        abort(404)
    movie = Movie(**movie_data)
    return render_template("film_detalji.html", movie=movie)


@pages.get("/movie/<string:_id>/rate")
@login_required
def rate_movie(_id):
    rating = int(request.args.get("rating"))
    current_app.db.movie.update_one({"_id":_id}, {"$set": {"rating": rating}})

    return redirect(url_for(".movie", _id=_id))

@pages.get("/movie/<string:_id>/watch") 
@login_required
def watch_today(_id):
    current_app.db.movie.update_one(
        {"_id":_id}, 
        {"$set": {"last_watched": datetime.datetime.today()}})
    
    return redirect(url_for(".movie", _id=_id))

@pages.get("/toggle-theme")
def toggle_theme():
    current_theme = session.get("theme")
    if current_theme == "dark":
        session["theme"] = "light"
    else:
        session["theme"] = "dark"

    return redirect(request.args.get("current_page"))
