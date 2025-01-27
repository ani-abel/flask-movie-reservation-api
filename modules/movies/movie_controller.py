from flask import Blueprint
from middlewares.middleware import token_required
from modules.movies.movie_service import find_movies, find_movie_by_id, create_movie, delete_movie, update_movie

# Create a blueprint
movie_blueprint_api = Blueprint('movie_routes', __name__)

@movie_blueprint_api.route("/", methods=["POST"])
@token_required
def controller_create_movie(current_user):
    print(f"current_user => {current_user}")
    return create_movie(current_user)

@movie_blueprint_api.route("/", methods=["GET"])
@token_required
def controller_find_movies(current_user):
    print(f"current_user => {current_user}")
    return find_movies()

@movie_blueprint_api.route("/<string:movie_id>", methods=["GET"])
@token_required
def controller_find_movie_by_id(current_user, movie_id: str):
    print(f"current_user => {current_user}")
    return find_movie_by_id(movie_id)

@movie_blueprint_api.route("/<string:movie_id>", methods=["DELETE"])
@token_required
def controller_delete_movie(current_user, movie_id: str):
    print(f"current_user => {current_user}")
    return delete_movie(movie_id)

@movie_blueprint_api.route("/<string:movie_id>", methods=["PATCH", "PUT"])
@token_required
def controller_update_movie(current_user, movie_id: str):
    print(f"current_user => {current_user}")
    return update_movie(current_user, movie_id)
