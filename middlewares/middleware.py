import time
from os import getenv
from functools import wraps
from dotenv import load_dotenv
from flask import abort, request
from util_functions import decode_jwt_token
from entities.user_entity import User

load_dotenv("../.env")

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]
        if not token:
            abort(401, "Authentication Token is missing!")
        try:
            data = decode_jwt_token(token, getenv('JWT_SECRET_KEY'))
            profile = data.get("profile")
            token_expiry_time = data.get("exp")

            # Check if the token has expired
            current_timestamp = int(time.time())  # Get current timestamp in seconds
            if token_expiry_time < current_timestamp:
                abort(401, "Authentication token has expired!")

            current_user = User.query.get(profile["user_id"]).toDict()
            if current_user is None:
                abort(401, "Invalid Authentication token!")
        except Exception as ex:
            abort(500, f"Something went wrong: {ex}")

        return f(current_user, *args, **kwargs)

    return decorated
