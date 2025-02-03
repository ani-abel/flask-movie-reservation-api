from flask import Blueprint
from middlewares.middleware import token_required
from modules.movie_theatre.movie_theatre_service import assign_movie_to_theatre, view_time_movie_slots_today

movie_theatre_blueprint_api = Blueprint('movie_theatre_routes', __name__)

@movie_theatre_blueprint_api.route("/assign-movie", methods=["POST"])
@token_required
def controller_assign_movie_to_theatre(current_user):
    print(f"current_user => {current_user}")
    return assign_movie_to_theatre(current_user)

@movie_theatre_blueprint_api.route("/movie-viewings-today", methods=["GET"])
def controller_view_time_movie_slots_today():
    return view_time_movie_slots_today()
