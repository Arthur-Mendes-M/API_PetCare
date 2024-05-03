import os
from supabase import create_client, Client
from dotenv import load_dotenv
from routes.patterns import validate_image

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
sale_table = supabase.table('sale')

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
    return operation.execute().data

def upload_file_bucket(file, bucket, bucket_folder_path, file_name):

    # verify type of image data
    if isinstance(file, bytes):
        file_to_upload = file
    else:
        file_to_upload = file.stream.read()

    if not validate_image(file_to_upload):
        raise Exception("Something is wrong with the image. Verify if the image is (jpg, jpeg or png) and if the size is less than or equal to 3 megabytes.")

    result = bucket.upload(f"{bucket_folder_path}/{file_name}", file_to_upload)

    if result.status_code == 200:
        return {
            "data": bucket.get_public_url(f"{bucket_folder_path}/{file_name}")
        }
    else:    
        raise Exception("Unable to complete the image update")
        
def update_file_bucket(bucket, bucket_folder_path, current_file_name, new_file_name, file):
    # remove old photo 
    bucket.remove(f"{bucket_folder_path}/{current_file_name}")

    # upload image
    return upload_file_bucket(file, bucket, bucket_folder_path, new_file_name)