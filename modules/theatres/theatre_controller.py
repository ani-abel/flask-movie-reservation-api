from flask import Blueprint
from middlewares.middleware import token_required
from modules.theatres.theatre_service import create_theatre, find_theatres, find_theatre_by_id, delete_theatre, \
    update_theatre, delete_theatres

theatre_blueprint_api = Blueprint('theatre_routes', __name__)

@theatre_blueprint_api.route("/", methods=["POST"])
@token_required
def controller_create_theatre(current_user):
    print(f"current_user => {current_user}")
    return create_theatre(current_user)

@theatre_blueprint_api.route("/", methods=["GET"])
@token_required
def controller_find_theatres(current_user):
    print(f"current_user => {current_user}")
    return find_theatres()

@theatre_blueprint_api.route("/<string:theatre_id>", methods=["GET"])
@token_required
def controller_find_theatre_by_id(current_user, theatre_id: str):
    print(f"current_user => {current_user}")
    return find_theatre_by_id(theatre_id)

@theatre_blueprint_api.route("/<string:theatre_id>", methods=["DELETE"])
@token_required
def controller_delete_theatre(current_user, theatre_id: str):
    print(f"current_user => {current_user}")
    return delete_theatre(theatre_id)

@theatre_blueprint_api.route("/", methods=["DELETE"])
@token_required
def controller_delete_theatres(current_user):
    print(f"current_user => {current_user}")
    return delete_theatres()


@theatre_blueprint_api.route("/<string:theatre_id>", methods=["PATCH", "PUT"])
@token_required
def controller_update_theatre(current_user, theatre_id: str):
    print(f"current_user => {current_user}")
    return update_theatre(current_user, theatre_id)
