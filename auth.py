import os
from flask import request, jsonify

access_token = os.getenv("API_SECRET_KEY")

def check_token(token):
    return token == access_token

def protect_routes():
    # If the auth argument is not equal then API_SECRET_KEY return a 401 error
    print('---------------')
    print(request.path)
    print('---------------')

    if not check_token(request.args.get('auth')) and not request.path == '/' and not request.path.startswith('/images'):
        return jsonify({"mensagem": "Token inválido"}), 401