from flask import Blueprint, jsonify, request
from database.connection import supabase_operation, sale_table, client_table
import json
from routes.product import update_product, get_product_by_id

from datetime import datetime
from pytz import timezone
from utils.valid_request_headers import verify_json_header
from werkzeug.exceptions import BadRequest

sale_blueprint = Blueprint("sales", __name__, url_prefix="/sales")

@sale_blueprint.get('/')
def get_all_sales():
    return jsonify(
        supabase_operation(
            sale_table
            .select("*")
        )
    )

@sale_blueprint.get('/<id>')
def get_sale_by_id(id):
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

    found_client_by_client_id = client_table.select("*").eq("id", sale['client_id']).execute().data

    if not found_client_by_client_id:
        raise BadRequest('Client was not found with client_id property')

    SP_timezone = timezone("America/Sao_Paulo")
    today = datetime.now().astimezone(SP_timezone)

    sale = {
        "client_id": sale['client_id'],
        "date_time": today.strftime("%F %X"),
        "payment_method": sale['payment_method'],
        "products": sale['products'],
    }

    products = []

    # Verify if some product don't have stock
    for info in sale['products']:
        product_by_id = get_product_by_id(info['product_id']).get_data(True)
        product_dic = json.loads(product_by_id)

        current_product = product_dic[0]
        products.append(current_product)

        if current_product['quantity_in_stock'] - info['quantity'] < 0:
            raise BadRequest('Wrong quantities on sold products. The quantity of purchase must be less or equal to quantity_in_stock of products.')    

    sale["total"] = sum(
        sale['products'][0]['quantity'] * product['sale_price'] for product in products
    )
    
    # get quantity_in_stock of each one product
    # update each one product just changing the quantity_in_stock property
    for info in sale["products"]:
        sold_quantity = info['quantity']

        # get object on products from id 
        product = next(product for product in products if product["id"] == info['product_id'])

        current_quantity_in_stock = product['quantity_in_stock']

        # decrease sold quantity of quantity_in_stock 
        product_to_update = {
            "quantity_in_stock": current_quantity_in_stock - sold_quantity
        }

        # update the quantity in stock of each product
        update_product(product['id'], product_to_update)
    
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