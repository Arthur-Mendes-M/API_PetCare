from flask import Blueprint, jsonify, request
from database.connection import supabase_operation, client_table, petcare_bucket, clients_bucket_folder_path, update_file_bucket
from lib.flask_bcrypt import encode_password, verify_encoded_password
from routes.patterns import verify_json_header, verify_multipart_header

client_blueprint = Blueprint("clients", __name__, url_prefix="/clients")

@client_blueprint.get('/')
def get_all_client():
    if request.content_length == 0 or request.content_length == None:
        return jsonify(
            supabase_operation(
                client_table
                .select("*")
            )
        )
    
    isJson = verify_json_header(request)
    if isJson:
        return jsonify(isJson)

    client_data = request.json
    email = client_data["email"]
    password = client_data["password"]

    found_client = supabase_operation(
        client_table.select("*").eq('email', email)
    )

    if found_client:
        client = found_client[0]
        encoded_password = client["password"]

        # verify if input password is equal to saved encoded password
        if verify_encoded_password(encoded_password, password):
            return jsonify(
                found_client
            )
        
    return jsonify({
        "error": "email or password is wrong"
    })

@client_blueprint.get('/<id>')
def get_client_by_id(id):
    return jsonify(
            supabase_operation(
            client_table
            .select("*")
            .eq("id", id)
        )
    )

@client_blueprint.post('/')
def save_client():
    isMultipart = verify_multipart_header(request)
    if isMultipart:
        return jsonify(isMultipart)
    
    client = request.form

    client = {
        "name": client.get('name'),
        "email": client.get('email'),
        "password": encode_password(client.get('password'))
    }

    if 'image' in request.files:
        file = request.files['image']
        file_name = client['email']

        result = petcare_bucket.upload(f"{clients_bucket_folder_path}/{file_name}", file.stream.read())

        if result.status_code == 200:
            client["avatarURL"] = petcare_bucket.get_public_url(f"{clients_bucket_folder_path}/{file_name}")
        
    client = {key.lower(): value for key, value in client.items()}

    return jsonify(
        supabase_operation(
            client_table
            .insert(client)
        )
    )

@client_blueprint.put('/<id>')
def update_client(id):
    isMultipart = verify_multipart_header(request)
    if isMultipart:
        return jsonify(isMultipart)
    
    client = request.form

    found_client = client_table.select("*").eq("id", id).execute()

    if not found_client:
        return jsonify(
            found_client
        )
    
    client = {
        "name": client.get('name') if client.get('name') else found_client.data[0]['name'],
        "email": client.get('email') if client.get('email') else found_client.data[0]['email'], 
        "password": encode_password(client.get('password')) if client.get('password') else found_client.data[0]['password']
    }

    if 'image' in request.files:
        file = request.files['image']

        # invoke change photo file 
        current_file_name = found_client.data[0]["email"]
        new_file_name = client["email"]

        updated = update_file_bucket(petcare_bucket, clients_bucket_folder_path, current_file_name, new_file_name, file)

        if 'data' in updated:
            client['avatarURL'] = updated["data"]

    if client.get('email') and found_client.data[0]['avatarurl'] and not 'image' in request.files:
        # change photo file on bucket
        current_file_name = found_client.data[0]['email']
        new_file_name = client.get('email')

        # download current photo (to get file variable)
        file_as_byte = petcare_bucket.download(f"{clients_bucket_folder_path}/{current_file_name}")

        current_file_name = found_client.data[0]["email"]

        client['avatarUrl'] = update_file_bucket(petcare_bucket, clients_bucket_folder_path, current_file_name, new_file_name, file_as_byte)['data']

    client = {key.lower(): value for key, value in client.items()}

    return jsonify(
        supabase_operation(
            client_table
            .update(client)
            .eq("id", id)
        )
    )

@client_blueprint.delete('/<id>')
def delete_client(id):
    found_client = client_table.select("*").eq("id", id).execute().data

    if not found_client:
        return jsonify(
           {
               "error": "Index out of the range"
           }
        )

    supabase_operation(
        client_table
        .delete()
        .eq("id", id)
    )

    file_name = found_client[0]['email']

    all_files_on_employees = petcare_bucket.list(clients_bucket_folder_path)
    for file in all_files_on_employees:
        if file["name"] == file_name:
            petcare_bucket.remove([f'{clients_bucket_folder_path}/{file_name}'])
            break

    return jsonify(
        found_client
    )