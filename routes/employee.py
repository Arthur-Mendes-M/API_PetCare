from flask import Blueprint, jsonify, request
from database.connection import supabase, supabase_operation, bucket_petcare, bucket_employees
from lib.flask_bcrypt import encode_password, verify_encoded_password

# All routes in this file will use the prefix "/employees"
employee_blueprint = Blueprint("employees", __name__, url_prefix="/employees")

# All the operations used here, will use "employees" table
employee_table = supabase.table('employee')

# All the bucket operations use the employee bucket
bucket = supabase.storage.from_(bucket_petcare)

# Define get root route
@employee_blueprint.get("/")
def get_all_employees():
    # If not exists request body
    if request.content_length == 0 or request.content_length == None:
        return jsonify(
            supabase_operation(
                employee_table
                .select("*")
            )
        )

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
    else:
        return jsonify({
            "error": "email or password is wrong"
        })
    

@employee_blueprint.get("/<id>")
def get_employee_by_id(id):
    return jsonify(
            supabase_operation(
            employee_table
            .select("*")
            .eq("id", id)
        )
    )

@employee_blueprint.post("/")
def save_employee():
    employee = request.form

    employee = {
        "name": employee.get('name'), 
        "email": employee.get('email'), 
        "password": encode_password(employee.get('password')),
        "role": employee.get('role'),
        "salesCount": employee.get('salesCount')
    }

    if 'image' in request.files:
        try:
            file = request.files['image']
            file_name = employee['email']

            result = bucket.upload(f"{bucket_employees}/{file_name}", file.stream.read())

            if result.status_code == 200:
                employee['avatarUrl'] = bucket.get_public_url(f"{bucket_employees}/{file_name}")
        except Exception as e:
            return jsonify({"error": str(e)})

    employee = {key.lower(): value for key, value in employee.items()}

    return jsonify(
        supabase_operation(
            employee_table
            .insert(employee)
        )
    )

@employee_blueprint.put("/<id>")
def update_employee(id):
    employee = request.form
    
    # look for employee before save the changes
    found_employee = employee_table.select("*").eq("id", id).execute()

    if not found_employee:
        return jsonify(
            found_employee
        )
    
    employee = {
        "name": employee.get('name'),
        "email": employee.get('email'), 
        "password": encode_password(employee.get('password')),
        "role": employee.get('role'),
        "salesCount": employee.get('salesCount')
    }

    if 'image' in request.files:
        file = request.files['image']

        try:
            # get current email from employee (infos before changes)
            current_file_name = found_employee.data[0]["email"]

            # get new email for name of photo file
            new_file_name = employee["email"]

            # remove old photo 
            bucket.remove(f"{bucket_employees}/{current_file_name}")

            # save new photo
            result = bucket.upload(f"{bucket_employees}/{new_file_name}", file.stream.read())

            if result.status_code == 200:
                employee['avatarUrl'] = bucket.get_public_url(f"{bucket_employees}/{new_file_name}")

        except Exception as e:
            return jsonify({"error": str(e)})

    employee = {key.lower(): value for key, value in employee.items()}

    return jsonify(
        supabase_operation(
            employee_table
            .update(employee)
            .eq("id", id)
        )
    )

@employee_blueprint.delete("/<id>")
def delete_employee(id):
    found_employee = employee_table.select("*").eq("id", id).execute().data

    if not found_employee:
        return jsonify(
           {
               "error": "Index out of the range"
           }
        )

    # delete employee
    supabase_operation(
        employee_table
        .delete()
        .eq("id", id)
    )

    file_name = found_employee[0]['email']

    all_files_on_employees = bucket.list(bucket_employees)
    for file in all_files_on_employees:
        if file["name"] == file_name:
            bucket.remove([f'{bucket_employees}/{file_name}'])
            break

    return jsonify(
        found_employee
    )