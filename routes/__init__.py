from modules.users import user_controller
from modules.movies import movie_controller
from modules.tickets import ticket_controller
from modules.theatres import theatre_controller
from modules.payments import payment_controller
from modules.generals import general_controller
from modules.ticket_prices import ticket_price_controller
from modules.movie_theatre import movie_theatre_controller

def register_blueprints(app):
    app.register_blueprint(user_controller.user_blueprint_api, url_prefix="/api/users")
    app.register_blueprint(movie_controller.movie_blueprint_api, url_prefix='/api/movies')
    app.register_blueprint(ticket_controller.ticket_blueprint_api, url_prefix="/api/tickets")
    app.register_blueprint(general_controller.general_blueprint_api, url_prefix='/api/general')
    app.register_blueprint(theatre_controller.theatre_blueprint_api, url_prefix="/api/theatres")
    app.register_blueprint(payment_controller.payment_blueprint_api, url_prefix="/api/payments")
    app.register_blueprint(ticket_price_controller.ticket_price_blueprint_api, url_prefix="/api/ticket-prices")
    app.register_blueprint(movie_theatre_controller.movie_theatre_blueprint_api, url_prefix="/api/theatre-assignment")