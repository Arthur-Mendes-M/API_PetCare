from flask import Flask, render_template
from auth import protect_routes

# Import blueprints
from routes.employee import employee_blueprint

# Create flask instance and save blueprints
app = Flask(__name__)
app.register_blueprint(employee_blueprint)

# Default route - documentation
@app.route("/")
def get_documentation():
    return render_template('index.html')

# Protects routes before all requests
@app.before_request
def before_request():
    return protect_routes()

if __name__ == "__main__":
    app.run(host='localhost', port=5500, debug=True)