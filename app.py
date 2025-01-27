from os import getenv
from flask import jsonify
from dotenv import load_dotenv
from init_app import create_app
from routes import register_blueprints
from werkzeug.exceptions import  HTTPException

load_dotenv("./.env")

env_mode = getenv('CONFIG_MODE')
app = create_app(env_mode)

@app.errorhandler(HTTPException)
def handle_http_exception(ex):
    http_code = ex.code if ex.code is not None else 500
    response = jsonify({
        "success": False,
        "code": http_code,
        "error": ex.name,
        "message": ex.description,
    })
    response.status_code = http_code
    return response

# Root URL: Hello world
@app.route("/")
def hello_world():
    return jsonify({
        "code": 200,
        "success": True,
        "message": "Hello world 😇"
    })

# Register all blueprints
register_blueprints(app)

# ----------------------------------------------- #
if __name__ == '__main__':
    # To Run the Server in Terminal => flask run -h localhost -p 5000
    # To Run the Server with Automatic Restart When Changes Occurred => FLASK_DEBUG=1 flask run -h localhost -p 4004
    app.run(debug=True, port=4004, host="localhost", load_dotenv=True)
