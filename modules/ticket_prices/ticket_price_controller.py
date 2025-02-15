from flask import Blueprint
from middlewares.middleware import token_required
from modules.ticket_prices.ticket_price_service import set_ticket_price, find_current_ticket_price

# Create a blueprint
ticket_price_blueprint_api = Blueprint("ticket_price_routes", __name__)

@ticket_price_blueprint_api.route("/set-official-price", methods=["POST"])
@token_required
def controller_set_ticket_prices(current_user):
    print(f"current_user => {current_user}")
    return set_ticket_price(current_user)

@ticket_price_blueprint_api.route("/official-ticket-price", methods=["GET"])
def controller_find_current_ticket_price():
    return find_current_ticket_price()