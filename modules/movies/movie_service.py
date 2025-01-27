from init_app import db
from flask import request, jsonify, abort
from entities.movie_entity import Movie
from util_functions import extract_request_body, validate_uuid_field, validate_runtime_string, validate_url_field, check_for_required_fields

# Add pagination
def find_movies():
    movies = Movie.query.all()
    result = []
    for movie in movies: result.append(movie.toDict())
    return jsonify({
        "success": True,
        "code": 200,
        "message": "Records found",
        "data": result,
    })

def find_movie_by_id(movie_id: str):
    validate_uuid_field(movie_id, "movie_id")
    record = Movie.query.filter(Movie.id == movie_id).first()
    if not record:
        abort(404, "Movie not found")
    return jsonify({
        "success": True,
        "code": 200,
        "message": "Record found",
        "data": record
    })

def update_movie(current_user, movie_id: str):
    request_form = extract_request_body(request)
    movie_record = Movie.query.get(movie_id)
    if not movie_record or movie_record is None:
        abort(404, "Movie was not found")

    if current_user["user_id"] != movie_record["userId"]:
        abort(409, "You cannot update a movie you never added")

    # note_group_id = request_form["note_group_id"] if request_form["note_group_id"] else None

    if request_form["title"] is not None and movie_record["title"] != request_form["title"]:
        movie_record["title"] = request_form["title"]

    if request_form["synopsis"] is not None and movie_record["synopsis"] != request_form["synopsis"]:
        movie_record["synopsis"] = request_form["synopsis"]

    if request_form["promotional_image"] is not None and movie_record["promotional_image"] != request_form["promotional_image"]:
        validate_url_field(request_form["promotional_image"], 'promotional_image')
        movie_record["promotional_image"] = request_form["promotional_image"]

    if request_form["runtime"] is not None and movie_record["runtime"] != request_form["runtime"]:
        validate_runtime_string(request_form["runtime"], 'runtime')
        movie_record["runtime"] = request_form["runtime"]

    db.session.commit()
    result = Movie.query.get(movie_id).toDict()
    return jsonify({
        "success": True,
        "code": 200,
        "message": "Updated",
        "data": result,
    })

def delete_movie(movie_id: str):
    validate_uuid_field(movie_id, "movie_id")
    movie_record = Movie.query.get(movie_id)
    if not movie_record:
        abort(404, "Movie not found")

    Movie.query.delete(id=movie_id).delete()
    db.session.commit()

    return jsonify({
        "success": True,
        "code": 200,
        "message": f"Movie with id '{movie_id}' deleted successfully"
    })

def create_movie(current_user):
    request_form = extract_request_body(request)
    check_for_required_fields(["title", "synopsis", "promotional_image"], request_form)
    admin_user_id = current_user["user_id"]
    title = str(request_form["title"]).lower()
    synopsis = request_form["synopsis"]
    promotional_image = request_form["promotional_image"]
    # validate runtime string to match format 2h 50m
    runtime = request_form["runtime"]
    validate_runtime_string(runtime)
    validate_url_field(promotional_image, 'promotional_image')

    existing_movie = Movie.query.filter(Movie.title == title).first()
    if existing_movie:
        abort(409, "Similar movie already exists")

    new_movie = Movie(title=title, synopsis=synopsis, promotional_image=promotional_image, user_id=admin_user_id, runtime=runtime)
    db.session.add(new_movie)
    db.session.commit()

    new_movie_record = Movie.query.get(new_movie.id).toDict()
    return jsonify({
        "success": True,
        "code": 201,
        "message": "Created",
        "data": new_movie_record
    })
