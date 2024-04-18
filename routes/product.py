from flask import Blueprint, jsonify, request

product_blueprint = Blueprint("products", __name__, url_prefix="/products")