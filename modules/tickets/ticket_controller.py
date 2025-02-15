from flask import Blueprint
from middlewares.middleware import token_required
from modules.tickets.ticket_service import verify_theatre_space, buy_movie_ticket

ticket_blueprint_api = Blueprint("ticket_routes", __name__)

@ticket_blueprint_api.route("/buy-movie-ticket", methods=["POST"])
@token_required
def controller_buy_movie_ticket(current_user):
    print(f"{current_user}")
    return buy_movie_ticket(current_user)

@ticket_blueprint_api.route("/verify-theatre-space", methods=["GET"])
@token_required
def controller_verify_theatre_space(current_user):
    print(f"{current_user}")
    return verify_theatre_space()