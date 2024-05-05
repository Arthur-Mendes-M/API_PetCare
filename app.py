from werkzeug.exceptions import HTTPException
from flask import Flask, render_template, jsonify, make_response
from utils.auth import protect_routes
import json

# import all blueprints (routes set by entity)
from routes.employee import employee_blueprint
from routes.product import product_blueprint
from routes.client import client_blueprint
from routes.sale import sale_blueprint

# Create flask instance and save blueprints
app = Flask(__name__, static_folder="./images")

# register all blueprint
app.register_blueprint(employee_blueprint)
app.register_blueprint(product_blueprint)
app.register_blueprint(client_blueprint)
app.register_blueprint(sale_blueprint)

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

@app.errorhandler(Exception)
def handle_all_exceptions(error):
    return make_response(
        jsonify({
            'error': str(error)
        }),
        500
    )

# Default route - documentation
@app.route("/")
def get_documentation():
    return render_template('index.html', html_variables=html_variables)

@app.errorhandler(HTTPException)
def handle_exception(error):
    response = error.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": error.code,
        "name": error.name,
        "description": error.description,
    })
    response.content_type = "application/json"
    return response

if __name__ == "__main__":
    app.run(host='localhost', port=5500, debug=True)