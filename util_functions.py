import re
import jwt
from os import getenv, remove
from flask import abort
from uuid import uuid4
from typing import List, Dict
from dotenv import load_dotenv
from imagekitio import ImageKit
from datetime import datetime, timedelta
from bcrypt import gensalt, hashpw, checkpw
from imagekitio.models.results.UploadFileResult import UploadFileResult
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions

load_dotenv("./.env")

def upload_file_to_imagekit(
        file_path: str,
        delete_after_upload: bool = True,
        folder_name: str = 'uploads'
) -> str:

    """
    Uploads a file to ImageKit and optionally deletes it locally after upload.

    :param file_path: Path to the file to be uploaded
    :param delete_after_upload: Whether to delete the file after uploading
    :param folder_name: Folder name in ImageKit where the file will be stored
    :return: The URL of the uploaded file
    """
    # Initialize ImageKit client
    imagekit = ImageKit(
        private_key=getenv('IMAGE_KIT_PRIVATE_KEY'),
        public_key=getenv("IMAGE_KIT_PUBLIC_KEY"),
        url_endpoint=getenv("IMAGE_KIT_ENDPOINT"),
    )

    # Extract file extension
    file_extension = file_path.split('.').pop()

    # Generate a unique file name
    file_name = f"{uuid4()}.{file_extension}"
    url = f"{folder_name}/{file_name}"

    # Read the file content
    # try:
    #     with open(file_path, 'rb') as file:
    #         file_data = file.read()
    # except FileNotFoundError as e:
    #     abort(404, f"File not found: {file_path}")

    # Upload the file to ImageKit
    try:
        upload_result: UploadFileResult = imagekit.upload_file(
            file=url,
            file_name=file_name,
            options=UploadFileRequestOptions(
                response_fields=["is_private_file", "tags"],
                tags=["tag1", "tag2"]
            )
        )
    except Exception as ex:
        abort(500, f"ImageKit upload failed: {ex}")

    # Delete the local file if required
    if delete_after_upload:
        try:
            remove(file_path)
        except OSError as ex:
            raise Exception(f"Error deleting file: {file_path}") from ex
    # Return the URL of the uploaded file
    return upload_result.url




def extract_request_body(request) -> dict:
    request_form: dict = {}
    if request.content_type.startswith('multipart/form-data'):
        request_form = request.form.to_dict()
    else:
        request_form = request.get_json()

    return request_form

def validate_uuid(uuid_string: str) -> bool:
    # /^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$/;
    reg_exp = r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
    return bool(re.match(reg_exp, uuid_string))

def validate_uuid_field(uuid_string: str, field_name="uuid") -> None:
    if not validate_uuid(uuid_string):
        abort(400, f"Field {field_name} has invalid uuid format")

def validate_url(uuid_string: str) -> bool:
    # /https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)/g;
    reg_exp = r'^/https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
    return bool(re.match(reg_exp, uuid_string))

def validate_url_field(url_string: str, field_name="url") -> None:
    if not validate_url(url_string):
        abort(400, f"Field {field_name} has invalid url format")

def validate_email(email: str) -> bool:
    reg_exp = r'^[a-zA-Z0-9.!#$%&\'*+\/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$'
    return bool(re.match(reg_exp, email))

def validate_email_field(email: str, field_name="email") -> None:
    if not validate_email(email):
        abort(400, f'Field {field_name} has invalid format')

def decode_jwt_token(encoded_token: str, secret_key: str) -> dict:
    # Decode the JWT
    return jwt.decode(encoded_token, secret_key, algorithms=['HS256'])

def generate_jwt_token(payload: dict, secret_key: str) -> str:
    # Encode the JWT
    return jwt.encode(
        payload={ "profile": payload, "exp": datetime.utcnow() + timedelta(hours=24)},
        key=secret_key,
        algorithm="HS256"
    )

def hash_password(password: str) -> str:
    try:
        pw_hash = hashpw(password.encode('utf8'), gensalt())
        return pw_hash.decode('utf8')
    except Exception as ex:
        print(f"An error occurred: {ex}")
        raise Exception(ex)

def check_password(plain_password: str, hashed_password: str) -> bool:
    # Compare the plain password with the hashed password
    try:
        # Hashing in bcrypt includes the salt, so we can use `checkpw`
        is_valid = checkpw(plain_password.encode('utf8'), hashed_password.encode('utf8'))
        return is_valid
    except Exception as ex:
        print(f"An error occurred: {ex}")
        return False

def validate_runtime_string(runtime_string: str, field = "runtime") -> None:
    reg_exp = r'^(\d+h )?\d+m$'
    is_valid = bool(re.match(reg_exp, runtime_string))
    if not is_valid:
        abort(400, f"Fild {field} should match format '2h 45m'")

def check_for_required_fields(required_fields: List[str], request_payload: Dict) -> None:
    missing_fields = [
        field for field in required_fields
        if field not in request_payload or request_payload.get(field) == ''
    ]
    if missing_fields:
        abort(400, f"Missing required field(s): '{', '.join(missing_fields)}'")