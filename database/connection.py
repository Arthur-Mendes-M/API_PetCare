import os
from flask import jsonify
from supabase import create_client, Client
from dotenv import load_dotenv

# load environment variables 
load_dotenv()

# create supabase cliente for manage database
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# create all used tables
employee_table = supabase.table('employee')
product_table = supabase.table('product')
client_table = supabase.table('client')

# set bucket variables
petcare_bucket = 'PetCare_Files'
employees_bucket_folder_path = 'Employees'
products_bucket_folder_path = 'Products'
clients_bucket_folder_path = 'Clients'

# create buckets - commented because already exists
# supabase.storage.create_bucket(employees_bucket_folder_path, options={"public": True})
# supabase.storage.create_bucket(products_bucket_folder_path, options={"public": True})
# supabase.storage.create_bucket(clients_bucket_folder_path, options={"public": True})

# set bucket
petcare_bucket = supabase.storage.from_(petcare_bucket)

# create a function for control sql operation - handle to error or success query's
def supabase_operation(operation):
    try:
        return operation.execute().data
    except Exception as e:        
        return {"error": str(e)}
    
def update_file_bucket(bucket, bucket_folder_path, current_file_name, new_file_name, file):
    try:
        # remove old photo 
        bucket.remove(f"{bucket_folder_path}/{current_file_name}")

        # save new photo
        if isinstance(file, bytes):
            file_to_upload = file
        else:
            file_to_upload = file.stream.read()

        result = bucket.upload(f"{bucket_folder_path}/{new_file_name}", file_to_upload)

        if result.status_code == 200:
            return {
                "data": bucket.get_public_url(f"{bucket_folder_path}/{new_file_name}")
            }
        else:
            return {
                "error": "Unable to complete the update"
            }

    except Exception as e:
        return jsonify({"error": str(e)})

def upload_file_bucket():
    return 'Criando'