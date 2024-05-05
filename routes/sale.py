from flask import Blueprint, jsonify, request
from database.connection import supabase_operation, sale_table, client_table
from datetime import datetime
from pytz import timezone
from utils.valid_request_headers import verify_json_header
from werkzeug.exceptions import BadRequest

sale_blueprint = Blueprint("sales", __name__, url_prefix="/sales")

@sale_blueprint.get('/')
def get_all_products():
    return jsonify(
        supabase_operation(
            sale_table
            .select("*")
        )
    )

@sale_blueprint.get('/<id>')
def get_product_by_id(id):
    return jsonify(
        supabase_operation(
            sale_table
            .select("*")
            .eq("id", id)
        )
    )

@sale_blueprint.post('/')
def save_sale():
    # Throw an error if request is not a json
    verify_json_header(request)
    
    sale = request.json

    found_client_by_clientID = client_table.select("*").eq("id", sale['clientID']).execute().data

    if not found_client_by_clientID:
        raise BadRequest('Cliente was not found with clientID property')

    SP_timezone = timezone("America/Sao_Paulo")
    today = datetime.now().astimezone(SP_timezone)

    sale = {
        "clientID": sale['clientID'],
        "date_time": today.strftime("%F %X"),
        "payment_method": sale['payment_method'],
        "products": sale['products'],
    }
    sale["total"] = sum(product['quantity'] * product['product']['sale_price'] for product in sale['products'])
    
    sale = {key.lower(): value for key, value in sale.items()}
    return jsonify(
        supabase_operation(
            sale_table
            .insert(sale)
        )
    )

@sale_blueprint.delete('/<id>')
def delete_sale(id):
    found_sale = sale_table.select("*").eq("id", id).execute().data
    
    if not found_sale:
        raise BadRequest('Sale was not found')

    return jsonify(
        supabase_operation(
            sale_table
            .delete()
            .eq("id", id)
        )
    )