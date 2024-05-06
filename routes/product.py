from flask import Blueprint, jsonify, request
from database.connection import supabase_operation, product_table, petcare_bucket, products_bucket_folder_path, upload_file_bucket, update_file_bucket
import uuid
from datetime import datetime
from pytz import timezone
from utils.valid_request_headers import verify_multipart_header
from werkzeug.exceptions import BadRequest

# set blueprint for products route
product_blueprint = Blueprint("products", __name__, url_prefix="/products")

# set get root route
@product_blueprint.get('/')
def get_all_products():
    return jsonify(
        supabase_operation(
            product_table
            .select("*")
        )
    )

@product_blueprint.get('/<id>')
def get_product_by_id(id):
    return jsonify(
        supabase_operation(
            product_table
            .select("*")
            .eq("id", id)
        )
    )

@product_blueprint.post('/')
def save_product():
    # Throw an error if request is not a multipart
    verify_multipart_header(request)
    
    product = request.form
    SP_timezone = timezone("America/Sao_Paulo")
    today = datetime.now().astimezone(SP_timezone)

    product = {
        "name": product.get('name'),
        "code": str(uuid.uuid1()),
        "description": product.get('description'),
        "quantity_in_stock": product.get('quantity_in_stock'),
        "sale_price": product.get('sale_price'),
        "purchase_price": product.get('purchase_price'),
        "last_refill": today.strftime("%F %X")
    }

    if 'image' in request.files:
        file = request.files['image']
        file_name = product['code']

        result = upload_file_bucket(file, petcare_bucket, products_bucket_folder_path, file_name)

        product['image_url'] = result['data']

    product = {key.lower(): value for key, value in product.items()}

    return jsonify(
        supabase_operation(
            product_table
            .insert(product)
        )
    )

@product_blueprint.put('/<id>')
def update_product(id, product=None):
    # Throw an error if request is not a multipart
    verify_multipart_header(request)
    
    product = product if product else request.form

    found_product = product_table.select("*").eq("id", id).execute()

    if not found_product:
        raise BadRequest('Product was not found')
    
    SP_timezone = timezone("America/Sao_Paulo")
    today = datetime.now().astimezone(SP_timezone)

    product = {
        "name": product.get('name') if product.get("name") else found_product.data[0]['name'],
        "description": product.get('description') if product.get("description") else found_product.data[0]['description'],
        "quantity_in_stock": product.get('quantity_in_stock') if product.get("quantity_in_stock") or product.get("quantity_in_stock") == 0 else found_product.data[0]['quantity_in_stock'],
        "sale_price": product.get('sale_price') if product.get("sale_price") else found_product.data[0]['sale_price'],
        "purchase_price": product.get('purchase_price') if product.get("purchase_price") else found_product.data[0]['purchase_price'],
        "last_refill": today.strftime("%F %X") if product.get("quantity_in_stock") else found_product.data[0]['last_refill']
    }

    if 'image' in request.files:
        file = request.files['image']

        # invoke change photo file 
        current_file_name = found_product.data[0]["code"]
        new_file_name = current_file_name

        updated = update_file_bucket(petcare_bucket, products_bucket_folder_path, current_file_name, new_file_name, file)

        product['image_url'] = updated["data"]
    
    product = {key.lower(): value for key, value in product.items()}

    return jsonify(
        supabase_operation(
            product_table
            .update(product)
            .eq("id", id)
        )
    )

@product_blueprint.delete('<id>')
def delete_product(id):
    found_product = product_table.select("*").eq("id", id).execute().data

    if not found_product:
        raise BadRequest('Product was not found')

    supabase_operation(
        product_table
        .delete()
        .eq("id", id)
    )

    file_name = found_product[0]['code']

    all_files_on_products = petcare_bucket.list(products_bucket_folder_path)

    for file in all_files_on_products:
        if file["name"] == file_name:
            petcare_bucket.remove([f'{products_bucket_folder_path}/{file_name}'])
            break

    return jsonify(
        found_product
    )