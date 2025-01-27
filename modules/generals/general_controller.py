from flask import Blueprint
from modules.generals.general_service import file_uploads_save_on_disk, file_uploads

general_blueprint_api = Blueprint('general_routes', __name__)

@general_blueprint_api.route("/file-upload/save-on-disk", methods=["POST"])
def controller_file_uploads_save_on_disk() -> None:
    return file_uploads_save_on_disk()

@general_blueprint_api.route("/file-upload", methods=["POST"])
def controller_file_uploads() -> None:
    return file_uploads()