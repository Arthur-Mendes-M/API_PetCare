from flask import Blueprint, jsonify, request
from database.connection import supabase_operation, product_table, petcare_bucket, products_bucket_folder_path, update_file_bucket
import uuid
from datetime import datetime
from pytz import timezone

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
    product = request.form
    SP_timezone = timezone("America/Sao_Paulo")
    today = datetime.now().astimezone(SP_timezone)

    product = {
        "name": product.get('name'),
        "code": str(uuid.uuid1()),
        "description": product.get('description'),
        "quantityInStock": product.get('quantityInStock'),
        "salePrice": product.get('salePrice'),
        "purchasePrice": product.get('purchasePrice'),
        "lastRefill": today.strftime("%F %X")
    }

    if 'image' in request.files:
        try:
            file = request.files['image']
            file_name = product['code']

            result = petcare_bucket.upload(f"{products_bucket_folder_path}/{file_name}", file.stream.read())

            if result.status_code == 200:
                product['imageURL'] = petcare_bucket.get_public_url(f"{products_bucket_folder_path}/{file_name}")
        except Exception as e:
            return jsonify({"error": str(e)})

    product = {key.lower(): value for key, value in product.items()}

    return jsonify(
        supabase_operation(
            product_table
            .insert(product)
        )
    )

@product_blueprint.put('/<id>')
def update_product(id):
    product = request.form

    found_product = product_table.select("*").eq("id", id).execute()

    if not found_product:
        return jsonify(
            found_product
        )
    
    SP_timezone = timezone("America/Sao_Paulo")
    today = datetime.now().astimezone(SP_timezone)

    product = {
        "name": product.get('name') if product.get("name") else found_product.data[0]['name'],
        "description": product.get('description') if product.get("description") else found_product.data[0]['description'],
        "quantityInStock": product.get('quantityInStock') if product.get("quantityInStock") else found_product.data[0]['quantityinstock'],
        "salePrice": product.get('salePrice') if product.get("salePrice") else found_product.data[0]['saleprice'],
        "purchasePrice": product.get('purchasePrice') if product.get("purchasePrice") else found_product.data[0]['purchaseprice'],
        "lastRefill": today.strftime("%F %X") if product.get("quantityInStock") else found_product.data[0]['lastrefill']
    }

    if 'image' in request.files:
        file = request.files['image']

        # invoke change photo file 
        current_file_name = found_product.data[0]["code"]
        new_file_name = current_file_name

        updated = update_file_bucket(petcare_bucket, products_bucket_folder_path, current_file_name, new_file_name, file)

        if 'data' in updated:
            product['imageURL'] = updated["data"]
    
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
        return jsonify(
            {
                "error": "Index out of the range"
            }
        )

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