from flask import Blueprint
from util_constants import UserRole
from middlewares.middleware import token_required
from modules.users.user_service import login, sign_up, find_users, find_user_by_id

user_blueprint_api = Blueprint('user_routes', __name__)

@user_blueprint_api.route("/auth/sign-up", methods=["POST"])
def controller_sign_up():
    return sign_up(UserRole.CUSTOMER.value)

@user_blueprint_api.route("/auth/admin/sign-up", methods=["POST"])
def controller_admin_sign_up():
    return sign_up(UserRole.ADMIN.value)

@user_blueprint_api.route("/auth/login", methods=["POST"])
def controller_login():
    return login()

@user_blueprint_api.route("/", methods=["GET"])
@token_required
def controller_find_users(current_user):
    print(f"current_user => {current_user}")
    return find_users()

@user_blueprint_api.route("/<string:user_id>", methods=["GET"])
def controller_find_user_by_id(user_id):
    return find_user_by_id(user_id)