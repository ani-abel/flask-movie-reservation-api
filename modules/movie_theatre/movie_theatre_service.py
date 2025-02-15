from init_app import db
from sqlalchemy import Date
from datetime import datetime
from sqlalchemy.sql import cast
from sqlalchemy.orm import joinedload
from entities.movie_entity import Movie
from flask import request, jsonify, abort
from entities.theatre_entity import Theatre

from entities.movie_theatre_entity import MovieTheatre
from util_functions import extract_request_body, check_movie_duration, check_for_required_fields, validate_uuid_field, \
    validate_past_date, time_frame_check, extract_request_query_params


def assign_movie_to_theatre(current_user):
    request_form = extract_request_body(request)
    # Validate data
    check_for_required_fields(["theatre_id", "viewing_date", "movie_id", "is_active", "start_time", "end_time"], request_form)
    validate_uuid_field(request_form["movie_id"], "movie_id")
    validate_uuid_field(request_form["theatre_id"], "theatre_id")
    validate_past_date(request_form["viewing_date"], "viewing_date")

    # Extract request_body params
    start_time = request_form["start_time"]
    end_time = request_form["end_time"]
    movie_id = request_form["movie_id"]
    theatre_id = request_form["theatre_id"]
    is_active = request_form["is_active"]
    viewing_date_input = datetime.strptime(request_form["viewing_date"], "%m/%d/%Y").date()

    movie_record = Movie.query.filter(Movie.id == movie_id).first()
    if not movie_record:
        abort(404, f"Movie record with id: {movie_id} was not found")

    theatre_record = Theatre.query.filter(Theatre.id == theatre_id).first()
    if not theatre_record:
        abort(404, f"Theatre record with id: {theatre_id} was not found")

    movie_check_details = check_movie_duration(start_time, end_time, movie_record.runtime)
    if not movie_check_details[1]:
        error_message = f"Timeframe is only: [{movie_check_details[0]}] Movie runtime exceeds the time window set for viewing"
        abort(400, error_message)

    # Limit theatre schedules to just those from the same day
    theatre_times = MovieTheatre.query.filter(
        cast(MovieTheatre.viewing_date, Date) == viewing_date_input,
        MovieTheatre.theatre_id == theatre_id,
        MovieTheatre.is_active == True,
    ).all()
    formatted_times: list[dict] = []
    for theatre_time in theatre_times:
        time_in_dict_format = theatre_time.toDict()
        formatted_times.append({
            "start_time": time_in_dict_format["start_time"],
            "end_time": time_in_dict_format["end_time"],
        })

    time_overlap = time_frame_check(formatted_times, { "start_time": start_time, "end_time": end_time })
    if time_overlap["has_overlap"]:
        error_message = f"Viewing time for movie: '{movie_record.title} - [{movie_record.runtime}]' clashes with another movie by '{time_overlap["total_overlap_minutes"]} minutes'"
        abort(400, error_message)

    new_assignment = MovieTheatre(start_time=start_time, end_time=end_time, viewing_date=viewing_date_input, theatre_id=theatre_id, is_active=is_active, movie_id=movie_id)
    db.session.add(new_assignment)
    db.session.commit()

    newly_created_assignment = MovieTheatre.query.get(new_assignment.id).toDict()
    return jsonify({
        "success": True,
        "code": 201,
        "message": "Movie assignment made",
        "data": newly_created_assignment
    })

def view_time_movie_slots_today():
    # today = datetime.today().date()
    request_form = extract_request_query_params(request)
    print(request_form)
    start_date = datetime.strptime(request_form["start_date"], "%m/%d/%Y").date()
    end_date = datetime.strptime(request_form["end_date"], "%m/%d/%Y").date()
    records = (MovieTheatre.query
                .options(joinedload(MovieTheatre.movie))
                .options(joinedload(MovieTheatre.theatre))
                # .join(Movie, Movie.id == MovieTheatre.movie_id)
                # .join(Theatre, Theatre.id == MovieTheatre.theatre_id)
                .filter(MovieTheatre.viewing_date.between(start_date, end_date))
                .all())

    records_dict: list[dict] = []
    for record in records:
        result = MovieTheatre.toDict(record, ['movie', 'theatre'])
        records_dict.append(result)

    return jsonify({
        "success": True,
        "code": 200,
        "message": "Records found",
        "data": records_dict
    })
