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
    query_parameters = request.args
    completed = query_parameters.get('completed')

    if not completed or completed != 'true':
        return jsonify(
            supabase_operation(
                sale_table
                .select('*')
            )
        )

    completed_sales = supabase_operation(
        sale_table
        .select('*, client(*)')
    )
    
    for sale in completed_sales:
        sale_index = completed_sales.index(sale)

        for product in sale['products']:
            product_index = sale['products'].index(product)
            found_product = json.loads(get_product_by_id(product['product_id']).get_data(True))[0]

            completed_sales[sale_index]['products'][product_index] = {
                **completed_sales[sale_index]['products'][product_index],
                "product": found_product
            }

    return jsonify(completed_sales)
    
@sale_blueprint.get('/<id>')
def get_sale_by_id(id):
    query_parameters = request.args
    completed = query_parameters.get('completed')

    if not completed or completed != 'true':
        return jsonify(
            supabase_operation(
                sale_table
                .select("*")
                .eq("id", id)
            )
        )

    completed_sale = supabase_operation(
        sale_table
        .select('*, client(*)')
        .eq("id", id)
    )[0]
    
    for product in completed_sale['products']:
        product_index = completed_sale['products'].index(product)
        found_product = json.loads(get_product_by_id(product['product_id']).get_data(True))[0]

        completed_sale['products'][product_index] = {
            **completed_sale['products'][product_index],
            "product": found_product
        }

    return jsonify(completed_sale)

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
        "total": 0
    }

    products = {
        product['product_id']: json.loads(get_product_by_id(product['product_id']).get_data(True))[0] for product in sale['products']
    }

    for sold_product_info in sale['products']:
        sold_product_id = sold_product_info['product_id']

        sold_quantity = sold_product_info['quantity']
        sold_product_price = products[sold_product_id]['sale_price']

        calculated_current_sold_product = sum([sold_quantity * sold_product_price])

        if calculated_current_sold_product < 0:
            raise BadRequest('Wrong quantities on sold products. The quantity of purchase must be less or equal to quantity_in_stock of products.')
        
        sale['total'] += calculated_current_sold_product

    # # get quantity_in_stock of each one product
    # # update each one product just changing the quantity_in_stock property
    for sold_product_info in sale["products"]:
        sold_quantity = sold_product_info['quantity']
        sold_product_id = sold_product_info['product_id']

        product = products[sold_product_id]
        current_quantity_in_stock = product['quantity_in_stock']

        # decrease sold quantity of quantity_in_stock 
        product_to_update = {
            "quantity_in_stock": current_quantity_in_stock - sold_quantity
        }

        # update the quantity in stock of each product
        update_product(sold_product_id, product_to_update)
    
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