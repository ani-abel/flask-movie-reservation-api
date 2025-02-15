from init_app import db
from sqlalchemy.orm import joinedload
from entities.ticket_entity import Ticket
from flask import request, jsonify, abort
from entities.payment_entity import Payment
from entities.ticket_price_entity import TicketPrice
from entities.movie_theatre_entity import MovieTheatre
from util_constants import PaymentStatus
from util_functions import extract_request_body, check_for_required_fields, extract_request_query_params, \
    validate_uuid_field

def buy_movie_ticket(current_user):
    request_form = extract_request_body(request)
    check_for_required_fields(["movie_theatre_id", "number_of_tickets", "payment_id"], request_form)
    movie_theatre_id = request_form["movie_theatre_id"]
    number_of_tickets = request_form["number_of_tickets"]
    payment_id = request_form["payment_id"]
    validate_uuid_field(payment_id, "payment_id")
    validate_uuid_field(movie_theatre_id, "movie_theatre_id")

    if number_of_tickets <= 0:
        abort(400, "Field 'number_of_tickets' must be > zero")

    active_ticket_price = TicketPrice.query.filter_by(is_active = True).first()
    if not active_ticket_price:
        abort(404, "No active price has been set for tickets")

    # Verify the payment
    payment_record = Payment.query.get(payment_id)
    if not payment_record or payment_record.payment_status != PaymentStatus.SUCCESSFUL.value:
        abort(404, "Could not verify payment")

    user_id = current_user["id"]
    ticket_price_id = active_ticket_price.id

    movie_theatre_record = MovieTheatre.query.get(movie_theatre_id)
    if not movie_theatre_record:
        abort(404, "Movie showing not found for this theatre")

    # Update the number of tickets bought for future reference
    current_number_of_tickets_bought = movie_theatre_record.current_number_of_tickets_bought + number_of_tickets
    movie_theatre_record.current_number_of_tickets_bought = current_number_of_tickets_bought
    db.session.commit()

    # Find similar ticket record
    similar_ticket_purchase = Ticket.query.filter(
        Ticket.payment_id == payment_id,
        Ticket.movie_theatre_id == movie_theatre_id,
        Ticket.user_id == user_id,
        Ticket.ticket_price_id == ticket_price_id
    ).first()
    if similar_ticket_purchase:
        abort(409, "Similar request for movie tickets has already been sent")

    new_ticket = Ticket(
        user_id=user_id,
        payment_id = payment_id,
        number_bought=number_of_tickets,
        ticket_price_id=ticket_price_id,
        movie_theatre_id = movie_theatre_id,
    )
    db.session.add(new_ticket)
    db.session.commit()

    new_ticket_record = (Ticket.query
                         .options(joinedload(MovieTheatre.movie))
                         .options(joinedload(MovieTheatre.theatre))
                         .get(new_ticket.id))
    new_ticket_record_dict = Ticket.toDict(new_ticket_record, ["move_theatre", "user", "ticket_price"])
    return jsonify({
        "success": True,
        "code": 200,
        "message": f"({number_of_tickets}) tickets bought successfully",
        "data": new_ticket_record_dict,
    })

def verify_theatre_space():
    request_form = extract_request_query_params(request)
    check_for_required_fields(["movie_theatre_id", "number_of_tickets"], request_form)
    movie_theatre_id = request_form["movie_theatre_id"]
    number_of_tickets = int(request_form["number_of_tickets"])
    validate_uuid_field(movie_theatre_id, "movie_theatre_id")

    movie_theatre_record = (MovieTheatre.query
                            .options(joinedload(MovieTheatre.movie))
                            .options(joinedload(MovieTheatre.theatre))
                            .get(movie_theatre_id))
    if not movie_theatre_record:
        abort(404, "Could not find movie-theatre record")

    movie_theatre_record_dict = MovieTheatre.toDict(movie_theatre_record, ['theatre'])

    active_ticket_price = TicketPrice.query.filter_by(is_active = True).first()
    if not active_ticket_price:
        abort(404, "No active price has been set on the backend for tickets")
    sum_user_should_pay = (active_ticket_price.price * number_of_tickets)

    # Query movie_theatre table to make sure records exists, include relation for "theatre" to know it's capacity
    theatre_full_capacity = int(movie_theatre_record_dict["theatre"]["seat_count"])

    # Method 1
    # movie_tickets = Ticket.query.filter_by(MovieTheatre.movie_theatre_id == movie_theatre_id).all()
    # count_array = []
    # for ticket in movie_tickets: count_array.append(ticket.number_bought)

    # Method 2
    tickets_bought_for_movie = 0
    movie_tickets = Ticket.query.filter(Ticket.movie_theatre_id == movie_theatre_id).all()
    if len(movie_tickets) > 0:
        count_array = [ticket.number_bought for ticket in movie_tickets]
        tickets_bought_for_movie = sum(count_array)

    tickets_free = theatre_full_capacity - tickets_bought_for_movie
    if number_of_tickets > tickets_free:
        error_message = f"Not enough tickets available. Only {tickets_free} seats are left"
        abort(409, error_message)

    return jsonify({
        "success": True,
        "code": 200,
        "message": "Movie seating space verified",
        "data": {
            "has_enough_space": True,
            "remaining_seats": tickets_free,
            "pricing_for_ticket": sum_user_should_pay
        }
    })
