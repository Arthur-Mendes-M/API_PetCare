import os
from flask import request
from werkzeug.exceptions import Unauthorized

access_token = os.getenv("API_SECRET_KEY")

def check_token(token):
    return token == access_token

def protect_routes():
    # If the auth argument is not equal then API_SECRET_KEY return a 401 error
    if not check_token(request.args.get('auth')) and not request.path == '/' and not request.path.startswith('/images'):
        raise Unauthorized("Token inválido")