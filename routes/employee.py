from flask import jsonify, request, Blueprint
from database.connection import supabase_operation, employee_table, petcare_bucket, employees_bucket_folder_path, upload_file_bucket, update_file_bucket
from lib.flask_bcrypt import encode_password, verify_encoded_password
from utils.valid_request_headers import verify_json_header, verify_multipart_header
from werkzeug.exceptions import BadRequest

# set blueprint for employees route
employee_blueprint = Blueprint("employees", __name__, url_prefix="/employees")

# Define get root route
@employee_blueprint.get('/')
def get_all_employees():
    # If not exists request body
    if request.content_length == 0 or request.content_length == None:
        return jsonify(
            supabase_operation(
                employee_table
                .select("*")
            )
        )

    # throw an error if request is not a json
    verify_json_header(request)

    employee_data = request.json
    email = employee_data["email"]
    password = employee_data["password"]

    # query -> look for email eq
    found_employee = supabase_operation(
        employee_table.select("*").eq('email', email)
    )

    if found_employee:
        employee = found_employee[0]
        encoded_password = employee["password"]

        # verify if input password is equal to saved encoded password
        if verify_encoded_password(encoded_password, password):
            return jsonify(
                found_employee
            )

    raise BadRequest("email or password is wrong")
    
@employee_blueprint.get('/<id>')
def get_employee_by_id(id):
    found_employee = supabase_operation(
        employee_table
        .select("*")
        .eq("id", id)
    )

    return jsonify(found_employee)


@employee_blueprint.post('/')
def save_employee():
    # Throw an error if request is not a multipart
    verify_multipart_header(request)

    employee = request.form

    employee = {
        "name": employee.get('name'), 
        "email": employee.get('email'), 
        "password": encode_password(employee.get('password')),
        "role": employee.get('role')
    }

    if 'image' in request.files:
        file = request.files['image']
        file_name = employee['email']
        
        result = upload_file_bucket(file, petcare_bucket, employees_bucket_folder_path, file_name)

        employee['avatar_url'] = result['data']

    employee = {key.lower(): value for key, value in employee.items()}

    return jsonify(
        supabase_operation(
            employee_table
            .insert(employee)
        )
    )

@employee_blueprint.put('/<id>')
def update_employee(id):
    # Throw an error if request is not a multipart
    verify_multipart_header(request)
    
    employee = request.form
    
    # look for employee before save the changes
    found_employee = employee_table.select("*").eq("id", id).execute()

    if not found_employee:
        raise BadRequest('Employee was not found')
    
    employee = {
        "name": employee.get('name') if employee.get('name') else found_employee.data[0]['name'],
        "email": employee.get('email') if employee.get('email') else found_employee.data[0]['email'], 
        "password": encode_password(employee.get('password')) if employee.get('password') else found_employee.data[0]['password'],
        "role": employee.get('role') if employee.get('role') else found_employee.data[0]['role'],
    }

    if 'image' in request.files:
        file = request.files['image']

        # invoke change photo file 
        current_file_name = found_employee.data[0]["email"]
        new_file_name = employee["email"]

        updated = update_file_bucket(petcare_bucket, employees_bucket_folder_path, current_file_name, new_file_name, file)

        employee['avatar_url'] = updated["data"]

    if employee.get('email') and found_employee.data[0]['avatar_url'] and not 'image' in request.files:
        # change photo file on bucket
        current_file_name = found_employee.data[0]['email']
        new_file_name = employee.get('email')

        # download current photo (to get file variable)
        file_as_byte = petcare_bucket.download(f"{employees_bucket_folder_path}/{current_file_name}")

        current_file_name = found_employee.data[0]["email"]

        employee['avatar_url'] = update_file_bucket(petcare_bucket, employees_bucket_folder_path, current_file_name, new_file_name, file_as_byte)['data']

    employee = {key.lower(): value for key, value in employee.items()}

    return jsonify(
        supabase_operation(
            employee_table
            .update(employee)
            .eq("id", id)
        )
    )

@employee_blueprint.delete('/<id>')
def delete_employee(id):
    found_employee = employee_table.select("*").eq("id", id).execute().data

    if not found_employee:
        raise BadRequest('Employee was not found')

    # delete employee
    supabase_operation(
        employee_table
        .delete()
        .eq("id", id)
    )

    file_name = found_employee[0]['email']

    all_files_on_employees = petcare_bucket.list(employees_bucket_folder_path)
    for file in all_files_on_employees:
        if file["name"] == file_name:
            petcare_bucket.remove([f'{employees_bucket_folder_path}/{file_name}'])
            break

    return jsonify(
        found_employee
    )