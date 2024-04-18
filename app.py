from werkzeug.exceptions import HTTPException
from flask import Flask, render_template
from auth import protect_routes
import json

# import all blueprints (routes set by entity)
from routes.employee import employee_blueprint

# Create flask instance and save blueprints
app = Flask(__name__, static_folder="./images")

# register all blueprint
app.register_blueprint(employee_blueprint)

# Set variables to import on html
html_variables = {
    "logo": "/images/PetCare.svg",
    "exemple_url_pattern": "/images/url_pattern.png",
    "favicon": "/images/favicon.svg"
}

# Protects routes before all requests
@app.before_request
def before_request():
    return protect_routes()

# Default route - documentation
@app.route("/")
def get_documentation():
    return render_template('index.html', html_variables=html_variables)

@app.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response

# if __name__ == "__main__":
#     app.run(host='localhost', port=5500, debug=True)