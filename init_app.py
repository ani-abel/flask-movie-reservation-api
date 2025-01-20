from flask import Flask
from config import config
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_mode):
    app = Flask(__name__)

    app.config.from_object(config[config_mode])

    db.init_app(app)
    migrate.init_app(app, db)

    # Import your models here and run db connection here
    with app.app_context():
        from entities.user_entity import User
        from entities.movie_entity import Movie
        from entities.ticket_entity import Ticket
        from entities.theatre_entity import Theatre
        from entities.payment_entity import Payment
        from entities.ticket_price_entity import TicketPrice
        from entities.movie_theatre_entity import MovieTheatre

        db.create_all()  # Optional, only if not using migrations

    return app

# ----------------------------------------------- #

# Migrate Commands:
# flask db init
# flask db migrate
# flask db upgrade
# ERROR [flask_migrate] Error: Can't locate revision identified by 'ID' => flask db revision --rev-id ID
