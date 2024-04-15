from flask import Flask, render_template
from auth import protect_routes

# Import blueprints
from routes.employee import employee_blueprint

# Set variables to import on html
html_variables = {
    "logo": "/images/PetCare.svg",
    "exemple_url_pattern": "/images/url_pattern.png"
}

# Create flask instance and save blueprints
app = Flask(__name__, static_folder="./images")
app.register_blueprint(employee_blueprint)

# Default route - documentation
@app.route("/")
def get_documentation():
    return render_template('index.html', html_variables=html_variables)

# Protects routes before all requests
@app.before_request
def before_request():
    return protect_routes()

# if __name__ == "__main__":
#     app.run(host='localhost', port=5500, debug=True)