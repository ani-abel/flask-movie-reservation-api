from init_app import db
from flask import request, jsonify, abort
from entities.theatre_entity import Theatre
from util_functions import extract_request_body, validate_uuid_field, check_for_required_fields

def find_theatre_by_id(theatre_id: str):
    validate_uuid_field(theatre_id, 'theatre_id')
    record = Theatre.query.filter(Theatre.id == theatre_id).first()
    if not record:
        abort(404, "Theatre not found")
    return jsonify({
        "success": True,
        "code": 200,
        "message": "Record found",
        "data": record,
    })

# (=> Add pagination)
def find_theatres():
    theatres = Theatre.query.all()
    result = []
    for theatre in theatres: result.append(theatre.toDict())
    return jsonify({
        "success": True,
        "code": 200,
        "message": "Records found",
        "data": result
    })


# def delete_theatres(theatre_ids: list[str]):
def delete_theatres():
    """
    Deletes multiple theatre records based on their IDs.
    """
    request_form = extract_request_body(request)
    theatre_ids: list[str] = request_form["theatre_ids"]
    if not isinstance(theatre_ids, list):
        abort(400, "Invalid input. Expected a list of theatre IDs.")

    for theatre_id in theatre_ids:
        validate_uuid_field(theatre_id, "theatre_id")

    # Fetch the records to ensure they exist
    theatre_records = Theatre.query.filter(Theatre.id.in_(theatre_ids)).all()
    if not theatre_records or len(theatre_records) != len(theatre_ids):
        abort(404, "Not all theatres could be matched")

    # Delete the records
    Theatre.query.filter(Theatre.id.in_(theatre_ids)).delete(synchronize_session=False)
    db.session.commit()

    return jsonify({
        "success": True,
        "code": 200,
        "message": f"Theatres with IDs {", ".join(map(str, theatre_ids))} deleted successfully"
    })

def delete_theatre(theatre_id: str):
    validate_uuid_field(theatre_id, "theatre_id")
    theatre_record = Theatre.query.get(theatre_id)
    if not theatre_record:
        abort(404, "Theatre not found")
    Theatre.query.delete(id=theatre_id).delete()
    db.session.commit()

    return jsonify({
        "success": True,
        "code": 200,
        "message": f"Theatre with id '{theatre_id}' deleted successfully"
    })

def update_theatre(current_user, theatre_id: str):
    request_form = extract_request_body(request)
    theatre_record = Theatre.query.get(theatre_id)
    if not theatre_record or theatre_record is None:
        abort(404, "Movie was not found")

    if current_user["user_id"] != theatre_record["userId"]:
        abort(409, "You cannot update a theatre you never added")

    if request_form["location"] is not None and theatre_record["location"] != request_form["location"]:
        theatre_record["location"] = str(request_form["location"]).lower()

    if request_form["seat_count"] is not None and theatre_record["seat_count"] != request_form["seat_count"]:
        if int(request_form["seat_count"]) <= 0:
            abort(400, "Seat count for a theatre must be > 0")
        theatre_record["seat_count"] = int(request_form["seat_count"])

    if request_form["name"] is not None and theatre_record["name"] != request_form["name"]:
        theatre_record["name"] = str(request_form["name"]).lower()

    if request_form["status"]:
        theatre_record["status"] = request_form["status"]

    db.session.commit()
    result = Theatre.query(theatre_id).toDict()
    return jsonify({
        "success": True,
        "code": 200,
        "message": "Updated",
        "data": result,
    })

def create_theatre(current_user):
    request_form = extract_request_body(request)
    check_for_required_fields(["name", "location", "seat_count"], request_form)
    admin_user_id = current_user["user_id"]
    name = str(request_form["name"]).lower()
    location = str(request_form["location"]).lower()
    seat_count = int(request_form["seat_count"])

    if seat_count <= 0:
        abort(400, "Seat_count for a theatre must be > 0")

    existing_theatre = Theatre.query.filter(Theatre.name == name).first()
    if existing_theatre:
        abort(409, "Similar theatre already exists")

    new_theatre = Theatre(name=name, location=location, seat_count=seat_count, user_id=admin_user_id)
    db.session.add(new_theatre)
    db.session.commit()

    new_theatre_record = Theatre.query.get(new_theatre.id).toDict()
    return jsonify({
        "success": True,
        "code": 201,
        "message": "Created",
        "data": new_theatre_record
    })


