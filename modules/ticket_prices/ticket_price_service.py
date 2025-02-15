from init_app import db
from flask import request, jsonify, abort
from entities.ticket_price_entity import TicketPrice
from util_functions import extract_request_body, check_for_required_fields

def set_ticket_price(current_user):
    request_form = extract_request_body(request)
    check_for_required_fields(["price"], request_form)
    price = float(request_form["price"])
    if price <= 0:
        abort(400, "Price must be > zero")

    # Bulk update: Method 1
    TicketPrice.query.filter_by(is_active = True).update({ "is_active": False })
    db.session.commit()

    # Bulk update: Method 2
    # previous_ticket_prices = TicketPrice.query.filter_by(TicketPrice.is_active == True).all()
    # for ticket_price in previous_ticket_prices:
    #     ticket_price.is_active = False
    #
    # # Commit the changes
    # db.session.commit()

    new_ticket_price = TicketPrice(price=price, user_id=current_user["id"])
    db.session.add(new_ticket_price)
    db.session.commit()

    newly_created_ticket_price = TicketPrice.query.get(new_ticket_price.id).toDict()
    return jsonify({
        "success": True,
        "code": 201,
        "message": "New ticket price added",
        "data": newly_created_ticket_price
    })

def find_current_ticket_price():
    ticket_price = TicketPrice.query.filter_by(is_active = True).first()
    if not ticket_price:
        abort(404, "No active ticket price has been set")
    return jsonify({
        "success": True,
        "code": 200,
        "message": "Record found",
        "data": ticket_price.toDict()
    })