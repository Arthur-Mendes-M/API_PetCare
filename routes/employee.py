import os
from flask import Blueprint, jsonify, request
from database.connection import supabase, supabase_operation, bucket_petcare, bucket_employees

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

    return jsonify(
        supabase_operation(
            employee_table.select("*").match({'email': email, 'password': password})
        )
    )

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
        "password": employee.get('password'),
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

    employee = {
        "name": employee.get('name'),
        "email": employee.get('email'), 
        "password": employee.get('password'),
        "role": employee.get('role'),
        "salesCount": employee.get('salesCount')
    }

    if 'image' in request.files:
        file = request.files['image']

        try:
            # look for employee before save ther changes
            found_employee = employee_table.select("*").eq("id", id).execute()
            # get current email from employee
            found_employee_file_name = found_employee.data[0]["email"]

            files_list = bucket.list('Employees')

            file_exists = False
            for file_info in files_list:
                file_name, extension = os.path.splitext(file_info["name"])

                if file_name == found_employee_file_name:
                    file_exists = True
                    break

            if file_exists:
                result = bucket.update(f"{bucket_employees}/{file_name}", file.stream.read())
            else:
                result = bucket.upload(f"{bucket_employees}/{file_name}", file.stream.read())

            if result.status_code == 200:
                employee['avatarUrl'] = bucket.get_public_url(f"{bucket_employees}/{file_name}")
                
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
    deleted_employee = supabase_operation(
        employee_table
        .delete()
        .eq("id", id)
    )

    file_url = deleted_employee['avatarurl']

    if file_url.endswith('?'):
        file_url = file_url[:-1]

    file_name = file_url.split()[-1]

    bucket.remove([f'{bucket_employees}/{file_name}'])
    return jsonify(
        deleted_employee
    )