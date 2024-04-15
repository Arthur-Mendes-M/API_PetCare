from flask import Blueprint, jsonify, request
from database.connection import supabase, supabase_operation, bucket, bucket_employees

# All routes in this file will use the prefix "/employees"
employee_blueprint = Blueprint("employees", __name__, url_prefix="/employees")

# All the operations used here, will use "employees" table
employee_table = supabase.table('employee')

# All the bucket operations use the employee bucket
bucket = supabase.storage.from_(bucket)

# Define get root route
@employee_blueprint.get("/")
def get_all_employees():
    # Transform the object (sql or error) on json
    return jsonify(
        supabase_operation(
            employee_table
            .select("*")
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

    print(request)

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
            file_name = f"{employee['email']}_{file.filename}"

            result = bucket.upload(f"{bucket_employees}/{file_name}", file.stream.read())

            if result.status_code == 200:
                employee['avatarUrl'] = bucket.get_public_url(file_name)
        except Exception as e:
            return jsonify({"error": str(e)})

    employee = {key.lower(): value for key, value in employee.items()}

    print(employee)

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
        print(f"have image {request.files}")
        try:
            file = request.files['image']
            file_name = f"{employee['email']}_{file.filename}"

            file_list = bucket.list()

            file_exists = any(file_info['name'] == file_name for file_info in file_list)

            if file_exists:
                result = bucket.update(f"{bucket_employees}/{file_name}", file.stream.read())

            else:
                result = bucket.upload(f"{bucket_employees}/{file_name}", file.stream.read())

            if result.status_code == 200:
                employee['avatarUrl'] = bucket.get_public_url(file_name)
                
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